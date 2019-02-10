# -*- coding: utf-8 -*-

from unittest.mock import patch, mock_open, ANY
from unittest import TestCase
from azkaban_cli.exceptions import LoginError, NotLoggedOnError, UploadError, ScheduleError, ExecuteError, SessionError,CreateError
import requests
import responses
import azkaban_cli.azkaban
import os

class AzkabanLoginTest(TestCase):
    def setUp(self):
        """
        Creates an Azkaban instance for all login tests
        """

        self.azk = azkaban_cli.azkaban.Azkaban()

    def tearDown(self):
        pass

    @patch('azkaban_cli.azkaban.api.login_request')
    def test_validate_login_request_parameters(self, mock_login_request):
        """
        Test if login method from Azkaban class is calling login request with valid parameters
        """

        host       = 'https://testhost:testport/'
        valid_host = 'https://testhost:testport'
        user       = 'user'
        password   = 'password'

        self.azk.login(host, user, password)

        mock_login_request.assert_called_with(ANY, valid_host, user, password)

    @responses.activate
    def test_login(self):
        """
        Test if login method from Azkaban class creates a logged session as expected
        """

        host = "http://azkaban-mock.com"
        session_id = 'aebe406b-d5e6-4056-add6-bf41091e42c6'
        responses.add(responses.POST, host, json={'session.id': session_id, 'status': 'success'}, status=200)

        self.azk.login(host, 'user', 'password')

        logged_session = self.azk.get_logged_session()
        expected = {'host': host, 'session_id': session_id}

        self.assertEqual(logged_session, expected)

    @responses.activate
    def test_wrong_host_login(self):
        """
        Test if login method from Azkaban class treats correctly ConnectionError, usually raised when host is wrong.

        Expected to not save logged session and method to raise requests.exceptions.ConnectionError
        """

        host = "http://azkaban-mock.com"
        responses.add(responses.POST, host, body=requests.exceptions.ConnectionError())

        with self.assertRaises(requests.exceptions.ConnectionError):
            self.azk.login(host, 'user', 'password')

        logged_session = self.azk.get_logged_session()
        expected = {'host': None, 'session_id': None}

        self.assertEqual(logged_session, expected)

    @responses.activate
    def test_wrong_user_login(self):
        """
        Test if login method from Azkaban class treats correctly when request returns error caused by wrong user.

        Expected to not save logged session and method to raise LoginError
        """

        host = 'http://azkaban-mock.com'
        responses.add(responses.POST, host, json={'error': 'Incorrect Login.'}, status=200)

        with self.assertRaises(LoginError):
            self.azk.login(host, 'wrong_user', 'password')

        logged_session = self.azk.get_logged_session()
        expected = {'host': None, 'session_id': None}

        self.assertEqual(logged_session, expected)

    @responses.activate
    def test_wrong_password_login(self):
        """
        Test if login method from Azkaban class treats correctly when request returns error caused by wrong password.

        Expected to not save logged session and method to raise LoginError
        """

        host = 'http://azkaban-mock.com'
        responses.add(responses.POST, host, json={'error': 'Incorrect Login.'}, status=200)

        with self.assertRaises(LoginError):
            self.azk.login(host, 'user', 'wrong_password')

        logged_session = self.azk.get_logged_session()
        expected = {'host': None, 'session_id': None}

        self.assertEqual(logged_session, expected)

class AzkabanUploadTest(TestCase):
    def setUp(self):
        """
        Creates an Azkaban instance and set a logged session for all upload tests
        """

        self.azk = azkaban_cli.azkaban.Azkaban()

        self.host = 'http://azkaban-mock.com'
        self.session_id = 'aebe406b-d5e6-4056-add6-bf41091e42c6'

        self.azk.set_logged_session(self.host, self.session_id)

    def tearDown(self):
        pass

