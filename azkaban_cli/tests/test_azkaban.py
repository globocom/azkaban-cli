from unittest.mock import patch, Mock, ANY
from unittest import TestCase
from azkaban_cli.exceptions import LoginError, NotLoggedOnError, UploadError, ScheduleError, ExecuteError, SessionError,CreateError
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
        mock_response.text = "{'session.id': 'aebe406b-d5e6-4056-add6-bf41091e42c6', 'status': 'success'}"
        mock_response.json.return_value = {'session.id': 'aebe406b-d5e6-4056-add6-bf41091e42c6', 'status': 'success'}

        self.azk.login('host', 'user', 'password')

        logged_session = self.azk.get_logged_session()
        expected = {'host': 'host', 'session_id': 'aebe406b-d5e6-4056-add6-bf41091e42c6'}

        self.assertEqual(logged_session, expected)

    @patch('azkaban_cli.azkaban.api.login_request')
    def test_wrong_host_login(self, mock_login_request):
        """
        Test if login method from Azkaban class treats correctly ConnectionError, usually raised when host is wrong.

        Expected to not save logged session and method to raise requests.exceptions.ConnectionError
        """

        mock_login_request.side_effect = requests.exceptions.ConnectionError

        with self.assertRaises(requests.exceptions.ConnectionError):
            self.azk.login('wrong_host', 'user', 'password')

        logged_session = self.azk.get_logged_session()
        expected = {'host': None, 'session_id': None}

        self.assertEqual(logged_session, expected)

    @patch('azkaban_cli.azkaban.api.login_request')
    def test_wrong_user_login(self, mock_login_request):
        """
        Test if login method from Azkaban class treats correctly when request returns error caused by wrong user.

        Expected to not save logged session and method to raise LoginError
        """

        mock_response = Mock()
        mock_login_request.return_value = mock_response
        mock_response.text = "{'error': 'Incorrect Login. No user wrong_user found'}"
        mock_response.json.return_value = {'error': 'Incorrect Login. No user wrong_user found'}

        with self.assertRaises(LoginError):
            self.azk.login('host', 'wrong_user', 'password')

        logged_session = self.azk.get_logged_session()
        expected = {'host': None, 'session_id': None}

        self.assertEqual(logged_session, expected)

    @patch('azkaban_cli.azkaban.api.login_request')
    def test_wrong_password_login(self, mock_login_request):
        """
        Test if login method from Azkaban class treats correctly when request returns error caused by wrong password.

        Expected to not save logged session and method to raise LoginError
        """

        mock_response = Mock()
        mock_login_request.return_value = mock_response
        mock_response.text = "{'error': 'Incorrect Login. LDAP error: '}"
        mock_response.json.return_value = {'error': 'Incorrect Login. LDAP error: '}

        with self.assertRaises(LoginError):
            self.azk.login('host', 'user', 'wrong_password')

        logged_session = self.azk.get_logged_session()
        expected = {'host': None, 'session_id': None}

        self.assertEqual(logged_session, expected)

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

    @patch('azkaban_cli.azkaban.os.remove')
    @patch('azkaban_cli.azkaban.make_archive')
    @patch('azkaban_cli.azkaban.api.upload_request')
    def test_upload(self, mock_upload_request, mock_make_archive, mock_os_remove):
        """
        Test upload method from Azkaban class
        """

        mock_response = Mock()
        mock_upload_request.return_value = mock_response
        mock_response.text = "{'projectId': '33', 'version': '58'}"
        mock_response.json.return_value = {'projectId': '33', 'version': '58'}

        mock_make_archive.return_value = 'zip_path'

        self.azk.upload('path', 'project', 'zip_name')

    @patch('azkaban_cli.azkaban.api.upload_request')
    def test_error_not_logged_upload(self, mock_upload_request):
        """
        Test if upload method from Azkaban class raises NotLoggedOnError and doesn't make the request if there is no logged session
        """

        self.azk.logout()

        with self.assertRaises(NotLoggedOnError):
            self.azk.upload('path', 'project', 'zip_name')

        mock_upload_request.assert_not_called()

    @patch('azkaban_cli.azkaban.os.remove')
    @patch('azkaban_cli.azkaban.make_archive')
    @patch('azkaban_cli.azkaban.api.upload_request')
    def test_error_unzip_file_upload(self, mock_upload_request, mock_make_archive, mock_os_remove):
        """
        Test if upload method from Azkaban class raises UploadError if request returns error unzipping file
        """

        mock_response = Mock()
        mock_upload_request.return_value = mock_response
        mock_response.text = "{'projectId': '33', 'version': '58', 'error': 'Installation Failed.\nError unzipping file.'}"
        mock_response.json.return_value = {'projectId': '33', 'version': '58', 'error': 'Installation Failed.\nError unzipping file.'}

        mock_make_archive.return_value = 'zip_path'

        with self.assertRaises(UploadError):
            self.azk.upload('path', 'project', 'zip_name')

    @patch('azkaban_cli.azkaban.os.remove')
    @patch('azkaban_cli.azkaban.make_archive')
    @patch('azkaban_cli.azkaban.api.upload_request')
    def test_error_project_doesnt_exist_upload(self, mock_upload_request, mock_make_archive, mock_os_remove):
        """
        Test if upload method from Azkaban class raises UploadError if request returns error caused by project doesn't exist
        """

        mock_response = Mock()
        mock_upload_request.return_value = mock_response
        mock_response.text = "{\"error\" : \"Installation Failed. Project 'no-existing-project' doesn't exist.\"}"
        mock_response.json.return_value = {"error" : "Installation Failed. Project 'no-existing-project' doesn't exist."}

        mock_make_archive.return_value = 'zip_path'

        with self.assertRaises(UploadError):
            self.azk.upload('path', 'project', 'zip_name')

    @patch('azkaban_cli.azkaban.os.remove')
    @patch('azkaban_cli.azkaban.make_archive')
    @patch('azkaban_cli.azkaban.api.upload_request')
    def test_error_file_not_found_upload(self, mock_upload_request, mock_make_archive, mock_os_remove):
        """
        Test if upload method from Azkaban class raises UploadError if could not create zip from path passed as argument, 
        usually because path is wrong
        """

        mock_make_archive.side_effect = FileNotFoundError

        with self.assertRaises(UploadError):
           self.azk.upload('path', 'project', 'zip_name')

        mock_upload_request.assert_not_called()

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

    @patch('azkaban_cli.azkaban.os.remove')
    @patch('azkaban_cli.azkaban.make_archive')
    @patch('azkaban_cli.azkaban.api.upload_request')
    def test_delete_zip_after_upload(self, mock_upload_request, mock_make_archive, mock_os_remove):
        """
        Test if upload method from Azkaban class is removing the zip that created for upload 
        """

        path     = '/path/to/project'
        project  = 'project'
        zip_path = 'zip_path'

        mock_make_archive.return_value = zip_path

        self.azk.upload(path, project=project)

        mock_os_remove.assert_called_with(zip_path)
        mock_upload_request.assert_called_with(ANY, self.host, self.session_id, ANY, ANY)

    @patch('azkaban_cli.azkaban.os.remove')
    @patch('azkaban_cli.azkaban.make_archive')
    @patch('azkaban_cli.azkaban.api.upload_request')
    def test_error_session_expired_upload(self, mock_upload_request, mock_make_archive, mock_os_remove):
        """
        Test if upload method from Azkaban class raises Session if request returns error caused by expired session
        """

        mock_response = Mock()
        mock_upload_request.return_value = mock_response
        mock_response.text = "Login error. Need username and password"

        path     = '/path/to/project'

        with self.assertRaises(SessionError):
            self.azk.upload(path)


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
        Test schedule method from Azkaban class 
        """

        mock_response = Mock()
        mock_schedule_request.return_value = mock_response
        mock_response.text = "{'message': 'ProjectTest.FlowTest scheduled.','scheduleId': '41','status': 'success'}"
        mock_response.json.return_value = {
            'message': 'ProjectTest.FlowTest scheduled.',
            'scheduleId': '41',
            'status': 'success'
        }

        self.azk.schedule(self.project, self.flow, self.cron)

    @patch('azkaban_cli.azkaban.api.schedule_request')
    def test_schedule_request_called(self, mock_schedule_request):
        """
        Test if schedule method from Azkaban class is calling schedule request with expected arguments
        """

        self.azk.schedule(self.project, self.flow, self.cron)

        mock_schedule_request.assert_called_with(ANY, self.host, self.session_id, self.project, self.flow, self.cron)

    @patch('azkaban_cli.azkaban.api.schedule_request')
    def test_error_project_doesnt_exist_schedule(self, mock_schedule_request):
        """
        Test if schedule method from Azkaban class raises ScheduleError if request returns error caused by project doesn't exist
        """

        mock_response = Mock()
        mock_schedule_request.return_value = mock_response
        mock_response.text = "{'message': 'Project ProjectTest does not exist','status': 'error'}"
        mock_response.json.return_value = {
            'message': 'Project ProjectTest does not exist',
            'status': 'error'
        }

        with self.assertRaises(ScheduleError):
            self.azk.schedule(self.project, self.flow, self.cron)

    @patch('azkaban_cli.azkaban.api.schedule_request')
    def test_error_flow_cannot_be_found_schedule(self, mock_schedule_request):
        """
        Test if schedule method from Azkaban class raises ScheduleError if request returns error caused by flow not be found
        """

        mock_response = Mock()
        mock_schedule_request.return_value = mock_response
        mock_response.text = "{'message': 'Flow FlowTest cannot be found in project GustavoTest','status': 'error'}"
        mock_response.json.return_value = {
            'message': 'Flow FlowTest cannot be found in project GustavoTest',
            'status': 'error'
        }

        with self.assertRaises(ScheduleError):
            self.azk.schedule(self.project, self.flow, self.cron)

    @patch('azkaban_cli.azkaban.api.schedule_request')
    def test_error_cron_cannot_be_parsed_schedule(self, mock_schedule_request):
        """
        Test if schedule method from Azkaban class raises ScheduleError if request returns error caused by wrong cron expression
        """

        mock_response = Mock()
        mock_schedule_request.return_value = mock_response
        mock_response.text = "{'error': 'This expression <0 23 ? * *> can not be parsed to quartz cron.'}"
        mock_response.json.return_value = {
            'error': 'This expression <0 23 ? * *> can not be parsed to quartz cron.'
        }

        with self.assertRaises(ScheduleError):
            self.azk.schedule(self.project, self.flow, self.cron)

    @patch('azkaban_cli.azkaban.api.schedule_request')
    def test_error_session_expired_schedule(self, mock_schedule_request):
        """
        Test if schedule method from Azkaban class raises SessionError if request returns html from login because of expired session
        """

        mock_response = Mock()
        mock_schedule_request.return_value = mock_response
        with open("azkaban_cli/tests/resources/schedule_session_expired.html") as f:
            mock_response.text = f.read()

        with self.assertRaises(SessionError):
            self.azk.schedule(self.project, self.flow, self.cron)

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
        Test execute method from Azkaban class
        """

        mock_response = Mock()
        mock_execute_request.return_value = mock_response
        mock_response.text = "{'project': 'ProjectTest','message': 'Execution submitted successfully with exec id 6867','flow': 'FlowTest','execid': '6867'}"
        mock_response.json.return_value = {
            'project': 'ProjectTest',
            'message': 'Execution submitted successfully with exec id 6867',
            'flow': 'FlowTest',
            'execid': '6867'
        }

        self.azk.execute(self.project, self.flow)

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
        Test if execute method from Azkaban class raises ExecuteError if request returns error caused by flow not be found
        """

        mock_response = Mock()
        mock_execute_request.return_value = mock_response
        mock_response.text = "{'project': 'ProjectTest','error': \"Flow 'FlowTest' cannot be found in project ProjectTest\",'flow': 'FlowTest'}"
        mock_response.json.return_value = {
            'project': 'ProjectTest',
            'error': "Flow 'FlowTest' cannot be found in project ProjectTest",
            'flow': 'FlowTest'
        }

        with self.assertRaises(ExecuteError):
            self.azk.execute(self.project, self.flow)

    @patch('azkaban_cli.azkaban.api.execute_request')
    def test_project_doesnt_exist_execute(self, mock_execute_request):
        """
        Test if execute method from Azkaban class raises ExecuteError if request returns error caused by flow not be found
        """

        mock_response = Mock()
        mock_execute_request.return_value = mock_response
        mock_response.text = "{'project': 'ProjectTest','error': \"Project 'ProjectTest' doesn't exist.\"}"
        mock_response.json.return_value = {
            'project': 'ProjectTest',
            'error': "Project 'ProjectTest' doesn't exist."
        }

        with self.assertRaises(ExecuteError):
            self.azk.execute(self.project, self.flow)

    @patch('azkaban_cli.azkaban.api.execute_request')
    def test_error_session_expired_execute(self, mock_execute_request):
        """
        Test if execute method from Azkaban class raises SessionError if request returns error caused by session expired
        """

        mock_response = Mock()
        mock_execute_request.return_value = mock_response
        mock_response.text = "{\"error\" : \"session\"}"
        mock_response.json.return_value = {
            "error": "session"
        }

        with self.assertRaises(SessionError):
            self.azk.execute(self.project, self.flow)

class AzkabanCreateTest(TestCase):
    
    def setUp(self):
        """
        Creates an Azkaban instance and set a logged session for all upload tests
        """

        self.azk = azkaban_cli.azkaban.Azkaban()

        self.host = 'host'
        self.session_id = 'aebe406b-d5e6-4056-add6-bf41091e42c6'

        self.azk.set_logged_session(self.host, self.session_id)

        self.project = 'ProjectTest'
        self.description = 'DescriptionTest'
    
    def tearDown(self):
        pass
    
    @patch('azkaban_cli.azkaban.api.create_request')
    def test_create(self,mock_create_request):
        """
        Test execute method from Azkaban class
        """
        mock_response = Mock()
        mock_create_request.return_value = mock_response
        mock_response.text = "{'project': 'ProjectTest','message': 'Project 'ProjectTest' created successful','description':'DescriptionTest'}"
        mock_response.json.return_value = {
            'project': 'ProjectTest',
            'message': 'Project ProjectTest created successful',
            'description': 'DescriptionTest'
        }

        self.azk.create(self.project, self.description)

    @patch('azkaban_cli.azkaban.api.create_request')
    def test_create_request_called(self, mock_create_request):
        """
        Test if create method from Azkaban class is calling create request with expected arguments
        """

        self.azk.create(self.project, self.description)

        mock_create_request.assert_called_with(ANY, self.host, self.session_id, self.project, self.description) 

    @patch('azkaban_cli.azkaban.api.create_request')
    def test_error_session_expired_create(self, mock_create_request):
        """
        Test if create method from Azkaban class raises SessionError if request returns error caused by session expired
        """

        mock_response = Mock()
        mock_create_request.return_value = mock_response
        mock_response.text = "{\"error\" : \"session\"}"
        mock_response.json.return_value = {
            "error": "session"
        }

        with self.assertRaises(SessionError):
            self.azk.create(self.project, self.description)
    
    @patch('azkaban_cli.azkaban.api.create_request')
    def test_project_exists_create(self, mock_create_request):
        """
        Test if create method from Azkaban class raises CreateError if request returns error caused by project already exists
        """

        mock_response = Mock()
        mock_create_request.return_value = mock_response
        mock_response.text = '{"message":"Project already exists.","status":"error"}'
        mock_response.json.return_value = {
            'status': 'error',
            'message': "Project already exists."
        }

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

    @patch('azkaban_cli.azkaban.api.create_request')
    def test_invalid_project_create(self, mock_create_request):
        """
        Test if create method from Azkaban class treats correctly when request returns error caused by  invalid project.
        """

        mock_response = Mock()
        mock_create_request.return_value = mock_response
        mock_response.text = "{'message': \"Project names must start with a letter, followed by any number of letters, digits, '-' or '_'. \", 'status':'error'}"
        mock_response.json.return_value = {'message': "Project names must start with a letter, followed by any number of letters, digits, '-' or '_'.", 'status':"error"}

        with self.assertRaises(CreateError):
            self.azk.create('123','description')

    @patch('azkaban_cli.azkaban.api.create_request')
    def test_empty_project_create(self, mock_create_request):
        """
        Test if create method from Azkaban class treats correctly when request returns error caused by  empty project.
        """

        mock_response = Mock()
        mock_create_request.return_value = mock_response
        mock_response.text = "{'message': 'Project name cannot be empty.', 'status':'error'}"
        mock_response.json.return_value = {'message': "Project name cannot be empty.", 'status':"error"}

        with self.assertRaises(CreateError):
            self.azk.create('','description')

    @patch('azkaban_cli.azkaban.api.create_request')
    def test_empty_description_create(self, mock_create_request):
        """
        Test if create method from Azkaban class treats correctly when request returns error caused by  empty description.
        """

        mock_response = Mock()
        mock_create_request.return_value = mock_response
        mock_response.text = "{'message': 'Description cannot be empty.', 'status':'error'}"
        mock_response.json.return_value = {'message': "Description cannot be empty.", 'status':"error"}

        with self.assertRaises(CreateError):
            self.azk.create('Project','')
