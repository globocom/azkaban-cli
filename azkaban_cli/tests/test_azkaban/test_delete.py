import os
from unittest import TestCase
from unittest.mock import patch, ANY

import responses

import azkaban_cli.azkaban
from azkaban_cli.exceptions import SessionError, NotLoggedOnError


class AzkabanDeleteTest(TestCase):

    def setUp(self):
        """
        Creates an Azkaban instance and set a logged session for all upload tests
        """

        self.azk = azkaban_cli.azkaban.Azkaban()

        self.host = 'http://azkaban-mock.com'
        self.user = 'username'
        self.session_id = 'aebe406b-d5e6-4056-add6-bf41091e42c6'

        self.azk.set_logged_session(self.host, self.user, self.session_id)

        self.project = 'ProjectTest'

    def tearDown(self):
        pass

    @responses.activate
    def test_delete(self):
        """
        Test execute method from Azkaban class
        """

        responses.add(
            responses.GET,
            self.host + "/manager",
            json={},
            status=200
        )

        self.azk.delete(self.project)

    @patch('azkaban_cli.azkaban.api.delete_request')
    def test_delete_request_called(self, mock_delete_request):
        """
        Test if delete method from Azkaban class is calling delete request with expected arguments
        """

        self.azk.delete(self.project)

        mock_delete_request.assert_called_with(ANY, self.host, self.session_id, self.project)

    @patch('azkaban_cli.azkaban.api.delete_request')
    def test_error_not_logged_delete(self, mock_delete_request):
        """
        Test if delete method from Azkaban class raises NotLoggedOnError and doesn't make the request if there is no logged session
        """

        self.azk.logout()

        with self.assertRaises(NotLoggedOnError):
            self.azk.delete('project')

        mock_delete_request.assert_not_called()
