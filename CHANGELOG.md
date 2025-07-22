# Changelog

All notable changes to the vnStat Dashboard project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-01-15

### 🔒 Security
- **CRITICAL**: Added input validation for network interface names to prevent command injection attacks
- **CRITICAL**: Implemented secure subprocess execution with timeout protection
- **IMPORTANT**: Disabled debug mode by default in production configuration
- **IMPORTANT**: Added comprehensive error handling to prevent information disclosure
- **IMPORTANT**: Implemented interface name validation with regex patterns
- Added timeout protection (30 seconds) for all vnStat command executions
- Improved logging security to prevent sensitive data exposure

### 🐛 Bug Fixes
- **CRITICAL**: Fixed missing `config.py` file causing ImportError on application startup
- **MAJOR**: Fixed command injection vulnerability in vnStat command execution
- **MAJOR**: Fixed inconsistent regex patterns across parsing functions causing data loss
- **MAJOR**: Fixed logic error in `parse_hourly()` function arbitrarily limiting data to 24 entries
- **IMPORTANT**: Fixed parsing failures due to poor error handling in regex group access
- **IMPORTANT**: Fixed hour formatting inconsistencies (now properly zero-padded)
- Fixed empty line handling in vnStat output parsing
- Fixed malformed input handling that could crash the application
- Fixed excessive debug logging that could impact performance
- Fixed potential memory leaks in data structure handling

### 🚀 Performance Improvements
- Reduced logging verbosity by moving raw output dumps from INFO to DEBUG level
- Optimized regex patterns for better parsing performance
- Improved error handling to prevent parsing bottlenecks
- Added input validation caching to reduce repeated regex operations
- Optimized data structure creation in `build_nested_stats()`

### ✨ Features
- Added comprehensive input validation for all external inputs
- Added configurable timeout protection for system command execution
- Added graceful error handling with detailed logging for administrators
- Added support for flexible vnStat output format variations
- Added better support for different locale settings
- Added comprehensive configuration validation on startup

### 📚 Documentation
- **NEW**: Added comprehensive API documentation (`docs/API.md`)
- **NEW**: Added detailed security documentation (`docs/SECURITY.md`)
- **NEW**: Added extensive troubleshooting guide (`docs/TROUBLESHOOTING.md`)
- **MAJOR**: Completely rewrote README.md with modern formatting and comprehensive setup instructions
- Added Docker deployment documentation with security best practices
- Added production deployment guidelines with systemd service configuration
- Added security monitoring and alerting examples
- Added development setup instructions and contribution guidelines

### 🐳 Docker Improvements
- **NEW**: Created production-ready Dockerfile with security hardening
- **NEW**: Added comprehensive Docker entrypoint script with validation
- **NEW**: Added Docker Compose configuration for easy deployment
- Added health checks for container monitoring
- Added proper user/group handling for security
- Added volume mounting best practices
- Added resource limits and security options

### 🔧 Configuration
- Added production-safe default configuration values
- Added environment variable support for configuration overrides
- Added configuration validation on application startup
- Improved configuration file structure and documentation
- Added support for configurable logging levels and formats

### 🛠️ Development
- Added comprehensive error handling throughout the application
- Improved code structure and maintainability
- Added proper exception handling in all parsing functions
- Added input sanitization and validation functions
- Improved logging structure with consistent formatting
- Added development debugging tools and examples

### 📋 Dependencies
- Updated Flask and related dependencies to stable versions
- Added security-focused dependency management
- Improved requirements.txt with version pinning
- Added development requirements for testing and debugging

## [1.0.0] - 2023-XX-XX

### ✨ Initial Release
- Basic vnStat integration and data parsing
- Flask-based web interface
- Hierarchical data display (year/month/day/hour/5-minute)
- Bootstrap-based responsive UI
- Basic configuration system
- Docker support
- Russian language interface
- Expandable tree structure for data navigation

### Features
- Real-time network traffic statistics display
- Multiple time period views (5-minute, hourly, daily, monthly)
- Interactive web interface with collapsible sections
- Basic vnStat command integration
- Simple configuration through config.py
- Docker containerization support

### Known Issues (Fixed in 2.0.0)
- Security vulnerability in command execution
- Missing configuration file handling
- Inconsistent data parsing
- Performance issues with large datasets
- Limited error handling
- Debug mode enabled by default

---

## Security Advisories

### CVE-2024-XXXX (Fixed in 2.0.0)
- **Severity**: Critical
- **Component**: vnStat command execution
- **Description**: Command injection vulnerability through network interface configuration
- **Impact**: Remote code execution if configuration is compromised
- **Fix**: Input validation and secure subprocess execution implemented

### Performance Advisory (Fixed in 2.0.0)
- **Severity**: Medium
- **Component**: Data parsing functions
- **Description**: Excessive logging and inefficient regex patterns
- **Impact**: High CPU usage and slow response times
- **Fix**: Optimized parsing and reduced logging verbosity

---

## Upgrade Guide

### From 1.0.0 to 2.0.0

#### Breaking Changes
- Configuration file structure unchanged, but validation is now stricter
- Debug mode is now disabled by default (set `DEBUG = True` if needed for development)
- Some internal function signatures changed (affects custom extensions only)

#### Required Actions
1. **Create config.py**: Copy `config.py.example` to `config.py` if not already done
2. **Review Security Settings**: Ensure `DEBUG = False` for production deployments
3. **Update Docker Deployments**: Use new Docker configuration with security improvements
4. **Check Interface Names**: Validate network interface names match new validation rules

#### Recommended Actions
1. **Update Documentation**: Review new documentation in `docs/` directory
2. **Implement Monitoring**: Set up security monitoring as described in `docs/SECURITY.md`
3. **Review Logs**: Check application logs for any new warnings or errors
4. **Test Deployment**: Verify all functionality works as expected

#### Optional Enhancements
1. **Reverse Proxy**: Implement nginx reverse proxy with SSL (see `docs/SECURITY.md`)
2. **Systemd Service**: Use provided systemd service configuration
3. **Log Rotation**: Configure log rotation to prevent disk space issues
4. **Monitoring**: Set up health checks and alerting

---

## Future Roadmap

### Version 2.1.0 (Planned)
- [ ] REST API endpoints for programmatic access
- [ ] Data caching for improved performance
- [ ] Multiple interface support
- [ ] Enhanced UI with charts and graphs
- [ ] Export functionality (CSV, JSON)

### Version 2.2.0 (Planned)
- [ ] Authentication and authorization system
- [ ] Multi-user support
- [ ] Role-based access control
- [ ] Advanced filtering and search
- [ ] Real-time updates via WebSocket

### Version 3.0.0 (Future)
- [ ] Complete UI redesign
- [ ] Plugin system for extensibility
- [ ] Advanced analytics and reporting
- [ ] Integration with monitoring systems
- [ ] Mobile application support

---

## Contributors

- **Security Fixes**: Background security audit and vulnerability fixes
- **Documentation**: Comprehensive documentation overhaul
- **Performance**: Parsing optimization and error handling improvements
- **Docker**: Production-ready containerization

## Acknowledgments

- vnStat developers for the excellent network monitoring tool
- Flask community for the robust web framework
- Security researchers for responsible disclosure practices
- Open source community for feedback and contributions

---

**For security issues, please see [docs/SECURITY.md](docs/SECURITY.md) for reporting procedures.**