#!/usr/bin/env python3
"""
NetBox and Zabbix Connection Test Script
=========================================

This script tests connectivity to both NetBox and Zabbix APIs
using credentials from a .env file.

Requirements:
  pip install pynetbox pyzabbix requests python-dotenv

Usage:
  python3 test_connections.py

Environment Variables (from .env):
  - NETBOX_URL: NetBox API URL (default: http://localhost:8000)
  - NETBOX_TOKEN: NetBox API token
  - ZABBIX_URL: Zabbix API URL (default: http://localhost:8080)
  - ZABBIX_USER: Zabbix username (default: Admin)
  - ZABBIX_PASSWORD: Zabbix password (default: zabbix)

Author: Connection Test Script
License: MIT
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import logging
import urllib3
import requests

# ============================================
# COLOR CODES FOR TERMINAL OUTPUT
# ============================================
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ============================================
# LOGGING SETUP
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================
# LOAD ENVIRONMENT VARIABLES
# ============================================
def load_environment():
    """Load environment variables from .env file"""
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
            logger.info(f"✅ Loaded environment from: {env_file}")
            return True
        else:
            logger.warning(f"{Colors.WARNING}⚠️  No .env file found{Colors.ENDC}")
            logger.info("Using environment variables or defaults")
            return False
    except ImportError:
        logger.error(f"{Colors.FAIL}❌ python-dotenv not installed{Colors.ENDC}")
        logger.info("Install with: pip install python-dotenv")
        logger.info("Continuing with system environment variables...")
        return False

# ============================================
# SSL AND PROXY CONFIGURATION
# ============================================
def configure_network():
    """Configure SSL and proxy settings"""
    # Get configuration from environment
    verify_ssl = os.getenv('VERIFY_SSL', 'false').lower() in ('true', '1', 'yes')
    disable_proxy = os.getenv('DISABLE_PROXY', 'true').lower() in ('true', '1', 'yes')

    # Disable SSL warnings if SSL verification is disabled
    if not verify_ssl:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        print(f"{Colors.WARNING}⚠️  SSL verification disabled{Colors.ENDC}")

    # Disable proxy for internal network communication
    if disable_proxy:
        os.environ['NO_PROXY'] = '*'
        os.environ['no_proxy'] = '*'
        # Clear any existing proxy settings
        for proxy_var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
            if proxy_var in os.environ:
                del os.environ[proxy_var]
        print(f"{Colors.OKCYAN}🔧 Proxy disabled for all connections{Colors.ENDC}")

    return verify_ssl, disable_proxy

# ============================================
# CONFIGURATION
# ============================================
def get_config():
    """Get configuration from environment variables"""
    config = {
        'netbox': {
            'url': os.getenv('NETBOX_URL', 'http://localhost:8000'),
            'token': os.getenv('NETBOX_TOKEN', ''),
        },
        'zabbix': {
            'url': os.getenv('ZABBIX_URL', 'http://localhost:8080'),
            'user': os.getenv('ZABBIX_USER', 'Admin'),
            'password': os.getenv('ZABBIX_PASSWORD', 'zabbix'),
        }
    }
    return config

# ============================================
# NETBOX CONNECTION TEST
# ============================================
def test_netbox_connection(url, token, verify_ssl=False, disable_proxy=False):
    """Test connection to NetBox API"""
    print(f"\n{Colors.HEADER}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}TESTING NETBOX CONNECTION{Colors.ENDC}")
    print(f"{Colors.HEADER}{'=' * 60}{Colors.ENDC}\n")

    logger.info(f"NetBox URL: {url}")
    logger.info(f"Token: {'*' * 20 if token else '(empty)'}")

    if not token:
        logger.error(f"{Colors.FAIL}❌ NETBOX_TOKEN not set{Colors.ENDC}")
        logger.info("Set NETBOX_TOKEN in your .env file")
        return False

    try:
        from pynetbox import api as netbox_api

        logger.info("Connecting to NetBox...")

        # Create custom session with SSL and proxy settings
        session = requests.Session()
        session.verify = verify_ssl
        if disable_proxy:
            session.proxies = {'http': None, 'https': None}

        # Initialize NetBox API
        nb = netbox_api(url, token=token)
        nb.http_session = session

        # Test connection by getting status
        status = nb.status()

        logger.info(f"{Colors.OKGREEN}✅ NetBox connection successful!{Colors.ENDC}")

        # Get version information
        if hasattr(status, 'netbox-version'):
            version = getattr(status, 'netbox-version')
            logger.info(f"   NetBox Version: {version}")

        if hasattr(status, 'python-version'):
            python_version = getattr(status, 'python-version')
            logger.info(f"   Python Version: {python_version}")

        # Test basic API calls
        logger.info("\nTesting API endpoints:")

        # Test sites endpoint
        try:
            sites = nb.dcim.sites.all()
            site_count = len(list(sites))
            logger.info(f"{Colors.OKGREEN}   ✓{Colors.ENDC} Sites: {site_count} found")
        except Exception as e:
            logger.warning(f"{Colors.WARNING}   ⚠{Colors.ENDC} Sites: Error - {str(e)}")

        # Test devices endpoint
        try:
            devices = nb.dcim.devices.all()
            device_count = len(list(devices))
            logger.info(f"{Colors.OKGREEN}   ✓{Colors.ENDC} Devices: {device_count} found")
        except Exception as e:
            logger.warning(f"{Colors.WARNING}   ⚠{Colors.ENDC} Devices: Error - {str(e)}")

        # Test virtual machines endpoint
        try:
            vms = nb.virtualization.virtual_machines.all()
            vm_count = len(list(vms))
            logger.info(f"{Colors.OKGREEN}   ✓{Colors.ENDC} Virtual Machines: {vm_count} found")
        except Exception as e:
            logger.warning(f"{Colors.WARNING}   ⚠{Colors.ENDC} Virtual Machines: Error - {str(e)}")

        return True

    except ImportError:
        logger.error(f"{Colors.FAIL}❌ pynetbox library not installed{Colors.ENDC}")
        logger.info("Install with: pip install pynetbox")
        return False
    except Exception as e:
        logger.error(f"{Colors.FAIL}❌ NetBox connection failed: {str(e)}{Colors.ENDC}")
        logger.info("\nTroubleshooting:")
        logger.info("1. Verify NETBOX_URL is correct")
        logger.info("2. Verify NETBOX_TOKEN is valid")
        logger.info("3. Ensure NetBox is running and accessible")
        logger.info("4. Check network connectivity")
        return False

# ============================================
# ZABBIX CONNECTION TEST
# ============================================
def test_zabbix_connection(url, user, password, verify_ssl=False, disable_proxy=False):
    """Test connection to Zabbix API"""
    print(f"\n{Colors.HEADER}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}TESTING ZABBIX CONNECTION{Colors.ENDC}")
    print(f"{Colors.HEADER}{'=' * 60}{Colors.ENDC}\n")

    logger.info(f"Zabbix URL: {url}")
    logger.info(f"Username: {user}")
    logger.info(f"Password: {'*' * len(password) if password else '(empty)'}")

    if not password:
        logger.warning(f"{Colors.WARNING}⚠️  ZABBIX_PASSWORD not set, using default{Colors.ENDC}")

    try:
        from pyzabbix import ZabbixAPI, ZabbixAPIException

        logger.info("Connecting to Zabbix...")

        # Initialize Zabbix API
        zapi = ZabbixAPI(url)

        # Configure Zabbix session with SSL and proxy settings
        zapi.session.verify = verify_ssl
        if disable_proxy:
            zapi.session.proxies = {'http': None, 'https': None}

        # Login to Zabbix
        zapi.login(user, password)

        logger.info(f"{Colors.OKGREEN}✅ Zabbix connection successful!{Colors.ENDC}")

        # Get version information
        version = zapi.apiinfo.version()
        logger.info(f"   Zabbix Version: {version}")

        # Test basic API calls
        logger.info("\nTesting API endpoints:")

        # Test hosts
        try:
            hosts = zapi.host.get(output=['hostid', 'host', 'name'])
            host_count = len(hosts)
            logger.info(f"{Colors.OKGREEN}   ✓{Colors.ENDC} Hosts: {host_count} found")
            if host_count > 0:
                logger.info(f"      First host: {hosts[0].get('name', 'N/A')}")
        except Exception as e:
            logger.warning(f"{Colors.WARNING}   ⚠{Colors.ENDC} Hosts: Error - {str(e)}")

        # Test host groups
        try:
            groups = zapi.hostgroup.get(output=['groupid', 'name'])
            group_count = len(groups)
            logger.info(f"{Colors.OKGREEN}   ✓{Colors.ENDC} Host Groups: {group_count} found")
        except Exception as e:
            logger.warning(f"{Colors.WARNING}   ⚠{Colors.ENDC} Host Groups: Error - {str(e)}")

        # Test templates
        try:
            templates = zapi.template.get(output=['templateid', 'name'])
            template_count = len(templates)
            logger.info(f"{Colors.OKGREEN}   ✓{Colors.ENDC} Templates: {template_count} found")
        except Exception as e:
            logger.warning(f"{Colors.WARNING}   ⚠{Colors.ENDC} Templates: Error - {str(e)}")

        # Test user information
        try:
            user_info = zapi.user.get(output=['userid', 'username', 'name', 'surname'])
            user_count = len(user_info)
            logger.info(f"{Colors.OKGREEN}   ✓{Colors.ENDC} Users: {user_count} found")
        except Exception as e:
            logger.warning(f"{Colors.WARNING}   ⚠{Colors.ENDC} Users: Error - {str(e)}")

        return True

    except ImportError:
        logger.error(f"{Colors.FAIL}❌ pyzabbix library not installed{Colors.ENDC}")
        logger.info("Install with: pip install pyzabbix")
        return False
    except Exception as e:
        logger.error(f"{Colors.FAIL}❌ Zabbix connection failed: {str(e)}{Colors.ENDC}")
        logger.info("\nTroubleshooting:")
        logger.info("1. Verify ZABBIX_URL is correct")
        logger.info("2. Verify ZABBIX_USER and ZABBIX_PASSWORD are correct")
        logger.info("3. Ensure Zabbix is running and accessible")
        logger.info("4. Check network connectivity")
        logger.info("5. Default credentials: Admin/zabbix")
        return False

# ============================================
# MAIN FUNCTION
# ============================================
def main():
    """Main function to run connection tests"""
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                                                            ║")
    print("║     NetBox & Zabbix Connection Test Script                ║")
    print("║                                                            ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")

    start_time = datetime.now()

    # Load environment variables
    load_environment()

    # Configure network settings (SSL and proxy)
    verify_ssl, disable_proxy = configure_network()

    # Get configuration
    config = get_config()

    # Test connections
    netbox_success = test_netbox_connection(
        config['netbox']['url'],
        config['netbox']['token'],
        verify_ssl,
        disable_proxy
    )

    zabbix_success = test_zabbix_connection(
        config['zabbix']['url'],
        config['zabbix']['user'],
        config['zabbix']['password'],
        verify_ssl,
        disable_proxy
    )

    # Print summary
    print(f"\n{Colors.HEADER}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}SUMMARY{Colors.ENDC}")
    print(f"{Colors.HEADER}{'=' * 60}{Colors.ENDC}\n")

    if netbox_success:
        print(f"{Colors.OKGREEN}✅ NetBox: Connected successfully{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ NetBox: Connection failed{Colors.ENDC}")

    if zabbix_success:
        print(f"{Colors.OKGREEN}✅ Zabbix: Connected successfully{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Zabbix: Connection failed{Colors.ENDC}")

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print(f"\nTest Duration: {duration:.2f} seconds")
    print(f"Completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Exit code
    if netbox_success and zabbix_success:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 All tests passed!{Colors.ENDC}\n")
        return 0
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}⚠️  Some tests failed. Check logs above.{Colors.ENDC}\n")
        return 1

# ============================================
# SCRIPT ENTRY POINT
# ============================================
if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}⚠️  Test interrupted by user{Colors.ENDC}\n")
        sys.exit(130)
    except Exception as e:
        logger.error(f"\n{Colors.FAIL}❌ Unexpected error: {str(e)}{Colors.ENDC}\n")
        sys.exit(1)
