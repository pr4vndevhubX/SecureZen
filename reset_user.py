import sqlite3
import bcrypt

db_path = "data/users.db"
email = "praveenkumar.suresh@kryasolutions.com"
new_password = "password123"

# Hash
hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("UPDATE users SET password_hash = ? WHERE email = ?", (hashed, email))
if c.rowcount > 0:
    print(f"Successfully reset password for {email} to 'password123'")
else:
    print(f"User {email} not found")
conn.commit()
conn.close()
