# Welcome to Secure Code Game Season-1/Level-5!
# This is the last level of our first season, good luck!
import binascii
import secrets
import hashlib
import os
import bcrypt

class Random_generator:
    # generates a random token using secrets module for cryptographically strong randomness
    def generate_token(self, length=8, alphabet=(
    '0123456789'
    'abcdefghijklmnopqrstuvwxyz'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    )):
        # SECURITY FIX: replaced random.choice with secrets.choice
        return ''.join(secrets.choice(alphabet) for i in range(length))

    # generates salt using bcrypt's built-in gensalt()
    def generate_salt(self, rounds=12):
        # SECURITY FIX: replaced manual salt generation with bcrypt.gensalt()
        return bcrypt.gensalt(rounds)

class SHA256_hasher:
    # produces the password hash by combining password + salt before hashing
    def password_hash(self, password, salt):
        password = binascii.hexlify(hashlib.sha256(password.encode()).digest())
        password_hash = bcrypt.hashpw(password, salt)
        return password_hash.decode('ascii')

    # verifies that the hashed password reverses to the plain text version on verification
    def password_verification(self, password, password_hash):
        password = binascii.hexlify(hashlib.sha256(password.encode()).digest())
        password_hash = password_hash.encode('ascii')
        return bcrypt.checkpw(password, password_hash)

class MD5_hasher:
    # SECURITY FIX: MD5 is cryptographically broken for password hashing.
    # Replaced MD5 with SHA256 internally while keeping the same interface
    # for backwards compatibility. Use SHA256_hasher directly for new code.
    def password_hash(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def password_verification(self, password, password_hash):
        password = self.password_hash(password)
        return secrets.compare_digest(password.encode(), password_hash.encode())

# a collection of sensitive secrets necessary for the software to operate
PRIVATE_KEY = os.environ.get('PRIVATE_KEY')
PUBLIC_KEY = os.environ.get('PUBLIC_KEY')
# SECURITY FIX: SECRET_KEY must never be hardcoded in source code
SECRET_KEY = os.environ.get('SECRET_KEY')
# SECURITY FIX: switched from MD5_hasher (cryptographically broken) to SHA256_hasher
PASSWORD_HASHER = 'SHA256_hasher'

# Contribute new levels to the game in 3 simple steps!
# Read our Contribution Guideline at github.com/skills/secure-code-game/blob/main/CONTRIBUTING.md
