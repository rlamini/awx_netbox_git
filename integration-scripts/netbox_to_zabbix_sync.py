#!/usr/bin/env python3
"""
NetBox to Zabbix Synchronization Script
========================================

This script synchronizes devices from NetBox to Zabbix for monitoring.

Features:
- Creates/Updates hosts in Zabbix based on NetBox devices
- Organizes hosts into groups based on NetBox sites
- Supports tag-based grouping
- Handles IP addresses (IPv4/IPv6)
- Applies Zabbix templates

Requirements:
  pip install pynetbox pyzabbix requests

Usage:
  python3 netbox_to_zabbix_sync.py

Author: Integration Script
License: MIT
"""

import sys
import os
from pynetbox import api as netbox_api
from pyzabbix import ZabbixAPI
import logging
from datetime import datetime

# ============================================
# CONFIGURATION
# ============================================

# NetBox Configuration
NETBOX_URL = os.getenv('NETBOX_URL', 'http://localhost:8000')
NETBOX_TOKEN = os.getenv('NETBOX_TOKEN', 'your_netbox_token_here')

# Zabbix Configuration
ZABBIX_URL = os.getenv('ZABBIX_URL', 'http://localhost:8080')
ZABBIX_USER = os.getenv('ZABBIX_USER', 'Admin')
ZABBIX_PASSWORD = os.getenv('ZABBIX_PASSWORD', 'zabbix')

# Default Settings
DEFAULT_HOST_GROUP = "NetBox Devices"
DEFAULT_TEMPLATE = "Linux by Zabbix agent"
ZABBIX_AGENT_PORT = 10050

# Logging Configuration
LOG_FILE = os.getenv('LOG_FILE', '/var/log/netbox-zabbix-sync.log')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# ============================================
# LOGGING SETUP
# ============================================

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================
# MAIN CLASS
# ============================================

