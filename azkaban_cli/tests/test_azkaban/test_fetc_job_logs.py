from unittest import TestCase
from unittest.mock import patch, ANY

import responses

import azkaban_cli.azkaban
from azkaban_cli.exceptions import FetchExecutionJobsLogError, SessionError


class AzkabanFetchJobLog(TestCase):
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
        self.jobid = 'test-job-1'
        self.offset = '0' 
        self.length = '10'
        
    def tearDown(self):
        pass

    @responses.activate
    def test_execution_job_log_updates(self):
        """
        Test fetch flow execution updates method from Azkaban class
        """

        responses.add(
            responses.GET,
            self.host + "/executor",
            json={
                "id" : "test",
                "startTime" : 1407778382894,
                "attempt" : 0,
                "status" : "FAILED",
                "updateTime" : 1407778404708,
                "nodes" : [ {
                    "attempt" : 0,
                    "startTime" : 1407778404683,
                    "id" : "test",
                    "updateTime" : 1407778404683,
                    "status" : "CANCELLED",
                    "endTime" : 1407778404683
                }, {
                    "attempt" : 0,
                    "startTime" : 1407778382913,
                    "id" : "test-job-1",
                    "updateTime" : 1407778393850,
                    "status" : "SUCCEEDED",
                    "endTime" : 1407778393845
                }, {
                    "attempt" : 0,
                    "startTime" : 1407778393849,
                    "id" : "test-job-2",
                    "updateTime" : 1407778404679,
                    "status" : "FAILED",
                    "endTime" : 1407778404675
                  }, {
                    "attempt" : 0,
                    "startTime" : 1407778404675,
                    "id" : "test-job-3",
                    "updateTime" : 1407778404675,
                    "status" : "CANCELLED",
                    "endTime" : 1407778404675
                } ],
              "flow" : "test",
              "endTime" : 1407778404705
            },
            status=200
        )

        self.azk.fetch_execution_job_log(self.exec_id, self.jobid, self.offset, self.length)

    @patch('azkaban_cli.azkaban.api.fetch_execution_job_log_request')
    def test_fetch_execution_job_log(self, mock_fetch_execution_job_log_request):
        """
        Test if fetch execution job log method from Azkaban class is calling execution job log
         with expected arguments
        """

        self.azk.fetch_execution_job_log(self.exec_id, self.jobid, self.offset, self.length)

        mock_fetch_execution_job_log_request.assert_called_with(
            ANY, self.host, self.session_id, self.exec_id, self.jobid, self.offset, self.length)

    @responses.activate
    def test_execution_cannot_be_found_fetch_execution_job_log(self):
        """
        Test if fetch execution job log method from Azkaban class raises FetchExecutionJobsLogError
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

        with self.assertRaises(FetchExecutionJobsLogError):
            self.azk.fetch_execution_job_log(self.exec_id, self.jobid, self.offset, self.length)

    @responses.activate
    def test_error_session_expired_fetch_flow_execution_updates(self):
        """
        Test if fetch execution job log method from Azkaban class raises SessionError if request
        returns error caused by session expired
        """

        responses.add(responses.GET, self.host + "/executor", json={"error": "session"}, status=200)

        with self.assertRaises(SessionError):
            self.azk.fetch_execution_job_log(self.exec_id, self.jobid, self.offset, self.length)