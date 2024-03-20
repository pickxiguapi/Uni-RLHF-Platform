import pytest

@pytest.mark.usefixtures("testapp")
class TestLogin:
    def test_successful_login(self, testapp):
        response = testapp.post('/login', json={
            'username': 'validuser',
            'password': 'validpassword'
        })

        assert response.status_code == 200
        assert 'login success' in response.get_data(as_text=True)

    def test_failed_login(self, testapp):
        response = testapp.post('/login', json={
            'username': 'invaliduser',
            'password': 'invalidpassword'
        })

        assert response.status_code == 200
        assert 'Invalid username or password' in response.get_data(as_text=True)
