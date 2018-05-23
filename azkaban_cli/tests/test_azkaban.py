from unittest.mock import patch, Mock, ANY
from unittest import TestCase
import requests
import azkaban_cli.azkaban

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

    @patch('azkaban_cli.azkaban.api.login_request')
    def test_login(self, mock_login_request):
        """
        Test if login method from Azkaban class creates a logged session as expected
        """

        mock_response = Mock()
        mock_login_request.return_value = mock_response
        mock_response.json.return_value = {'session.id': 'aebe406b-d5e6-4056-add6-bf41091e42c6', 'status': 'success'}

        return_value = self.azk.login('host', 'user', 'password')

        logged_session = self.azk.get_logged_session()
        expected = {'host': 'host', 'session_id': 'aebe406b-d5e6-4056-add6-bf41091e42c6'}

        self.assertEqual(logged_session, expected)
        self.assertTrue(return_value)

    @patch('azkaban_cli.azkaban.api.login_request')
    def test_wrong_host_login(self, mock_login_request):
        """
        Test if login method from Azkaban class treats correctly ConnectionError, usually raised when host is wrong.

        Expected to not save logged session and method return false
        """

        mock_login_request.side_effect = requests.exceptions.ConnectionError

        return_value = self.azk.login('wrong_host', 'user', 'password')

        logged_session = self.azk.get_logged_session()
        expected = {'host': None, 'session_id': None}

        self.assertEqual(logged_session, expected)
        self.assertFalse(return_value)
    
    @patch('azkaban_cli.azkaban.api.login_request')
    def test_wrong_user_login(self, mock_login_request):
        """
        Test if login method from Azkaban class treats correctly when request returns error caused by wrong user.

        Expected to not save logged session and method return false
        """

        mock_response = Mock()
        mock_login_request.return_value = mock_response
        mock_response.json.return_value = {'error': 'Incorrect Login. No user wrong_user found'}

        return_value = self.azk.login('host', 'wrong_user', 'password')

        logged_session = self.azk.get_logged_session()
        expected = {'host': None, 'session_id': None}

        self.assertEqual(logged_session, expected)
        self.assertFalse(return_value)
    
    @patch('azkaban_cli.azkaban.api.login_request')
    def test_wrong_password_login(self, mock_login_request):
        """
        Test if login method from Azkaban class treats correctly when request returns error caused by wrong password.

        Expected to not save logged session and method return false
        """

        mock_response = Mock()
        mock_login_request.return_value = mock_response
        mock_response.json.return_value = {'error': 'Incorrect Login. LDAP error: '}

        return_value = self.azk.login('host', 'user', 'wrong_password')

        logged_session = self.azk.get_logged_session()
        expected = {'host': None, 'session_id': None}

        self.assertEqual(logged_session, expected)
        self.assertFalse(return_value)

