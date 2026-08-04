from pwdlib import PasswordHash

password_manager: PasswordHash = PasswordHash.recommended()


def create_password(password: str):
    return password_manager.hash(password)


def check_password(password: str, hash: str):
    return password_manager.verify(password, hash)
