from unittest import TestCase
from unittest.mock import patch, ANY

import responses

import azkaban_cli.azkaban
from azkaban_cli.exceptions import ExecuteError, SessionError


class AzkabanExecuteTest(TestCase):
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
        self.flow    = 'FlowTest'

    def tearDown(self):
        pass

    @responses.activate
    def test_execute(self):
        """
        Test execute method from Azkaban class
        """

        responses.add(
            responses.GET,
            self.host + "/executor",
            json={
                'project': 'ProjectTest',
                'message': 'Execution submitted successfully with exec id 6867',
                'flow': 'FlowTest',
                'execid': '6867'
            },
            status=200
        )

        self.azk.execute(self.project, self.flow)

    @patch('azkaban_cli.azkaban.api.execute_request')
    def test_execute_request_called(self, mock_execute_request):
        """
        Test if execute method from Azkaban class is calling execute request with expected arguments
        """

        self.azk.execute(self.project, self.flow)

        mock_execute_request.assert_called_with(ANY, self.host, self.session_id, self.project, self.flow)


    @responses.activate
    def test_flow_cannot_be_found_execute(self):
        """
        Test if execute method from Azkaban class raises ExecuteError if request returns error caused by flow not be found
        """

        responses.add(
            responses.GET,
            self.host + "/executor",
            json={
                'project': 'ProjectTest',
                'error': "Flow 'FlowTest' cannot be found in project ProjectTest",
                'flow': 'FlowTest'
            },
            status=200
        )

        with self.assertRaises(ExecuteError):
            self.azk.execute(self.project, self.flow)

    @responses.activate
    def test_project_doesnt_exist_execute(self):
        """
        Test if execute method from Azkaban class raises ExecuteError if request returns error caused by project doesn't exist
        """

        responses.add(
            responses.GET,
            self.host + "/executor",
            json={
                'project': 'ProjectTest',
                'error': "Project 'ProjectTest' doesn't exist."
            },
            status=200
        )

        with self.assertRaises(ExecuteError):
            self.azk.execute(self.project, self.flow)

    @responses.activate
    def test_error_session_expired_execute(self):
        """
        Test if execute method from Azkaban class raises SessionError if request returns error caused by session expired
        """

        responses.add(responses.GET, self.host + "/executor", json={"error": "session"}, status=200)

        with self.assertRaises(SessionError):
            self.azk.execute(self.project, self.flow)