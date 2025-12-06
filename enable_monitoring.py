#!/usr/bin/env python3
"""
Enable Zabbix monitoring for NetBox devices

This script sets the custom field cf_monitoring = "Yes" for devices,
allowing them to be synchronized to Zabbix.

Usage:
    # Enable monitoring for all active devices in a site
    python3 enable_monitoring.py --site "EMEA-DC-ONPREM"

    # Enable monitoring for specific device
    python3 enable_monitoring.py --device "EMEA-DC-ONPREM-CORE-SW01"

    # Enable monitoring for devices with specific role
    python3 enable_monitoring.py --role "Core Switch"

    # Dry run (show what would be done)
    python3 enable_monitoring.py --site "EMEA-DC-ONPREM" --dry-run

Requirements:
    pip3 install pynetbox

Configuration:
    Set environment variables or edit this script:
    - NETBOX_URL
    - NETBOX_TOKEN
"""

import os
import sys
import argparse

try:
    import pynetbox
except ImportError:
    print("ERROR: pynetbox library not found")
    print("Install: pip3 install pynetbox")
    sys.exit(1)

# Configuration (can be overridden with environment variables)
NETBOX_URL = os.getenv('NETBOX_URL', 'https://netbox.acme.com')
NETBOX_TOKEN = os.getenv('NETBOX_TOKEN', '')


def enable_monitoring(site=None, device_name=None, role=None, dry_run=False):
    """
    Enable monitoring (cf_monitoring = Yes) for devices

    Args:
        site: Site name filter
        device_name: Specific device name
        role: Device role filter
        dry_run: If True, only show what would be done
    """

    if not NETBOX_TOKEN:
        print("ERROR: NetBox API token not configured")
        print("Set NETBOX_TOKEN environment variable or edit this script")
        sys.exit(1)

    # Connect to NetBox
    print(f"Connecting to NetBox: {NETBOX_URL}")
    nb = pynetbox.api(NETBOX_URL, token=NETBOX_TOKEN)

    # Disable SSL warnings if needed
    # import urllib3
    # urllib3.disable_warnings()
    # nb.http_session.verify = False

    # Build filters
    filters = {'status': 'active'}

    if site:
        filters['site'] = site
    if role:
        filters['role'] = role
    if device_name:
        filters['name'] = device_name

    # Get devices
    print(f"Fetching devices with filters: {filters}")
    devices = list(nb.dcim.devices.filter(**filters))

    if not devices:
        print("No devices found matching criteria")
        return

    print(f"Found {len(devices)} device(s)")
    print()

    if dry_run:
        print("=" * 70)
        print("DRY RUN MODE - No changes will be made")
        print("=" * 70)
        print()

    # Update each device
    updated_count = 0
    already_enabled_count = 0
    error_count = 0

    for device in devices:
        current_value = device.custom_fields.get('cf_monitoring')

        if current_value == 'Yes':
            print(f"⏭️  {device.name:40} - Already enabled")
            already_enabled_count += 1
            continue

        if dry_run:
            print(f"[DRY-RUN] {device.name:40} - Would enable monitoring")
            updated_count += 1
        else:
            try:
                # Set custom field
                device.custom_fields['cf_monitoring'] = 'Yes'
                device.save()

                print(f"✅ {device.name:40} - Monitoring enabled")
                updated_count += 1

            except Exception as e:
                print(f"❌ {device.name:40} - Error: {e}")
                error_count += 1

    # Summary
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Total devices found:     {len(devices)}")
    print(f"Already enabled:         {already_enabled_count}")
    print(f"Enabled (new):           {updated_count}")
    print(f"Errors:                  {error_count}")
    print("=" * 70)

    if dry_run:
        print()
        print("This was a DRY RUN. Run without --dry-run to apply changes.")
    elif updated_count > 0:
        print()
        print("✅ Monitoring enabled successfully!")
        print()
        print("Next steps:")
        print("1. Run Zabbix sync to add devices to Zabbix:")
        if site:
            print(f"   python3 sync_netbox_to_zabbix.py --mode site --site \"{site}\"")
        else:
            print("   python3 sync_netbox_to_zabbix.py --mode full")
        print()
        print("2. Verify devices in Zabbix UI:")
        print("   Configuration → Hosts")


