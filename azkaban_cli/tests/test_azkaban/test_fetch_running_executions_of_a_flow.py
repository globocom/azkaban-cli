from unittest import TestCase
from unittest.mock import patch, ANY
import os

import responses

import azkaban_cli.azkaban
from azkaban_cli.exceptions import SessionError


class AzkabanFetchRunningExecutionsOfAFlowTest(TestCase):
    def setUp(self):
        """
        Creates an Azkaban instance and set a logged session for all fetch running executions of a flow tests.
        """

        self.azk = azkaban_cli.azkaban.Azkaban()

        self.host = 'http://azkaban-mock.com'
        self.user = 'username'
        self.session_id = 'aebe406b-d5e6-4056-add6-bf41091e42c6'

        self.azk.set_logged_session(self.host, self.user, self.session_id)

        self.project = 'ProjectTest'
        self.flow = 'testFlowName'

    @responses.activate
    def test_fetch_running_executions_of_a_flow(self):
        """
        Test fetch running executions of a flow method from Azkaban class
        """

        responses.add(
            responses.GET,
            self.host + "/executor",
            json={
                'project': self.project,
                'flow': self.flow
            },
            status=200
        )

        self.azk.fetch_running_executions_of_a_flow(self.project, self.flow)

    @patch('azkaban_cli.azkaban.api.fetch_running_executions_of_a_flow_request')
    def test_fetch_running_executions_request_called(self, mock_fetch_running_executions_of_a_flow_request):
        """
        Test if fetch running executions of a flow method from Azkaban class is calling fetch it's request with expected arguments
        """

        self.azk.fetch_running_executions_of_a_flow(self.project, self.flow)

        mock_fetch_running_executions_of_a_flow_request.assert_called_with(ANY, self.host, self.session_id, self.project, self.flow)

    @responses.activate
    def test_error_session_expired_fetch_executions_of_a_flow(self):
        """
        Test if fetch runnning executions of a flow method from Azkaban class raises SessionError if request returns error caused by session expired
        """

        fixture_path = os.path.join(os.path.dirname(__file__), os.pardir, "fixtures", "session_expired.html")
        with open(fixture_path) as f:
            responses.add(responses.GET, self.host + "/executor", json={"error": "session"}, status=200)
        with self.assertRaises(SessionError):
            self.azk.fetch_running_executions_of_a_flow(self.project, self.flow)
