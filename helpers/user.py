import bcrypt
from typing import Dict, Optional

# Function to hash a plain text password
def hash_password(plain_password: str) -> str:
    """Hash a plain text password using bcrypt"""
    # Generate salt
    salt = bcrypt.gensalt()
    # Generate hashed password
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    # Return as decoded string to store in DB
    return hashed.decode('utf-8')

# Function to verify password during login
def check_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password during login by comparing with stored hash"""
    # Compare entered password with stored hashed password
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))