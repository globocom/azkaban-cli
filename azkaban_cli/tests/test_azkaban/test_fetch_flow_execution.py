from unittest import TestCase
from unittest.mock import patch, ANY

import responses

import azkaban_cli.azkaban
from azkaban_cli.exceptions import FetchFlowExecutionError, SessionError


class AzkabanFetchFlowExecutionTest(TestCase):
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
    def test_fetch_flow_execution(self):
        """
        Test fetch flow execution method from Azkaban class
        """

        responses.add(
            responses.GET,
            self.host + "/executor",
            json={
                'project': 'test_project',
                'updateTime': 1234,
                'type': None,
                'attempt': 0,
                'execid': self.exec_id,
                'submitTime': 2345,
                'nodes': [
                    {
                        'nestedId': 'my_id',
                        'in': ['my_dependency'],
                        'startTime': 4567,
                        'updateTime': 3456,
                        'id': 'my_id',
                        'endTime': 5678,
                        'type': 'command',
                        'attempt': 0,
                        'status': 'SUCCEEDED'
                    }
                ],
                'nestedId': 'test_id',
                'submitUser': 'test.user',
                'startTime': 2345,
                'id': 'test_id',
                'endTime': 6789,
                'projectId': 111,
                'flowId': 'test_id',
                'flow': 'test_id',
                'status': 'SUCCEEDED'
            },
            status=200
        )

        self.azk.fetch_flow_execution(self.exec_id)

    @patch('azkaban_cli.azkaban.api.fetch_flow_execution_request')
    def test_fetch_flow_execution_request_called(self, mock_fetch_flow_execution_request):
        """
        Test if fetch flow execution method from Azkaban class is calling fetch flow execution
        request with expected arguments
        """

        self.azk.fetch_flow_execution(self.exec_id)

        mock_fetch_flow_execution_request.assert_called_with(
            ANY, self.host, self.session_id, self.exec_id)


    @responses.activate
    def test_execution_cannot_be_found_fetch_flow_execution(self):
        """
        Test if fetch flow execution method from Azkaban class raises FetchFlowExecutionError
        if request returns error caused by execution not be found
        """

        responses.add(
            responses.GET,
            self.host + "/executor",
            json={
                'error': "Cannot find execution '0'"
            },
            status=200
        )

        with self.assertRaises(FetchFlowExecutionError):
            self.azk.fetch_flow_execution(self.exec_id)

    @responses.activate
    def test_error_session_expired_fetch_flow_execution(self):
        """
        Test if fetch flow execution method from Azkaban class raises SessionError if request
        returns error caused by session expired
        """

        responses.add(responses.GET, self.host + "/executor", json={"error": "session"}, status=200)

        with self.assertRaises(SessionError):
            self.azk.fetch_flow_execution(self.exec_id)