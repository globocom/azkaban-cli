from unittest import TestCase
from unittest.mock import patch, ANY

import responses

import azkaban_cli.azkaban
from azkaban_cli.exceptions import FetchFlowsError, SessionError


class AzkabanFetchFlowsTest(TestCase):
    def setUp(self):
        """
        Creates an Azkaban instance and set a logged session for all fetch flows tests
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
    def test_fetch_flows(self):
        """
        Test fetch flows method from Azkaban class
        """

        responses.add(
            responses.GET,
            self.host + "/manager",
            json={
                'project': 'ProjectTest',
                'projectId': 123,
                'flows': [{'FlowId': 'FlowTest'}]
            },
            status=200
        )

        self.azk.fetch_flows(self.project)

    @patch('azkaban_cli.azkaban.api.fetch_flows_request')
    def test_fetch_flows_request_called(self, mock_fetch_flows_request):
        """
        Test if fetch flows method from Azkaban class is calling fetch flows request with expected arguments
        """

        self.azk.fetch_flows(self.project)

        mock_fetch_flows_request.assert_called_with(ANY, self.host, self.session_id, self.project)

    @responses.activate
    def test_project_doesnt_exist_fetch_flows(self):
        """
        Test if fetch flows method from Azkaban class raises FetchFlowsError if request returns error caused by project doesn't exist
        """

        responses.add(
            responses.GET,
            self.host + "/manager",
            json={
                'project': 'ProjectTest',
                'error': "Project ProjectTest doesn't exist."
            },
            status=200
        )

        with self.assertRaises(FetchFlowsError):
            self.azk.fetch_flows(self.project)

    @responses.activate
    def test_permission_error_fetch_flows(self):
        """
        Test if fetch flows method from Azkaban class raises FetchFlowsError if request returns error caused by permission error
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

        with self.assertRaises(FetchFlowsError):
            self.azk.fetch_flows(self.project)

    @responses.activate
    def test_error_session_expired_fetch_flows(self):
        """
        Test if fetch flows method from Azkaban class raises SessionError if request returns error caused by session expired
        """

        responses.add(responses.GET, self.host + "/manager", json={"error": "session"}, status=200)

        with self.assertRaises(SessionError):
            self.azk.fetch_flows(self.project)