#!/bin/bash
# Setup script for Codoctopus - Initializes the Keys directory with example files

echo "========================================"
echo "Codoctopus Security Setup"
echo "========================================"
echo ""

# Check if Keys directory exists
if [ -d "Keys" ]; then
    echo "⚠️  WARNING: Keys directory already exists!"
    echo "This script will not overwrite existing credential files."
    read -p "Do you want to continue and only create missing files? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 1
    fi
else
    echo "Creating Keys directory..."
    mkdir -p Keys
fi

echo ""
echo "Copying example files to Keys directory..."

# Function to copy example file if target doesn't exist
copy_if_not_exists() {
    local example_file=$1
    local target_file=$2
    
    if [ ! -f "$target_file" ]; then
        if [ -f "$example_file" ]; then
            cp "$example_file" "$target_file"
            echo "✓ Created: $target_file"
        else
            echo "⚠️  Warning: Example file not found: $example_file"
        fi
    else
        echo "⊘ Skipped (already exists): $target_file"
    fi
}

# Copy example files
copy_if_not_exists "Keys.example/openai_key.txt.example" "Keys/openai_key.txt"
copy_if_not_exists "Keys.example/database_uri.txt.example" "Keys/database_uri.txt"
copy_if_not_exists "Keys.example/jwt_secret.txt.example" "Keys/jwt_secret.txt"

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "⚠️  IMPORTANT: Next steps:"
echo ""
echo "1. Edit the files in the Keys/ directory:"
echo "   - Keys/openai_key.txt     - Add your OpenAI API keys"
echo "   - Keys/database_uri.txt   - Add your MongoDB connection URI"
echo "   - Keys/jwt_secret.txt     - Generate a secure JWT secret"
echo ""
echo "2. Generate secure secrets:"
echo "   JWT Secret:  python3 -c \"import secrets; print(secrets.token_urlsafe(32))\""
echo ""
echo "3. Generate RSA keys (if needed):"
echo "   cd Keys"
echo "   openssl genrsa -out private_key.pem 2048"
echo "   openssl rsa -in private_key.pem -pubout -out public_key.pem"
echo ""
echo "4. See SECURITY.md for complete setup instructions"
echo ""
echo "⚠️  NEVER commit the Keys/ directory to version control!"
echo ""