#        responses.add(responses.POST, self.host, json={'projectId': '33', 'version': '58'}, status=200)

    @responses.activate
    @patch('azkaban_cli.azkaban.os.remove')
    @patch('azkaban_cli.azkaban.make_archive')
    @patch('builtins.open', new_callable=mock_open)
    def test_upload(self, mock_zip, mock_make_archive, mock_os_remove):
        """
        Test upload method from Azkaban class
        """

        responses.add(responses.POST, self.host + "/manager", json={'projectId': '33', 'version': '58'}, status=200)

        mock_make_archive.return_value = 'zip_path'

        self.azk.upload('path', 'project', 'zip_name')
        self.assertEqual(len(responses.calls), 1)

    @responses.activate
    def test_error_not_logged_upload(self):
        """
        Test if upload method from Azkaban class raises NotLoggedOnError and doesn't make the request if there is no logged session
        """

        responses.add(responses.POST, self.host + "/manager")

        self.azk.logout()

        with self.assertRaises(NotLoggedOnError):
            self.azk.upload('path', 'project', 'zip_name')

        self.assertEqual(len(responses.calls), 0)

    @responses.activate
    @patch('azkaban_cli.azkaban.os.remove')
    @patch('azkaban_cli.azkaban.make_archive')
    @patch('builtins.open', new_callable=mock_open)
    def test_error_unzip_file_upload(self, mock_open, mock_make_archive, mock_os_remove):
        """
        Test if upload method from Azkaban class raises UploadError if request returns error unzipping file
        """

        responses.add(
            responses.POST, self.host + "/manager",
            json={'projectId': '33', 'version': '58', 'error': 'Installation Failed.\nError unzipping file.'},
            status=500
        )

        mock_make_archive.return_value = 'zip_path'

        with self.assertRaises(UploadError):
            self.azk.upload('path', 'project', 'zip_name')

    @responses.activate
    @patch('azkaban_cli.azkaban.os.remove')
    @patch('azkaban_cli.azkaban.make_archive')
    @patch('builtins.open', new_callable=mock_open)
    def test_error_project_doesnt_exist_upload(self, mock_open, mock_make_archive, mock_os_remove):
        """
        Test if upload method from Azkaban class raises UploadError if request returns error caused by project doesn't exist
        """
        responses.add(
            responses.POST, self.host + "/manager",
            json={"error": "Installation Failed. Project 'no-existing-project' doesn't exist."},
            status=400
        )

        mock_make_archive.return_value = 'zip_path'

        with self.assertRaises(UploadError):
            self.azk.upload('path', 'project', 'zip_name')

    @responses.activate
    @patch('azkaban_cli.azkaban.os.remove')
    @patch('azkaban_cli.azkaban.make_archive')
    def test_error_file_not_found_upload(self, mock_make_archive, mock_os_remove):
        """
        Test if upload method from Azkaban class raises UploadError if could not create zip from path passed as argument, 
        usually because path is wrong
        """

        mock_make_archive.side_effect = FileNotFoundError

        with self.assertRaises(UploadError):
           self.azk.upload('path', 'project', 'zip_name')

        self.assertEqual(len(responses.calls), 0)

    @patch('azkaban_cli.azkaban.os.remove')
    @patch('azkaban_cli.azkaban.make_archive')
    @patch('azkaban_cli.azkaban.api.upload_request')
    def test_upload_request_called(self, mock_upload_request, mock_make_archive, mock_os_remove):
        """
        Test if upload method from Azkaban class is calling upload request with expected arguments
        """

        path     = '/path/to/project'
        project  = 'project'
        zip_name = 'zip_name'
        zip_path = '/path/to/zip_name.zip'

        mock_make_archive.return_value = zip_path

        self.azk.upload(path, project, zip_name)

        mock_upload_request.assert_called_with(ANY, self.host, self.session_id, project, zip_path)

    @patch('azkaban_cli.azkaban.os.remove')
    @patch('azkaban_cli.azkaban.make_archive')
    @patch('azkaban_cli.azkaban.api.upload_request')
    def test_get_project_name(self, mock_upload_request, mock_make_archive, mock_os_remove):
        """
        Test if upload method from Azkaban class still works if project name is not passed.

        Expected to get project name from path
        """

        path             = '/path/to/project'
        get_project_name = 'project'

        mock_make_archive.return_value = 'zip_path'

        self.azk.upload(path)

        mock_upload_request.assert_called_with(ANY, self.host, self.session_id, get_project_name, ANY)

    @patch('azkaban_cli.azkaban.os.remove')
    @patch('azkaban_cli.azkaban.make_archive')
    @patch('azkaban_cli.azkaban.api.upload_request')
    def test_get_zip_name(self, mock_upload_request, mock_make_archive, mock_os_remove):
        """
        Test if upload method from Azkaban class still works if zip name is not passed.

        Expected to get zip name from project
        """

        path     = '/path/to/project'
        project  = 'project'

        self.azk.upload(path, project=project)

        mock_make_archive.assert_called_with(project, 'zip', path)
        mock_upload_request.assert_called_with(ANY, self.host, self.session_id, ANY, ANY)

    @responses.activate
    @patch('azkaban_cli.azkaban.os.remove')
    @patch('azkaban_cli.azkaban.make_archive')
    @patch('builtins.open', new_callable=mock_open)
    def test_delete_zip_after_upload(self, mock_open, mock_make_archive, mock_os_remove):
        """
        Test if upload method from Azkaban class is removing the zip that created for upload 
        """

        path     = '/path/to/project'
        project  = 'project'
        zip_path = 'zip_path'
        responses.add(responses.POST, self.host + "/manager", json={'projectId': '33', 'version': '58'})

        mock_make_archive.return_value = zip_path

        self.azk.upload(path, project=project)

        mock_os_remove.assert_called_with(zip_path)

    @responses.activate
    @patch('azkaban_cli.azkaban.os.remove')
    @patch('azkaban_cli.azkaban.make_archive')
    @patch('builtins.open', new_callable=mock_open)
    def test_error_session_expired_upload(self, mock_open, mock_make_archive, mock_os_remove):
        """
        Test if upload method from Azkaban class raises Session if request returns error caused by expired session
        """

        responses.add(responses.POST, self.host + "/manager", body="Login error. Need username and password", status=200)

        path     = '/path/to/project'

        with self.assertRaises(SessionError):
            self.azk.upload(path)