class AzkabanUploadTest(TestCase):
    def setUp(self):
        """
        Creates an Azkaban instance and set a logged session for all upload tests
        """

        self.azk = azkaban_cli.azkaban.Azkaban()

        self.host = 'host'
        self.session_id = 'aebe406b-d5e6-4056-add6-bf41091e42c6'

        self.azk.set_logged_session(self.host, self.session_id)

    def tearDown(self):
        pass

    @patch('azkaban_cli.azkaban.zip_directory')
    @patch('azkaban_cli.azkaban.api.upload_request')
    def test_upload(self, mock_upload_request, mock_zip_directory):
        """
        Test if upload method from Azkaban class returns True if request is fine
        """

        mock_response = Mock()
        mock_upload_request.return_value = mock_response
        mock_response.json.return_value = {'projectId': '33', 'version': '58'}

        mock_zip_directory.return_value = 'zip_path'

        return_value = self.azk.upload('path', 'project', 'zip_name')

        self.assertTrue(return_value)

    @patch('azkaban_cli.azkaban.api.upload_request')
    def test_error_not_logged_upload(self, mock_upload_request):
        """
        Test if upload method from Azkaban class returns False and doesn't make the request if there is no logged session
        """

        self.azk.logout()

        return_value = self.azk.upload('path', 'project', 'zip_name')

        mock_upload_request.assert_not_called()
        self.assertFalse(return_value)

    @patch('azkaban_cli.azkaban.zip_directory')
    @patch('azkaban_cli.azkaban.api.upload_request')
    def test_error_unzip_file_upload(self, mock_upload_request, mock_zip_directory):
        """
        Test if upload method from Azkaban class returns False if request returns error unzipping file
        """

        mock_response = Mock()
        mock_upload_request.return_value = mock_response
        mock_response.json.return_value = {'projectId': '33', 'version': '58', 'error': 'Installation Failed.\nError unzipping file.'}

        mock_zip_directory.return_value = 'zip_path'

        return_value = self.azk.upload('path', 'project', 'zip_name')

        self.assertFalse(return_value)

    @patch('azkaban_cli.azkaban.zip_directory')
    @patch('azkaban_cli.azkaban.api.upload_request')
    def test_error_project_doesnt_exist_upload(self, mock_upload_request, mock_zip_directory):
        """
        Test if upload method from Azkaban class returns False if request returns error caused by project doesn't exist
        """

        mock_response = Mock()
        mock_upload_request.return_value = mock_response
        mock_response.json.return_value = {"error" : "Installation Failed. Project 'no-existing-project' doesn't exist."}

        mock_zip_directory.return_value = 'zip_path'

        return_value = self.azk.upload('path', 'project', 'zip_name')

        self.assertFalse(return_value)

    @patch('azkaban_cli.azkaban.zip_directory')
    @patch('azkaban_cli.azkaban.api.upload_request')
    def test_error_could_not_find_zip_upload(self, mock_upload_request, mock_zip_directory):
        """
        Test if upload method from Azkaban class returns False if could not create zip from path passed as argument, 
        usually because path is wrong
        """

        mock_zip_directory.return_value = None

        return_value = self.azk.upload('path', 'project', 'zip_name')

        mock_upload_request.assert_not_called()
        self.assertFalse(return_value)

    @patch('azkaban_cli.azkaban.zip_directory')
    @patch('azkaban_cli.azkaban.api.upload_request')
    def test_upload_request_called(self, mock_upload_request, mock_zip_directory):
        """
        Test if upload method from Azkaban class is calling upload request with expected arguments
        """

        path     = '/path/to/project'
        project  = 'project'
        zip_name = 'zip_name.zip'
        zip_path = '/path/to/zip_name.zip'

        mock_zip_directory.return_value = zip_path

        self.azk.upload(path, project, zip_name)

        mock_upload_request.assert_called_with(ANY, self.host, self.session_id, project, zip_name, zip_path)

    @patch('azkaban_cli.azkaban.zip_directory')
    @patch('azkaban_cli.azkaban.api.upload_request')
    def test_get_project_name(self, mock_upload_request, mock_zip_directory):
        """
        Test if upload method from Azkaban class still works if project name is not passed. 
        
        Expected to get project name from path
        """

        path             = '/path/to/project'
        get_project_name = 'project'

        mock_zip_directory.return_value = 'zip_path'

        self.azk.upload(path)

        mock_upload_request.assert_called_with(ANY, self.host, self.session_id, get_project_name, ANY, ANY)

    @patch('azkaban_cli.azkaban.zip_directory')
    @patch('azkaban_cli.azkaban.api.upload_request')
    def test_get_zip_name(self, mock_upload_request, mock_zip_directory):
        """
        Test if upload method from Azkaban class still works if project name is not passed. 

        Expected to get zip name from project name, adding .zip suffix
        """

        path     = '/path/to/project'
        project  = 'project'
        zip_name = 'project.zip'

        mock_zip_directory.return_value = 'zip_path'

        self.azk.upload(path, project=project)

        mock_upload_request.assert_called_with(ANY, self.host, self.session_id, ANY, zip_name, ANY)


    @patch('azkaban_cli.azkaban.zip_directory')
    @patch('azkaban_cli.azkaban.api.upload_request')
    def test_validate_zip_name(self, mock_upload_request, mock_zip_directory):
        """
        Test if upload method from Azkaban class still works if zip name is passed without zip suffix

        Expected to validate zip_name, adding .zip suffix
        """

        path            = '/path/to/project'
        project         = 'project'
        zip_name        = 'zip_name'
        valid_zip_name  = 'zip_name.zip'

        mock_zip_directory.return_value = 'zip_path'

        self.azk.upload(path, project=project, zip_name=zip_name)

        mock_upload_request.assert_called_with(ANY, self.host, self.session_id, ANY, valid_zip_name, ANY)

