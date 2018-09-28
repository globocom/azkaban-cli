from __future__ import absolute_import
from azkaban_cli.exceptions import NotLoggedOnError, SessionError, LoginError, UploadError, ScheduleError, ExecuteError, CreateError
from shutil import make_archive
from urllib3.exceptions import InsecureRequestWarning
import azkaban_cli.api as api
import json
import logging
import os
import requests
import urllib3

class Azkaban(object):
    def __init__(self):
        # Session ignoring SSL verify requests
        session = requests.Session()
        session.verify = False
        urllib3.disable_warnings(InsecureRequestWarning)

        self.__session = session

        self.set_logged_session(None, None)

    def __validate_host(self, host):
        valid_host = host

        while valid_host.endswith(u'/'):
            valid_host = valid_host[:-1]

        return valid_host

    def __check_if_logged(self):
        if not self.__session_id:
            raise NotLoggedOnError()

    def __catch_response_error(self, response, exception):
        if (response.text == "Login error. Need username and password"):
            raise SessionError(response.text)

        if ("  <script type=\"text/javascript\" src=\"/js/azkaban/view/login.js\"></script>" in response.text.splitlines()):
            raise SessionError(response.text)

        response_json = response.json()
        if u'error' in response_json.keys():
            error_msg = response_json[u'error']
            if error_msg == "session":
                raise SessionError(error_msg)
            raise exception(error_msg)

        response_status = response_json.get('status')
        if response_status == u'error':
            error_msg = response_json[u'message']
            raise exception(error_msg)

    def get_logged_session(self):
        """Method for return the host and session id of the logged session saved on the class

        :return: A dictionary containing host and session_id as keys
        :rtype: dict
        """

        logged_session = {
            u'host': self.__host,
            u'session_id': self.__session_id
        }

        return logged_session

    def set_logged_session(self, host, session_id):
        """Method for set host and session_id, attributes of the class

        :param host: Azkaban hostname
        :type host: str
        :param session_id: session.id received from a login request
        :type session_id: str
        """

        self.__host = host
        self.__session_id = session_id

    def logout(self):
        """Logout command, intended to clear the host and session_id attributes from the class"""

        self.set_logged_session(None, None)

    def login(self, host, user, password):
        """Login command, intended to make the request to Azkaban and treat the response properly

        This method validate the host, make the request to Azkaban, and avaliate the response. If host, user or
        password is wrong or could not connect to host, it returns false and do not change the host and session_id
        attribute from the class. If everything is fine, saves the new session_id and corresponding host as attributes
        in the class and returns True

        :param str host: Azkaban hostname
        :param str user: Username to login
        :param str password: Password from user
        :raises LoginError: when Azkaban api returns error in response
        """

        valid_host = self.__validate_host(host)

        response = api.login_request(self.__session, valid_host, user, password)

        self.__catch_response_error(response, LoginError)

        response_json = response.json()
        self.set_logged_session(valid_host, response_json['session.id'])

        logging.info('Logged as %s' % (user))

    def upload(self, path, project=None, zip_name=None):
        """Upload command, intended to make the request to Azkaban and treat the response properly

        This method receives a path to a directory that contains all the files that should be in the Azkaban project,
        zip this path (as Azkaban expects it zipped), make the upload request to Azkaban, deletes the zip that was
        created and avaliate the response.

        If project name is not passed as argument, it will be assumed that the project name is the basename of the path
        passed. If zip name is not passed as argument, the project name will be used for the zip.

        If project or path is wrong or if there is no session_id, it returns false. If everything is fine, returns True.

        :param path: path to be zipped and uploaded
        :type path: str
        :param project: Project name on Azkaban
        :type project: str, optional
        :param zip_name: Zip name that will be created and uploaded
        :type zip_name: str, optional
        :raises UploadError: when Azkaban api returns error in response
        """

        self.__check_if_logged()

        if not project:
            # define project name as basename
            project = os.path.basename(os.path.abspath(path))

        if not zip_name:
            # define zip name as project name
            zip_name = project

        try:
            zip_path = make_archive(zip_name, 'zip', path)
        except FileNotFoundError as e:
            raise UploadError(str(e))

        try:
            response = api.upload_request(self.__session ,self.__host, self.__session_id, project, zip_path)
        finally:
            os.remove(zip_path)

        self.__catch_response_error(response, UploadError)

        response_json = response.json()
        logging.info('Project %s updated to version %s' % (project, response_json[u'version']))

    def schedule(self, project, flow, cron, **execution_options):
        """Schedule command, intended to make the request to Azkaban and treat the response properly.

        This method receives the project, the flow, the cron expression in quartz format and optional execution options,
        make the schedule request to schedule the flow with the cron specified and avaliate the response.

        If project, flow or cron is wrong or if there is no session_id, it returns false. If everything is fine, returns
        True.

        :param project: Project name on Azkaban
        :type project: str
        :param flow: Flow name on Azkaban
        :type flow: str
        :param cron: Cron expression, in quartz format
        :type cron: str
        :raises ScheduleError: when Azkaban api returns error in response
        """

        self.__check_if_logged()

        execution_options = {k:v for (k, v) in execution_options.items() if v}

        response = api.schedule_request(
            self.__session,
            self.__host,
            self.__session_id,
            project,
            flow,
            cron,
            **execution_options
        )

        self.__catch_response_error(response, ScheduleError)

        response_json = response.json()
        logging.info(response_json[u'message'])
        logging.info('scheduleId: %s' % (response_json[u'scheduleId']))

    def execute(self, project, flow):
        """Execute command, intended to make the request to Azkaban and treat the response properly.

        This method receives the project and the flow, make the execute request to execute the flow and avaliate the
        response.

        If project or flow is wrong or if there is no session_id, it returns false. If everything is fine, returns True.

        :param project: Project name on Azkaban
        :type project: str
        :param flow: Flow name on Azkaban
        :type flow: str
        :raises ExecuteError: when Azkaban api returns error in response
        """

        self.__check_if_logged()

        response = api.execute_request(
            self.__session,
            self.__host,
            self.__session_id,
            project,
            flow,
        )

        self.__catch_response_error(response, ExecuteError)

        response_json = response.json()
        logging.info('%s' % (response_json[u'message']))

    def create(self, project, description):
        """Create command, intended to make the request to Azkaban and trear the response properly.

        This method receives the project name and the description, make the execute request to create the project and avaliate
        the response.

        :param project: Project name on Azkaban
        :type project: str
        : param description: Description for the project
        :type: str
        """
        
        self.__check_if_logged()

        response = api.create_request(
            self.__session,
            self.__host,
            self.__session_id,
            project,
            description
        )

        self.__catch_response_error(response, CreateError)

        logging.info('Project %s created successful' % (project))