class AzkabanScheduleTest(TestCase):
    def setUp(self):
        """
        Creates an Azkaban instance and set a logged session for all upload tests
        """

        self.azk = azkaban_cli.azkaban.Azkaban()

        self.host = 'http://azkaban-mock.com'
        self.session_id = 'aebe406b-d5e6-4056-add6-bf41091e42c6'

        self.azk.set_logged_session(self.host, self.session_id)

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

        fixture_path = os.path.join(os.path.dirname(__file__), "resources", "session_expired.html")
        with open(fixture_path) as f:
            responses.add(responses.POST, self.host + "/schedule", body=f.read(), status=200)

        with self.assertRaises(SessionError):
            self.azk.schedule(self.project, self.flow, self.cron)

class AzkabanExecuteTest(TestCase):
    def setUp(self):
        """
        Creates an Azkaban instance and set a logged session for all upload tests
        """

        self.azk = azkaban_cli.azkaban.Azkaban()

        self.host = 'http://azkaban-mock.com'
        self.session_id = 'aebe406b-d5e6-4056-add6-bf41091e42c6'

        self.azk.set_logged_session(self.host, self.session_id)

        self.project = 'ProjectTest'
        self.flow    = 'FlowTest'

    def tearDown(self):
        pass

    @responses.activate
    def test_execute(self):
        """
        Test execute method from Azkaban class
        """

        responses.add(
            responses.GET,
            self.host + "/executor",
            json={
                'project': 'ProjectTest',
                'message': 'Execution submitted successfully with exec id 6867',
                'flow': 'FlowTest',
                'execid': '6867'
            },
            status=200
        )

        self.azk.execute(self.project, self.flow)

    @patch('azkaban_cli.azkaban.api.execute_request')
    def test_execute_request_called(self, mock_execute_request):
        """
        Test if execute method from Azkaban class is calling execute request with expected arguments
        """

        self.azk.execute(self.project, self.flow)

        mock_execute_request.assert_called_with(ANY, self.host, self.session_id, self.project, self.flow)


    @responses.activate
    def test_flow_cannot_be_found_execute(self):
        """
        Test if execute method from Azkaban class raises ExecuteError if request returns error caused by flow not be found
        """

        responses.add(
            responses.GET,
            self.host + "/executor",
            json={
                'project': 'ProjectTest',
                'error': "Flow 'FlowTest' cannot be found in project ProjectTest",
                'flow': 'FlowTest'
            },
            status=200
        )

        with self.assertRaises(ExecuteError):
            self.azk.execute(self.project, self.flow)

    @responses.activate
    def test_project_doesnt_exist_execute(self):
        """
        Test if execute method from Azkaban class raises ExecuteError if request returns error caused by project doesn't exist
        """

        responses.add(
            responses.GET,
            self.host + "/executor",
            json={
                'project': 'ProjectTest',
                'error': "Project 'ProjectTest' doesn't exist."
            },
            status=200
        )

        with self.assertRaises(ExecuteError):
            self.azk.execute(self.project, self.flow)

    @responses.activate
    def test_error_session_expired_execute(self):
        """
        Test if execute method from Azkaban class raises SessionError if request returns error caused by session expired
        """

        responses.add(responses.GET, self.host + "/executor", json={"error": "session"}, status=200)

        with self.assertRaises(SessionError):
            self.azk.execute(self.project, self.flow)

class AzkabanCreateTest(TestCase):
    
    def setUp(self):
        """
        Creates an Azkaban instance and set a logged session for all upload tests
        """

        self.azk = azkaban_cli.azkaban.Azkaban()

        self.host = 'http://azkaban-mock.com'
        self.session_id = 'aebe406b-d5e6-4056-add6-bf41091e42c6'

        self.azk.set_logged_session(self.host, self.session_id)

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

        fixture_path = os.path.join(os.path.dirname(__file__), "resources", "session_expired.html")
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
