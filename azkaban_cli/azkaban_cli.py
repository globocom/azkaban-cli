import logging
import click
import requests
import sys
import zipfile
import os
from azkaban import Azkaban

__version__ = u'0.1.1'

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return

    click.echo(u'Azkaban CLI v%s' % (__version__))
    ctx.exit()

def __login(ctx, host, user, password):
    azkaban = Azkaban(host)

    azkaban.login(user, password)

    ctx.obj[u'azkaban'] = azkaban

def __upload(ctx, path, project, zip_name):
    azkaban = ctx.obj[u'azkaban']

    azkaban.upload(path, project, zip_name)

def __schedule(ctx, project, flow, cron):
    azkaban = ctx.obj[u'azkaban']

    azkaban.schedule(project, flow, cron)

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
@click.option(u'--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True)
def cli():
    log_level = logging.INFO

    # log record format string
    format_string = u'%(asctime)s\t%(levelname)s\t%(message)s'

    # set default logging (to console)
    logging.basicConfig(level=log_level, format=format_string)
    
    ctx = click.get_current_context()

    ctx.obj = {}

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