class AzkabanScheduleTest(TestCase):
    def setUp(self):
        """
        Creates an Azkaban instance and set a logged session for all upload tests
        """

        self.azk = azkaban_cli.azkaban.Azkaban()

        self.host = 'host'
        self.session_id = 'aebe406b-d5e6-4056-add6-bf41091e42c6'

        self.azk.set_logged_session(self.host, self.session_id)

        self.project = 'ProjectTest'
        self.flow    = 'FlowTest'
        self.cron    = '0 0 23 ? * *'

    def tearDown(self):
        pass

    @patch('azkaban_cli.azkaban.api.schedule_request')
    def test_schedule(self, mock_schedule_request):
        """
        Test if schedule method from Azkaban class returns True if request is fine
        """

        mock_response = Mock()
        mock_schedule_request.return_value = mock_response
        mock_response.json.return_value = {
            'message': 'ProjectTest.FlowTest scheduled.',
            'scheduleId': '41',
            'status': 'success'
        }

        return_value = self.azk.schedule(self.project, self.flow, self.cron)

        self.assertTrue(return_value)

    @patch('azkaban_cli.azkaban.api.schedule_request')
    def test_schedule_request_called(self, mock_schedule_request):
        """
        Test if schedule method from Azkaban class is calling schedule request with expected arguments
        """

        self.azk.schedule(self.project, self.flow, self.cron)

        mock_schedule_request.assert_called_with(ANY, self.host, self.session_id, self.project, self.flow, self.cron)

    @patch('azkaban_cli.azkaban.api.schedule_request')
    def test_error_project_doesnt_exist_upload(self, mock_schedule_request):
        """
        Test if schedule method from Azkaban class returns False if request returns error caused by project doesn't exist
        """

        mock_response = Mock()
        mock_schedule_request.return_value = mock_response
        mock_response.json.return_value = {
            'message': 'Project ProjectTest does not exist',
            'status': 'error'
        }

        return_value = self.azk.schedule(self.project, self.flow, self.cron)

        self.assertFalse(return_value)

    @patch('azkaban_cli.azkaban.api.schedule_request')
    def test_error_flow_cannot_be_found_upload(self, mock_schedule_request):
        """
        Test if schedule method from Azkaban class returns False if request returns error caused by flow not be found
        """

        mock_response = Mock()
        mock_schedule_request.return_value = mock_response
        mock_response.json.return_value = {
            'message': 'Flow FlowTest cannot be found in project GustavoTest',
            'status': 'error'
        }

        return_value = self.azk.schedule(self.project, self.flow, self.cron)

        self.assertFalse(return_value)

    @patch('azkaban_cli.azkaban.api.schedule_request')
    def test_error_cron_cannot_be_parsed_upload(self, mock_schedule_request):
        """
        Test if schedule method from Azkaban class returns False if request returns error caused by wrong cron expression
        """

        mock_response = Mock()
        mock_schedule_request.return_value = mock_response
        mock_response.json.return_value = {
            'error': 'This expression <0 23 ? * *> can not be parsed to quartz cron.'
        }

        return_value = self.azk.schedule(self.project, self.flow, self.cron)

        self.assertFalse(return_value)

class AzkabanExecuteTest(TestCase):
    def setUp(self):
        """
        Creates an Azkaban instance and set a logged session for all upload tests
        """

        self.azk = azkaban_cli.azkaban.Azkaban()

        self.host = 'host'
        self.session_id = 'aebe406b-d5e6-4056-add6-bf41091e42c6'

        self.azk.set_logged_session(self.host, self.session_id)

        self.project = 'ProjectTest'
        self.flow    = 'FlowTest'

    def tearDown(self):
        pass

    @patch('azkaban_cli.azkaban.api.execute_request')
    def test_execute(self, mock_execute_request):
        """
        Test if execute method from Azkaban class returns True if request is fine
        """

        mock_response = Mock()
        mock_execute_request.return_value = mock_response
        mock_response.json.return_value = {
            'project': 'ProjectTest',
            'message': 'Execution submitted successfully with exec id 6867',
            'flow': 'FlowTest',
            'execid': '6867'
        }

        return_value = self.azk.execute(self.project, self.flow)

        self.assertTrue(return_value)


    @patch('azkaban_cli.azkaban.api.execute_request')
    def test_execute_request_called(self, mock_execute_request):
        """
        Test if execute method from Azkaban class is calling execute request with expected arguments
        """

        self.azk.execute(self.project, self.flow)

        mock_execute_request.assert_called_with(ANY, self.host, self.session_id, self.project, self.flow)


    @patch('azkaban_cli.azkaban.api.execute_request')
    def test_flow_cannot_be_found_execute(self, mock_execute_request):
        """
        Test if execute method from Azkaban class returns False if request returns error caused by flow not be found
        """

        mock_response = Mock()
        mock_execute_request.return_value = mock_response
        mock_response.json.return_value = {
            'project': 'ProjectTest',
            'error': "Flow 'FlowTest' cannot be found in project ProjectTest",
            'flow': 'FlowTest'
        }

        return_value = self.azk.execute(self.project, self.flow)

        self.assertFalse(return_value)

    @patch('azkaban_cli.azkaban.api.execute_request')
    def test_project_doesnt_exist_execute(self, mock_execute_request):
        """
        Test if execute method from Azkaban class returns False if request returns error caused by flow not be found
        """

        mock_response = Mock()
        mock_execute_request.return_value = mock_response
        mock_response.json.return_value = {
            'project': 'ProjectTest',
            'error': "Project 'ProjectTest' doesn't exist."
        }

        return_value = self.azk.execute(self.project, self.flow)

        self.assertFalse(return_value)
