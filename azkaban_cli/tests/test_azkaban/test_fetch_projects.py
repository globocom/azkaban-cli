from unittest import TestCase
from unittest.mock import patch, ANY
import os

import responses

import azkaban_cli.azkaban
from azkaban_cli.exceptions import SessionError


class AzkabanFetchProjectsTest(TestCase):
    def setUp(self):
        """
        Creates an Azkaban instance and set a logged session for all fetch flows tests
        """

        self.azk = azkaban_cli.azkaban.Azkaban()

        self.host = 'http://azkaban-mock.com'
        self.user = 'username'
        self.session_id = 'aebe406b-d5e6-4056-add6-bf41091e42c6'

        self.azk.set_logged_session(self.host, self.user, self.session_id)

    def tearDown(self):
        pass

    @responses.activate
    def test_fetch_projects(self):
        """
        Test fetch projects method from Azkaban class
        """

        responses.add(
            responses.GET,
            self.host + "/index",
            status=200
        )

        self.azk.fetch_projects()

    @patch('azkaban_cli.azkaban.api.fetch_projects_request')
    def test_fetch_projects_request_called(self, mock_fetch_projects_request):
        """
        Test if fetch projects method from Azkaban class is calling fetch projects request with expected arguments
        """

        self.azk.fetch_projects()

        mock_fetch_projects_request.assert_called_with(ANY, self.host, self.session_id)

    @responses.activate
    def test_error_session_expired_fetch_projects(self):
        """
        Test if fetch projects method from Azkaban class raises SessionError if request returns error caused by session expired
        """

        fixture_path = os.path.join(os.path.dirname(__file__), os.pardir, "fixtures", "session_expired.html")
        with open(fixture_path) as f:
            responses.add(responses.GET, self.host + "/index", body=f.read(), status=200)

        with self.assertRaises(SessionError):
            self.azk.fetch_projects()