def disable_monitoring(site=None, device_name=None, role=None, dry_run=False):
    """
    Disable monitoring (cf_monitoring = No) for devices

    Args:
        site: Site name filter
        device_name: Specific device name
        role: Device role filter
        dry_run: If True, only show what would be done
    """

    if not NETBOX_TOKEN:
        print("ERROR: NetBox API token not configured")
        print("Set NETBOX_TOKEN environment variable or edit this script")
        sys.exit(1)

    # Connect to NetBox
    print(f"Connecting to NetBox: {NETBOX_URL}")
    nb = pynetbox.api(NETBOX_URL, token=NETBOX_TOKEN)

    # Build filters
    filters = {}

    if site:
        filters['site'] = site
    if role:
        filters['role'] = role
    if device_name:
        filters['name'] = device_name

    # Get devices with monitoring enabled
    filters['cf_monitoring'] = 'Yes'

    # Get devices
    print(f"Fetching devices with filters: {filters}")
    devices = list(nb.dcim.devices.filter(**filters))

    if not devices:
        print("No devices found with monitoring enabled")
        return

    print(f"Found {len(devices)} device(s) with monitoring enabled")
    print()

    if dry_run:
        print("=" * 70)
        print("DRY RUN MODE - No changes will be made")
        print("=" * 70)
        print()

    # Update each device
    disabled_count = 0
    error_count = 0

    for device in devices:
        if dry_run:
            print(f"[DRY-RUN] {device.name:40} - Would disable monitoring")
            disabled_count += 1
        else:
            try:
                # Set custom field
                device.custom_fields['cf_monitoring'] = 'No'
                device.save()

                print(f"✅ {device.name:40} - Monitoring disabled")
                disabled_count += 1

            except Exception as e:
                print(f"❌ {device.name:40} - Error: {e}")
                error_count += 1

    # Summary
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Total devices found:     {len(devices)}")
    print(f"Disabled:                {disabled_count}")
    print(f"Errors:                  {error_count}")
    print("=" * 70)

    if dry_run:
        print()
        print("This was a DRY RUN. Run without --dry-run to apply changes.")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Enable or disable Zabbix monitoring for NetBox devices',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Enable monitoring for all active devices in a site
  python3 enable_monitoring.py --enable --site "EMEA-DC-ONPREM"

  # Enable monitoring for specific device
  python3 enable_monitoring.py --enable --device "EMEA-DC-ONPREM-CORE-SW01"

  # Enable monitoring for all core switches
  python3 enable_monitoring.py --enable --role "Core Switch"

  # Disable monitoring for a site (dry run)
  python3 enable_monitoring.py --disable --site "TEST-SITE" --dry-run

  # Disable monitoring for specific device
  python3 enable_monitoring.py --disable --device "OLD-DEVICE-01"
        """
    )

    parser.add_argument('--enable', action='store_true',
                        help='Enable monitoring (cf_monitoring = Yes)')
    parser.add_argument('--disable', action='store_true',
                        help='Disable monitoring (cf_monitoring = No)')
    parser.add_argument('--site', help='Filter by site name')
    parser.add_argument('--device', help='Filter by specific device name')
    parser.add_argument('--role', help='Filter by device role')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without making changes')

    args = parser.parse_args()

    # Validate arguments
    if not args.enable and not args.disable:
        parser.error("Must specify either --enable or --disable")

    if args.enable and args.disable:
        parser.error("Cannot specify both --enable and --disable")

    if not args.site and not args.device and not args.role:
        parser.error("Must specify at least one filter: --site, --device, or --role")

    # Run appropriate action
    if args.enable:
        enable_monitoring(
            site=args.site,
            device_name=args.device,
            role=args.role,
            dry_run=args.dry_run
        )
    else:
        disable_monitoring(
            site=args.site,
            device_name=args.device,
            role=args.role,
            dry_run=args.dry_run
        )


if __name__ == '__main__':
    main()
