from requests.packages.urllib3.exceptions import InsecureRequestWarning
import logging
import os
import requests
import zipfile

class Azkaban(object):
    def __init__(self):
        # Session ignoring SSL verify requests
        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        
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

    def __zip_project(self, path, zip_name):
        absolute_project_path = os.path.abspath(path)

        if not os.path.isdir(absolute_project_path):
            self.logger.error('No such directory: %s' % absolute_project_path)
            return None

        # Where .zip will be created
        zip_path = absolute_project_path + '/' + zip_name

        # Create .zip
        zf = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)

        for root, dirs, files in os.walk(path):
            # ensure .zip root dir will be the path basename
            zip_root = root.replace(path, '', 1)

            for file in files:
                # local file path
                file_path = os.path.join(root, file)

                # .zip file path
                zip_file_path = os.path.join(zip_root, file)

                # skip adding .zip files to our zip
                if zip_file_path.endswith('.zip'):
                    continue

                # add local file to zip
                zf.write(file_path, zip_file_path)

        zf.close()

        return zip_path

    def __upload_request(self, host, session_id, project, zip_name, zip_path):
        zip_file = open(zip_path, 'rb')

        response = self.__session.post(
            host + '/manager', 
            data = {
                u'session.id': session_id, 
                u'ajax': u'upload', 
                u'project': project
            }, 
            files = {
                u'file': (zip_name, zip_file, 'application/zip'),
            }
        )

        return response.json()

    def __login_request(self, host, user, password):
        response = self.__session.post(
            host, 
            data = {
                u'action': u'login',
                u'username': user,
                u'password': password
            }
        )

        return response.json()

    def __schedule_request(self, host, session_id, project, flow, cron):
        response = self.__session.post(
            host + '/schedule',
            data = {
                u'session.id': session_id,
                u'ajax': u'scheduleCronFlow',
                u'projectName': project,
                u'flow': flow,
                u'cronExpression': cron
            }
        )

        return response.json()

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

        response_json = self.__login_request(valid_host, user, password)

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

        zip_path = self.__zip_project(path, zip_name)

        # check if zip was created
        if not zip_path:
            self.logger.error('Could not find zip file. Aborting upload')
            return False

        response_json = self.__upload_request(self.__host, self.__session_id, project, zip_name, zip_path)

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
        
        response_json = self.__schedule_request(self.__host, self.__session_id, project, flow, cron)

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
