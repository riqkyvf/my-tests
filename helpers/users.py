import uuid


def make_user_data(role: str = "user") -> dict[str, str]:
    unique_id = uuid.uuid4().hex
    return {
        "name": f"{role} Autotest {unique_id[:8]}",
        "email": f"{role}-{unique_id}@example.com",
        "password": "12345678",
    }
