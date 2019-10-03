from unittest import TestCase
from unittest.mock import patch, ANY

import responses

import azkaban_cli.azkaban
from azkaban_cli.exceptions import ChangePermissionError, SessionError

class AzkabanChangePermissionTest(TestCase):
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
        self.permission_options = {'admin': False, 'read': True, 'write': True, 'execute': False, 'schedule': False}

    @responses.activate
    def test_change_permission(self):
        """
        Test change_permission method from Azkaban class
        """

        responses.add(
            responses.GET,
            self.host + "/manager",
            status=200
        )

        self.azk.change_permission(self.project, self.group, self.permission_options)

    @patch('azkaban_cli.azkaban.api.change_permission_request')
    def test_change_permission_request_called(self, mock_change_permission_request):
        """
        Test if change_permission method from Azkaban class is calling change_permission request with expected arguments
        """

        self.azk.change_permission(self.project, self.group, self.permission_options)

        mock_change_permission_request.assert_called_with(ANY, self.host, self.session_id, self.project, self.group, self.permission_options)


    @responses.activate
    def test_invalid_group_change_permission(self):
        """
        Test if change_permission method from Azkaban class raises ChangePermissionError if request returns error caused by group not be found
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

        with self.assertRaises(ChangePermissionError):
            self.azk.change_permission(self.project, self.group, self.permission_options)

    @responses.activate
    def test_if_group_already_exist_change_permission(self):
        """
        Test if change_permission method from Azkaban class raises ChangePermissionError if request returns error caused by group already have permission
        """

        responses.add(
            responses.GET,
            self.host + "/manager",
            json={
              "project" : "teste-permission-api-20190806",
              "error" : "Group permission already exists.",
              "projectId" : 107
            },
            status=200
        )

        with self.assertRaises(ChangePermissionError):
            self.azk.change_permission(self.project, self.group, self.permission_options)

    @responses.activate
    def test_error_session_expired_execute(self):
        """
        Test if execute method from Azkaban class raises SessionError if request returns error caused by session expired
        """

        responses.add(responses.GET, self.host + "/manager", json={"error": "session"}, status=200)

        with self.assertRaises(SessionError):
            self.azk.change_permission(self.project, self.group, self.permission_options)
