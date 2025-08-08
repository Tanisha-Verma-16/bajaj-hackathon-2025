#!/usr/bin/env python3
"""
Token Generator for RAG Document Query System
Run this script to generate secure tokens for deployment.
"""

import secrets
import string

def generate_bearer_token():
    """Generate a secure bearer token"""
    return secrets.token_hex(32)

def generate_session_secret():
    """Generate a secure session secret"""
    return secrets.token_hex(16)

def generate_random_password(length=16):
    """Generate a random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

if __name__ == "__main__":
    print("🔐 Secure Token Generator for RAG Document Query System")
    print("=" * 60)
    
    bearer_token = generate_bearer_token()
    session_secret = generate_session_secret()
    random_password = generate_random_password()
    
    print(f"""
Environment Variables for Deployment:

API_BEARER_TOKEN={bearer_token}
SESSION_SECRET={session_secret}

Optional - Random Password (for database etc.):
RANDOM_PASSWORD={random_password}

🔗 Copy these values to your .env file or Render environment variables.
🔒 Keep these values secure and never commit them to version control!
""")
    
    print("=" * 60)
    print("✅ Tokens generated successfully!")