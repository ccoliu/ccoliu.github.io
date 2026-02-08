# Keys Directory

This directory should contain sensitive configuration files that are **NOT** committed to git.

## Required Files

### 1. openai_key.txt
Contains OpenAI API keys (one per line):
```
sk-your-api-key-1
sk-your-api-key-2
sk-your-api-key-3
```

### 2. database_uri.txt
Contains MongoDB connection URI:
```
mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

### 3. jwt_secret.txt
Contains JWT secret key for authentication:
```
your-secure-random-jwt-secret-key-here
```

### 4. server_certificate.crt
SSL certificate for HTTPS connections (if using HTTPS)

### 5. server_private_key.key
SSL private key for HTTPS connections (if using HTTPS)

### 6. public_key.pem
RSA public key for password encryption

### 7. private_key.pem
RSA private key for password decryption

## Security Best Practices

1. **Never commit these files to git** - They are in `.gitignore`
2. **Use strong, randomly generated secrets** - Don't use default or simple values
3. **Rotate credentials regularly** - Change API keys and secrets periodically
4. **Restrict access** - Only authorized personnel should have access to these files
5. **Use environment variables in production** - Consider using environment variables or a secrets manager for production deployments

## Generating Secrets

### JWT Secret
Generate a secure random JWT secret:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### RSA Key Pair
Generate RSA keys for password encryption:
```bash
openssl genrsa -out private_key.pem 2048
openssl rsa -in private_key.pem -pubout -out public_key.pem
```

### SSL Certificate (Self-signed for development)
```bash
openssl req -x509 -newkey rsa:4096 -keyout server_private_key.key -out server_certificate.crt -days 365 -nodes
```
