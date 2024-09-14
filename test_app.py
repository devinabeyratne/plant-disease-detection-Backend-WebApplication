import unittest
from app import flask_app

class TestApp(unittest.TestCase):
    
    def setUp(self):
        flask_app .config['TESTING'] = True
        self.app = flask_app .test_client()

    def test_register_endpoint(self):
        data = {
            'firstName': 'Test4',
            'lastName': 'user',
            'email': 'test4@gmail.com',
            'password': '123',
            "userType": "USER"
        }
        response = self.app.post('/api/register', json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registration successful', response.data)

    def test_login_endpoint(self):

        data = {
            'email': 'tim@gmail.com',
            'password': '123'
        }
        response = self.app.post('/api/login', json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login successful', response.data)

    def test_view_plants_endpoint(self):

        with self.app.session_transaction() as sess:
            sess['user_id'] = 5
        response = self.app.get('/api/view_all_plants')
        self.assertEqual(response.status_code, 200)

    def test_view_disease_endpoint(self):

        with self.app.session_transaction() as sess:
            sess['user_id'] = 5
        response = self.app.get('/api/view_all_plants')
        self.assertEqual(response.status_code, 200)

    def test_get_total_users_endpoint(self):

        with self.app.session_transaction() as sess:
            sess['user_id'] = 3
        response = self.app.get('/api/admin/total_users')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()

