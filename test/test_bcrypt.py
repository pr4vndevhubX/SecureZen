import bcrypt

password = "password123"
# Hash it
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
print(f"Hashed type: {type(hashed)}")
print(f"Hashed value: {hashed}")

# Verify it
match = bcrypt.checkpw(password.encode('utf-8'), hashed)
print(f"Match: {match}")

# Test if it works with string representation if it was stored that way
hashed_str = hashed.decode('utf-8')
print(f"Match with string hash: {bcrypt.checkpw(password.encode('utf-8'), hashed_str.encode('utf-8'))}")
