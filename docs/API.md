# API Documentation

The vnStat Dashboard provides both web interface endpoints and potential REST API endpoints for programmatic access to network statistics.

## Table of Contents

- [Web Interface Endpoints](#web-interface-endpoints)
- [Data Format](#data-format)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Security Considerations](#security-considerations)

## Web Interface Endpoints

### Dashboard Endpoint

**GET /**

Returns the main dashboard interface with hierarchical network statistics.

**Parameters:**
- `years` (optional, integer): Number of years of data to display (default: 1)

**Example Requests:**
```bash
# Show default (1 year of data)
curl http://localhost:5000/

# Show 2 years of data
curl http://localhost:5000/?years=2

# Show 5 years of data
curl http://localhost:5000/?years=5
```

**Response:**
- Content-Type: `text/html`
- Returns rendered HTML dashboard interface

## Data Format

The dashboard processes vnStat data into a hierarchical structure:

### 5-Minute Data Structure
```json
{
  "date": "2024-01-15",
  "hour": "14",
  "minute": "14:35",
  "rx": "1.5 MB",
  "tx": "0.8 MB", 
  "total": "2.3 MB",
  "avg": "7.8 kbit/s"
}
```

### Hourly Data Structure
```json
{
  "date": "2024-01-15",
  "hour": "14",
  "rx": "45.2 MB",
  "tx": "23.1 MB",
  "total": "68.3 MB", 
  "avg": "156.2 kbit/s"
}
```

### Daily Data Structure
```json
{
  "date": "2024-01-15",
  "rx": "1.2 GB",
  "tx": "0.8 GB",
  "total": "2.0 GB",
  "avg": "185.4 kbit/s"
}
```

### Monthly Data Structure
```json
{
  "date": "2024-01",
  "rx": "35.6 GB", 
  "tx": "18.9 GB",
  "total": "54.5 GB",
  "avg": "172.8 kbit/s"
}
```

## Hierarchical Data Tree

The dashboard organizes data in a nested structure:

```
Year (2024)
├── Month (01 - January)
│   ├── Day (01)
│   │   ├── Hour (00)
│   │   │   ├── 5-min (00:00)
│   │   │   ├── 5-min (00:05)
│   │   │   └── ...
│   │   ├── Hour (01)
│   │   └── ...
│   ├── Day (02)
│   └── ...
├── Month (02 - February)
└── ...
```

## Error Handling

The application handles various error conditions gracefully:

### Common Error Scenarios

1. **vnStat Command Not Found**
   - Returns empty data arrays
   - Logs warning message
   - Dashboard shows "No data available"

2. **Invalid Network Interface**
   - Validates interface name format
   - Returns empty data if validation fails
   - Logs security warning for invalid attempts

3. **vnStat Database Empty**
   - Returns empty data structures
   - Shows message encouraging data collection time

4. **Permission Issues**
   - Logs access errors
   - Returns empty data gracefully
   - Suggests permission fixes in logs

### Error Response Format

When errors occur, the dashboard:
- Continues to render the interface
- Shows appropriate user messages
- Logs detailed error information
- Maintains application stability

## Rate Limiting

Currently, no explicit rate limiting is implemented. However, consider these factors:

### Performance Considerations
- vnStat parsing can be CPU intensive for large datasets
- Each request triggers fresh data parsing
- Consider caching for high-traffic deployments

### Recommended Limits
For production deployments, consider implementing:
- Max 60 requests per minute per IP
- Caching of parsed data (5-10 minutes)
- Connection limits in reverse proxy

## Security Considerations

### Input Validation
- Network interface names are strictly validated
- Only alphanumeric, dots, hyphens, and underscores allowed
- Maximum length of 15 characters enforced
- Command injection prevention implemented

### Command Execution Security
- Uses subprocess with argument lists (not shell strings)
- Timeout protection (30 seconds)
- No user input directly passed to shell commands
- Comprehensive error handling

### Information Disclosure Prevention
- Sensitive error details only in logs
- Generic error messages to users  
- Debug mode disabled by default
- Configurable logging levels

## Future API Enhancements

### Planned REST Endpoints

**GET /api/v1/stats/5min**
```json
{
  "status": "success",
  "data": [
    {
      "timestamp": "2024-01-15T14:35:00Z",
      "rx_bytes": 1572864,
      "tx_bytes": 838860,
      "total_bytes": 2411724,
      "avg_rate_bps": 7987
    }
  ],
  "metadata": {
    "interface": "eth0",
    "count": 5,
    "generated_at": "2024-01-15T14:40:23Z"
  }
}
```

**GET /api/v1/stats/hourly**
**GET /api/v1/stats/daily**  
**GET /api/v1/stats/monthly**

### Query Parameters (Planned)
- `interface`: Specify network interface
- `limit`: Number of records to return
- `from`: Start date (ISO 8601)
- `to`: End date (ISO 8601)
- `format`: Response format (json, csv, xml)

### Authentication (Planned)
- API key authentication
- JWT token support
- Rate limiting per key
- Role-based access control

## Integration Examples

### Python Integration
```python
import requests
import json

# Get dashboard data
response = requests.get('http://localhost:5000/?years=1')
if response.status_code == 200:
    # Parse HTML or wait for JSON API
    print("Dashboard loaded successfully")
```

### Bash/Shell Integration
```bash
#!/bin/bash
# Simple health check
response=$(curl -s -w "%{http_code}" http://localhost:5000/)
if [[ "${response: -3}" == "200" ]]; then
    echo "Dashboard is healthy"
else
    echo "Dashboard error: ${response: -3}"
fi
```

### Monitoring Integration
```yaml
# Prometheus monitoring (example)
- job_name: 'vnstat-dashboard'
  static_configs:
    - targets: ['localhost:5000']
  metrics_path: '/metrics'  # Future endpoint
  scrape_interval: 30s
```

## Development API

### Internal Functions

The following functions are available for extending the application:

```python
# vnstat_parser.py functions
parse_5min()      # Returns list of 5-minute intervals
parse_hourly()    # Returns list of hourly data
parse_daily()     # Returns list of daily data  
parse_monthly()   # Returns list of monthly data

# dashboard.py functions
build_nested_stats()  # Returns hierarchical data structure
```

### Adding Custom Endpoints

Example of adding a new endpoint:

```python
@app.route('/api/health')
def health_check():
    try:
        # Test vnstat availability
        test_data = parse_5min()
        return {
            'status': 'healthy',
            'vnstat_available': len(test_data) > 0,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            'status': 'error', 
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }, 500
```

## Support and Feedback

For API-related questions or feature requests:
- Open an issue on GitHub
- Check existing documentation
- Review security considerations before implementation