class NetBoxZabbixSync:
    """Synchronizes devices from NetBox to Zabbix"""

    def __init__(self):
        """Initialize API connections"""
        self.stats = {
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }

        try:
            logger.info("=" * 60)
            logger.info("NetBox to Zabbix Synchronization Started")
            logger.info("=" * 60)

            # Connect to NetBox
            logger.info(f"Connecting to NetBox at {NETBOX_URL}...")
            self.netbox = netbox_api(NETBOX_URL, token=NETBOX_TOKEN)

            # Test NetBox connection
            _ = self.netbox.status()
            logger.info("✅ NetBox connection successful")

            # Connect to Zabbix
            logger.info(f"Connecting to Zabbix at {ZABBIX_URL}...")
            self.zabbix = ZabbixAPI(ZABBIX_URL)
            self.zabbix.login(ZABBIX_USER, ZABBIX_PASSWORD)
            logger.info("✅ Zabbix connection successful")

        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            sys.exit(1)

    def get_or_create_host_group(self, group_name):
        """Get or create a Zabbix host group"""
        try:
            # Search for existing group
            groups = self.zabbix.hostgroup.get(filter={"name": group_name})

            if groups:
                return groups[0]['groupid']

            # Create group if it doesn't exist
            logger.info(f"Creating host group: {group_name}")
            result = self.zabbix.hostgroup.create(name=group_name)
            return result['groupids'][0]

        except Exception as e:
            logger.error(f"Error creating group {group_name}: {e}")
            return None

    def get_template_id(self, template_name):
        """Get Zabbix template ID by name"""
        try:
            templates = self.zabbix.template.get(filter={"host": template_name})

            if templates:
                return templates[0]['templateid']

            logger.warning(f"Template {template_name} not found")
            return None

        except Exception as e:
            logger.error(f"Error getting template: {e}")
            return None

    def get_device_ip(self, device):
        """Extract IP address from NetBox device"""
        if device.primary_ip4:
            return str(device.primary_ip4).split('/')[0]
        elif device.primary_ip6:
            return str(device.primary_ip6).split('/')[0]
        return None

    def sync_devices(self, filter_site=None, filter_status='active'):
        """
        Synchronize devices from NetBox to Zabbix

        Args:
            filter_site: Filter by NetBox site name (optional)
            filter_status: Device status filter (default: 'active')
        """
        try:
            logger.info("🔄 Starting device synchronization...")

            # Build filter
            filter_params = {'status': filter_status}
            if filter_site:
                filter_params['site'] = filter_site

            # Get devices from NetBox
            devices = list(self.netbox.dcim.devices.filter(**filter_params))
            logger.info(f"📦 Found {len(devices)} devices in NetBox")

            # Get default template ID
            template_id = self.get_template_id(DEFAULT_TEMPLATE)

            for device in devices:
                try:
                    self._sync_single_device(device, template_id)
                except Exception as e:
                    logger.error(f"❌ Error syncing {device.name}: {e}")
                    self.stats['errors'] += 1

            # Print summary
            self._print_summary()

        except Exception as e:
            logger.error(f"❌ Synchronization failed: {e}")
            raise

    def _sync_single_device(self, device, template_id):
        """Synchronize a single device to Zabbix"""
        device_name = device.name

        # Get IP address
        device_ip = self.get_device_ip(device)
        if not device_ip:
            logger.warning(f"⚠️  {device_name}: No IP address - skipped")
            self.stats['skipped'] += 1
            return

        # Determine group based on NetBox site
        if device.site:
            group_name = f"NetBox - {device.site.name}"
        else:
            group_name = DEFAULT_HOST_GROUP

        group_id = self.get_or_create_host_group(group_name)
        if not group_id:
            logger.error(f"❌ {device_name}: Cannot create group")
            self.stats['errors'] += 1
            return

        # Check if host already exists
        existing_hosts = self.zabbix.host.get(filter={"host": device_name})

        # Prepare interface configuration
        interface = {
            "type": 1,  # Zabbix agent
            "main": 1,
            "useip": 1,
            "ip": device_ip,
            "dns": "",
            "port": str(ZABBIX_AGENT_PORT)
        }

        if existing_hosts:
            # Update existing host
            host_id = existing_hosts[0]['hostid']

            update_params = {
                "hostid": host_id,
                "host": device_name,
                "interfaces": [interface],
                "groups": [{"groupid": group_id}]
            }

            self.zabbix.host.update(**update_params)
            logger.info(f"🔄 {device_name} ({device_ip}) - Updated")
            self.stats['updated'] += 1

        else:
            # Create new host
            create_params = {
                "host": device_name,
                "interfaces": [interface],
                "groups": [{"groupid": group_id}]
            }

            # Add template if available
            if template_id:
                create_params["templates"] = [{"templateid": template_id}]

            self.zabbix.host.create(**create_params)
            logger.info(f"✅ {device_name} ({device_ip}) - Created")
            self.stats['created'] += 1

    def sync_with_tags(self):
        """Advanced synchronization with NetBox tags support"""
        logger.info("🔄 Synchronization with tags...")

        devices = list(self.netbox.dcim.devices.filter(status='active'))

        for device in devices:
            try:
                device_name = device.name
                device_ip = self.get_device_ip(device)

                if not device_ip:
                    continue

                # Build group list based on tags
                group_ids = []

                if device.tags:
                    for tag in device.tags:
                        group_name = f"NetBox Tag - {tag.name}"
                        group_id = self.get_or_create_host_group(group_name)
                        if group_id:
                            group_ids.append({"groupid": group_id})

                # Add default group
                default_group_id = self.get_or_create_host_group(DEFAULT_HOST_GROUP)
                if default_group_id:
                    group_ids.append({"groupid": default_group_id})

                # Check if exists
                existing_hosts = self.zabbix.host.get(filter={"host": device_name})

                interface = {
                    "type": 1,
                    "main": 1,
                    "useip": 1,
                    "ip": device_ip,
                    "dns": "",
                    "port": str(ZABBIX_AGENT_PORT)
                }

                if existing_hosts:
                    # Update
                    host_id = existing_hosts[0]['hostid']
                    self.zabbix.host.update(
                        hostid=host_id,
                        groups=group_ids,
                        interfaces=[interface]
                    )
                    logger.info(f"🔄 {device_name} - Tags updated")
                    self.stats['updated'] += 1
                else:
                    # Create
                    self.zabbix.host.create(
                        host=device_name,
                        interfaces=[interface],
                        groups=group_ids
                    )
                    logger.info(f"✅ {device_name} - Created with tags")
                    self.stats['created'] += 1

            except Exception as e:
                logger.error(f"❌ Error for {device.name}: {e}")
                self.stats['errors'] += 1

    def _print_summary(self):
        """Print synchronization summary"""
        logger.info("=" * 60)
        logger.info("📊 Synchronization Summary:")
        logger.info(f"   ✅ Created:  {self.stats['created']}")
        logger.info(f"   🔄 Updated:  {self.stats['updated']}")
        logger.info(f"   ⚠️  Skipped:  {self.stats['skipped']}")
        logger.info(f"   ❌ Errors:   {self.stats['errors']}")
        logger.info(f"   📈 Total:    {sum(self.stats.values())}")
        logger.info("=" * 60)

# ============================================
# MAIN FUNCTION
# ============================================

def main():
    """Main function"""
    try:
        # Create sync instance
        sync = NetBoxZabbixSync()

        # Run synchronization
        sync.sync_devices()

        # Optional: Sync with tags
        # sync.sync_with_tags()

        logger.info("✅ Synchronization completed successfully!")
        return 0

    except KeyboardInterrupt:
        logger.info("\n⚠️  Synchronization interrupted by user")
        return 130

    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
