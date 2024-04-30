import pytest
from starlette.testclient import TestClient


def test_read_main(test_client: TestClient):
    login_post_data = {
        "email": "test_email@gmail.com",
        "password": "Test_password22",
    }
    response = test_client.post("/auth/login/", json=login_post_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid user credentials"


INVALID_SIGNUP_DATA = [
    ({"email": "string", "password": "Test_password22"}, 422),
    ({"email": "test_email2@gmail.com", "password": "no_uppercase2"}, 422),
    ({"email": "test_email2@gmail.com", "password": "NO_LOVERCASE2"}, 422),
    ({"email": "test_email2@gmail.com", "password": "No2symbol"}, 422),
    ({"email": "test_email2@gmail.com", "password": "No_digit"}, 422),
]


@pytest.mark.parametrize("login_data, expected_code", INVALID_SIGNUP_DATA)
def test_invalid_signup(
    test_client: TestClient, login_data: dict[str, str], expected_code: int
):
    response = test_client.post("/auth/signup/", json=login_data)
    assert response.status_code == expected_code
