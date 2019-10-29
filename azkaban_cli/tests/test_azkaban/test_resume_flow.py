from unittest import TestCase
from unittest.mock import patch, ANY

import responses

import azkaban_cli.azkaban
from azkaban_cli.exceptions import ResumeFlowExecutionError, SessionError


class AzkabanResumeFlowsTest(TestCase):
    def setUp(self):
        """
        Creates an Azkaban instance and set a logged session for all upload tests
        """

        self.azk = azkaban_cli.azkaban.Azkaban()

        self.host = 'http://azkaban-mock.com'
        self.user = 'username'
        self.session_id = 'aebe406b-d5e6-4056-add6-bf41091e42c6'

        self.azk.set_logged_session(self.host, self.user, self.session_id)

        self.exec_id = '1234'

    @responses.activate
    def test_resume_flows(self):
        """
        Test resume flows method from Azkaban class
        """

        responses.add(
            responses.GET,
            self.host + "/executor",
            json={},
            status=200
        )

        self.azk.resume_flow_execution(self.exec_id)

    @patch('azkaban_cli.azkaban.api.resume_flow_execution')
    def test_resume_flow_execution_request_called(self, mock_resume_flow_execution_request):
        """
        Test if resume flow execution method from Azkaban class is calling resume flow execution
        request with expected arguments
        """

        self.azk.resume_flow_execution(self.exec_id)

        mock_resume_flow_execution_request.assert_called_with(
            ANY, self.host, self.session_id, self.exec_id)

    @responses.activate
    def test_error_session_expired_resume_flow_execution(self):
        """
        Test if resume flow execution method from Azkaban class raises SessionError if request
        returns error caused by session expired
        """

        responses.add(responses.GET, self.host + "/executor", json={"error": "session"}, status=200)

        with self.assertRaises(SessionError):
            self.azk.resume_flow_execution(self.exec_id)

    @responses.activate
    def test_execution_cannot_be_found_resume_flow_execution(self):
        """
        Test if resume flow execution method from Azkaban class raises ResumeFlowExecutionError
        if request returns error caused by execution not be found
        """

        responses.add(
            responses.GET,
            self.host + "/executor",
            json={
                'error': "Execution 1234 of flow test isn't running."
            },
            status=200
        )

        with self.assertRaises(ResumeFlowExecutionError):
            self.azk.resume_flow_execution(self.exec_id)