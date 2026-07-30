import sqlite3
from authentication.security import hash_password

conn = sqlite3.connect("pharmacy.db")
cursor = conn.cursor()

cursor.execute("SELECT id, password FROM users")
users = cursor.fetchall()

for user_id, password in users:
    if password:
        password_hash = hash_password(password)

        cursor.execute(
            """
            UPDATE users
            SET password_hash=?
            WHERE id=?
            """,
            (password_hash, user_id)
        )

conn.commit()
conn.close()

print("✅ Users migrated successfully.")