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
import io
from pathlib import Path
from pynetbox import api as netbox_api
from pyzabbix import ZabbixAPI
import logging
from datetime import datetime
import urllib3
import requests

# ============================================
# LOAD ENVIRONMENT VARIABLES
# ============================================

try:
    from dotenv import load_dotenv

    # Try to find .env file in current directory or parent directories
    current_dir = Path.cwd()
    env_file = None

    # Check current directory and up to 2 parent levels
    for parent in [current_dir] + list(current_dir.parents)[:2]:
        potential_env = parent / '.env'
        if potential_env.exists():
            env_file = potential_env
            break

    if env_file:
        load_dotenv(env_file)
        print(f"✅ Loaded environment from: {env_file}")
    else:
        print("⚠️  No .env file found, using environment variables or defaults")
except ImportError:
    print("⚠️  python-dotenv not installed, using environment variables only")

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

# Custom Fields for Monitoring Control and Zabbix Integration
# NetBox custom field names
CF_MONITORED = "cf_monitored"      # Boolean field to enable/disable monitoring
CF_ZABBIX_ID = "cf_zabbix_id"      # Store Zabbix host ID back to NetBox

# Logging Configuration
LOG_FILE = os.getenv('LOG_FILE', '/var/log/netbox-zabbix-sync.log')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Network Configuration
VERIFY_SSL = os.getenv('VERIFY_SSL', 'false').lower() in ('true', '1', 'yes')
DISABLE_PROXY = os.getenv('DISABLE_PROXY', 'true').lower() in ('true', '1', 'yes')

# ============================================
# SSL AND PROXY CONFIGURATION
# ============================================

# Disable SSL warnings if SSL verification is disabled
if not VERIFY_SSL:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    print("⚠️  SSL verification disabled")

# Disable proxy for internal network communication
if DISABLE_PROXY:
    os.environ['NO_PROXY'] = '*'
    os.environ['no_proxy'] = '*'
    # Clear any existing proxy settings
    for proxy_var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
        if proxy_var in os.environ:
            del os.environ[proxy_var]
    print("🔧 Proxy disabled for all connections")

# ============================================
# LOGGING SETUP
# ============================================

