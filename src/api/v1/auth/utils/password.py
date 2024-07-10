from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def validate_password(password: str) -> str:

    if not any(char.isdigit() for char in password):
        raise ValueError("Password must contain at least one digit")

    if not any(char.isupper() for char in password):
        raise ValueError("Password must contain at least one uppercase letter")

    if not any(char.islower() for char in password):
        raise ValueError("Password must contain at least one lowercase letter")

    symbols = "!#$%&()*+,-.:;=?[]^_`{|}~"
    if not any(char in symbols for char in password):
        raise ValueError(
            "Password must contain at least one symbol:"
            " '!#$%&()*+,-.:;=?[]^_`{|}~'"
        )

    forbidden_symbols = "@\"'<>\\"
    if any(char in forbidden_symbols for char in password):
        raise ValueError("Password cannot contain this symbols: '@\"'<>\\'")

    return password
