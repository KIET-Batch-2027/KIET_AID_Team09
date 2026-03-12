import requests


class FirebaseAuthService:
    """Optional Firebase Authentication sync via REST API."""

    def __init__(self, api_key=''):
        self.api_key = api_key

    @property
    def enabled(self):
        return bool(self.api_key)

    def signup(self, email, password):
        if not self.enabled:
            return True, None

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.api_key}"
        payload = {'email': email, 'password': password, 'returnSecureToken': True}
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.ok:
                return True, response.json().get('localId')
            return False, response.json().get('error', {}).get('message', 'Firebase signup failed')
        except requests.RequestException:
            return False, 'Firebase service unavailable'