# Setup logging handlers with UTF-8 encoding for Windows compatibility
# Create console handler with UTF-8 encoding to support emojis on Windows
console_handler = logging.StreamHandler(io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'))
handlers = [console_handler]

# Try to add file handler if possible
try:
    # Create log directory if it doesn't exist
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    # File handler with UTF-8 encoding
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    handlers.append(file_handler)
except (OSError, PermissionError) as e:
    # If we can't write to the log file, just use console logging
    print(f"Warning: Could not create log file {LOG_FILE}: {e}")
    print("Continuing with console logging only...")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
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

            # Create custom session for NetBox with SSL and proxy settings
            session = requests.Session()
            session.verify = VERIFY_SSL
            if DISABLE_PROXY:
                session.proxies = {'http': None, 'https': None}

            self.netbox = netbox_api(NETBOX_URL, token=NETBOX_TOKEN)
            self.netbox.http_session = session

            # Test NetBox connection
            _ = self.netbox.status()
            logger.info("✅ NetBox connection successful")

            # Connect to Zabbix
            logger.info(f"Connecting to Zabbix at {ZABBIX_URL}...")
            self.zabbix = ZabbixAPI(ZABBIX_URL)

            # Configure Zabbix session with SSL and proxy settings
            self.zabbix.session.verify = VERIFY_SSL
            if DISABLE_PROXY:
                self.zabbix.session.proxies = {'http': None, 'https': None}
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

    def get_monitoring_status(self, device):
        """
        Determine if monitoring should be enabled based on NetBox cf_monitored custom field

        Returns:
            0 = Enabled (monitored)
            1 = Disabled (not monitored)
        """
        try:
            # Get cf_monitored value (boolean field)
            cf_monitored = device.custom_fields.get(CF_MONITORED)

            if cf_monitored is None:
                # Custom field not set, default to enabled
                logger.debug(f"{device.name}: cf_monitored not set, defaulting to enabled")
                return 0  # Enabled

            # Handle boolean or string values
            if isinstance(cf_monitored, bool):
                # Boolean field: True = enabled, False = disabled
                status = 0 if cf_monitored else 1
                status_text = "ENABLED" if cf_monitored else "DISABLED"
                logger.debug(f"{device.name}: cf_monitored={cf_monitored} → {status_text}")
                return status
            else:
                # String value: convert to boolean
                cf_str = str(cf_monitored).lower().strip()
                if cf_str in ('true', '1', 'yes', 'enabled'):
                    logger.debug(f"{device.name}: cf_monitored='{cf_monitored}' → ENABLED")
                    return 0
                elif cf_str in ('false', '0', 'no', 'disabled'):
                    logger.debug(f"{device.name}: cf_monitored='{cf_monitored}' → DISABLED")
                    return 1
                else:
                    logger.warning(f"{device.name}: Unknown cf_monitored value '{cf_monitored}', defaulting to enabled")
                    return 0

        except Exception as e:
            logger.warning(f"{device.name}: Error reading cf_monitored: {e}, defaulting to enabled")
            return 0

    def update_netbox_zabbix_id(self, device, zabbix_host_id):
        """
        Write Zabbix host ID back to NetBox cf_zabbix_id custom field

        Args:
            device: NetBox device object
            zabbix_host_id: Zabbix host ID to store
        """
        try:
            # Update the custom field
            device.custom_fields[CF_ZABBIX_ID] = str(zabbix_host_id)
            device.save()
            logger.debug(f"{device.name}: Updated cf_zabbix_id={zabbix_host_id}")
            return True
        except Exception as e:
            logger.warning(f"{device.name}: Failed to update cf_zabbix_id: {e}")
            return False

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

        # Get monitoring status from custom field
        monitoring_status = self.get_monitoring_status(device)
        status_text = "ENABLED" if monitoring_status == 0 else "DISABLED"

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
            old_status = int(existing_hosts[0].get('status', 0))
            old_status_text = "ENABLED" if old_status == 0 else "DISABLED"

            update_params = {
                "hostid": host_id,
                "host": device_name,
                "interfaces": [interface],
                "groups": [{"groupid": group_id}],
                "status": monitoring_status
            }

            self.zabbix.host.update(**update_params)

            # Update cf_zabbix_id in NetBox
            self.update_netbox_zabbix_id(device, host_id)

            # Log status change if it occurred
            if old_status != monitoring_status:
                logger.info(f"🔄 {device_name} ({device_ip}) - Updated | Status: {old_status_text} → {status_text}")
            else:
                logger.info(f"🔄 {device_name} ({device_ip}) - Updated | Status: {status_text}")

            self.stats['updated'] += 1

        else:
            # Create new host
            create_params = {
                "host": device_name,
                "interfaces": [interface],
                "groups": [{"groupid": group_id}],
                "status": monitoring_status
            }

            # Add template if available
            if template_id:
                create_params["templates"] = [{"templateid": template_id}]

            result = self.zabbix.host.create(**create_params)
            host_id = result['hostids'][0]  # Get the newly created host ID

            # Update cf_zabbix_id in NetBox
            self.update_netbox_zabbix_id(device, host_id)

            logger.info(f"✅ {device_name} ({device_ip}) - Created | Status: {status_text} | Zabbix ID: {host_id}")
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

                # Get monitoring status from custom field
                monitoring_status = self.get_monitoring_status(device)
                status_text = "ENABLED" if monitoring_status == 0 else "DISABLED"

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
                    old_status = int(existing_hosts[0].get('status', 0))
                    old_status_text = "ENABLED" if old_status == 0 else "DISABLED"

                    self.zabbix.host.update(
                        hostid=host_id,
                        groups=group_ids,
                        interfaces=[interface],
                        status=monitoring_status
                    )

                    # Log status change if it occurred
                    if old_status != monitoring_status:
                        logger.info(f"🔄 {device_name} - Tags updated | Status: {old_status_text} → {status_text}")
                    else:
                        logger.info(f"🔄 {device_name} - Tags updated | Status: {status_text}")

                    self.stats['updated'] += 1
                else:
                    # Create
                    self.zabbix.host.create(
                        host=device_name,
                        interfaces=[interface],
                        groups=group_ids,
                        status=monitoring_status
                    )
                    logger.info(f"✅ {device_name} - Created with tags | Status: {status_text}")
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
