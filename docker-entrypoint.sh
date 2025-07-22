#!/bin/bash
set -e

# Docker entrypoint script for vnStat Dashboard

echo "Starting vnStat Dashboard container..."

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check if vnstat database exists and is accessible
check_vnstat_data() {
    if [ -d "/var/lib/vnstat" ]; then
        if [ "$(ls -A /var/lib/vnstat 2>/dev/null)" ]; then
            log "vnStat database directory found with data"
            return 0
        else
            log "vnStat database directory is empty"
            return 1
        fi
    else
        log "vnStat database directory not found"
        return 1
    fi
}

# Function to validate configuration
validate_config() {
    log "Validating configuration..."
    
    if [ ! -f "config.py" ]; then
        log "ERROR: config.py not found. Please mount your configuration file."
        exit 1
    fi
    
    # Test if config can be imported
    if ! python -c "import config" 2>/dev/null; then
        log "ERROR: config.py has syntax errors or missing dependencies"
        exit 1
    fi
    
    log "Configuration validation passed"
}

# Function to test vnstat availability
test_vnstat() {
    log "Testing vnStat availability..."
    
    if ! command -v vnstat >/dev/null 2>&1; then
        log "ERROR: vnstat command not found"
        exit 1
    fi
    
    # Get interface from config
    INTERFACE=$(python -c "import config; print(config.VNSTAT_IFACE)" 2>/dev/null || echo "eth0")
    log "Configured interface: $INTERFACE"
    
    # Test vnstat with a timeout
    if timeout 10 vnstat --version >/dev/null 2>&1; then
        log "vnStat is available (version: $(vnstat --version 2>/dev/null | head -1))"
    else
        log "WARNING: vnStat command failed or timed out"
    fi
}

# Function to wait for vnstat data
wait_for_data() {
    local max_wait=60  # Maximum wait time in seconds
    local wait_time=0
    local interval=5
    
    log "Checking for vnStat data availability..."
    
    while [ $wait_time -lt $max_wait ]; do
        if check_vnstat_data; then
            log "vnStat data is available"
            return 0
        fi
        
        log "Waiting for vnStat data... ($wait_time/$max_wait seconds)"
        sleep $interval
        wait_time=$((wait_time + interval))
    done
    
    log "WARNING: No vnStat data found after $max_wait seconds"
    log "The dashboard will start but may show no data until vnStat collects statistics"
    return 0
}

# Function to setup logging
setup_logging() {
    # Create logs directory if it doesn't exist
    mkdir -p logs
    
    # Set log file path from config or use default
    LOG_FILE=$(python -c "import config; print(getattr(config, 'LOG_FILE', 'vnstat_dashboard.log'))" 2>/dev/null || echo "vnstat_dashboard.log")
    
    # Ensure log file is writable
    touch "$LOG_FILE" 2>/dev/null || {
        log "WARNING: Cannot create log file $LOG_FILE, using stdout"
        export LOG_FILE=""
    }
    
    log "Logging setup complete (log file: ${LOG_FILE:-stdout})"
}

# Function to display startup information
show_startup_info() {
    log "=== vnStat Dashboard Startup Information ==="
    log "Python version: $(python --version)"
    log "Working directory: $(pwd)"
    log "User: $(whoami)"
    log "Available interfaces: $(ls /sys/class/net/ 2>/dev/null | tr '\n' ' ' || echo 'unknown')"
    
    if command -v vnstat >/dev/null 2>&1; then
        log "vnStat version: $(vnstat --version 2>/dev/null | head -1 || echo 'unknown')"
    fi
    
    # Show mounted volumes
    if [ -d "/var/lib/vnstat" ]; then
        local db_count=$(ls -1 /var/lib/vnstat/*.db 2>/dev/null | wc -l || echo "0")
        log "vnStat database files: $db_count"
    fi
    
    log "=============================================="
}

# Function to handle shutdown signals
cleanup() {
    log "Received shutdown signal, cleaning up..."
    # Add any cleanup tasks here
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Main execution
main() {
    log "vnStat Dashboard container starting..."
    
    # Show startup information
    show_startup_info
    
    # Validate configuration
    validate_config
    
    # Setup logging
    setup_logging
    
    # Test vnstat
    test_vnstat
    
    # Wait for data (with timeout)
    wait_for_data
    
    log "Starting vnStat Dashboard application..."
    
    # Execute the main command
    exec "$@"
}

# Handle special commands
case "$1" in
    "bash"|"sh"|"/bin/bash"|"/bin/sh")
        log "Starting interactive shell..."
        exec "$@"
        ;;
    "test")
        log "Running container tests..."
        validate_config
        test_vnstat
        check_vnstat_data
        log "Container tests completed"
        exit 0
        ;;
    "help"|"--help")
        echo "vnStat Dashboard Docker Container"
        echo ""
        echo "Usage:"
        echo "  docker run vnstat-dashboard                    # Start dashboard"
        echo "  docker run vnstat-dashboard test               # Run tests"
        echo "  docker run vnstat-dashboard bash               # Interactive shell"
        echo ""
        echo "Environment variables:"
        echo "  DEBUG=true                                      # Enable debug mode"
        echo ""
        echo "Required volumes:"
        echo "  -v /var/lib/vnstat:/var/lib/vnstat:ro          # vnStat database"
        echo "  -v /path/to/config.py:/app/config.py           # Configuration file"
        echo ""
        exit 0
        ;;
    *)
        # Default behavior - run main function
        main "$@"
        ;;
esac