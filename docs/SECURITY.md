# Security Documentation

This document outlines the security considerations, implemented protections, and best practices for the vnStat Dashboard application.

## Table of Contents

- [Security Overview](#security-overview)
- [Threat Model](#threat-model)
- [Implemented Security Measures](#implemented-security-measures)
- [Configuration Security](#configuration-security)
- [Deployment Security](#deployment-security)
- [Monitoring and Logging](#monitoring-and-logging)
- [Security Best Practices](#security-best-practices)
- [Incident Response](#incident-response)

## Security Overview

The vnStat Dashboard has been designed with security as a primary concern. The application processes system-level network statistics and executes system commands, making security critical for safe operation.

### Security Principles Applied

1. **Defense in Depth**: Multiple layers of security controls
2. **Least Privilege**: Minimal permissions and access rights
3. **Input Validation**: Strict validation of all external inputs
4. **Secure by Default**: Safe default configurations
5. **Fail Secure**: Graceful degradation when security checks fail

## Threat Model

### Potential Attack Vectors

1. **Command Injection**
   - **Risk**: High
   - **Vector**: Malicious network interface names
   - **Mitigation**: Input validation and safe command execution

2. **Information Disclosure**
   - **Risk**: Medium
   - **Vector**: Error messages, debug output, logs
   - **Mitigation**: Controlled error handling and logging

3. **Denial of Service**
   - **Risk**: Medium  
   - **Vector**: Resource exhaustion, infinite loops
   - **Mitigation**: Timeouts, resource limits

4. **Configuration Tampering**
   - **Risk**: Medium
   - **Vector**: Unauthorized config file modifications
   - **Mitigation**: File permissions, validation

5. **Network-based Attacks**
   - **Risk**: Low-Medium
   - **Vector**: Web interface exploitation
   - **Mitigation**: Secure defaults, proper headers

### Assets Protected

- System network statistics
- Server resources (CPU, memory)
- Network interface information
- Application logs and configuration
- Host system integrity

## Implemented Security Measures

### 1. Input Validation

#### Network Interface Name Validation
```python
def validate_interface_name(interface):
    """Validate network interface name to prevent command injection"""
    if not interface:
        raise ValueError("Interface name cannot be empty")
    
    # Allow only alphanumeric characters, dots, hyphens, and underscores
    if not re.match(r'^[a-zA-Z0-9._-]+$', interface):
        raise ValueError(f"Invalid interface name: {interface}")
    
    # Prevent excessively long interface names
    if len(interface) > 15:  # Linux interface names are typically <= 15 chars
        raise ValueError(f"Interface name too long: {interface}")
    
    return interface
```

**Protection Against:**
- Command injection attacks
- Path traversal attempts
- Buffer overflow attempts
- Special character exploitation

### 2. Secure Command Execution

#### Subprocess Security
```python
def get_vnstat_output(args):
    try:
        validated_interface = validate_interface_name(VNSTAT_IFACE)
        # Use list format to prevent shell injection
        cmd = ['vnstat', '-i', validated_interface] + args
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            logging.error(f"vnstat command failed with code {result.returncode}: {result.stderr}")
            return ""
            
        return result.stdout
    except (subprocess.TimeoutExpired, ValueError) as e:
        logging.error(f"Error executing vnstat command: {e}")
        return ""
```

**Security Features:**
- No shell interpretation (list-based command execution)
- Command timeout protection (30 seconds)
- Error code validation
- Exception handling for all failure modes
- No user input directly passed to system commands

### 3. Error Handling and Information Disclosure Prevention

#### Secure Error Responses
- Generic error messages to users
- Detailed errors only in server logs
- No stack traces exposed to clients
- Controlled logging levels

#### Example Implementation
```python
try:
    # Risky operation
    result = parse_vnstat_data()
except Exception as e:
    # Log detailed error for administrators
    logging.error(f"Parsing failed: {e}")
    # Return generic message to user
    return []  # Empty data, no error details exposed
```

### 4. Configuration Security

#### Secure Defaults
```python
# Production-safe defaults
DEBUG = False          # Debug mode disabled
WEB_HOST = "127.0.0.1" # Localhost only by default
LOG_LEVEL = "INFO"     # Appropriate logging level
```

#### Configuration Validation
- Interface names validated on startup
- Port number range checking
- Path validation for log files
- Boolean value validation

### 5. Logging Security

#### Structured Logging
```python
logging.basicConfig(
    filename=LOG_FILE,
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT
)
```

**Security Features:**
- Configurable log levels
- No sensitive data in logs
- Structured log format
- File-based logging (not stdout in production)

## Configuration Security

### File Permissions

Recommended file permissions:
```bash
# Configuration files - readable by application only
chmod 600 config.py
chown app-user:app-group config.py

# Application files - readable by application
chmod 644 *.py
chown app-user:app-group *.py

# Log directory - writable by application
chmod 750 /var/log/vnstat-dashboard/
chown app-user:app-group /var/log/vnstat-dashboard/
```

### Environment Variables

For sensitive configuration, use environment variables:
```bash
# More secure than config files
export VNSTAT_IFACE="eth0"
export WEB_PORT="5000" 
export DEBUG="False"
```

### Configuration Validation

The application validates all configuration values:
```python
# Validate on startup
if not re.match(r'^[a-zA-Z0-9._-]+$', VNSTAT_IFACE):
    raise ValueError(f"Invalid interface configuration: {VNSTAT_IFACE}")
```

## Deployment Security

### Production Deployment Checklist

- [ ] **Debug Mode**: Ensure `DEBUG = False`
- [ ] **Host Binding**: Use `127.0.0.1` unless external access needed
- [ ] **Reverse Proxy**: Deploy behind nginx/Apache with SSL
- [ ] **Firewall**: Restrict access to necessary ports only
- [ ] **User Account**: Run with dedicated non-root user
- [ ] **File Permissions**: Secure file and directory permissions
- [ ] **Log Rotation**: Configure log rotation to prevent disk fill
- [ ] **Updates**: Keep dependencies updated

### Reverse Proxy Security (Nginx Example)

```nginx
server {
    listen 443 ssl http2;
    server_name dashboard.example.com;
    
    # SSL Configuration
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=dashboard:10m rate=10r/m;
    limit_req zone=dashboard burst=5;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Security
        proxy_hide_header X-Powered-By;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

### Systemd Service Security

```ini
[Unit]
Description=vnStat Dashboard
After=network.target vnstat.service

[Service]
Type=simple
User=vnstat-dashboard
Group=vnstat-dashboard
WorkingDirectory=/opt/vnstat-dashboard
Environment=PATH=/opt/vnstat-dashboard/venv/bin

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/vnstat-dashboard/logs
PrivateTmp=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true

ExecStart=/opt/vnstat-dashboard/venv/bin/python dashboard.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Monitoring and Logging

### Security Monitoring

Monitor these events for security issues:

1. **Failed Command Executions**
   ```bash
   grep "vnstat command failed" /var/log/vnstat-dashboard/app.log
   ```

2. **Invalid Interface Names**
   ```bash
   grep "Invalid interface name" /var/log/vnstat-dashboard/app.log
   ```

3. **Command Timeouts**
   ```bash
   grep "TimeoutExpired" /var/log/vnstat-dashboard/app.log
   ```

4. **Parsing Failures**
   ```bash
   grep "Failed to parse" /var/log/vnstat-dashboard/app.log
   ```

### Log Analysis

Regular security log analysis:
```bash
# Daily security check script
#!/bin/bash
LOG_FILE="/var/log/vnstat-dashboard/app.log"
DATE=$(date -d "yesterday" +%Y-%m-%d)

echo "Security Analysis for $DATE"
echo "================================"

echo "Command Injection Attempts:"
grep "$DATE.*Invalid interface name" "$LOG_FILE" | wc -l

echo "Command Failures:"
grep "$DATE.*vnstat command failed" "$LOG_FILE" | wc -l

echo "Timeout Events:"
grep "$DATE.*TimeoutExpired" "$LOG_FILE" | wc -l
```

### Alerting

Set up alerts for security events:
```bash
# Example using systemd journal
journalctl -u vnstat-dashboard -f | grep -E "(Invalid interface|command failed|TimeoutExpired)" | \
while read line; do
    echo "SECURITY ALERT: $line" | mail -s "vnStat Dashboard Security Alert" admin@example.com
done
```

## Security Best Practices

### For Administrators

1. **Regular Updates**
   ```bash
   # Update dependencies regularly
   pip install --upgrade -r requirements.txt
   ```

2. **Security Auditing**
   ```bash
   # Check for known vulnerabilities
   pip install safety
   safety check
   ```

3. **Access Control**
   - Use strong passwords/keys
   - Implement IP-based access restrictions
   - Enable two-factor authentication where possible

4. **Network Security**
   - Use HTTPS/TLS for all connections
   - Implement proper firewall rules
   - Consider VPN for remote access

### For Developers

1. **Code Review**
   - Review all changes for security implications
   - Pay special attention to input handling
   - Validate all external data sources

2. **Testing**
   ```python
   # Security test example
   def test_interface_validation():
       # Test malicious inputs
       malicious_inputs = [
           "; rm -rf /",
           "eth0 && cat /etc/passwd",
           "../../../etc/passwd",
           "eth0$(whoami)",
           "a" * 100  # Long input
       ]
       
       for input_val in malicious_inputs:
           with pytest.raises(ValueError):
               validate_interface_name(input_val)
   ```

3. **Dependency Management**
   - Pin dependency versions
   - Regular security updates
   - Use virtual environments
   - Audit third-party packages

## Incident Response

### Security Incident Procedure

1. **Detection**
   - Monitor logs for suspicious activity
   - Set up automated alerts
   - Regular security audits

2. **Containment**
   ```bash
   # Emergency shutdown
   sudo systemctl stop vnstat-dashboard
   
   # Block suspicious IPs
   sudo iptables -A INPUT -s SUSPICIOUS_IP -j DROP
   ```

3. **Investigation**
   - Preserve log files
   - Analyze attack vectors
   - Identify compromised data

4. **Recovery**
   - Apply security patches
   - Update configurations
   - Restart services securely

5. **Lessons Learned**
   - Document the incident
   - Update security procedures
   - Implement additional controls

### Emergency Contacts

Maintain a list of emergency contacts:
- System Administrator
- Security Team
- Network Operations
- Management

### Recovery Procedures

```bash
# Emergency recovery script
#!/bin/bash
echo "Starting emergency recovery..."

# Stop service
sudo systemctl stop vnstat-dashboard

# Backup current state
sudo cp -r /opt/vnstat-dashboard /opt/vnstat-dashboard.backup.$(date +%s)

# Reset to known good state
sudo git checkout main
sudo git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Validate configuration
python -c "import config; print('Config validation passed')"

# Restart service
sudo systemctl start vnstat-dashboard
sudo systemctl status vnstat-dashboard

echo "Recovery completed. Check logs for any issues."
```

## Security Contact

For security-related issues:
- **Email**: security@example.com
- **GPG Key**: Available on keyservers
- **Response Time**: 24 hours for critical issues

### Responsible Disclosure

We encourage responsible disclosure of security vulnerabilities:
1. Report privately to security contact
2. Allow reasonable time for fix
3. Coordinate public disclosure timing
4. Provide credit for discovery (if desired)

---

**Remember**: Security is an ongoing process. Regularly review and update these procedures as threats evolve and the application grows.