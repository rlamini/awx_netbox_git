#!/usr/bin/env python3
"""
NetBox to Zabbix Synchronization Script

Synchronizes network devices from NetBox (Source of Truth) to Zabbix (Monitoring).

Features:
- Automatic host creation in Zabbix from NetBox devices
- Template mapping based on device type, platform, and role
- Host group organization by site, role, and platform
- SNMP interface configuration
- Host macros for integration metadata
- Dry-run mode for testing
- Incremental sync support

Usage:
    python3 sync_netbox_to_zabbix.py --mode full
    python3 sync_netbox_to_zabbix.py --mode site --site "EMEA-DC-ONPREM"
    python3 sync_netbox_to_zabbix.py --dry-run

Requirements:
    pip3 install pynetbox pyzabbix pyyaml requests

Author: NetOps Team
Version: 1.0
"""

import os
import sys
import argparse
import logging
import yaml
from datetime import datetime
from typing import Dict, List, Optional, Tuple

try:
    import pynetbox
    from pyzabbix import ZabbixAPI, ZabbixAPIException
except ImportError as e:
    print(f"ERROR: Missing required library: {e}")
    print("Please install: pip3 install pynetbox pyzabbix pyyaml")
    sys.exit(1)


class NetBoxZabbixSync:
    """Main synchronization class"""

    def __init__(self, config_file: str = "config.yaml", mapping_file: str = "lab/zabbix/zabbix_mapping.yaml", dry_run: bool = False):
        """
        Initialize sync manager

        Args:
            config_file: Path to configuration file
            mapping_file: Path to mapping configuration
            dry_run: If True, only show what would be done without making changes
        """
        self.dry_run = dry_run
        self.config = self.load_config(config_file)
        self.mapping = self.load_mapping(mapping_file)

        # Setup logging
        self.setup_logging()

        # Connect to APIs
        self.nb = None
        self.zabbix = None

        # Statistics
        self.stats = {
            'devices_found': 0,
            'devices_created': 0,
            'devices_updated': 0,
            'devices_skipped': 0,
            'errors': 0
        }

    def load_config(self, config_file: str) -> Dict:
        """Load configuration from file or environment variables"""
        config = {
            'netbox': {
                'url': os.getenv('NETBOX_URL', 'https://netbox.acme.com'),
                'token': os.getenv('NETBOX_TOKEN', ''),
                'verify_ssl': os.getenv('NETBOX_VERIFY_SSL', 'true').lower() == 'true'
            },
            'zabbix': {
                'url': os.getenv('ZABBIX_URL', 'https://zabbix.acme.com'),
                'user': os.getenv('ZABBIX_USER', 'admin'),
                'password': os.getenv('ZABBIX_PASSWORD', 'zabbix'),
                'verify_ssl': os.getenv('ZABBIX_VERIFY_SSL', 'true').lower() == 'true'
            },
            'monitoring': {
                'snmp_community': os.getenv('SNMP_COMMUNITY', 'public')
            }
        }

        # Override with config file if exists
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    config.update(file_config)

        return config

    def load_mapping(self, mapping_file: str) -> Dict:
        """Load template and host group mapping configuration"""
        if not os.path.exists(mapping_file):
            self.logger.error(f"Mapping file not found: {mapping_file}")
            sys.exit(1)

        with open(mapping_file, 'r') as f:
            return yaml.safe_load(f)

    def setup_logging(self):
        """Configure logging"""
        log_config = self.mapping.get('sync', {}).get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_format = log_config.get('format', '%(asctime)s - %(levelname)s - %(message)s')

        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[logging.StreamHandler()]
        )

        self.logger = logging.getLogger(__name__)

        if self.dry_run:
            self.logger.info("=" * 70)
            self.logger.info("DRY RUN MODE - No changes will be made to Zabbix")
            self.logger.info("=" * 70)

    def connect_netbox(self):
        """Connect to NetBox API"""
        try:
            self.logger.info(f"Connecting to NetBox: {self.config['netbox']['url']}")
            self.nb = pynetbox.api(
                url=self.config['netbox']['url'],
                token=self.config['netbox']['token']
            )

            # Disable SSL verification if configured
            if not self.config['netbox'].get('verify_ssl', True):
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                self.nb.http_session.verify = False

            # Test connection
            devices_count = len(list(self.nb.dcim.devices.all()))
            self.logger.info(f"✅ Connected to NetBox ({devices_count} devices total)")

        except Exception as e:
            self.logger.error(f"❌ Failed to connect to NetBox: {e}")
            sys.exit(1)

    def connect_zabbix(self):
        """Connect to Zabbix API"""
        try:
            self.logger.info(f"Connecting to Zabbix: {self.config['zabbix']['url']}")

            # Ensure URL ends with /api_jsonrpc.php
            zabbix_url = self.config['zabbix']['url']
            if not zabbix_url.endswith('/api_jsonrpc.php'):
                if zabbix_url.endswith('/'):
                    zabbix_url += 'api_jsonrpc.php'
                else:
                    zabbix_url += '/api_jsonrpc.php'

            self.zabbix = ZabbixAPI(zabbix_url)

            # Disable SSL verification if configured
            if not self.config['zabbix'].get('verify_ssl', True):
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                self.zabbix.session.verify = False

            # Login
            self.zabbix.login(
                self.config['zabbix']['user'],
                self.config['zabbix']['password']
            )

            # Get Zabbix version
            version = self.zabbix.apiinfo.version()
            self.logger.info(f"✅ Connected to Zabbix (version {version})")

        except ZabbixAPIException as e:
            self.logger.error(f"❌ Failed to connect to Zabbix: {e}")
            sys.exit(1)

    def get_devices_from_netbox(self, site_name: Optional[str] = None) -> List:
        """
        Fetch devices from NetBox

        Args:
            site_name: If provided, only fetch devices from this site

        Returns:
            List of NetBox device objects
        """
        filters = {}

        # Filter by allowed statuses
        allowed_statuses = self.mapping.get('sync', {}).get('filters', {}).get('allowed_statuses', ['active'])
        if allowed_statuses:
            filters['status'] = allowed_statuses

        # Filter by custom field for monitoring
        custom_field_config = self.mapping.get('sync', {}).get('filters', {}).get('custom_field_monitoring')
        if custom_field_config:
            field_name = custom_field_config.get('field_name')
            # Support both single value (old config) and multiple values (new config)
            field_values = custom_field_config.get('field_values') or [custom_field_config.get('field_value')]
            field_values = [v for v in field_values if v]  # Remove None/empty values

            if field_name and field_values:
                # NetBox API doesn't support OR filters easily, so we'll filter post-fetch
                # Just log what we're looking for
                self.logger.info(f"Filtering by custom field: {field_name} in {field_values}")

        # Filter by site if specified
        if site_name:
            filters['site'] = site_name
        elif self.mapping.get('sync', {}).get('filters', {}).get('allowed_sites'):
            filters['site'] = self.mapping['sync']['filters']['allowed_sites']

        # Exclude specific sites
        excluded_sites = self.mapping.get('sync', {}).get('filters', {}).get('excluded_sites', [])

        self.logger.info(f"Fetching devices from NetBox (filters: {filters})")

        devices = list(self.nb.dcim.devices.filter(**filters))

        # Filter out excluded sites
        if excluded_sites:
            devices = [d for d in devices if d.site.name not in excluded_sites]

        # Filter out excluded tags
        excluded_tags = self.mapping.get('sync', {}).get('filters', {}).get('excluded_tags', [])
        if excluded_tags:
            devices = [d for d in devices if not any(tag.name in excluded_tags for tag in d.tags)]

        # Additional validation: check custom field if configured (double-check)
        if custom_field_config:
            field_name = custom_field_config.get('field_name')
            # Support both single value (old config) and multiple values (new config)
            field_values = custom_field_config.get('field_values') or [custom_field_config.get('field_value')]
            field_values = [v for v in field_values if v]  # Remove None/empty values

            if field_name and field_values:
                # Filter devices that don't have the custom field or have value not in allowed list
                original_count = len(devices)
                devices = [
                    d for d in devices
                    if d.custom_fields.get(field_name) in field_values
                ]
                filtered_count = original_count - len(devices)
                if filtered_count > 0:
                    self.logger.info(f"Filtered out {filtered_count} devices without {field_name} in {field_values}")

        self.stats['devices_found'] = len(devices)
        self.logger.info(f"Found {len(devices)} devices to sync")

        return devices

    def get_template_for_device(self, device) -> str:
        """
        Determine Zabbix template for a NetBox device

        Priority:
        1. Device type specific
        2. Platform + Role combination
        3. Platform
        4. Role
        5. Manufacturer
        6. Default

        Args:
            device: NetBox device object

        Returns:
            Zabbix template name
        """
        templates_config = self.mapping.get('templates', {})

        # 1. Device type mapping (highest priority)
        if device.device_type:
            device_type_map = templates_config.get('device_type_mapping', {})
            template = device_type_map.get(device.device_type.model)
            if template:
                self.logger.debug(f"Template from device_type: {template}")
                return template

        # 2. Platform + Role combination
        if device.platform and device.device_role:
            platform_role_map = templates_config.get('platform_role_mapping', {})
            combo_key = f"{device.platform.name}+{device.device_role.name}"
            template = platform_role_map.get(combo_key)
            if template:
                self.logger.debug(f"Template from platform+role: {template}")
                return template

        # 3. Platform mapping
        if device.platform:
            platform_map = templates_config.get('platform_mapping', {})
            template = platform_map.get(device.platform.name)
            if template:
                self.logger.debug(f"Template from platform: {template}")
                return template

        # 4. Role mapping
        if device.device_role:
            role_map = templates_config.get('role_mapping', {})
            template = role_map.get(device.device_role.name)
            if template:
                self.logger.debug(f"Template from role: {template}")
                return template

        # 5. Manufacturer mapping
        if device.device_type and device.device_type.manufacturer:
            manufacturer_map = templates_config.get('manufacturer_mapping', {})
            template = manufacturer_map.get(device.device_type.manufacturer.name)
            if template:
                self.logger.debug(f"Template from manufacturer: {template}")
                return template

        # 6. Default template
        default_template = templates_config.get('default_template', 'Template Net Device SNMP')
        self.logger.debug(f"Using default template: {default_template}")
        return default_template

    def get_host_groups_for_device(self, device) -> List[str]:
        """
        Determine Zabbix host groups for a NetBox device

        Args:
            device: NetBox device object

        Returns:
            List of host group names
        """
        groups = []
        hg_config = self.mapping.get('host_groups', {})

        # Global group
        global_group = hg_config.get('global_group', 'All Devices')
        groups.append(global_group)

        # Site group
        if device.site and hg_config.get('auto_create_site_groups', True):
            site_prefix = hg_config.get('site_prefix', 'Site')
            groups.append(f"{site_prefix}: {device.site.name}")

        # Role group
        if device.device_role and hg_config.get('auto_create_role_groups', True):
            role_prefix = hg_config.get('role_prefix', 'Role')
            groups.append(f"{role_prefix}: {device.device_role.name}")

        # Platform group
        if device.platform and hg_config.get('auto_create_platform_groups', True):
            platform_prefix = hg_config.get('platform_prefix', 'Platform')
            groups.append(f"{platform_prefix}: {device.platform.name}")

        # Tag groups
        if device.tags and hg_config.get('auto_create_tag_groups', True):
            allowed_tags = hg_config.get('allowed_tags', [])
            tag_prefix = hg_config.get('tag_prefix', 'Tag')

            for tag in device.tags:
                # If allowed_tags is empty, allow all tags
                if not allowed_tags or tag.name in allowed_tags:
                    groups.append(f"{tag_prefix}: {tag.name}")

        return groups

    def get_or_create_host_group(self, group_name: str) -> Optional[str]:
        """
        Get host group ID or create if it doesn't exist

        Args:
            group_name: Name of host group

        Returns:
            Host group ID or None if failed
        """
        if self.dry_run:
            return "DRY-RUN-GROUP-ID"

        try:
            # Check if group exists
            groups = self.zabbix.hostgroup.get(filter={'name': group_name})

            if groups:
                return groups[0]['groupid']

            # Create group
            self.logger.info(f"Creating host group: {group_name}")
            result = self.zabbix.hostgroup.create(name=group_name)
            return result['groupids'][0]

        except ZabbixAPIException as e:
            self.logger.error(f"Failed to get/create host group '{group_name}': {e}")
            return None

    def get_template_id(self, template_name: str) -> Optional[str]:
        """
        Get Zabbix template ID by name

        Args:
            template_name: Template name

        Returns:
            Template ID or None if not found
        """
        if self.dry_run:
            return "DRY-RUN-TEMPLATE-ID"

        try:
            templates = self.zabbix.template.get(filter={'host': template_name})
            if templates:
                return templates[0]['templateid']
            else:
                self.logger.warning(f"Template not found: {template_name}")
                return None

        except ZabbixAPIException as e:
            self.logger.error(f"Failed to get template '{template_name}': {e}")
            return None

    def sync_device_to_zabbix(self, device) -> bool:
        """
        Sync a single device to Zabbix

        Args:
            device: NetBox device object

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate device has primary IP
            if not device.primary_ip4:
                self.logger.warning(f"Skipping {device.name}: No primary IPv4 address")
                self.stats['devices_skipped'] += 1
                return False

            # Extract IP address (remove CIDR mask)
            ip_address = str(device.primary_ip4).split('/')[0]

            # Get template
            template_name = self.get_template_for_device(device)
            template_id = self.get_template_id(template_name)

            if not template_id and not self.dry_run:
                self.logger.warning(f"Skipping {device.name}: Template '{template_name}' not found")
                self.stats['devices_skipped'] += 1
                return False

            # Get host groups
            group_names = self.get_host_groups_for_device(device)
            group_ids = []

            for group_name in group_names:
                group_id = self.get_or_create_host_group(group_name)
                if group_id:
                    group_ids.append({'groupid': group_id})

            if not group_ids and not self.dry_run:
                self.logger.error(f"Failed to get/create host groups for {device.name}")
                self.stats['errors'] += 1
                return False

            # Check if host exists
            existing_hosts = [] if self.dry_run else self.zabbix.host.get(filter={'host': device.name})

            # Determine host status based on cf_monitoring custom field
            # cf_monitoring = "Yes" → status = 0 (enabled/monitored)
            # cf_monitoring = "No" → status = 1 (disabled/not monitored)
            cf_monitoring = device.custom_fields.get('cf_monitoring', 'Yes')
            host_status = 0 if cf_monitoring == 'Yes' else 1
            status_text = "enabled" if host_status == 0 else "disabled"

            # Prepare host data
            host_data = {
                'host': device.name,
                'name': device.name,
                'status': host_status,
                'groups': group_ids,
                'templates': [{'templateid': template_id}] if template_id else [],
                'interfaces': [{
                    'type': 2,  # SNMP
                    'main': 1,
                    'useip': 1,
                    'ip': ip_address,
                    'dns': '',
                    'port': self.mapping.get('monitoring', {}).get('snmp', {}).get('port', '161'),
                    'details': {
                        'version': 2,  # SNMPv2
                        'community': '{$SNMP_COMMUNITY}'
                    }
                }],
                'macros': [
                    {'macro': '{$SNMP_COMMUNITY}', 'value': self.mapping.get('monitoring', {}).get('snmp', {}).get('community', 'public')},
                    {'macro': '{$NETBOX_SITE}', 'value': device.site.name if device.site else ''},
                    {'macro': '{$NETBOX_ROLE}', 'value': device.device_role.name if device.device_role else ''},
                    {'macro': '{$NETBOX_DEVICE_ID}', 'value': str(device.id)},
                ]
            }

            if self.dry_run:
                if existing_hosts:
                    self.logger.info(f"[DRY-RUN] Would UPDATE host: {device.name} (IP: {ip_address}, Template: {template_name}, Groups: {len(group_names)}, Status: {status_text})")
                    self.stats['devices_updated'] += 1
                else:
                    self.logger.info(f"[DRY-RUN] Would CREATE host: {device.name} (IP: {ip_address}, Template: {template_name}, Groups: {len(group_names)}, Status: {status_text})")
                    self.stats['devices_created'] += 1
                return True

            # Create or update host
            if existing_hosts:
                # Update existing host
                host_data['hostid'] = existing_hosts[0]['hostid']
                self.zabbix.host.update(host_data)
                self.logger.info(f"✅ Updated host: {device.name} (cf_monitoring={cf_monitoring}, status={status_text})")
                self.stats['devices_updated'] += 1
            else:
                # Create new host
                self.zabbix.host.create(host_data)
                self.logger.info(f"✅ Created host: {device.name} (cf_monitoring={cf_monitoring}, status={status_text})")
                self.stats['devices_created'] += 1

            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to sync {device.name}: {e}")
            self.stats['errors'] += 1
            return False

    def sync(self, mode: str = 'full', site_name: Optional[str] = None):
        """
        Main synchronization method

        Args:
            mode: Sync mode (full, site, incremental)
            site_name: Site name for site-specific sync
        """
        self.logger.info("=" * 70)
        self.logger.info("Starting NetBox to Zabbix Synchronization")
        self.logger.info("=" * 70)

        # Connect to APIs
        self.connect_netbox()
        self.connect_zabbix()

        # Get devices
        devices = self.get_devices_from_netbox(site_name=site_name)

        if not devices:
            self.logger.warning("No devices found to sync")
            return

        # Sync each device
        self.logger.info(f"Syncing {len(devices)} devices...")
        for device in devices:
            self.sync_device_to_zabbix(device)

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print sync summary statistics"""
        self.logger.info("=" * 70)
        self.logger.info("Synchronization Complete")
        self.logger.info("=" * 70)
        self.logger.info(f"Devices found:   {self.stats['devices_found']}")
        self.logger.info(f"Devices created: {self.stats['devices_created']}")
        self.logger.info(f"Devices updated: {self.stats['devices_updated']}")
        self.logger.info(f"Devices skipped: {self.stats['devices_skipped']}")
        self.logger.info(f"Errors:          {self.stats['errors']}")
        self.logger.info("=" * 70)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Synchronize devices from NetBox to Zabbix',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full sync of all devices
  python3 sync_netbox_to_zabbix.py --mode full

  # Sync specific site
  python3 sync_netbox_to_zabbix.py --mode site --site "EMEA-DC-ONPREM"

  # Dry run (test without making changes)
  python3 sync_netbox_to_zabbix.py --dry-run

  # Test API connections
  python3 sync_netbox_to_zabbix.py --test-connection
        """
    )

    parser.add_argument('--mode', choices=['full', 'site', 'incremental'], default='full',
                        help='Sync mode (default: full)')
    parser.add_argument('--site', help='Site name for site-specific sync')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without making changes')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    parser.add_argument('--config', default='config.yaml',
                        help='Config file path (default: config.yaml)')
    parser.add_argument('--mapping', default='lab/zabbix/zabbix_mapping.yaml',
                        help='Mapping file path (default: lab/zabbix/zabbix_mapping.yaml)')
    parser.add_argument('--test-connection', action='store_true',
                        help='Test API connections and exit')

    args = parser.parse_args()

    # Create sync manager
    syncer = NetBoxZabbixSync(
        config_file=args.config,
        mapping_file=args.mapping,
        dry_run=args.dry_run
    )

    # Test connection mode
    if args.test_connection:
        syncer.connect_netbox()
        syncer.connect_zabbix()
        print("\n✅ All connections successful!")
        sys.exit(0)

    # Run sync
    if args.mode == 'site' and not args.site:
        parser.error("--site is required when mode is 'site'")

    syncer.sync(mode=args.mode, site_name=args.site)


if __name__ == '__main__':
    main()
