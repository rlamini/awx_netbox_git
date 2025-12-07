# NetBox Webhook Setup for Automatic Zabbix Sync

This guide explains how to configure NetBox webhooks for **event-driven** Zabbix synchronization.

---

## Overview

There are **two methods** to sync NetBox devices to Zabbix:

### Method 1: Scheduled Sync (Traditional)
- Run `sync_netbox_to_zabbix.py` on a schedule (cron, systemd timer, AWX)
- Syncs all devices periodically (every 6 hours, daily, etc.)
- Good for: Bulk operations, initial setup

### Method 2: Event-Driven Sync (Webhooks) ⭐ **RECOMMENDED**
- NetBox sends webhook when device is created/updated
- Automatic real-time sync to Zabbix
- Good for: Immediate sync, operational efficiency

This guide covers **Method 2** (Event-Driven Sync).

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         NetBox                                  │
│                                                                 │
│  Device Created/Updated → Webhook Triggered                     │
│                              ↓                                  │
└──────────────────────────────┼──────────────────────────────────┘
                               │ HTTP POST
                               │ (JSON payload)
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│              Webhook Handler (Flask App)                        │
│              netbox_webhook_handler.py                          │
│                                                                 │
│  1. Receive webhook                                             │
│  2. Validate device (status=active, cf_monitoring=Yes/No)       │
│  3. Sync to Zabbix (create/update host)                         │
│                              ↓                                  │
└──────────────────────────────┼──────────────────────────────────┘
                               │ Zabbix API
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                         Zabbix                                  │
│                                                                 │
│  Host Created/Updated with status:                              │
│  - cf_monitoring = "Yes" → Enabled (monitored)                  │
│  - cf_monitoring = "No"  → Disabled (not monitored)             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Event-Driven Sync Behavior

| NetBox Action | cf_monitoring | Result in Zabbix |
|---------------|---------------|------------------|
| Create device (status=active) | Yes | ✅ Host created and **enabled** |
| Create device (status=active) | No | ⚠️ Host created and **disabled** |
| Update device → cf_monitoring: Yes | Yes | ✅ Host updated and **enabled** |
| Update device → cf_monitoring: No | No | ⚠️ Host updated and **disabled** |
| Update device → status: active | Yes/No | ✅ Host created/updated |
| Update device → status: offline | - | ⏸️ No action (can optionally disable) |

---

## Step 1: Install Webhook Handler

### 1.1 Install Dependencies

```bash
pip3 install flask pynetbox pyzabbix pyyaml requests
```

### 1.2 Configure Webhook Handler

The webhook handler uses the same configuration files as the sync script:
- `config.yaml` - NetBox and Zabbix credentials
- `lab/zabbix/zabbix_mapping.yaml` - Template mapping

No additional configuration needed!

### 1.3 Test Webhook Handler

```bash
# Test that it can connect to NetBox and Zabbix
python3 netbox_webhook_handler.py --test test_payload.json
```

Create `test_payload.json`:
```json
{
  "event": "created",
  "model": "device",
  "data": {
    "id": 1,
    "name": "TEST-DEVICE-01",
    "status": {
      "value": "active"
    },
    "custom_fields": {
      "cf_monitoring": "Yes"
    }
  }
}
```

---

## Step 2: Run Webhook Handler

### Option A: Foreground (Testing)

```bash
python3 netbox_webhook_handler.py --port 5000 --verbose
```

### Option B: Systemd Service (Production)

Create `/etc/systemd/system/netbox-webhook-handler.service`:

```ini
[Unit]
Description=NetBox Webhook Handler for Zabbix Sync
After=network.target

[Service]
Type=simple
User=netbox
Group=netbox
WorkingDirectory=/opt/netbox-zabbix-sync
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /opt/netbox-zabbix-sync/netbox_webhook_handler.py --port 5000
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=netbox-webhook

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable netbox-webhook-handler
sudo systemctl start netbox-webhook-handler
sudo systemctl status netbox-webhook-handler
```

