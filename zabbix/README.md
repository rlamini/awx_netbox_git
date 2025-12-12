# Zabbix Integration Files

This folder contains all Zabbix-related configuration, documentation, and integration scripts for the NetBox-Zabbix integration.

## 📁 Contents

### Configuration Files
- **zabbix-docker-compose.yml** - Docker Compose configuration for Zabbix stack
- **zabbix-env.example** - Environment variables template for Zabbix
- **.env.example** - Combined NetBox & Zabbix environment variables for integration
- **requirements.txt** - Python package dependencies

### Setup Scripts
- **setup-zabbix.sh** - Automated setup script for Zabbix installation
- **setup_venv.sh** - Virtual environment setup script (recommended)

### Integration Scripts
- **netbox_to_zabbix_sync.py** - Synchronizes devices from NetBox to Zabbix
- **test_connections.py** - Tests connectivity to both NetBox and Zabbix APIs

### Documentation
- **ZABBIX_DOCKER_SETUP.md** - Complete Zabbix Docker setup guide
- **NETBOX_ZABBIX_INTEGRATION.md** - NetBox and Zabbix integration guide

## 🚀 Quick Start

### 1. Setup Python Virtual Environment (Recommended)

Using a virtual environment isolates Python dependencies and is the recommended approach:

```bash
# Run automated setup script
./setup_venv.sh

# This will:
# - Create a virtual environment in ./venv
# - Install all required packages from requirements.txt
# - Verify all installations

# Activate the virtual environment
source venv/bin/activate
```

**Manual Setup (Alternative):**

If you prefer to set up manually:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Without Virtual Environment (Not Recommended):**

```bash
# Install globally (requires sudo on some systems)
pip install pynetbox pyzabbix python-dotenv requests
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### 3. Test Connections

Before running any integration, test connectivity to both NetBox and Zabbix:

```bash
# Ensure venv is activated
source venv/bin/activate

# Run connection test
python test_connections.py
```

### 4. Setup Zabbix (if not already running)

```bash
# Run setup script
./setup-zabbix.sh

# Or manually with docker-compose
docker-compose -f zabbix-docker-compose.yml up -d
```

### 5. Run NetBox to Zabbix Sync

```bash
# Ensure venv is activated
source venv/bin/activate

# After successful connection tests
python netbox_to_zabbix_sync.py
```

### Deactivating Virtual Environment

When you're done working with the scripts:

```bash
# Deactivate the virtual environment
deactivate
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# NetBox Configuration
NETBOX_URL=http://localhost:8000
NETBOX_TOKEN=your_netbox_api_token_here

# Zabbix Configuration
ZABBIX_URL=http://localhost:8080
ZABBIX_USER=Admin
ZABBIX_PASSWORD=zabbix

# Logging (optional)
LOG_FILE=/var/log/netbox-zabbix-sync.log
LOG_LEVEL=INFO
```

### Getting NetBox API Token

1. Log into NetBox web interface
2. Click your username (top right)
3. Go to "API Tokens" or "Profile"
4. Click "Add a token" or "Create Token"
5. Set permissions as needed (read/write)
6. Copy the generated token
7. Use it as `NETBOX_TOKEN` in your `.env` file

## 📊 Connection Test Output

The `test_connections.py` script will:

✅ Test NetBox connectivity and display:
- NetBox version
- Number of sites, devices, and VMs
- API endpoint availability

✅ Test Zabbix connectivity and display:
- Zabbix version
- Number of hosts, host groups, and templates
- User information

Example output:
```
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║     NetBox & Zabbix Connection Test Script                ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

============================================================
TESTING NETBOX CONNECTION
============================================================

✅ NetBox connection successful!
   NetBox Version: 4.4.7

Testing API endpoints:
   ✓ Sites: 5 found
   ✓ Devices: 23 found
   ✓ Virtual Machines: 12 found

============================================================
TESTING ZABBIX CONNECTION
============================================================

✅ Zabbix connection successful!
   Zabbix Version: 7.0.0

Testing API endpoints:
   ✓ Hosts: 15 found
   ✓ Host Groups: 8 found
   ✓ Templates: 45 found

============================================================
SUMMARY
============================================================

✅ NetBox: Connected successfully
✅ Zabbix: Connected successfully

🎉 All tests passed!
```

## 🔒 Security Best Practices

1. **Never commit `.env` files** to version control
2. Keep API tokens secure and rotate them regularly
3. Use strong passwords for Zabbix admin account
4. Limit API token permissions to minimum required
5. In production, use HTTPS for both NetBox and Zabbix
6. Consider using secrets management tools (Vault, etc.)
7. Regularly backup your credentials securely

## 📚 Additional Documentation

- [ZABBIX_DOCKER_SETUP.md](./ZABBIX_DOCKER_SETUP.md) - Detailed Zabbix setup instructions
- [NETBOX_ZABBIX_INTEGRATION.md](./NETBOX_ZABBIX_INTEGRATION.md) - Integration architecture and setup
- See parent directory for NetBox setup documentation

## 🐛 Troubleshooting

### Connection Test Fails

1. **NetBox Connection Issues:**
   - Verify NetBox is running: `docker ps | grep netbox`
   - Check NetBox URL is correct
   - Verify API token is valid
   - Ensure network connectivity

2. **Zabbix Connection Issues:**
   - Verify Zabbix is running: `docker ps | grep zabbix`
   - Check Zabbix URL is correct (usually port 8080)
   - Default credentials: Admin/zabbix
   - Try accessing Zabbix web interface manually

3. **Missing Python Packages:**
   ```bash
   pip install pynetbox pyzabbix python-dotenv requests
   ```

### Common Issues

- **ImportError**: Install missing Python packages
- **Authentication Error**: Check credentials in `.env` file
- **Connection Timeout**: Verify services are running and accessible
- **SSL Certificate Error**: Use HTTP for testing, or configure SSL properly

## 📝 License

MIT License - See parent directory for full license information.

## 🤝 Contributing

Contributions are welcome! Please ensure all tests pass before submitting changes.

## 📧 Support

For issues and questions, please refer to the main project documentation or open an issue in the repository.
