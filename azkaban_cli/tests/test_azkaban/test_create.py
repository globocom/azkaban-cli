import os
from unittest import TestCase
from unittest.mock import patch, ANY

import responses

import azkaban_cli.azkaban
from azkaban_cli.exceptions import SessionError, CreateError, NotLoggedOnError


class AzkabanCreateTest(TestCase):

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
        self.description = 'DescriptionTest'

    def tearDown(self):
        pass

    @responses.activate
    def test_create(self):
        """
        Test execute method from Azkaban class
        """

        responses.add(
            responses.POST,
            self.host + "/manager",
            json={"path": "manager?project=ProjectTest", "action": "redirect", "status": "success"},
            status=200
        )

        self.azk.create(self.project, self.description)

    @patch('azkaban_cli.azkaban.api.create_request')
    def test_create_request_called(self, mock_create_request):
        """
        Test if create method from Azkaban class is calling create request with expected arguments
        """

        self.azk.create(self.project, self.description)

        mock_create_request.assert_called_with(ANY, self.host, self.session_id, self.project, self.description)

    @responses.activate
    def test_error_session_expired_create(self):
        """
        Test if create method from Azkaban class raises SessionError if request returns error caused by session expired
        """

        fixture_path = os.path.join(os.path.dirname(__file__), os.pardir, "fixtures", "session_expired.html")
        with open(fixture_path) as f:
            responses.add(responses.POST, self.host + "/manager", body=f.read(), status=200)

        with self.assertRaises(SessionError):
            self.azk.create(self.project, self.description)

    @responses.activate
    def test_project_exists_create(self):
        """
        Test if create method from Azkaban class raises CreateError if request returns error caused by project already exists
        """

        responses.add(
            responses.POST,
            self.host + "/manager",
            json={'status': 'error', 'message': "Project already exists."},
            status=200
        )

        with self.assertRaises(CreateError):
            self.azk.create(self.project, self.description)

    @patch('azkaban_cli.azkaban.api.create_request')
    def test_error_not_logged_create(self, mock_create_request):
        """
        Test if create method from Azkaban class raises NotLoggedOnError and doesn't make the request if there is no logged session
        """

        self.azk.logout()

        with self.assertRaises(NotLoggedOnError):
            self.azk.create('project', 'description')

        mock_create_request.assert_not_called()

    @responses.activate
    def test_invalid_project_create(self):
        """
        Test if create method from Azkaban class treats correctly when request returns error caused by  invalid project.
        """

        responses.add(
            responses.POST,
            self.host + "/manager",
            json={
                'message': "Project names must start with a letter, followed by any number of letters, digits, '-' or '_'.",
                'status': "error"
            },
            status=200
        )

        with self.assertRaises(CreateError):
            self.azk.create('123', 'description')

    @responses.activate
    def test_empty_project_create(self):
        """
        Test if create method from Azkaban class treats correctly when request returns error caused by  empty project.
        """

        responses.add(
            responses.POST,
            self.host + "/manager",
            json={'message': "Project name cannot be empty.", 'status':"error"},
            status=200
        )

        with self.assertRaises(CreateError):
            self.azk.create('', 'description')

    @responses.activate
    def test_empty_description_create(self):
        """
        Test if create method from Azkaban class treats correctly when request returns error caused by  empty description.
        """

        responses.add(
            responses.POST,
            self.host + "/manager",
            json={'message': "Description cannot be empty.", 'status':"error"},
            status=200
        )

        with self.assertRaises(CreateError):
            self.azk.create('Project', '')