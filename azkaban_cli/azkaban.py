from __future__ import absolute_import
from azkaban_cli.zip import zip_directory
from urllib3.exceptions import InsecureRequestWarning
import azkaban_cli.api as api
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
        self.__session_id = None

        self.logger = self.__config_log()

    def __config_log(self):
        log_level = logging.INFO

        # log record format string
        format_string = u'%(asctime)s\t%(levelname)s\t%(message)s'

        # set default logging (to console)
        logging.basicConfig(level=log_level, format=format_string)

        logger = logging.getLogger()

        return logger

    def __validate_host(self, host):
        valid_host = host

        while valid_host.endswith(u'/'):
            valid_host = valid_host[:-1]

        return valid_host

    def set_logger(self, logger):
        self.logger = logger

    def get_logged_session(self):
        logged_session = {
            u'host': self.__host,
            u'session_id': self.__session_id
        }

        return logged_session

    def set_logged_session(self, logged_session):
        self.__host = None
        self.__session_id = None

        if logged_session:
            if u'host' in logged_session.keys() and u'session_id' in logged_session.keys():
                self.__host = logged_session[u'host']
                self.__session_id = logged_session[u'session_id']

    def login(self, host, user, password):
        valid_host = self.__validate_host(host)

        try:
            response_json = api.login_request(self.__session, valid_host, user, password).json()
        except requests.exceptions.ConnectionError:
            self.logger.error("Could not connect to host")
            return False

        if u'error' in response_json.keys():
            error_msg = response_json[u'error']
            self.logger.error(error_msg)
            return False

        logged_session = {
            u'host': valid_host,
            u'session_id': response_json['session.id']
        }

        self.set_logged_session(logged_session)

        self.logger.info('Logged as %s' % (user))

        return True

    def upload(self, path, project=None, zip_name=None):
        if not self.__session_id:
            self.logger.error(u'You are not logged')
            return False

        if not project:
            # define project name as basename
            project = os.path.basename(os.path.abspath(path))

        if not zip_name:
            # define zip name as project name
            zip_name = project
        
        if not zip_name.endswith('.zip'):
            zip_name = zip_name + '.zip'

        zip_path = zip_directory(path, zip_name)

        # check if zip was created
        if not zip_path:
            self.logger.error('Could not find zip file. Aborting upload')
            return False

        response_json = api.upload_request(self.__session ,self.__host, self.__session_id, project, zip_name, zip_path).json()

        if u'error' in response_json.keys():
            error_msg = response_json[u'error']
            self.logger.error(error_msg)
            return False
        else:
            self.logger.info('Project %s updated to version %s' % (project, response_json[u'version']))
            return True

    def schedule(self, project, flow, cron):
        if not self.__session_id:
            self.logger.error(u'You are not logged')
            return False
        
        response_json = api.schedule_request(self.__session, self.__host, self.__session_id, project, flow, cron).json()

        if u'error' in response_json.keys():
            error_msg = response_json[u'error']
            self.logger.error(error_msg)
            return False
        else:
            if response_json[u'status'] == u'error':
                self.logger.error(response_json[u'message'])
                return False
            else:
                self.logger.info(response_json[u'message'])
                self.logger.info('scheduleId: %s' % (response_json[u'scheduleId']))
                return True

    def execute(self, project, flow, **kwargs):
        if not self.__session_id:
            self.logger.error(u'You are not logged')
            return False
        
        response_json = api.execute_request(self.__session, self.__host, self.__session_id, project, flow, **kwargs).json()

        if u'error' in response_json.keys():
            error_msg = response_json[u'error']
            self.logger.error(error_msg)
            return False
        else:
            self.logger.info('%s' % (response_json[u'message']))
            return True
