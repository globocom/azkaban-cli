from unittest import TestCase
from unittest.mock import patch, mock_open, ANY

import responses

import azkaban_cli.azkaban
from azkaban_cli.exceptions import NotLoggedOnError, UploadError, SessionError


class AzkabanUploadTest(TestCase):
    def setUp(self):
        """
        Creates an Azkaban instance and set a logged session for all upload tests
        """

        self.azk = azkaban_cli.azkaban.Azkaban()

        self.host = 'http://azkaban-mock.com'
        self.user = 'username'
        self.session_id = 'aebe406b-d5e6-4056-add6-bf41091e42c6'

        self.azk.set_logged_session(self.host, self.user, self.session_id)

    def tearDown(self):
        pass

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
        zip_path = 'zip_path'

        mock_make_archive.return_value = zip_path

        with self.assertRaises(SessionError):
            self.azk.upload(path)