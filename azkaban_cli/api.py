import requests
import logging

def upload_request(session, host, session_id, project, zip_name, zip_path):
    zip_file = open(zip_path, 'rb')

    response = session.post(
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

    logging.debug("Response: \n%s" % (response.text))

    return response

def login_request(session, host, user, password):
    response = session.post(
        host, 
        data = {
            u'action': u'login',
            u'username': user,
            u'password': password
        }
    )

    logging.debug("Response: \n%s" % (response.text))

    return response

def schedule_request(session, host, session_id, project, flow, cron):
    response = session.post(
        host + '/schedule',
        data = {
            u'session.id': session_id,
            u'ajax': u'scheduleCronFlow',
            u'projectName': project,
            u'flow': flow,
            u'cronExpression': cron
        }
    )

    logging.debug("Response: \n%s" % (response.text))

    return response

def execute_request(session, host, session_id, project, flow, **kwargs):
    response = session.get(
        host + '/executor',
        params = { 
            u'session.id': session_id,
            u'ajax': 'executeFlow',
            u'project': project,
            u'flow': flow
        }
    )

    logging.debug("Response: \n%s" % (response.text))

    return response
