
from utils.auth_db import UserDatabase
import bcrypt

db = UserDatabase("data/users.db")
test_email = "diag@test.com"
test_pass = "password123"
test_name = "Diag User"

print("--- Testing Registration ---")
try:
    user = db.create_user(test_email, test_pass, test_name)
    print(f"User created: {user}")
except ValueError as e:
    print(f"Registration failed (expected if exists): {e}")
except Exception as e:
    print(f"Registration failed (UNEXPECTED): {e}")

print("\n--- Testing Login ---")
try:
    verified = db.verify_user(test_email, test_pass)
    if verified:
        print(f"Login successful: {verified}")
    else:
        print("Login failed: Invalid credentials")
except Exception as e:
    print(f"Login failed (UNEXPECTED): {e}")
????
