#!/usr/bin/env python3
"""
NetBox Webhook Handler for Zabbix Sync

This script handles NetBox webhooks and automatically syncs devices to Zabbix
when devices are created or updated.

Events handled:
- Device created with status "active" → Create in Zabbix
- Device updated (cf_monitoring changed) → Update Zabbix host status
- Device status changed to "active" → Create in Zabbix
- Device status changed from "active" → Remove from Zabbix (optional)

Usage:
    # Run as Flask web server
    python3 netbox_webhook_handler.py --port 5000

    # Process webhook payload from file (for testing)
    python3 netbox_webhook_handler.py --test webhook_payload.json
"""

import argparse
import logging
import sys
import json
from typing import Dict, Any, Optional
from pathlib import Path

import yaml
import pynetbox
from pyzabbix import ZabbixAPI
from flask import Flask, request, jsonify

# Import the NetBoxZabbixSync class
from sync_netbox_to_zabbix import NetBoxZabbixSync


class WebhookHandler:
    """Handle NetBox webhooks for Zabbix synchronization"""

    def __init__(self, config_file: str = 'config.yaml', mapping_file: str = 'lab/zabbix/zabbix_mapping.yaml'):
        """
        Initialize webhook handler

        Args:
            config_file: Path to configuration file with credentials
            mapping_file: Path to Zabbix mapping configuration
        """
        self.logger = logging.getLogger(__name__)

        # Load configuration
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)

        with open(mapping_file, 'r') as f:
            self.mapping = yaml.safe_load(f)

        # Initialize sync client
        self.sync = NetBoxZabbixSync(config_file, mapping_file)
        self.sync.connect_netbox()
        self.sync.connect_zabbix()

        self.logger.info("Webhook handler initialized")

    def process_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process webhook payload from NetBox

        Args:
            payload: Webhook payload from NetBox

        Returns:
            Response dict with status and message
        """
        try:
            event = payload.get('event')
            model = payload.get('model')
            data = payload.get('data', {})

            self.logger.info(f"Received webhook: event={event}, model={model}")

            # Only process device events
            if model != 'device':
                return {'status': 'ignored', 'message': f'Not a device event (model={model})'}

            # Get device details
            device_id = data.get('id')
            device_name = data.get('name')
            device_status = data.get('status', {}).get('value')
            cf_monitoring = data.get('custom_fields', {}).get('cf_monitoring')

            self.logger.info(f"Device: {device_name} (ID: {device_id}, Status: {device_status}, cf_monitoring: {cf_monitoring})")

            # Fetch full device object from NetBox
            device = self.sync.nb.dcim.devices.get(device_id)
            if not device:
                return {'status': 'error', 'message': f'Device {device_id} not found in NetBox'}

            # Check if device should be synced
            if not self._should_sync_device(device, event):
                return {'status': 'skipped', 'message': f'Device does not meet sync criteria'}

            # Handle different events
            if event in ['created', 'updated']:
                result = self._sync_device(device, event)
                return result
            elif event == 'deleted':
                result = self._delete_device(device)
                return result
            else:
                return {'status': 'ignored', 'message': f'Event {event} not handled'}

        except Exception as e:
            self.logger.error(f"Error processing webhook: {e}", exc_info=True)
            return {'status': 'error', 'message': str(e)}

    def _should_sync_device(self, device, event: str) -> bool:
        """
        Check if device should be synced to Zabbix

        Args:
            device: NetBox device object
            event: Webhook event type

        Returns:
            True if device should be synced
        """
        # Don't sync deleted devices (handled separately)
        if event == 'deleted':
            return True

        # Check status
        if device.status.value != 'active':
            self.logger.info(f"Device {device.name} is not active (status={device.status.value})")
            return False

        # Check custom field
        cf_monitoring = device.custom_fields.get('cf_monitoring')
        if cf_monitoring not in ['Yes', 'No']:
            self.logger.info(f"Device {device.name} cf_monitoring not set to Yes or No (value={cf_monitoring})")
            return False

        # Check primary IP
        if not device.primary_ip4:
            self.logger.info(f"Device {device.name} has no primary IPv4 address")
            return False

        return True

    def _sync_device(self, device, event: str) -> Dict[str, Any]:
        """
        Sync device to Zabbix (create or update)

        Args:
            device: NetBox device object
            event: Webhook event type

        Returns:
            Response dict with status and message
        """
        try:
            success = self.sync.sync_device_to_zabbix(device)

            if success:
                cf_monitoring = device.custom_fields.get('cf_monitoring')
                status_text = "enabled" if cf_monitoring == 'Yes' else "disabled"

                return {
                    'status': 'success',
                    'message': f'Device {device.name} synced to Zabbix ({status_text})',
                    'device': device.name,
                    'monitoring_status': status_text
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Failed to sync device {device.name} to Zabbix'
                }

        except Exception as e:
            self.logger.error(f"Error syncing device {device.name}: {e}", exc_info=True)
            return {'status': 'error', 'message': str(e)}

    def _delete_device(self, device) -> Dict[str, Any]:
        """
        Delete device from Zabbix (optional)

        Args:
            device: NetBox device object

        Returns:
            Response dict with status and message
        """
        try:
            # Check if host exists in Zabbix
            existing_hosts = self.sync.zabbix.host.get(filter={'host': device.name})

            if not existing_hosts:
                return {'status': 'skipped', 'message': f'Device {device.name} not found in Zabbix'}

            # Optional: Delete host from Zabbix
            # Uncomment if you want to automatically remove deleted devices
            # host_id = existing_hosts[0]['hostid']
            # self.sync.zabbix.host.delete(host_id)
            # self.logger.info(f"Deleted host {device.name} from Zabbix")
            # return {'status': 'success', 'message': f'Device {device.name} deleted from Zabbix'}

            # By default, don't delete - just log
            self.logger.info(f"Device {device.name} deleted in NetBox, but not removed from Zabbix (disabled by default)")
            return {'status': 'skipped', 'message': 'Auto-delete disabled'}

        except Exception as e:
            self.logger.error(f"Error deleting device {device.name}: {e}", exc_info=True)
            return {'status': 'error', 'message': str(e)}


# Flask application
app = Flask(__name__)
webhook_handler = None


@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """Flask endpoint to receive NetBox webhooks"""
    try:
        payload = request.get_json()

        if not payload:
            return jsonify({'status': 'error', 'message': 'No JSON payload received'}), 400

        result = webhook_handler.process_webhook(payload)

        if result['status'] == 'error':
            return jsonify(result), 500
        else:
            return jsonify(result), 200

    except Exception as e:
        app.logger.error(f"Error handling webhook: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'netbox-webhook-handler'}), 200


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('/var/log/netbox_webhook_handler.log')
        ]
    )


def test_webhook(payload_file: str, config_file: str, mapping_file: str):
    """
    Test webhook handler with payload from file

    Args:
        payload_file: Path to JSON file with webhook payload
        config_file: Path to config file
        mapping_file: Path to mapping file
    """
    with open(payload_file, 'r') as f:
        payload = json.load(f)

    handler = WebhookHandler(config_file, mapping_file)
    result = handler.process_webhook(payload)

    print("=" * 70)
    print("Webhook Test Result")
    print("=" * 70)
    print(json.dumps(result, indent=2))
    print("=" * 70)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='NetBox Webhook Handler for Zabbix Sync',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )

    parser.add_argument(
        '--mapping',
        default='lab/zabbix/zabbix_mapping.yaml',
        help='Path to Zabbix mapping file (default: lab/zabbix/zabbix_mapping.yaml)'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to run webhook server (default: 5000)'
    )

    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host to bind webhook server (default: 0.0.0.0)'
    )

    parser.add_argument(
        '--test',
        metavar='PAYLOAD_FILE',
        help='Test mode: process webhook payload from JSON file'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    # Test mode
    if args.test:
        test_webhook(args.test, args.config, args.mapping)
        return

    # Run Flask server
    global webhook_handler
    webhook_handler = WebhookHandler(args.config, args.mapping)

    print("=" * 70)
    print("NetBox Webhook Handler for Zabbix Sync")
    print("=" * 70)
    print(f"Listening on http://{args.host}:{args.port}/webhook")
    print(f"Health check: http://{args.host}:{args.port}/health")
    print("=" * 70)

    app.run(host=args.host, port=args.port, debug=args.verbose)


if __name__ == '__main__':
    main()
