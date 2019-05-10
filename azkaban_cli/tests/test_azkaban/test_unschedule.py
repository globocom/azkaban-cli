import os
from unittest import TestCase
from unittest.mock import patch, ANY

import responses

import azkaban_cli.azkaban
from azkaban_cli.exceptions import UnscheduleError, SessionError


class AzkabanUnscheduleTest(TestCase):
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
        self.flow = 'FlowTest'
        self.project_id = 123
        self.schedule_id = '456'

    def tearDown(self):
        pass

    @responses.activate
    def test_unschedule(self):
        """
        Test unschedule method from Azkaban class
        """

        responses.add(
            responses.POST,
            self.host + "/schedule",
            json={
                'message': 'flow FlowTest removed from Schedules.',
                'status': 'success'
            },
            status=200
        )

        self.azk.unschedule(self.schedule_id)

    @responses.activate
    @patch('azkaban_cli.azkaban.api.unschedule_request')
    def test_unschedule_request_called(self, mock_unschedule_request):
        """
        Test if unschedule method from Azkaban class is calling unschedule, fetch_schedule, fetch_flows requests
        with expected arguments
        """

        self.azk.unschedule(self.schedule_id)

        mock_unschedule_request.assert_called_with(ANY, self.host, self.session_id, self.schedule_id)

    @responses.activate
    def test_error_project_doesnt_exist_unschedule(self):
        """
        Test if unschedule method from Azkaban class raises UnscheduleError if request returns error caused by schedule ID doesn't exist
        """

        responses.add(
            responses.POST,
            self.host + "/schedule",
            json={
                'message': 'Schedule with ID FlowTest does not exist',
                'status': 'error'
            },
            status=400
        )

        with self.assertRaises(UnscheduleError):
            self.azk.unschedule(self.schedule_id)

    @responses.activate
    def test_error_session_expired_unschedule(self):
        """
        Test if unschedule method from Azkaban class raises SessionError if request returns html from login because of expired session
        """

        fixture_path = os.path.join(os.path.dirname(__file__), os.pardir, "fixtures", "session_expired.html")
        with open(fixture_path) as f:
            responses.add(responses.POST, self.host + "/schedule", body=f.read(), status=200)

        with self.assertRaises(SessionError):
            self.azk.unschedule(self.schedule_id)
