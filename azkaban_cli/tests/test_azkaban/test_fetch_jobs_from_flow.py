from unittest import TestCase
from unittest.mock import patch, ANY

import responses

import azkaban_cli.azkaban
from azkaban_cli.exceptions import FetchJobsFromFlowError, SessionError


class AzkabanFetchJobsFromFlowTest(TestCase):
    def setUp(self):
        """
        Creates an Azkaban instance and set a logged session for all fetch jobs from a flow tests
        """

        self.azk = azkaban_cli.azkaban.Azkaban()

        self.host = 'http://azkaban-mock.com'
        self.user = 'username'
        self.session_id = 'aebe406b-d5e6-4056-add6-bf41091e42c6'

        self.azk.set_logged_session(self.host, self.user, self.session_id)

        self.project = 'ProjectTest'
        self.flow = 'testFlowName'

    @responses.activate
    def test_fetch_jobs_from_flow(self):
        """
        Test fetch jobs of a flow method from Azkaban class
        """

        responses.add(
            responses.GET,
            self.host + "/manager",
            json={
                'project': self.project,
                'projectId': 123,
                'flow': self.flow,
                'nodes': [
                    {
                        'in': ['job_1', 'job_2'],
                        'id': '123',
                        'type': 'python'
                    }
                ]
            },
            status=200
        )

        self.azk.fetch_jobs_from_flow(self.project, self.flow)

    @patch('azkaban_cli.azkaban.api.fetch_jobs_from_flow_request')
    def test_fetch_flows_request_called(self, mock_fetch_jobs_from_flow_request):
        """
        Test if fetch jobs from flow method from Azkaban class is calling fetch jobs from flow
        request with expected arguments
        """

        self.azk.fetch_jobs_from_flow(self.project, self.flow)

        mock_fetch_jobs_from_flow_request.assert_called_with(
            ANY, self.host, self.session_id, self.project, self.flow)

    @responses.activate
    def test_flow_doesnt_exist_fetch_jobs_from_flow(self):
        """
        Test if fetch fetch jobs from flow method from Azkaban class raises FetchJobsFromFlowError
        if request returns error caused by flow doesn't exist
        """

        responses.add(
            responses.GET,
            self.host + "/manager",
            json={
                'error': "Flow doesn't exist."
            },
            status=200
        )

        with self.assertRaises(FetchJobsFromFlowError):
            self.azk.fetch_jobs_from_flow(self.project, self.flow)

    @responses.activate
    def test_permission_error_fetch_jobs_from_flow(self):
        """
        Test if fetch jobs from flow method from Azkaban class raises FetchJobsFromFlowError
        if request returns error caused by permission error
        """

        responses.add(
            responses.GET,
            self.host + "/manager",
            json={
                'project': 'ProjectTest',
                'error': "Permission denied. Need READ access.",
                'projectId': 123
            },
            status=200
        )

        with self.assertRaises(FetchJobsFromFlowError):
            self.azk.fetch_jobs_from_flow(self.project, self.flow)

    @responses.activate
    def test_error_session_expired_fetch_jobs_from_flow(self):
        """
        Test if fetch jobs from flow method from Azkaban class raises SessionError if request
        returns error caused by session expired
        """

        responses.add(responses.GET, self.host + "/manager", json={"error": "session"}, status=200)

        with self.assertRaises(SessionError):
            self.azk.fetch_jobs_from_flow(self.project, self.flow)
