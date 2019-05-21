# -*- coding: utf-8 -*-

from __future__ import absolute_import
from azkaban_cli.exceptions import (
    NotLoggedOnError,
    SessionError,
    LoginError,
    UploadError,
    ScheduleError,
    FetchFlowsError,
    FetchScheduleError,
    UnscheduleError,
    ExecuteError,
    CreateError
)
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
        self.__host = None
        self.__user = None
        self.__session_id = None

    def __validate_host(self, host):
        valid_host = host

        while valid_host.endswith(u'/'):
            valid_host = valid_host[:-1]

        return valid_host

    def __check_if_logged(self):
        if not self.__session_id:
            raise NotLoggedOnError()

    def __catch_login_html(self, response):
        if "  <script type=\"text/javascript\" src=\"/js/azkaban/view/login.js\"></script>" in response.text.splitlines():
            raise SessionError(response.text)

    def __catch_response_status_error(self, exception, response_json):
        response_status = response_json.get('status')
        if response_status == u'error':
            error_msg = response_json[u'message']
            raise exception(error_msg)

    def __catch_response_error_msg(self, exception, response_json):
        if u'error' in response_json.keys():
            error_msg = response_json[u'error']
            if error_msg == "session":
                raise SessionError(error_msg)
            raise exception(error_msg)

    def __catch_empty_response(self, exception, response_json):
        if response_json == {}:
            raise exception('Empty response')

    def __catch_login_text(self, response):
        if response.text == "Login error. Need username and password":
            raise SessionError(response.text)
    
    def __catch_login(self, response):
        self.__catch_login_text(response)
        self.__catch_login_html(response)

    def __catch_response_error(self, response, exception):
        self.__catch_login(response)

        response_json = response.json()

        self.__catch_response_error_msg(exception, response_json)
        self.__catch_response_status_error(exception, response_json)
        self.__catch_empty_response(exception, response_json)

    def get_logged_session(self):
        """Method for return the host and session id of the logged session saved on the class

        :return: A dictionary containing host and session_id as keys
        :rtype: dict
        """

        logged_session = {
            u'host': self.__host,
            u'user': self.__user,
            u'session_id': self.__session_id
        }

        return logged_session

    def set_logged_session(self, host, user, session_id):
        """Method for set host, user and session_id, attributes of the class

        :param str host: Azkaban hostname
        :param str user: Azkaban username
        :param str session_id: session.id received from a login request
        """

        self.__host = host
        self.__user = user
        self.__session_id = session_id

    def logout(self):
        """Logout command, intended to clear the host, user and session_id attributes from the class"""

        self.set_logged_session(None, None, None)

    def login(self, host, user, password):
        """Login command, intended to make the request to Azkaban and treat the response properly

        This method validate the host, make the request to Azkaban, and evaluate the response. If host, user or
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
        self.set_logged_session(valid_host, user, response_json['session.id'])

        logging.info('Logged as %s' % (user))

    def upload(self, path, project=None, zip_name=None):
        """Upload command, intended to make the request to Azkaban and treat the response properly

        This method receives a path to a directory that contains all the files that should be in the Azkaban project,
        zip this path (as Azkaban expects it zipped), make the upload request to Azkaban, deletes the zip that was
        created and evaluate the response.

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
        make the schedule request to schedule the flow with the cron specified and evaluate the response.

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

    def fetch_flows(self, project):
        """Fetch flows command, intended to make the request to Azkaban and treat the response properly.

        This method receives the project name, makes the fetch flows request to fetch the flows
        and evaluates the response.

        If project is wrong or there is no session_id, it returns false. If everything is fine, returns
        True.

        :param project: project name on Azkaban
        :type project: str
        :raises FetchFlowsError: when Azkaban api returns error in response
        """

        self.__check_if_logged()

        response = api.fetch_flows_request(
            self.__session,
            self.__host,
            self.__session_id,
            project
        )

        self.__catch_response_error(response, FetchFlowsError)

        response_json = response.json()
        logging.info('Project ID: %s' % (response_json[u'projectId']))
        return response_json

    def fetch_schedule(self, project_id, flow):
        """Fetch schedule command, intended to make the request to Azkaban and treat the response properly.

        This method receives the project id, flow name and optional execution options, makes the
        fetch schedule request to fetch the schedule of the flow and evaluates the response.

        If project_id or flow is wrong or there is no session_id, it returns false. If everything is fine, returns
        True.

        :param project_id: project id on Azkaban
        :type project_id: str
        :param flow: flow name on Azkaban
        :type flow: str
        :raises FetchScheduleError: when Azkaban api returns error in response
        """

        self.__check_if_logged()

        response = api.fetch_schedule_request(
            self.__session,
            self.__host,
            self.__session_id,
            project_id,
            flow
        )

        self.__catch_response_error(response, FetchScheduleError)

        response_json = response.json()
        logging.info('Schedule ID: %s' % (response_json[u'schedule'][u'scheduleId']))
        return response_json

    def unschedule(self, schedule_id):
        """Unschedule command, intended to make the request to Azkaban and treat the response properly.

        This method receives the schedule id and optional execution options, makes the unschedule
        request to unschedule the flow and evaluates the response.

        If schedule_id is wrong or there is no session_id, it returns false. If everything is fine, returns
        True.

        :param schedule_id: Schedule id on Azkaban
        :type schedule: str
        :raises UnscheduleError: when Azkaban api returns error in response
        """

        self.__check_if_logged()

        response = api.unschedule_request(
            self.__session,
            self.__host,
            self.__session_id,
            schedule_id
        )

        self.__catch_response_error(response, UnscheduleError)

        response_json = response.json()
        logging.info(response_json[u'message'])

    def execute(self, project, flow):
        """Execute command, intended to make the request to Azkaban and treat the response properly.

        This method receives the project and the flow, make the execute request to execute the flow and evaluate the
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
        """Create command, intended to make the request to Azkaban and treat the response properly.

        This method receives the project name and the description, make the execute request to create the project and
        evaluate the response.

        :param project: Project name on Azkaban
        :type project: str
        :param description: Description for the project
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

        logging.info('Project %s created successfully' % (project))

    def delete(self, project):
        """Delete command, intended to make the request to Azkaban and treat the response properly.

        This method receives the project name, make the execute request to delete the project and
        evaluate the response.

        :param project: Project name on Azkaban
        :type project: str
        """

        self.__check_if_logged()

        api.delete_request(
            self.__session,
            self.__host,
            self.__session_id,
            project
        )

        # The delete request does not return any message

    def fetch_projects(self):
        """Fetch all projects command, intended to make the request to Azkaban and treat the response properly.

        This method makes the fetch projects request to fetch all the projects and evaluates the response.
        """

        self.__check_if_logged()

        response = api.fetch_projects_request(
            self.__session,
            self.__host,
            self.__session_id
        )

        # The fetch projects request returns an html content, so we only catch login errors
        self.__catch_login(response)

        return response.text
