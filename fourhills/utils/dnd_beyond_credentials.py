import keyring
from typing import Optional


def save_password(username: str, password: str):
    keyring.set_password("fourhills", username, password)


def get_password(username: str) -> Optional[str]:
    return keyring.get_password("fourhills", username)


def clear_password(username: str):
    keyring.delete_password("fourhills", username)
