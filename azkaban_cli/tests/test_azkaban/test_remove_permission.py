from unittest import TestCase
from unittest.mock import patch, ANY

import responses

import azkaban_cli.azkaban
from azkaban_cli.exceptions import RemovePermissionError, SessionError

class AzkabanRemovePermissionTest(TestCase):
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
        self.group   = 'GroupTest'

    @responses.activate
    def test_remove_permission(self):
        """
        Test remove_permission method from Azkaban class
        """

        responses.add(
            responses.GET,
            self.host + "/manager",
            status=200
        )

        self.azk.remove_permission(self.project, self.group)

    @patch('azkaban_cli.azkaban.api.remove_permission_request')
    def test_remove_permission_request_called(self, mock_remove_permission_request):
        """
        Test if remove_permission method from Azkaban class is calling remove_permission request with expected arguments
        """

        self.azk.remove_permission(self.project, self.group)

        mock_remove_permission_request.assert_called_with(ANY, self.host, self.session_id, self.project, self.group)


    @responses.activate
    def test_invalid_group_remove_permission(self):
        """
        Test if remove_permission method from Azkaban class raises RemovePermissionError if request returns error caused by group not be found
        """

        responses.add(
            responses.GET,
            self.host + "/manager",
            json={
              'project' : 'teste-permission-api-20190806',
              'error' : 'Group is invalid.',
              'projectId' : 107
            },
            status=200
        )

        with self.assertRaises(RemovePermissionError):
            self.azk.remove_permission(self.project, self.group)

    @responses.activate
    def test_if_group_dont_exist_remove_permission(self):
        """
        Test if remove_permission method from Azkaban class raises RemovePermissionError if request returns error caused by group already have permission
        """

        responses.add(
            responses.GET,
            self.host + "/manager",
            json={
              "project" : "teste-permission-api-20190806",
              "error" : "Group permission don't exists.",
              "projectId" : 107
            },
            status=200
        )

        with self.assertRaises(RemovePermissionError):
            self.azk.remove_permission(self.project, self.group)

    @responses.activate
    def test_error_session_expired_execute(self):
        """
        Test if execute method from Azkaban class raises SessionError if request returns error caused by session expired
        """

        responses.add(responses.GET, self.host + "/manager", json={"error": "session"}, status=200)

        with self.assertRaises(SessionError):
            self.azk.remove_permission(self.project, self.group)
