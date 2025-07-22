# Troubleshooting Guide

This guide helps diagnose and resolve common issues with the vnStat Dashboard application.

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Installation Issues](#installation-issues)
- [Configuration Problems](#configuration-problems)
- [Runtime Errors](#runtime-errors)
- [Data Issues](#data-issues)
- [Performance Problems](#performance-problems)
- [Network and Connectivity](#network-and-connectivity)
- [Docker Issues](#docker-issues)
- [Advanced Debugging](#advanced-debugging)

## Quick Diagnostics

Run these commands first to get an overview of the system status:

```bash
# Check if vnStat is installed and working
vnstat --version
vnstat -i eth0  # Replace eth0 with your interface

# Check Python and dependencies
python3 --version
python3 -c "import flask; print('Flask version:', flask.__version__)"

# Check application files
ls -la /path/to/vnstat-dashboard/
python3 -m py_compile dashboard.py vnstat_parser.py config.py

# Check logs
tail -f vnstat_dashboard.log
```

## Installation Issues

### 1. Python Module Import Errors

**Error**: `ModuleNotFoundError: No module named 'flask'`

**Cause**: Missing Python dependencies

**Solution**:
```bash
# Option 1: Use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Option 2: System-wide installation (not recommended)
pip3 install --user -r requirements.txt

# Option 3: Using package manager
sudo apt install python3-flask python3-werkzeug  # Ubuntu/Debian
sudo yum install python3-flask python3-werkzeug  # CentOS/RHEL
```

### 2. Virtual Environment Creation Fails

**Error**: `The virtual environment was not created successfully because ensurepip is not available`

**Solution**:
```bash
# Ubuntu/Debian
sudo apt install python3-venv python3-pip

# CentOS/RHEL
sudo yum install python3-pip
# or
sudo dnf install python3-pip

# Alternative: use system python
pip3 install --user -r requirements.txt
```

### 3. Permission Denied During Installation

**Error**: `Permission denied` when installing packages

**Solution**:
```bash
# Use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Or install for current user only
pip3 install --user -r requirements.txt

# Check file permissions
ls -la requirements.txt
chmod 644 requirements.txt
```

## Configuration Problems

### 1. Missing Configuration File

**Error**: `ModuleNotFoundError: No module named 'config'`

**Cause**: Missing `config.py` file

**Solution**:
```bash
# Copy example configuration
cp config.py.example config.py

# Edit configuration
nano config.py

# Verify configuration loads
python3 -c "import config; print('Config loaded successfully')"
```

### 2. Invalid Network Interface

**Error**: Application runs but shows no data

**Cause**: Wrong network interface name in configuration

**Diagnosis**:
```bash
# List all network interfaces
ip link show
# or
ifconfig -a
# or
ls /sys/class/net/

# Check vnStat database
vnstat --dbdir /var/lib/vnstat --list

# Test with different interface
vnstat -i eth0
vnstat -i enp0s3
vnstat -i wlan0
```

**Solution**:
```bash
# Update config.py with correct interface
nano config.py
# Change: VNSTAT_IFACE = "correct_interface_name"

# Restart application
python3 dashboard.py
```

### 3. Port Already in Use

**Error**: `OSError: [Errno 98] Address already in use`

**Cause**: Another service using the same port

**Diagnosis**:
```bash
# Check what's using the port
sudo netstat -tlnp | grep :5000
# or
sudo ss -tlnp | grep :5000
# or
sudo lsof -i :5000
```

**Solution**:
```bash
# Option 1: Change port in config.py
nano config.py
# Change: WEB_PORT = 5001

# Option 2: Stop conflicting service
sudo systemctl stop other-service

# Option 3: Kill process using port
sudo kill -9 PID_NUMBER
```

## Runtime Errors

### 1. vnStat Command Not Found

**Error**: Application shows no data, logs show command errors

**Diagnosis**:
```bash
# Check if vnStat is installed
which vnstat
vnstat --version

# Check PATH
echo $PATH

# Try running vnStat manually
vnstat -i eth0
```

**Solution**:
```bash
# Install vnStat
# Ubuntu/Debian
sudo apt update
sudo apt install vnstat

# CentOS/RHEL
sudo yum install vnstat
# or
sudo dnf install vnstat

# Start vnStat daemon
sudo systemctl start vnstat
sudo systemctl enable vnstat

# Verify installation
vnstat --version
```

### 2. Permission Denied Accessing vnStat Database

**Error**: No data displayed, permission errors in logs

**Diagnosis**:
```bash
# Check vnStat database permissions
ls -la /var/lib/vnstat/
ls -la /var/lib/vnstat/*.db

# Check current user
whoami
groups

# Test vnStat access
vnstat -i eth0
```

**Solution**:
```bash
# Option 1: Add user to vnstat group
sudo usermod -a -G vnstat $USER
# Logout and login again

# Option 2: Run with sudo (not recommended for production)
sudo python3 dashboard.py

# Option 3: Adjust permissions (careful!)
sudo chmod 644 /var/lib/vnstat/*.db
```

### 3. Flask Application Crashes

**Error**: Application exits unexpectedly

**Diagnosis**:
```bash
# Run with debug output
export DEBUG=True
python3 dashboard.py

# Check logs
tail -f vnstat_dashboard.log

# Run with Python error output
python3 -u dashboard.py 2>&1 | tee debug.log
```

**Solution**:
```bash
# Check for syntax errors
python3 -m py_compile dashboard.py vnstat_parser.py config.py

# Verify all imports
python3 -c "
import dashboard
import vnstat_parser
import config
print('All modules import successfully')
"

# Check Flask installation
python3 -c "import flask; print(flask.__version__)"
```

## Data Issues

### 1. No Data Displayed

**Cause**: vnStat database empty or not collecting data

**Diagnosis**:
```bash
# Check vnStat status
sudo systemctl status vnstat

# Check vnStat database
vnstat -i eth0
vnstat --dbdir /var/lib/vnstat --list

# Check interface activity
ip -s link show eth0
```

**Solution**:
```bash
# Start vnStat daemon
sudo systemctl start vnstat
sudo systemctl enable vnstat

# Wait for data collection (may take several minutes)
# Force database creation (if needed)
sudo vnstat -i eth0 --create

# Check data collection
watch -n 5 'vnstat -i eth0'
```

### 2. Partial Data Missing

**Cause**: vnStat collecting data but parsing fails

**Diagnosis**:
```bash
# Test vnStat output formats
vnstat -i eth0 -5  # 5-minute data
vnstat -i eth0 -h  # Hourly data
vnstat -i eth0 -d  # Daily data
vnstat -i eth0 -m  # Monthly data

# Enable debug logging
# In config.py: LOG_LEVEL = "DEBUG"
tail -f vnstat_dashboard.log
```

**Solution**:
```bash
# Check for parsing errors in logs
grep "Failed to parse" vnstat_dashboard.log
grep "NO DATA PARSED" vnstat_dashboard.log

# Test parsing manually
python3 -c "
from vnstat_parser import parse_5min, parse_hourly, parse_daily, parse_monthly
print('5-min:', len(parse_5min()))
print('Hourly:', len(parse_hourly()))
print('Daily:', len(parse_daily()))
print('Monthly:', len(parse_monthly()))
"
```

### 3. Incorrect Data Values

**Cause**: vnStat output format changes or parsing errors

**Diagnosis**:
```bash
# Compare raw vnStat output with parsed data
vnstat -i eth0 -5 > raw_5min.txt
cat raw_5min.txt

# Check for locale issues
locale
export LC_ALL=C
vnstat -i eth0 -5
```

**Solution**:
```bash
# Set consistent locale
export LC_ALL=C
export LANG=C

# Add to systemd service or startup script
# Environment=LC_ALL=C

# Update parsing regex if vnStat format changed
# Check vnstat_parser.py for regex patterns
```

## Performance Problems

### 1. Slow Page Loading

**Cause**: Large datasets or inefficient parsing

**Diagnosis**:
```bash
# Time the parsing functions
python3 -c "
import time
from vnstat_parser import parse_5min, parse_hourly, parse_daily, parse_monthly

start = time.time()
data = parse_5min()
print(f'5-min parsing: {time.time() - start:.2f}s, {len(data)} records')

start = time.time()
data = parse_hourly()
print(f'Hourly parsing: {time.time() - start:.2f}s, {len(data)} records')
"

# Check system resources
top
htop
iostat -x 1
```

**Solution**:
```bash
# Reduce data displayed
# In config.py:
TOP_MIN5_COUNT = 5  # Reduce from larger number

# Implement caching (future enhancement)
# Consider using Redis or memcached

# Optimize vnStat database
sudo vnstat --rebuilddb
```

### 2. High Memory Usage

**Cause**: Large data structures in memory

**Diagnosis**:
```bash
# Monitor memory usage
ps aux | grep python
top -p $(pgrep -f dashboard.py)

# Check data structure sizes
python3 -c "
import sys
from dashboard import build_nested_stats
data = build_nested_stats()
print(f'Data structure size: {sys.getsizeof(data)} bytes')
"
```

**Solution**:
```bash
# Limit years displayed
# Default to 1 year instead of all available data

# Implement pagination
# Process data in chunks

# Clear variables after use
# Use generators instead of lists where possible
```

### 3. High CPU Usage

**Cause**: Frequent parsing or inefficient regex

**Diagnosis**:
```bash
# Profile the application
python3 -m cProfile -o profile.stats dashboard.py
python3 -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(10)
"

# Monitor CPU usage
top -p $(pgrep -f dashboard.py)
```

**Solution**:
```bash
# Implement caching for parsed data
# Cache results for 5-10 minutes

# Optimize regex patterns
# Use compiled regex objects

# Consider background processing
# Parse data in separate thread/process
```

## Network and Connectivity

### 1. Cannot Access Dashboard Remotely

**Cause**: Binding to localhost only

**Diagnosis**:
```bash
# Check binding address
netstat -tlnp | grep :5000
ss -tlnp | grep :5000

# Check config.py
grep WEB_HOST config.py
```

**Solution**:
```bash
# Change host binding in config.py
WEB_HOST = "0.0.0.0"  # Allow all interfaces

# Or bind to specific interface
WEB_HOST = "192.168.1.100"  # Specific IP

# Check firewall
sudo ufw status
sudo iptables -L

# Open port if needed
sudo ufw allow 5000
```

### 2. SSL/HTTPS Issues

**Cause**: Direct Flask deployment without reverse proxy

**Solution**:
```bash
# Use reverse proxy (recommended)
# See nginx configuration in SECURITY.md

# Or add SSL to Flask (not recommended for production)
# pip install pyopenssl
# app.run(ssl_context='adhoc', ...)
```

### 3. Connection Timeouts

**Cause**: Slow parsing or network issues

**Diagnosis**:
```bash
# Test locally
curl -w "@curl-format.txt" http://localhost:5000/

# Create curl-format.txt:
echo "     time_namelookup:  %{time_namelookup}
       time_connect:  %{time_connect}
    time_appconnect:  %{time_appconnect}
   time_pretransfer:  %{time_pretransfer}
      time_redirect:  %{time_redirect}
 time_starttransfer:  %{time_starttransfer}
                    ----------
         time_total:  %{time_total}" > curl-format.txt
```

**Solution**:
```bash
# Increase timeouts in reverse proxy
# nginx: proxy_read_timeout 60s;

# Optimize application performance
# Implement caching and pagination

# Use production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 dashboard:app
```

## Docker Issues

### 1. Container Won't Start

**Error**: Container exits immediately

**Diagnosis**:
```bash
# Check container logs
docker logs vnstat-dashboard

# Run interactively
docker run -it --rm vnstat-dashboard /bin/bash

# Check Dockerfile
cat Dockerfile
```

**Solution**:
```bash
# Verify base image
docker pull python:3.9-slim

# Check file permissions
docker run -it --rm -v $(pwd):/app python:3.9-slim ls -la /app

# Rebuild image
docker build --no-cache -t vnstat-dashboard .
```

### 2. No Data in Docker Container

**Cause**: vnStat database not accessible in container

**Solution**:
```bash
# Mount vnStat database directory
docker run -d \
  -p 5000:5000 \
  -v /var/lib/vnstat:/var/lib/vnstat:ro \
  -v $(pwd)/config.py:/app/config.py \
  --name vnstat-dashboard \
  vnstat-dashboard

# Check volume mounts
docker inspect vnstat-dashboard | grep -A 10 "Mounts"
```

### 3. Network Interface Not Found

**Cause**: Container network namespace different from host

**Solution**:
```bash
# Use host network mode
docker run -d \
  --net=host \
  -v /var/lib/vnstat:/var/lib/vnstat:ro \
  vnstat-dashboard

# Or install vnStat in container and share data
# See Docker documentation for details
```

## Advanced Debugging

### 1. Enable Debug Logging

```bash
# In config.py
LOG_LEVEL = "DEBUG"
DEBUG = True

# Or via environment
export LOG_LEVEL=DEBUG
export DEBUG=True
python3 dashboard.py
```

### 2. Python Debugger

```python
# Add to dashboard.py for interactive debugging
import pdb; pdb.set_trace()

# Or use remote debugger
# pip install remote-pdb
# import remote_pdb; remote_pdb.set_trace()
```

### 3. Network Traffic Analysis

```bash
# Monitor network traffic
sudo tcpdump -i any port 5000

# Check application traffic
sudo netstat -tulpn | grep python
sudo ss -tulpn | grep python
```

### 4. System Call Tracing

```bash
# Trace system calls (Linux)
strace -f -e trace=network,file python3 dashboard.py

# Monitor file access
sudo inotifywait -m -r /var/lib/vnstat/
```

## Getting Help

### 1. Collect Debug Information

```bash
#!/bin/bash
# debug-info.sh - Collect system information

echo "=== System Information ==="
uname -a
lsb_release -a 2>/dev/null || cat /etc/os-release

echo "=== Python Information ==="
python3 --version
pip3 list | grep -E "(flask|werkzeug|jinja)"

echo "=== vnStat Information ==="
vnstat --version
sudo systemctl status vnstat
ls -la /var/lib/vnstat/

echo "=== Network Interfaces ==="
ip link show

echo "=== Application Status ==="
ls -la /path/to/vnstat-dashboard/
python3 -m py_compile dashboard.py vnstat_parser.py config.py

echo "=== Recent Logs ==="
tail -20 vnstat_dashboard.log 2>/dev/null || echo "No log file found"

echo "=== Process Information ==="
ps aux | grep -E "(vnstat|python.*dashboard)"
```

### 2. Minimal Test Case

```python
#!/usr/bin/env python3
# test-minimal.py - Minimal test case

import sys
import subprocess

def test_vnstat():
    try:
        result = subprocess.run(['vnstat', '--version'], 
                              capture_output=True, text=True, timeout=10)
        print(f"vnStat version: {result.stdout.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"vnStat test failed: {e}")
        return False

def test_imports():
    try:
        import flask
        import config
        import vnstat_parser
        print("All imports successful")
        return True
    except Exception as e:
        print(f"Import test failed: {e}")
        return False

if __name__ == "__main__":
    print("Running minimal tests...")
    vnstat_ok = test_vnstat()
    import_ok = test_imports()
    
    if vnstat_ok and import_ok:
        print("Basic tests passed!")
        sys.exit(0)
    else:
        print("Tests failed!")
        sys.exit(1)
```

### 3. Report Issues

When reporting issues, include:
- Operating system and version
- Python version
- vnStat version
- Complete error messages
- Relevant log entries
- Steps to reproduce
- Output from debug scripts above

### 4. Community Resources

- GitHub Issues: Report bugs and feature requests
- Documentation: Check docs/ directory
- Security Issues: Use responsible disclosure process

---

**Remember**: Most issues are configuration-related. Double-check your `config.py` file and ensure vnStat is properly installed and collecting data before diving into complex debugging.