View logs:
```bash
sudo journalctl -u netbox-webhook-handler -f
```

### Option C: Docker Container

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY netbox_webhook_handler.py .
COPY sync_netbox_to_zabbix.py .
COPY config.yaml .
COPY lab/ ./lab/

EXPOSE 5000

CMD ["python3", "netbox_webhook_handler.py", "--host", "0.0.0.0", "--port", "5000"]
```

Run:
```bash
docker build -t netbox-webhook-handler .
docker run -d -p 5000:5000 --name netbox-webhook netbox-webhook-handler
```

---

## Step 3: Configure NetBox Webhook

### 3.1 Via NetBox UI

1. **Navigate to Webhooks**
   - Go to **Other → Webhooks**
   - Click **+ Add**

2. **Configure Webhook**

   **Basic Settings:**
   - **Name**: `Zabbix Sync Webhook`
   - **Object Type**: `dcim > device`
   - **Enabled**: `☑` (checked)

   **Events:**
   - ☑ **Creations**
   - ☑ **Updates**
   - ☐ **Deletions** (optional - see note below)

   **HTTP Request:**
   - **URL**: `http://webhook-server:5000/webhook`
   - **HTTP Method**: `POST`
   - **HTTP Content Type**: `application/json`

   **Conditions (Optional):**
   ```json
   {
     "and": [
       {
         "attr": "status.value",
         "value": "active"
       }
     ]
   }
   ```
   This ensures webhook only fires for active devices.

   **SSL Verification:**
   - ☐ Disable if using self-signed certificates (not recommended for production)

   **Headers (Optional):**
   ```
   X-Webhook-Secret: your-secret-token
   ```

3. **Save** the webhook

### 3.2 Via NetBox API

```python
import requests

NETBOX_URL = "https://netbox.acme.com"
TOKEN = "your-netbox-api-token"

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

data = {
    "name": "Zabbix Sync Webhook",
    "content_types": ["dcim.device"],
    "enabled": True,
    "type_create": True,
    "type_update": True,
    "type_delete": False,
    "url": "http://webhook-server:5000/webhook",
    "http_method": "POST",
    "http_content_type": "application/json",
    "ssl_verification": True,
    "conditions": {
        "and": [
            {
                "attr": "status.value",
                "value": "active"
            }
        ]
    }
}

response = requests.post(
    f"{NETBOX_URL}/api/extras/webhooks/",
    headers=headers,
    json=data
)

print(f"Webhook created: {response.json()}")
```

---

## Step 4: Test the Webhook

### 4.1 Create Test Device in NetBox

1. Create a new device in NetBox
2. Set **Status** = `active`
3. Set **cf_monitoring** = `Yes`
4. Assign **primary IPv4 address**
5. Save the device

### 4.2 Check Webhook Handler Logs

```bash
# If using systemd
sudo journalctl -u netbox-webhook-handler -f

# If running in foreground
# Check terminal output

# If using Docker
docker logs -f netbox-webhook
```

Expected output:
```
2025-12-07 10:30:15 - INFO - Received webhook: event=created, model=device
2025-12-07 10:30:15 - INFO - Device: TEST-DEVICE-01 (ID: 1, Status: active, cf_monitoring: Yes)
2025-12-07 10:30:16 - INFO - ✅ Created host: TEST-DEVICE-01 (cf_monitoring=Yes, status=enabled)
```

### 4.3 Verify in Zabbix

1. Log in to Zabbix UI
2. Go to **Configuration → Hosts**
3. Search for `TEST-DEVICE-01`
4. Verify:
   - Host exists
   - Status = **Enabled** (green)
   - Templates assigned
   - Host groups assigned
   - SNMP interface configured

---

## Step 5: Test Monitoring Enable/Disable

### 5.1 Disable Monitoring

1. In NetBox, edit the device
2. Change **cf_monitoring** from `Yes` to `No`
3. Save

**Expected behavior:**
- Webhook triggered
- Zabbix host updated
- Host status changed to **Disabled** (red)
- No monitoring alerts generated

### 5.2 Enable Monitoring

