import uuid


def make_user_data(role: str = "user") -> dict[str, str]:
    return {
        "name": f"{role} Autotest",
        "email": f"{role}-{uuid.uuid4().hex}@example.com",
        "password": "12345678",
    }
