# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New dashboard analytics feature
- Dark mode support

### Changed
- Improved performance of report generation

## [2.1.0] - 2024-02-07

### Added
- Two-factor authentication via TOTP
- Export reports to PDF and Excel
- User profile customization
- API rate limiting configuration
- Webhook support for events

### Changed
- Updated Node.js dependencies to latest versions
- Improved search algorithm performance by 40%
- Refactored database query optimization
- Enhanced error messages with actionable steps

### Fixed
- Fixed login timeout issue on Safari
- Fixed CSV export formatting
- Fixed timezone handling for international users
- Fixed memory leak in WebSocket connections

### Deprecated
- Deprecated `/api/v1/` endpoints (migrate to `/api/v2/`)
- Deprecated CSV export (use PDF export instead)

### Security
- Added CSRF token validation
- Updated SSL/TLS to version 1.3
- Fixed SQL injection vulnerability in search
- Implemented rate limiting on auth endpoints

## [2.0.0] - 2024-01-15

### Added
- Complete UI redesign with modern components
- New REST API v2 with OpenAPI documentation
- User feedback and rating system
- Advanced filtering and sorting
- Real-time notifications
- Dark mode theme

### Changed
- Migrated frontend from Angular to React
- Changed authentication from basic auth to JWT
- API response format completely restructured
- Database schema redesign for better performance

### Removed
- Removed Angular components (migrate to React)
- Removed basic authentication (use JWT)
- Removed legacy XML API v1
- Removed deprecated user roles

### Fixed
- Fixed performance issues on large datasets
- Fixed cross-browser compatibility

## [1.5.2] - 2023-12-20

### Fixed
- Fixed email notification delivery
- Fixed report generation timeout
- Fixed file upload validation

## [1.5.1] - 2023-12-10

### Fixed
- Hot fix for critical bug in payment processing

## [1.5.0] - 2023-12-01

### Added
- Email notification preferences
- Advanced user filtering
- Export data to multiple formats
- User activity audit log

### Changed
- Improved UI responsiveness
- Updated authentication flow

### Fixed
- Fixed navigation menu on mobile devices

## [1.0.0] - 2023-10-15

### Added
- Initial release
- User management system
- Basic dashboard
- Report generation
- Email notifications
