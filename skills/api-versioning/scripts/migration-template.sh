#!/usr/bin/env bash
# Migration Guide Generator
# Creates template for API versioning migration

cat << 'EOF'
# API Migration Guide: v1 to v2

## Summary
Breaking changes in v2 API. This guide helps you migrate.

## Timeline
- **Jan 1**: v2 Released
- **Feb 1**: v1 Sunset Warning issued
- **Jul 1**: v1 Deprecated
- **Jan 1**: v1 Removed

## Key Changes

### Authentication
- v1: `Authorization: Bearer {token}`
- v2: `Authorization: Bearer {token}` (same)

### Response Format
- v1: `{ "data": {...}, "status": "ok" }`
- v2: `{ "result": {...}, "code": 200 }`

### Endpoints Changed
- v1: `GET /api/v1/users/{id}`
- v2: `GET /api/v2/users/{id}` (same path structure)

## Migration Checklist
- [ ] Update base URL to /api/v2
- [ ] Update response parsing code
- [ ] Test all endpoints
- [ ] Update error handling
- [ ] Deploy to staging
- [ ] Full regression testing

## Support
- Migration Guide: https://docs.example.com/v1-to-v2
- Slack: #api-migration
- Email: api-team@example.com
EOF