1. In NetBox, edit the device
2. Change **cf_monitoring** from `No` to `Yes`
3. Save

**Expected behavior:**
- Webhook triggered
- Zabbix host updated
- Host status changed to **Enabled** (green)
- Monitoring resumes

---

## Webhook Payload Reference

### Device Created Event

```json
{
  "event": "created",
  "timestamp": "2025-12-07T10:30:15.123456Z",
  "model": "device",
  "username": "admin",
  "request_id": "abc-123-def-456",
  "data": {
    "id": 1,
    "url": "https://netbox.acme.com/api/dcim/devices/1/",
    "name": "EMEA-DC-ONPREM-CORE-SW01",
    "display": "EMEA-DC-ONPREM-CORE-SW01",
    "device_type": {
      "id": 1,
      "url": "https://netbox.acme.com/api/dcim/device-types/1/",
      "manufacturer": {
        "id": 1,
        "url": "https://netbox.acme.com/api/dcim/manufacturers/1/",
        "name": "Cisco Systems",
        "slug": "cisco"
      },
      "model": "Nexus 9508",
      "slug": "nexus-9508"
    },
    "device_role": {
      "id": 1,
      "url": "https://netbox.acme.com/api/dcim/device-roles/1/",
      "name": "Core Switch",
      "slug": "core-switch"
    },
    "platform": {
      "id": 1,
      "url": "https://netbox.acme.com/api/dcim/platforms/1/",
      "name": "Cisco NX-OS",
      "slug": "nxos"
    },
    "site": {
      "id": 1,
      "url": "https://netbox.acme.com/api/dcim/sites/1/",
      "name": "EMEA-DC-ONPREM",
      "slug": "emea-dc-onprem"
    },
    "status": {
      "value": "active",
      "label": "Active"
    },
    "primary_ip4": {
      "id": 1,
      "url": "https://netbox.acme.com/api/ipam/ip-addresses/1/",
      "address": "10.10.100.1/24",
      "display": "10.10.100.1/24"
    },
    "custom_fields": {
      "cf_monitoring": "Yes"
    },
    "tags": [
      {
        "id": 1,
        "url": "https://netbox.acme.com/api/extras/tags/1/",
        "name": "production",
        "slug": "production",
        "color": "4caf50"
      }
    ]
  }
}
```

### Device Updated Event

```json
{
  "event": "updated",
  "timestamp": "2025-12-07T10:35:20.654321Z",
  "model": "device",
  "username": "admin",
  "request_id": "xyz-789-uvw-012",
  "data": {
    "id": 1,
    "name": "EMEA-DC-ONPREM-CORE-SW01",
    "status": {
      "value": "active",
      "label": "Active"
    },
    "custom_fields": {
      "cf_monitoring": "No"
    }
    // ... rest of device data ...
  },
  "snapshots": {
    "prechange": {
      "custom_fields": {
        "cf_monitoring": "Yes"
      }
    },
    "postchange": {
      "custom_fields": {
        "cf_monitoring": "No"
      }
    }
  }
}
```

---

## Comparison: Scheduled vs Event-Driven

| Feature | Scheduled Sync | Event-Driven (Webhooks) |
|---------|----------------|-------------------------|
| **Latency** | Minutes to hours | Seconds |
| **Resource Usage** | Periodic bulk processing | On-demand per device |
| **NetBox Load** | High (API queries all devices) | Low (only changed devices) |
| **Zabbix Load** | High (bulk updates) | Low (single device) |
| **Complexity** | Simple | Moderate (requires webhook server) |
| **Best For** | Initial setup, bulk changes | Day-to-day operations |
| **Failure Recovery** | Automatic on next run | Requires retry mechanism |

**Recommendation:** Use **both methods**:
- Event-driven for real-time sync
- Scheduled sync daily/weekly as backup

---

## Troubleshooting

### Webhook Not Triggering

**Check NetBox webhook status:**
1. Go to **Other → Webhooks**
2. Click on webhook name
3. Check **Recent deliveries** tab

