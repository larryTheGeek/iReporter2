import json
from tests.v2.base_test import BaseTest


class UsersTest(BaseTest):

    def test_create_user(self):
        response = self.registration()
        result = json.loads(response.data)
        self.assertEqual(result['Message'], 'User saved successfully')
        self.assertEqual(response.status_code, 201)

    def test_user_login(self):
        self.registration()
        response = self.login()
        result = json.loads(response.data)
        self.assertEqual(result[0]['Message'], 'Welcome issa. You are now logged in!')
        self.assertEqual(response.status_code, 200)

    def test_login_unregistered_user(self):
        response = self.login()
        result = json.loads(response.data)
        self.assertEqual(result['Error'],
                         'No user with that username found!')
        self.assertEqual(response.status_code, 404)

    def test_unmatching_password_during_registration(self):
        response = self.wrongpasswordregistration()
        result = json.loads(response.data)
        self.assertEqual(result['Error'],
                         'Please ensure that both passwords match!')
        self.assertEqual(response.status_code, 401)

    def test_registration_with_invalid_password(self):
        response = self.invalidpasswordregistration()
        result = json.loads(response.data)
        self.assertEqual(
            result['Error'], 'Please fill in a valid password! Password must be 8 characters long.')
        self.assertEqual(response.status_code, 422)

    def test_existingusername(self):
        self.registration()
        response = self.existingusernameregistration()
        result = json.loads(response.data)
        self.assertEqual(result['Error'], 'Username already exists!')
        self.assertEqual(response.status_code, 401)

    def test_existingemail(self):
        self.registration()
        response = self.existingemailregistration()
        result = json.loads(response.data)
        self.assertEqual(result['Error'], 'Email already exists!')
        self.assertEqual(response.status_code, 401)

    def test_getallusers(self):
        self.registration()
        response = self.app.get('/api/v2/auth/signup',
                                headers={'Authorization': 'Bearer {}'.format(self.superadmintoken()),
                                         'content-type': 'application/json'})
        result = json.loads(response.data)
        self.assertEqual(result[0]['Message'], 'Records returned successfully!')
        self.assertEqual(response.status_code, 200)

    def test_firstnamemissing(self):
        response = self.registerwithoutfirstname()
        result = json.loads(response.data)
        self.assertEqual(result['Error'], 'Please enter a first name!')
