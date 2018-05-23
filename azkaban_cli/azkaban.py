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

    def __validate_host(self, host):
        valid_host = host

        while valid_host.endswith(u'/'):
            valid_host = valid_host[:-1]

        return valid_host

    def get_logged_session(self):
        logged_session = {
            u'host': self.__host,
            u'session_id': self.__session_id
        }

        return logged_session

    def set_logged_session(self, host, session_id):
        self.__host = host
        self.__session_id = session_id

    def logout(self):
        self.set_logged_session(None, None)

    def login(self, host, user, password):
        valid_host = self.__validate_host(host)

        try:
            response_json = api.login_request(self.__session, valid_host, user, password).json()
        except requests.exceptions.ConnectionError:
            logging.error("Could not connect to host")
            return False

        if u'error' in response_json.keys():
            error_msg = response_json[u'error']
            logging.error(error_msg)
            return False

        self.set_logged_session(valid_host, response_json['session.id'])

        logging.info('Logged as %s' % (user))

        return True

    def upload(self, path, project=None, zip_name=None):
        if not self.__session_id:
            logging.error(u'You are not logged')
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
            logging.error('Could not find zip file. Aborting upload')
            return False

        response_json = api.upload_request(self.__session ,self.__host, self.__session_id, project, zip_name, zip_path).json()

        if u'error' in response_json.keys():
            error_msg = response_json[u'error']
            logging.error(error_msg)
            return False
        else:
            logging.info('Project %s updated to version %s' % (project, response_json[u'version']))
            return True

    def schedule(self, project, flow, cron):
        if not self.__session_id:
            logging.error(u'You are not logged')
            return False

        response_json = api.schedule_request(self.__session, self.__host, self.__session_id, project, flow, cron).json()

        if u'error' in response_json.keys():
            error_msg = response_json[u'error']
            logging.error(error_msg)
            return False
        else:
            if response_json[u'status'] == u'error':
                logging.error(response_json[u'message'])
                return False
            else:
                logging.info(response_json[u'message'])
                logging.info('scheduleId: %s' % (response_json[u'scheduleId']))
                return True

    def execute(self, project, flow, **kwargs):
        if not self.__session_id:
            logging.error(u'You are not logged')
            return False
        
        response_json = api.execute_request(self.__session, self.__host, self.__session_id, project, flow, **kwargs).json()

        if u'error' in response_json.keys():
            error_msg = response_json[u'error']
            logging.error(error_msg)
            return False
        else:
            logging.info('%s' % (response_json[u'message']))
            return True
