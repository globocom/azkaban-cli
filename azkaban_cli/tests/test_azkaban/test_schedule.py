import os
from unittest import TestCase
from unittest.mock import patch, ANY

import responses

import azkaban_cli.azkaban
from azkaban_cli.exceptions import ScheduleError, SessionError


class AzkabanScheduleTest(TestCase):
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
        self.cron    = '0 0 23 ? * *'

    def tearDown(self):
        pass

    @responses.activate
    @patch('azkaban_cli.azkaban.api.schedule_request')
    def test_schedule(self, mock_schedule_request):
        """
        Test schedule method from Azkaban class
        """

        responses.add(
            responses.POST,
            self.host + "/schedule",
            json={
                'message': 'ProjectTest.FlowTest scheduled.',
                'scheduleId': '41',
                'status': 'success'
            },
            status=200
        )

        self.azk.schedule(self.project, self.flow, self.cron)

    @patch('azkaban_cli.azkaban.api.schedule_request')
    def test_schedule_request_called(self, mock_schedule_request):
        """
        Test if schedule method from Azkaban class is calling schedule request with expected arguments
        """

        self.azk.schedule(self.project, self.flow, self.cron)

        mock_schedule_request.assert_called_with(ANY, self.host, self.session_id, self.project, self.flow, self.cron)

    @responses.activate
    def test_error_project_doesnt_exist_schedule(self):
        """
        Test if schedule method from Azkaban class raises ScheduleError if request returns error caused by project doesn't exist
        """

        responses.add(
            responses.POST,
            self.host + "/schedule",
            json={
                'message': 'Project ProjectTest does not exist',
                'status': 'error'
            },
            status=200
        )

        with self.assertRaises(ScheduleError):
            self.azk.schedule(self.project, self.flow, self.cron)

    @responses.activate
    def test_error_flow_cannot_be_found_schedule(self):
        """
        Test if schedule method from Azkaban class raises ScheduleError if request returns error caused by flow not be found
        """
        responses.add(
            responses.POST,
            self.host + "/schedule",
            json={
                'message': 'Flow FlowTest cannot be found in project GustavoTest',
                'status': 'error'
            },
            status=200
        )

        with self.assertRaises(ScheduleError):
            self.azk.schedule(self.project, self.flow, self.cron)

    @responses.activate
    def test_error_cron_cannot_be_parsed_schedule(self):
        """
        Test if schedule method from Azkaban class raises ScheduleError if request returns error caused by wrong cron expression
        """

        responses.add(
            responses.POST,
            self.host + "/schedule",
            json={
                'error': 'This expression <0 23 ? * *> can not be parsed to quartz cron.'
            },
            status=200
        )

        with self.assertRaises(ScheduleError):
            self.azk.schedule(self.project, self.flow, self.cron)

    @responses.activate
    def test_error_session_expired_schedule(self):
        """
        Test if schedule method from Azkaban class raises SessionError if request returns html from login because of expired session
        """

        fixture_path = os.path.join(os.path.dirname(__file__), os.pardir, "fixtures", "session_expired.html")
        with open(fixture_path) as f:
            responses.add(responses.POST, self.host + "/schedule", body=f.read(), status=200)

        with self.assertRaises(SessionError):
            self.azk.schedule(self.project, self.flow, self.cron)