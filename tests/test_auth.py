from starlette.testclient import TestClient


def test_read_main(test_client: TestClient):
    login_post_data = {
        "email": "test_email@gmail.com",
        "password": "Test_password22"
    }
    response = test_client.post("/auth/login/", json=login_post_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid user credentials"
