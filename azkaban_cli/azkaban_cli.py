import logging
import click
import requests
import sys
import zipfile
import os

__version__ = u'0.1.0'

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return

    click.echo(u'Azkaban CLI v%s' % (__version__))
    ctx.exit()

def __validate_host(host):
    valid_host = host

    while valid_host.endswith(u'/'):
        valid_host = valid_host[:-1]

    return valid_host


def __login(ctx, host, user, password):
    s = ctx.obj[u'session']    

    response = s.post(
        host, 
        data = {
            u'action': u'login',
            u'username': user,
            u'password': password
        }
    )

    response_json = response.json()

    valid_host = __validate_host(host)

    if u'error' in response_json.keys():
        error_msg = response_json[u'error']
        click.echo(error_msg)
    else:
        ctx.obj[u'azkaban_session_id'] = response_json['session.id']
        ctx.obj[u'logged'] = True
        ctx.obj[u'host'] = valid_host

        click.echo('Successfully logged in!')


def __zip_project(path, zip_name):
    absolute_project_path = os.path.abspath(path)

    # Where .zip will be created
    zip_path = absolute_project_path + '/' + zip_name

    # Create .zip
    zf = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)

    for root, dirs, files in os.walk(path):
        # ensure .zip root dir will be the path basename
        zip_root = root[len(path):]

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

def __upload(ctx, path, project, zip_name):
    if not ctx.obj[u'logged']:
        logging.error(u'You are not logged')
        exit(1)

    s = ctx.obj[u'session']
    host = ctx.obj[u'host']
    session_id = ctx.obj[u'azkaban_session_id']

    if not project:
        # define project name as basename
        project = os.path.basename(os.path.abspath(path))

    if not zip_name:
        # define zip name as project name
        zip_name = project
    
    if not zip_name.endswith('.zip'):
        zip_name = zip_name + '.zip'

    zip_path = __zip_project(path, zip_name)    

    zip_file = open(zip_path, 'rb')

    response = s.post(
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

    response_json = response.json()

    if u'error' in response_json.keys():
        error_msg = response_json[u'error']
        click.echo(error_msg)
    else:
        click.echo('Success uploading! Project %s updated to version %s' % (project, response_json[u'version']))

def __schedule(ctx, project, flow, cron):
    if not ctx.obj[u'logged']:
        logging.error(u'You are not logged')
        exit(1)

    s = ctx.obj[u'session']
    host = ctx.obj[u'host']
    session_id = ctx.obj[u'azkaban_session_id']

    response = s.post(
        host + '/schedule',
        data = {
            u'session.id': session_id,
            u'ajax': u'scheduleCronFlow',
            u'projectName': project,
            u'flow': flow,
            u'cronExpression': cron
        }
    )

    response_json = response.json()

    if u'error' in response_json.keys():
        error_msg = response_json[u'error']
        click.echo('Error scheduling: %s' % error_msg)
    else:
        click.echo('Success! %s' % (response_json[u'message']))
        click.echo('scheduleId: %s' % (response_json[u'scheduleId']))

def _upload(ctx, path, host, user, password, project, zip_name):
    __login(ctx, host, user, password)
    __upload(ctx, path, project, zip_name)

def _schedule(ctx, host, user, password, project, flow, cron):
    __login(ctx, host, user, password)
    __schedule(ctx, project, flow, cron)

# ----------------------------------------------------------------------------------------------------------------------
# Interface
# ----------------------------------------------------------------------------------------------------------------------

@click.group()
@click.option(u'--ca-root', type=click.Path(), default=os.getenv('AZKABAN_CA_ROOT'), help=u'Path to CA root for SSL requests.')
@click.option(u'--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True)
def cli(ca_root):
    log_level = logging.INFO

    # log record format string
    format_string = u'%(asctime)s\t%(levelname)s\t%(message)s'

    # set default logging (to console)
    logging.basicConfig(level=log_level, format=format_string)
    
    ctx = click.get_current_context()

    ctx.obj = {}

    # Session adding ca_root for SSL requests
    session = requests.Session()
    if ca_root:
        session.verify = ca_root

    ctx.obj[u'logged'] = False
    ctx.obj[u'session'] = session


@click.command(u'upload')
@click.pass_context
@click.argument(u'path', type=click.STRING)
@click.option(u'--host', prompt=True, help=u'Azkaban hostname with protocol.')
@click.option(u'--user', prompt=True, help=u'Login user.')
@click.option(u'--password', prompt=True, hide_input=True, help=u'Login password.')
@click.option(u'--project', type=click.STRING, help=u'Project name in Azkaban, default value is the dirname specified in path argument.')
@click.option(u'--zip-name', type=click.STRING, help=u'Zip file name that will be uploaded to Azkaban. Default value is project name.')
def upload(ctx, path, host, user, password, project, zip_name):
    _upload(ctx, path, host, user, password, project, zip_name)

@click.command(u'schedule')
@click.pass_context
@click.option(u'--host', prompt=True, help=u'Azkaban hostname with protocol.')
@click.option(u'--user', prompt=True, help=u'Login user.')
@click.option(u'--password', prompt=True, hide_input=True, help=u'Login password.')
@click.argument(u'project', type=click.STRING)
@click.argument(u'flow', type=click.STRING)
@click.argument(u'cron', type=click.STRING)
def schedule(ctx, host, user, password, project, flow, cron):
    _schedule(ctx, host, user, password, project, flow, cron)

cli.add_command(upload)
cli.add_command(schedule)

# ----------------------------------------------------------------------------------------------------------------------
# Interface
# ----------------------------------------------------------------------------------------------------------------------

        
if __name__ == u'__main__':
    try:
        cli()

    except Exception as ex:
        logging.error(ex)

        sys.exit()