**Common issues:**
- Webhook disabled
- Conditions not met (e.g., status not "active")
- URL unreachable
- SSL verification failing

### Webhook Triggered but Device Not Synced

**Check webhook handler logs:**
```bash
sudo journalctl -u netbox-webhook-handler -f
```

**Common issues:**
- Device missing primary IP
- cf_monitoring not set to Yes/No
- Zabbix template not found
- Network connectivity issue

### Webhook Returns HTTP 500 Error

**Check webhook handler for errors:**
```bash
# Check last 50 lines
sudo journalctl -u netbox-webhook-handler -n 50
```

**Common causes:**
- Configuration file not found
- NetBox/Zabbix API credentials invalid
- Python dependencies missing

### Testing Webhook Manually

Send test webhook using curl:
```bash
curl -X POST http://webhook-server:5000/webhook \
  -H "Content-Type: application/json" \
  -d @test_payload.json
```

---

## Security Considerations

### 1. Network Security

- Run webhook handler on internal network
- Use firewall rules to restrict access
- Consider using reverse proxy (nginx) with SSL

### 2. Authentication

Add webhook secret verification:

**In NetBox webhook:**
```
Headers:
X-Webhook-Secret: your-secret-token-here
```

**In webhook handler:**
```python
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    secret = request.headers.get('X-Webhook-Secret')
    if secret != 'your-secret-token-here':
        return jsonify({'error': 'Unauthorized'}), 401
    # ... rest of handler
```

### 3. HTTPS/TLS

Use HTTPS for webhook endpoint:
- Configure nginx as reverse proxy with SSL
- Use Let's Encrypt for certificates
- Enable SSL verification in NetBox webhook

Example nginx config:
```nginx
server {
    listen 443 ssl;
    server_name webhook.acme.com;

    ssl_certificate /etc/letsencrypt/live/webhook.acme.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/webhook.acme.com/privkey.pem;

    location /webhook {
        proxy_pass http://127.0.0.1:5000/webhook;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Advanced Configuration

### Rate Limiting

Prevent webhook flooding:

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["100 per hour"]
)

@app.route('/webhook', methods=['POST'])
@limiter.limit("10 per minute")
def handle_webhook():
    # ... handler code
```

### Queue-Based Processing

For high-volume environments, use message queue:

```
NetBox Webhook → Redis Queue → Worker Processes → Zabbix
```

### Monitoring the Webhook Handler

Add Prometheus metrics:
```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)

# Metrics automatically tracked:
# - HTTP requests
# - Response times
# - Error rates
```

---

## Example Workflows

### Workflow 1: New Device Onboarding

1. Network engineer creates device in NetBox
   - Status: `active`
   - cf_monitoring: `No` (default)
   - Assigns primary IP

2. Webhook triggers → Device synced to Zabbix (disabled)
   - ⚠️ Host exists but disabled (no alerts)

3. Engineer validates SNMP connectivity
   ```bash
   snmpwalk -v2c -c public 10.10.100.1 sysDescr
   ```

4. Engineer enables monitoring in NetBox
   - Changes cf_monitoring: `No` → `Yes`

5. Webhook triggers → Device monitoring enabled
   - ✅ Host enabled in Zabbix (alerts active)

### Workflow 2: Maintenance Window

1. Engineer disables monitoring before maintenance
   - In NetBox: cf_monitoring: `Yes` → `No`

2. Webhook triggers → Host disabled in Zabbix
   - ⏸️ No alerts during maintenance

3. Maintenance complete → Engineer enables monitoring
   - In NetBox: cf_monitoring: `No` → `Yes`

4. Webhook triggers → Host enabled in Zabbix
   - ✅ Monitoring resumes

---

## Documentation

For complete documentation, see:
- **NETBOX_ZABBIX_SYNC.md** - Main integration guide
- **lab/zabbix/README.md** - Quick start guide
- **lab/zabbix/CUSTOM_FIELD_SETUP.md** - Custom field setup

---

**Version**: 2.0
**Last Updated**: 2025-12-07
