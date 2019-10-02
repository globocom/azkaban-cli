from unittest import TestCase
from unittest.mock import patch, ANY

import responses

import azkaban_cli.azkaban
from azkaban_cli.exceptions import FetchSLAError, SessionError


class AzkabanFetchSLATest(TestCase):
    def setUp(self):
        """
        Creates an Azkaban instance and set a logged session for all fetch schedule tests
        """

        self.azk = azkaban_cli.azkaban.Azkaban()

        self.host = 'http://azkaban-mock.com'
        self.user = 'username'
        self.session_id = 'aebe406b-d5e6-4056-add6-bf41091e42c6'

        self.azk.set_logged_session(self.host, self.user, self.session_id)

        self.schedule_id = 123

    @responses.activate
    def test_fetch_sla(self):
        """
        Test fetch SLA method from Azkaban class
        """

        responses.add(
            responses.GET,
            self.host + "/schedule",
            json={
                "settings":[{
                    "duration" : "300m",
                    "rule" : "SUCCESS",
                    "id" : "aaa",
                    "actions" : [ "EMAIL" ]
                }],
                "slaEmails": ["a@example.com"],
                "allJobNames" : [ "aaa"]
            },
            status=200
        )

        self.azk.fetch_sla(self.schedule_id)

    @patch('azkaban_cli.azkaban.api.fetch_sla_request')
    def test_fetch_sla_request_called(self, mock_fetch_sla_request):
        """
        Test if fetch SLA method from Azkaban class is calling fetch SLA request with expected arguments
        """

        self.azk.fetch_sla(self.schedule_id)

        mock_fetch_sla_request.assert_called_with(ANY, self.host, self.session_id, self.schedule_id)

    @responses.activate
    def test_schedule_doesnt_exist_fetch_sla(self):
        """
        Test if fetch SLA method from Azkaban class raises FetchSLA if request returns error caused by schedule doesn't exist
        """

        responses.add(
            responses.GET,
            self.host + "/schedule",
            json={},
            status=200
        )

        with self.assertRaises(FetchSLAError):
            self.azk.fetch_sla(self.session_id)

    @responses.activate
    def test_error_session_expired_fetch_sla(self):
        """
        Test if fetch SLA method from Azkaban class raises SessionError if request returns error caused by session expired
        """

        responses.add(responses.GET, self.host + "/schedule", json={"error": "session"}, status=200)

        with self.assertRaises(SessionError):
            self.azk.fetch_sla(self.session_id)
