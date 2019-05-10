from unittest import TestCase
from unittest.mock import patch, ANY

import responses

import azkaban_cli.azkaban
from azkaban_cli.exceptions import FetchScheduleError, SessionError


class AzkabanFetchScheduleTest(TestCase):
    def setUp(self):
        """
        Creates an Azkaban instance and set a logged session for all fetch schedule tests
        """

        self.azk = azkaban_cli.azkaban.Azkaban()

        self.host = 'http://azkaban-mock.com'
        self.user = 'username'
        self.session_id = 'aebe406b-d5e6-4056-add6-bf41091e42c6'

        self.azk.set_logged_session(self.host, self.user, self.session_id)

        self.project_id = 123
        self.flow = 'FlowTest'

    def tearDown(self):
        pass

    @responses.activate
    def test_fetch_schedule(self):
        """
        Test fetch schedule method from Azkaban class
        """

        responses.add(
            responses.GET,
            self.host + "/schedule",
            json={
                'schedule': {
                    'scheduleId': '456'
                }
            },
            status=200
        )

        self.azk.fetch_schedule(self.project_id, self.flow)

    @patch('azkaban_cli.azkaban.api.fetch_schedule_request')
    def test_fetch_schedule_request_called(self, mock_fetch_schedule_request):
        """
        Test if fetch schedule method from Azkaban class is calling fetch schedule request with expected arguments
        """

        self.azk.fetch_schedule(self.project_id, self.flow)

        mock_fetch_schedule_request.assert_called_with(ANY, self.host, self.session_id, self.project_id, self.flow)

    @responses.activate
    def test_project_doesnt_exist_fetch_flows(self):
        """
        Test if fetch schedule method from Azkaban class raises FetchSchedule if request returns error caused by project doesn't exist
        """

        responses.add(
            responses.GET,
            self.host + "/schedule",
            json={},
            status=200
        )

        with self.assertRaises(FetchScheduleError):
            self.azk.fetch_schedule(self.project_id, self.flow)

    @responses.activate
    def test_flow_doesnt_exist_fetch_flows(self):
        """
        Test if fetch schedule method from Azkaban class raises FetchSchedule if request returns error caused by flow doesn't exist
        """

        responses.add(
            responses.GET,
            self.host + "/schedule",
            json={},
            status=200
        )

        with self.assertRaises(FetchScheduleError):
            self.azk.fetch_schedule(self.project_id, self.flow)

    @responses.activate
    def test_error_session_expired_fetch_schedule(self):
        """
        Test if fetch schedule method from Azkaban class raises SessionError if request returns error caused by session expired
        """

        responses.add(responses.GET, self.host + "/schedule", json={"error": "session"}, status=200)

        with self.assertRaises(SessionError):
            self.azk.fetch_schedule(self.project_id, self.flow)