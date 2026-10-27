from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def hash_password_func(password: str) -> str:
    return password_hash.hash(password)