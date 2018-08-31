from __future__ import absolute_import
import logging
import click
import json
import requests
import sys
import zipfile
import os
from azkaban_cli.azkaban import Azkaban
from azkaban_cli.exceptions import NotLoggedOnError, LoginError

__version__ = u'0.3.0beta'
APP_NAME = 'Azkaban CLI'

HOME_PATH = os.path.expanduser("~")
AZKABAN_CLI_PATH = os.path.join(HOME_PATH, ".azkaban_cli")
SESSION_JSON_PATH = os.path.join(AZKABAN_CLI_PATH, "session.json")


def __call_for_login(ctx):
    ctx.invoke(login, host=click.prompt('Host'), user=click.prompt('User'), password=click.prompt('Password', hide_input=True))

def login_required(function):
    def function_wrapper(ctx, *args):
        try:
            function(ctx, *args)
        except NotLoggedOnError:
            __call_for_login(ctx)
            function_wrapper(ctx, *args)

    return function_wrapper

def __save_logged_session(logged_session):
    if not os.path.exists(AZKABAN_CLI_PATH):
        os.mkdir(AZKABAN_CLI_PATH)

    with open(SESSION_JSON_PATH, "w") as session_file:
        json.dump(logged_session, session_file)

def __load_logged_session():
    if os.path.exists(SESSION_JSON_PATH):
        with open(SESSION_JSON_PATH, "r") as session_file:
            logged_session = json.load(session_file)
            return logged_session

def __delete_logged_session():
    if os.path.exists(SESSION_JSON_PATH):
        os.remove(SESSION_JSON_PATH)

def __login(ctx, host, user, password):
    azkaban = ctx.obj[u'azkaban']

    try:
        azkaban.login(host, user, password)
        __save_logged_session(azkaban.get_logged_session())
    except (requests.exceptions.ConnectionError, requests.exceptions.MissingSchema) as e:
        logging.error("Could not connect to host: %s", str(e))
    except LoginError as e:
        logging.error("Login error: %s", str(e))

def __logout():
    __delete_logged_session()

@login_required
def __upload(ctx, path, project, zip_name):
    azkaban = ctx.obj[u'azkaban']

    azkaban.upload(path, project, zip_name)

@login_required
def __schedule(ctx, project, flow, cron):
    azkaban = ctx.obj[u'azkaban']

    azkaban.schedule(project, flow, cron)

@login_required
def __execute(ctx, project, flow):
    azkaban = ctx.obj[u'azkaban']

    azkaban.execute(project, flow)

# ----------------------------------------------------------------------------------------------------------------------
# Interface
# ----------------------------------------------------------------------------------------------------------------------

@click.group(chain=True)
@click.version_option(version=__version__, prog_name=APP_NAME)
def cli():
    log_level = logging.INFO

    # log record format string
    format_string = u'%(asctime)s\t%(levelname)s\t%(message)s'

    # set default logging (to console)
    logging.basicConfig(level=log_level, format=format_string)

    ctx = click.get_current_context()
    ctx.obj = {}

    azkaban = Azkaban()

    logged_session = __load_logged_session()

    if logged_session:
        azkaban.set_logged_session(**logged_session)

    ctx.obj['azkaban'] = azkaban


@click.command(u'login')
@click.pass_context
@click.option(u'--host', prompt=True, help=u'Azkaban hostname with protocol.')
@click.option(u'--user', prompt=True, help=u'Login user.')
@click.option(u'--password', prompt=True, hide_input=True, help=u'Login password.')
def login(ctx, host, user, password):
    """Login to an Azkaban server"""
    __login(ctx, host, user, password)

@click.command(u'logout')
def logout():
    """Logout from Azkaban session"""
    __logout()

@click.command(u'upload')
@click.pass_context
@click.argument(u'path', type=click.STRING)
@click.option(u'--project', type=click.STRING, help=u'Project name in Azkaban, default value is the dirname specified in path argument.')
@click.option(u'--zip-name', type=click.STRING, help=u'If you wanna specify Zip file name that will be generated and uploaded to Azkaban. Default value is project name.')
def upload(ctx, path, project, zip_name):
    """Generates a zip of path passed as argument and uploads it to Azkaban."""
    __upload(ctx, path, project, zip_name)

@click.command(u'schedule')
@click.pass_context
@click.argument(u'project', type=click.STRING)
@click.argument(u'flow', type=click.STRING)
@click.argument(u'cron', type=click.STRING)
def schedule(ctx, project, flow, cron):
    """Schedule a flow from a project with specified cron in quartz format"""
    __schedule(ctx, project, flow, cron)

@click.command(u'execute')
@click.pass_context
@click.argument(u'project', type=click.STRING)
@click.argument(u'flow', type=click.STRING)
def execute(ctx, project, flow):
    """Execute a flow from a project"""
    __execute(ctx, project, flow)

cli.add_command(login)
cli.add_command(logout)
cli.add_command(upload)
cli.add_command(schedule)
cli.add_command(execute)

# ----------------------------------------------------------------------------------------------------------------------
# Interface
# ----------------------------------------------------------------------------------------------------------------------

        
if __name__ == u'__main__':
    try:
        cli()

    except Exception as ex:
        logging.error(ex)

        sys.exit()

