from authentication.security import hash_password, verify_password

password = "admin123"

hashed = hash_password(password)

print("Hash:", hashed)
print("Verify:", verify_password(password, hashed))