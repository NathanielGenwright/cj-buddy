# SSL Certificate Management (`bin/ssl`)

## Quick Start
| Command | Use Case |
|---------|----------|
| `bin/ssl/create-certs` | Generate local SSL certificates |
| `bin/ssl/register-ca` | Register CA cert with macOS keychain |
| `bin/ssl/remove-ca` | Remove CA cert from keychain |
| `bin/ssl/remove-certs` | Delete all local certificates |

## Why SSL for Local Development?

The Muni dev environment uses `*.munidev.local` domains with HTTPS because:
- Tabi Excel Add-In requires HTTPS for all dependent services
- Microsoft's default localhost certs don't work with custom domains
- Provides realistic development environment matching production

## Initial Setup (One-time)

### 1. Configure Environment
```bash
# Add MUNISSL section from bash_muni.template.txt to your bash_muni file
```

### 2. Generate Certificates
```bash
bin/ssl/create-certs                    # Generate wildcard cert for *.munidev.local
```

### 3. Register with System
```bash
bin/ssl/register-ca                     # Add CA to macOS keychain
```

### 4. Start Services
```bash
bin/dc/up                               # SSL-proxy container uses certs automatically
```

## Certificate Management

### Generate New Certificates
```bash
bin/ssl/create-certs                    # Create all certificate files
bin/ssl/create-certs --force            # Force regenerate (deletes existing)
```

### System Integration
```bash
bin/ssl/register-ca                     # Add CA to system keychain
bin/ssl/remove-ca                       # Remove CA from keychain
```

### Cleanup
```bash
bin/ssl/remove-certs                    # Delete all certificate files
```

## Generated Files

The scripts create certificates in `~/.muni/ssl/`:

| File | Environment Variable | Use Case |
|------|---------------------|----------|
| ca.crt | `MUNI_SSL_CA_CERT` | Certificate Authority |
| server.key | `MUNI_SSL_SERVER_KEY` | Private key |
| server.crt | `MUNI_SSL_SERVER_CERT` | Server certificate |
| server.pem | `MUNI_SSL_SERVER_PEM` | Combined PEM format |
| server.pfx | `MUNI_SSL_SERVER_PFX` | PKCS#12 format |

## How It Works

1. **Certificate Generation**: Creates self-signed wildcard cert for `*.munidev.local`
2. **System Registration**: Adds CA cert to macOS keychain for browser trust
3. **Docker Integration**: Volumes mount certs into ssl-proxy container
4. **Service Access**: All services accessible via `https://*.munidev.local`

## Common Workflows

### First-Time Setup
```bash
# 1. Configure bash_muni with MUNISSL section
# 2. Generate certificates
bin/ssl/create-certs

# 3. Register with system
bin/ssl/register-ca

# 4. Start development environment
bin/dc/up
```

### Certificate Renewal
```bash
bin/ssl/create-certs --force            # Regenerate certs
bin/ssl/register-ca                     # Re-register if needed
```

### Troubleshooting SSL Issues
```bash
# Remove and recreate everything
bin/ssl/remove-ca                       # Remove from keychain
bin/ssl/remove-certs                    # Delete files
bin/ssl/create-certs                    # Regenerate
bin/ssl/register-ca                     # Re-register
```

### Environment Cleanup
```bash
bin/ssl/remove-ca                       # Remove from system
bin/ssl/remove-certs                    # Delete files
```

## Service URLs

After setup, access services via HTTPS:
- Main app: `https://web.munidev.local`
- API services: `https://api.munidev.local`
- Customer portal: `https://portal.munidev.local`

## Important Notes

- **Development Only**: These certificates are ONLY for local development
- **Self-Signed**: Browser will show warnings until CA is registered
- **Wildcard Domain**: Covers all `*.munidev.local` subdomains
- **macOS Specific**: Registration scripts designed for macOS keychain
- **Docker Integration**: Certificates automatically mounted via environment variables

## Prerequisites

- macOS with security command-line tools
- OpenSSL for certificate generation
- MUNISSL environment variables configured
- Docker for ssl-proxy container