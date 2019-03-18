from unittest import TestCase
from unittest.mock import patch, ANY

import requests
import responses

import azkaban_cli.azkaban
from azkaban_cli.exceptions import LoginError


class AzkabanLoginTest(TestCase):
    def setUp(self):
        """
        Creates an Azkaban instance for all login tests
        """

        self.azk = azkaban_cli.azkaban.Azkaban()

    def tearDown(self):
        pass

    @patch('azkaban_cli.azkaban.api.login_request')
    def test_validate_login_request_parameters(self, mock_login_request):
        """
        Test if login method from Azkaban class is calling login request with valid parameters
        """

        host       = 'https://testhost:testport/'
        valid_host = 'https://testhost:testport'
        user       = 'user'
        password   = 'password'

        self.azk.login(host, user, password)

        mock_login_request.assert_called_with(ANY, valid_host, user, password)

    @responses.activate
    def test_login(self):
        """
        Test if login method from Azkaban class creates a logged session as expected
        """

        host = "http://azkaban-mock.com"
        user = 'user'
        session_id = 'aebe406b-d5e6-4056-add6-bf41091e42c6'
        responses.add(responses.POST, host, json={'session.id': session_id, 'status': 'success'}, status=200)

        self.azk.login(host, user, 'password')

        logged_session = self.azk.get_logged_session()
        expected = {'host': host, 'user': user, 'session_id': session_id}

        self.assertEqual(logged_session, expected)

    @responses.activate
    def test_wrong_host_login(self):
        """
        Test if login method from Azkaban class treats correctly ConnectionError, usually raised when host is wrong.

        Expected to not save logged session and method to raise requests.exceptions.ConnectionError
        """

        host = "http://azkaban-mock.com"
        responses.add(responses.POST, host, body=requests.exceptions.ConnectionError())

        with self.assertRaises(requests.exceptions.ConnectionError):
            self.azk.login(host, 'user', 'password')

        logged_session = self.azk.get_logged_session()
        expected = {'host': None, 'user': None, 'session_id': None}

        self.assertEqual(logged_session, expected)

    @responses.activate
    def test_wrong_user_login(self):
        """
        Test if login method from Azkaban class treats correctly when request returns error caused by wrong user.

        Expected to not save logged session and method to raise LoginError
        """

        host = 'http://azkaban-mock.com'
        responses.add(responses.POST, host, json={'error': 'Incorrect Login.'}, status=200)

        with self.assertRaises(LoginError):
            self.azk.login(host, 'wrong_user', 'password')

        logged_session = self.azk.get_logged_session()
        expected = {'host': None, 'user': None, 'session_id': None}

        self.assertEqual(logged_session, expected)

    @responses.activate
    def test_wrong_password_login(self):
        """
        Test if login method from Azkaban class treats correctly when request returns error caused by wrong password.

        Expected to not save logged session and method to raise LoginError
        """

        host = 'http://azkaban-mock.com'
        responses.add(responses.POST, host, json={'error': 'Incorrect Login.'}, status=200)

        with self.assertRaises(LoginError):
            self.azk.login(host, 'user', 'wrong_password')

        logged_session = self.azk.get_logged_session()
        expected = {'host': None, 'user': None, 'session_id': None}

        self.assertEqual(logged_session, expected)