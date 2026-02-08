# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Codoctopus, please report it by:
- Opening a private security advisory on GitHub
- Or contacting the maintainers directly

Please do **NOT** create public issues for security vulnerabilities.

## Security Best Practices

### API Keys and Secrets Management

This project requires several API keys and secrets to function:

1. **OpenAI API Keys** - Required for AI code generation and analysis
2. **MongoDB Connection URI** - Database connection string
3. **JWT Secret** - Used for user authentication
4. **SSL Certificates** - For HTTPS connections
5. **RSA Key Pair** - For password encryption/decryption

### Setting Up Secrets

All sensitive credentials should be placed in the `Keys/` directory, which is excluded from version control via `.gitignore`.

**⚠️ CRITICAL: Never commit the `Keys/` directory or any files containing actual secrets to git.**

To set up your environment:

1. Copy the example files from `Keys.example/` to a new `Keys/` directory:
   ```bash
   cp -r Keys.example Keys
   ```

2. Edit each file in the `Keys/` directory and replace the placeholder values with your actual credentials:
   - `openai_key.txt` - Add your OpenAI API keys (one per line)
   - `database_uri.txt` - Add your MongoDB connection URI
   - `jwt_secret.txt` - Generate and add a secure JWT secret
   - Other certificate and key files as needed

3. Ensure proper file permissions (recommended for production):
   ```bash
   chmod 600 Keys/*
   ```

### Generating Secure Secrets

#### JWT Secret
Generate a cryptographically secure JWT secret:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### RSA Key Pair
Generate RSA keys for password encryption:
```bash
cd Keys
openssl genrsa -out private_key.pem 2048
openssl rsa -in private_key.pem -pubout -out public_key.pem
```

#### SSL Certificate
For development (self-signed):
```bash
cd Keys
openssl req -x509 -newkey rsa:4096 -keyout server_private_key.key -out server_certificate.crt -days 365 -nodes
```

For production, obtain certificates from a trusted Certificate Authority (e.g., Let's Encrypt).

## Known Security Considerations

### Fixed Issues

1. **JWT Secret Hardcoded** (Fixed in this commit)
   - **Issue**: JWT secret was hardcoded in `Servers/Log_in.py`
   - **Impact**: Anyone with repository access could compromise user authentication
   - **Fix**: JWT secret moved to `Keys/jwt_secret.txt` (gitignored)

### Current Security Features

1. **Password Hashing**: User passwords are hashed using bcrypt
2. **Password Encryption in Transit**: Passwords are RSA-encrypted during transmission
3. **JWT Authentication**: Time-limited JWT tokens for session management
4. **HTTPS Support**: SSL/TLS encryption for API communications
5. **Gitignored Secrets**: All sensitive files are excluded from version control

## Security Checklist for Deployment

- [ ] Generate strong, unique secrets for all credentials
- [ ] Use HTTPS in production (not HTTP)
- [ ] Obtain valid SSL certificates from a trusted CA
- [ ] Restrict file permissions on the Keys directory
- [ ] Enable MongoDB authentication and use strong passwords
- [ ] Regularly rotate API keys and secrets
- [ ] Monitor API usage for unusual activity
- [ ] Keep dependencies up to date
- [ ] Review and limit CORS origins in production
- [ ] Enable rate limiting on API endpoints
- [ ] Set up proper logging and monitoring

## Dependencies Security

Regularly update dependencies to patch known vulnerabilities:
```bash
pip install --upgrade -r requirements.txt
npm audit fix
```

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OpenAI API Best Practices](https://platform.openai.com/docs/guides/production-best-practices)
- [MongoDB Security Checklist](https://docs.mongodb.com/manual/administration/security-checklist/)
