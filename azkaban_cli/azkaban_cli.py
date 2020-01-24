# -*- coding: utf-8 -*-

from __future__ import absolute_import
from bs4 import BeautifulSoup
import logging
import click
import json
import requests
import sys
import os
from azkaban_cli.azkaban import Azkaban
from azkaban_cli.exceptions import (
    NotLoggedOnError,
    LoginError,
    SessionError,
    UploadError,
    ScheduleError,
    FetchFlowsError,
    FetchJobsFromFlowError,
    FetchScheduleError,
    FetchSLAError,
    UnscheduleError,
    ExecuteError,
    CancelError,
    CreateError,
    FetchProjectsError,
    ChangePermissionError,
    AddPermissionError,
    RemovePermissionError,
    FetchFlowExecutionError,
    FetchFlowExecutionUpdatesError,
    FetchExecutionsOfAFlowError,
    FetchExecutionJobsLogError,
    ResumeFlowExecutionError,
    FetchRunningExecutionsOfAFlowError,
)
from azkaban_cli.__version__ import __version__

APP_NAME = "Azkaban CLI"

AZKABAN_CLI_PATH = os.getenv("AZKABAN_CLI_PATH", "")
if AZKABAN_CLI_PATH == "":
    HOME_PATH = os.path.expanduser("~")
    AZKABAN_CLI_PATH = os.path.join(HOME_PATH, ".azkaban_cli")

SESSION_JSON_PATH = os.path.join(AZKABAN_CLI_PATH, "user-session.json")


def __call_for_login(ctx):
    ctx.invoke(
        login, host=click.prompt("Host"), user=click.prompt("User"), password=click.prompt("Password", hide_input=True)
    )


def __login_expired(ctx):
    azkaban = ctx.obj[u"azkaban"]

    session = azkaban.get_logged_session()
    host = session["host"]
    user = session["user"]

    click.echo("Host: {}".format(host))
    click.echo("User: {}".format(user))
    ctx.invoke(login, host=host, user=user, password=click.prompt("Password", hide_input=True))


def login_required(function):
    def function_wrapper(ctx, *args, **kwargs):
        try:
            function(ctx, *args, **kwargs)
        except NotLoggedOnError:
            __call_for_login(ctx)
            function_wrapper(ctx, *args, **kwargs)
        except SessionError:
            __login_expired(ctx)
            function_wrapper(ctx, *args, **kwargs)

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
    azkaban = ctx.obj[u"azkaban"]

    try:
        azkaban.login(host, user, password)
        __save_logged_session(azkaban.get_logged_session())
        logging.info("Logged in successfully!")
    except (requests.exceptions.ConnectionError, requests.exceptions.MissingSchema) as e:
        logging.error("Could not connect to host: %s", str(e))
    except LoginError as e:
        logging.error("Login error: %s", str(e))


def __logout(ctx):
    azkaban = ctx.obj[u"azkaban"]

    azkaban.logout()
    __delete_logged_session()

    logging.info("Logged out")


@login_required
def __upload(ctx, path, project, zip_name):
    azkaban = ctx.obj[u"azkaban"]

    try:
        azkaban.upload(path, project, zip_name)
    except UploadError as e:
        logging.error(str(e))


@login_required
def __schedule(ctx, project, flow, cron, concurrent_option):
    azkaban = ctx.obj[u"azkaban"]

    try:
        azkaban.schedule(project, flow, cron, concurrentOption=concurrent_option)
    except ScheduleError as e:
        logging.error(str(e))


@login_required
def __unschedule(ctx, project, flow):
    azkaban = ctx.obj[u"azkaban"]

    try:
        flows = azkaban.fetch_flows(project)
        project_id = flows[u"projectId"]
        schedule = azkaban.fetch_schedule(project_id, flow)
        schedule_id = schedule[u"schedule"][u"scheduleId"]
        azkaban.unschedule(schedule_id)
    except FetchFlowsError as e:
        logging.error(str(e))
    except FetchScheduleError as e:
        logging.error(str(e))
    except UnscheduleError as e:
        logging.error(str(e))


@login_required
def __execute(ctx, project, flow, **execution_options):
    azkaban = ctx.obj[u'azkaban']

    try:
        azkaban.execute(project, flow, **execution_options)
    except ExecuteError as e:
        logging.error(str(e))


@login_required
def __cancel(ctx, execution_id):
    azkaban = ctx.obj[u"azkaban"]

    try:
        azkaban.cancel(execution_id)
    except CancelError as e:
        logging.error(str(e))


@login_required
def __create(ctx, project, description):
    azkaban = ctx.obj[u"azkaban"]
    try:
        azkaban.create(project, description)
    except CreateError as e:
        logging.error(str(e))


@login_required
def __delete(ctx, project):
    azkaban = ctx.obj[u"azkaban"]
    try:
        # To delete a project, all flows must be unscheduled. The first thing we do
        # is try fetching the project flows and unscheduling each one in succession.
        # Then, we attempt to delete the project. If no exception was raised, it means
        # the project was deleted successfully.
        # Note: the projectID is stored in Azkaban's internal database. Therefore,
        # fetching its flows will work even if the project has already been deleted.
        # An INFO log is printed to explain this scenario, since this command will say that
        # the project was deleted (even though it had already been deleted prior to this).

        flows = azkaban.fetch_flows(project)
        project_id = flows[u"projectId"]
        flow_ids = flows[u"flows"]

        if len(flow_ids) > 0:
            logging.debug("Will unschedule %d flows before deleting the project" % (len(flow_ids)))
        else:
            logging.info("Project %s has no flows or does not exist anymore!" % (project))

        for flow_id in flow_ids:
            flow_name = flow_id[u"flowId"]
            logging.debug("Unscheduling flow %s" % (flow_name))

            try:
                schedule = azkaban.fetch_schedule(project_id, flow_name)
            except:
                logging.debug("Schedule not found")
                schedule = None

            if schedule is not None:
                schedule_id = schedule[u"schedule"][u"scheduleId"]
                azkaban.unschedule(schedule_id)

            logging.debug("Done")

        azkaban.delete(project)

    except FetchScheduleError as e:
        logging.error(str(e))
    except FetchFlowsError as e:
        logging.error(str(e))
    except UnscheduleError as e:
        logging.error(str(e))
    else:
        logging.info("Project %s was successfully deleted" % (project))


def __parse_projects(text, user):
    def get_text(div):
        return div.find_all("a")[0].text

    def get_user(div):
        return div.find_all("p", {"class": "project-last-modified"})[0].text.split("\n")[-1].strip()[:-1]

    try:
        soup = BeautifulSoup(text, "html.parser")
        all_projects = soup.find_all("div", {"class": "project-info"})
        all_projects_for_user = [get_text(div) for div in all_projects if get_user(div) == user]
        logging.info("Found %d projects for user %s:" % (len(all_projects_for_user), user))

        for project in all_projects_for_user:
            logging.info("- %s" % (project))
    except Exception:
        raise FetchProjectsError("Error parsing response")


@login_required
def __fetch_projects(ctx, user):
    azkaban = ctx.obj[u"azkaban"]

    if not user:
        user = azkaban.get_logged_session().get(u"user")

    try:
        text = azkaban.fetch_projects()
        __parse_projects(text, user)
    except FetchProjectsError as e:
        logging.error(str(e))


def __log_sla(json):
    for settings in json.get("settings", []):
        logging.info("Settings")
        logging.info("\tId: %s" % (settings.get("id")))
        logging.info("\tDuration: %s" % (settings.get("duration")))
        logging.info("\tRule: %s" % (settings.get("rule")))
        logging.info("\tActions:")
        for action in settings.get("actions", []):
            logging.info("\t\t%s" % action)
    logging.info("Emails:")
    for email in json.get("slaEmails", []):
        logging.info("\t%s" % email)
    logging.info("Job Names:")
    for job_name in json.get("allJobNames", []):
        logging.info("\t%s" % job_name)


@login_required
def __fetch_sla(ctx, schedule):
    azkaban = ctx.obj[u"azkaban"]

    try:
        json = azkaban.fetch_sla(schedule)
        __log_sla(json)
    except FetchSLAError as e:
        logging.error(str(e))


@login_required
def __add_permission(ctx, project, group, admin, read, write, _execute, _schedule):
    azkaban = ctx.obj[u"azkaban"]
    try:
        azkaban.add_permission(
            project,
            group,
            permission_options={
                "admin": admin,
                "read": read,
                "write": write,
                "execute": _execute,
                "schedule": _schedule,
            },
        )
    except AddPermissionError as e:
        logging.error(str(e))


@login_required
def __remove_permission(ctx, project, group):
    azkaban = ctx.obj[u"azkaban"]
    try:
        azkaban.remove_permission(project, group)
    except RemovePermissionError as e:
        logging.error(str(e))


@login_required
def __change_permission(ctx, project, group, admin, read, write, _execute, _schedule):
    azkaban = ctx.obj[u"azkaban"]
    try:
        azkaban.change_permission(
            project,
            group,
            permission_options={
                "admin": admin,
                "read": read,
                "write": write,
                "execute": _execute,
                "schedule": _schedule,
            },
        )
    except ChangePermissionError as e:
        logging.error(str(e))


def __log_jobs(json):
    logging.info("Project: %s" % (json.get("project")))
    logging.info("Project Id: %s" % (json.get("projectId")))
    logging.info("Flow: %s" % (json.get("flow")))
    nodes = json.get("nodes", [])
    for node in nodes:
        logging.info("Node")
        logging.info("\tId: %s" % (node.get("id")))
        logging.info("\tType: %s" % (node.get("type")))
        _in = node.get("in")
        if _in:
            logging.info("\tIn")
            for i in _in:
                logging.info("\t- %s" % (i))


@login_required
def __fetch_jobs_from_flow(ctx, project, flow):
    azkaban = ctx.obj[u"azkaban"]

    try:
        json = azkaban.fetch_jobs_from_flow(project, flow)
        __parse_jobs(json)
    except FetchJobsFromFlowError as e:
        logging.error(str(e))


def __log_flow_execution(json):
    logging.info("Execution Id: %s" % (json.get("execid")))
    logging.info("Id: %s" % (json.get("id")))
    logging.info("Nested Id: %s" % (json.get("nestedId")))
    logging.info("Project: %s" % (json.get("project")))
    logging.info("Project Id: %s" % (json.get("projectId")))
    logging.info("Flow Id: %s" % (json.get("flowId")))
    logging.info("Flow: %s" % (json.get("flow")))
    logging.info("Type: %s" % (json.get("type")))
    logging.info("Update time: %s" % (json.get("updateTime")))
    logging.info("Submit user: %s" % (json.get("submitUser")))
    logging.info("Attempt: %s" % (json.get("attempt")))
    logging.info("Submit time: %s" % (json.get("submitTime")))
    logging.info("Start time: %s" % (json.get("startTime")))
    logging.info("End time: %s" % (json.get("endTime")))
    logging.info("Status: %s" % (json.get("status")))
    nodes = json.get("nodes", [])
    for node in nodes:
        logging.info("Node")
        logging.info("\tId: %s" % (node.get("id")))
        logging.info("\tNested Id: %s" % (node.get("nestedId")))
        logging.info("\tType: %s" % (node.get("type")))
        logging.info("\tAttempt: %s" % (node.get("attempt")))
        _in = node.get("in", [])
        if _in:
            logging.info("\tIn")
            for i in _in:
                logging.info("\t- %s" % (i))
        logging.info("\tUpdate time: %s" % (node.get("updateTime")))
        logging.info("\tStart time: %s" % (node.get("startTime")))
        logging.info("\tEnd time: %s" % (node.get("endTime")))
        logging.info("\tStatus: %s" % (node.get("status")))


@login_required
def __fetch_flow_execution(ctx, execution_id):
    azkaban = ctx.obj[u"azkaban"]

    try:
        json = azkaban.fetch_flow_execution(execution_id)
        __log_flow_execution(json)
    except FetchFlowExecutionError as e:
        logging.error(str(e))


def __log_flow_execution_updates(json):
    logging.info("Id: %s" % (json.get("id")))
    logging.info("Start time: %s" % (json.get("startTime")))
    logging.info("Attempt: %s" % (json.get("attempt")))
    logging.info("Status: %s" % (json.get("status")))
    logging.info("Update time: %s" % (json.get("updateTime")))
    nodes = json.get("nodes", [])
    for node in nodes:
        logging.info("Node")
        logging.info("\tAttempt: %s" % (node.get("attempt")))
        logging.info("\tStart time: %s" % (node.get("startTime")))
        logging.info("\tId: %s" % (node.get("id")))
        logging.info("\tUpdate time: %s" % (node.get("updateTime")))
        logging.info("\tStatus: %s" % (node.get("status")))
        logging.info("\tEnd time: %s" % (node.get("endTime")))
    logging.info("Flow: %s" % (json.get("flow")))
    logging.info("Flow end time: %s" % (json.get("endTime")))


@login_required
def __fetch_flow_execution_updates(ctx, execution_id, last_update_time):
    azkaban = ctx.obj[u"azkaban"]

    try:
        json = azkaban.fetch_flow_execution_updates(execution_id, last_update_time)
        __log_flow_execution_updates(json)
    except FetchFlowExecutionUpdatesError as e:
        logging.error(str(e))


def __log_executions_of_a_flow(json):
    logging.info("Total: %s" % (json.get("total")))
    logging.info("Project: %s" % (json.get("project")))
    logging.info("Length: %s" % (json.get("length")))
    logging.info("From: %s" % (json.get("from")))
    logging.info("Flow: %s" % (json.get("flow")))
    logging.info("ProjectId: %s" % (json.get("projectId")))
    executions = json.get("executions", [])
    for execution in executions:
        logging.info("StartTime: %s" % (json.get("startTime")))
        logging.info("SubmitUser: %s" % (json.get("submitUser")))
        logging.info("Status: %s" % (json.get("status")))
        logging.info("SubmitTime: %s" % (json.get("submitTime")))
        logging.info("Execution Id: %s" % (json.get("execId")))
        logging.info("Project Id: %s" % (json.get("projectId")))
        logging.info("End time: %s" % (json.get("endTime")))
        logging.info("Flow Id: %s" % (json.get("flowId")))


@login_required
def __fetch_executions_of_a_flow(ctx, project, flow, start, length):
    azkaban = ctx.obj[u"azkaban"]

    try:
        json = azkaban.fetch_executions_of_a_flow(project, flow, start, length)
        __log_executions_of_a_flow(json)
    except FetchExecutionsOfAFlowError as e:
        logging.error(str(e))


def __log_execution_job_log(json):
    logging.info("Data: %s" % (json.get("data")))
    logging.info("Offset: %s" % (json.get("offset")))
    logging.info("Length: %s" % (json.get("length")))


@login_required
def __fetch_execution_job_log(ctx, execution_id, jobid, offset, length):
    azkaban = ctx.obj[u"azkaban"]
    try:
        json = azkaban.fetch_execution_job_log(execution_id, jobid, offset, length)
        __log_execution_job_log(json)
    except FetchExecutionJobsLogError as e:
        logging.error(str(e))


@login_required
def __resume_flow_execution(ctx, execution_id):
    azkaban = ctx.obj[u"azkaban"]

    try:
        azkaban.resume_flow_execution(execution_id)
        logging.info("Flow successfully resumed")
    except ResumeFlowExecutionError as e:
        logging.error(str(e))


def __log_running_executions_of_a_flow(json):
    logging.info("ExecIds: %s" % (json.get("execIds")))


@login_required
def _fetch_running_executions_of_a_flow(ctx, project, flow):
    azkaban = ctx.obj[u"azkaban"]

    try:
        json = azkaban.fetch_running_executions_of_a_flow(ctx, project, flow)
        __log_running_executions_of_a_flow(json)
    except FetchRunningExecutionsOfAFlowError as e:
        logging.error(str(e))


# ----------------------------------------------------------------------------------------------------------------------
# Interface
# ----------------------------------------------------------------------------------------------------------------------


@click.group(chain=True)
@click.version_option(version=__version__, prog_name=APP_NAME)
def cli():
    # set default logging (to console)
    logging.basicConfig(level=logging.INFO, format=u"%(asctime)s\t%(levelname)s\t%(message)s")

    ctx = click.get_current_context()
    ctx.obj = {}

    azkaban = Azkaban()

    logged_session = __load_logged_session()

    if logged_session:
        azkaban.set_logged_session(**logged_session)

    ctx.obj["azkaban"] = azkaban


@click.command(u"login")
@click.pass_context
@click.option(u"--host", prompt=True, help=u"Azkaban hostname with protocol.")
@click.option(u"--user", prompt=True, help=u"Login user.")
@click.option(u"--password", prompt=True, hide_input=True, help=u"Login password.")
def login(ctx, host, user, password):
    """Login to an Azkaban server"""
    __login(ctx, host, user, password)


@click.command(u"logout")
@click.pass_context
def logout(ctx):
    """Logout from Azkaban session"""
    __logout(ctx)


@click.command(u"upload")
@click.pass_context
@click.argument(u"path", type=click.STRING)
@click.option(
    u"--project",
    type=click.STRING,
    help=u"Project name in Azkaban, default value is the dirname specified in path argument.",
)
@click.option(
    u"--zip-name",
    type=click.STRING,
    help=u"If you wanna specify Zip file name that will be generated and uploaded to Azkaban. Default value is project name.",
)
def upload(ctx, path, project, zip_name):
    """Generates a zip of path passed as argument and uploads it to Azkaban."""
    __upload(ctx, path, project, zip_name)


@click.command(u"schedule")
@click.pass_context
@click.argument(u"project", type=click.STRING)
@click.argument(u"flow", type=click.STRING)
@click.argument(u"cron", type=click.STRING)
@click.option(
    u"--concurrent-option",
    type=click.STRING,
    help=u"If you wanna specify concurrent option for scheduling flow. Possible values: ignore, pipeline, skip",
)
def schedule(ctx, project, flow, cron, concurrent_option):
    """Schedule a flow from a project with specified cron in quartz format"""
    __schedule(ctx, project, flow, cron, concurrent_option)


@click.command(u"unschedule")
@click.pass_context
@click.argument(u"project", type=click.STRING)
@click.argument(u"flow", type=click.STRING)
def unschedule(ctx, project, flow):
    """Unschedule a flow from a project"""
    __unschedule(ctx, project, flow)


@click.command(u"execute")
@click.pass_context
@click.argument(u'project', type=click.STRING)
@click.argument(u'flow', type=click.STRING)
@click.option(u'--disabled', type=click.STRING, help=u'A list of job names that should be disabled for this execution. Should be formatted as a JSON Array String. Example Values: ["job_name_1", "job_name_2", "job_name_N"]')
@click.option(u'--success-emails', type=click.STRING, help=u'A list of emails to be notified if the execution succeeds. All emails are delimitted with [,|;|\s+]. Example Values: foo@email.com,bar@email.com')
@click.option(u'--failure-emails', type=click.STRING, help=u'A list of emails to be notified if the execution fails. All emails are delimitted with [,|;|\s+]. Example Values: foo@email.com,bar@email.com')
@click.option(u'--success-emails-override/--no-success-emails-override', help=u'Whether uses system default email settings to override successEmails.')
@click.option(u'--failure-emails-override/--no-failure-emails-override', help=u'Whether uses system default email settings to override failureEmails.')
@click.option(u'--notify-failure-first/--no-notify-failure-first', help=u'Whether sends out email notifications as long as the first failure occurs.')
@click.option(u'--notify-failure-last/--no-notify-failure-last', help=u'Whether sends out email notifications as long as the last failure occurs.')
@click.option(u'--failure-action', type=click.STRING, help=u'If a failure occurs, how should the execution behaves. Possible Values: finishCurrent, cancelImmediately, finishPossible')
@click.option(u'--concurrent-option', type=click.STRING, help=u'If you wanna specify concurrent option for scheduling flow. Possible values: ignore, pipeline, skip')
def execute(ctx, project, flow, disabled, success_emails, failure_emails,
            success_emails_override, failure_emails_override, notify_failure_first,
            notify_failure_last, failure_action, concurrent_option):
    """Execute a flow from a project"""

    execution_options = {
        'disabled': disabled,
        'successEmails': success_emails,
        'failureEmails': failure_emails,
        'successEmailsOverride': success_emails_override,
        'failureEmailsOverride': failure_emails_override,
        'notifyFailureFirst': notify_failure_first,
        'notifyFailureLast': notify_failure_last,
        'failureAction': failure_action,
        'concurrentOption': concurrent_option,
    }
    __execute(ctx, project, flow, **execution_options)


@click.command(u"cancel")
@click.pass_context
@click.argument(u"execution_id", type=click.STRING)
def cancel(ctx, execution_id):
    """Cancel a flow execution"""
    __cancel(ctx, execution_id)


@click.command(u"create")
@click.pass_context
@click.argument(u"project", type=click.STRING)
@click.argument(u"description", type=click.STRING)
def create(ctx, project, description):
    """Create a new project"""
    __create(ctx, project, description)


@click.command(u"delete")
@click.pass_context
@click.argument(u"project", type=click.STRING)
def delete(ctx, project):
    """Delete a project"""
    __delete(ctx, project)


@click.command(u"fetch_projects")
@click.pass_context
@click.option(u"--user", type=click.STRING, required=False, help=u"Azkaban user to fetch projects from")
def fetch_projects(ctx, user):
    """Fetch all project from a user"""
    __fetch_projects(ctx, user)


@click.command(u"fetch_sla")
@click.pass_context
@click.argument(u"schedule", type=click.STRING)
def fetch_sla(ctx, schedule):
    """Fetch the SLA from a schedule"""
    __fetch_sla(ctx, schedule)


@click.command(u"add_permission")
@click.pass_context
@click.argument(u"project", type=click.STRING)
@click.argument(u"group", type=click.STRING)
@click.option(
    "--admin", "-a", "_admin", required=False, help=u"The group has admin rights in the project", is_flag=True
)
@click.option("--read", "-r", "_read", required=False, help=u"The group can read the project", is_flag=True)
@click.option("--write", "-w", "_write", required=False, help=u"The group can write on the project", is_flag=True)
@click.option(
    "--execute", "-e", "_execute", required=False, help=u"The group can execute on the project", is_flag=True
)
@click.option(
    "--schedule", "-s", "_schedule", required=False, help=u"The group can schedule on the project", is_flag=True
)
def add_permission(ctx, project, group, _admin, _read, _write, _execute, _schedule):
    """Add a group with permission in a project"""
    __add_permission(ctx, project, group, _admin, _read, _write, _execute, _schedule)


@click.command(u"remove_permission")
@click.pass_context
@click.argument(u"project", type=click.STRING)
@click.argument(u"group", type=click.STRING)
def remove_permission(ctx, project, group):
    """Remove group permission from a project"""
    __remove_permission(ctx, project, group)


@click.command(u"change_permission")
@click.pass_context
@click.argument(u"project", type=click.STRING)
@click.argument(u"group", type=click.STRING)
@click.option(
    "--admin", "-a", "_admin", required=False, help=u"The group has admin rights in the project", is_flag=True
)
@click.option("--read", "-r", "_read", required=False, help=u"The group can read the project", is_flag=True)
@click.option("--write", "-w", "_write", required=False, help=u"The group can write on the project", is_flag=True)
@click.option(
    "--execute", "-e", "_execute", required=False, help=u"The group can execute on the project", is_flag=True
)
@click.option(
    "--schedule", "-s", "_schedule", required=False, help=u"The group can schedule on the project", is_flag=True
)
def change_permission(ctx, project, group, _admin, _read, _write, _execute, _schedule):
    """Change a group permission in a project"""
    __change_permission(ctx, project, group, _admin, _read, _write, _execute, _schedule)


@click.command(u"fetch_jobs_from_flow")
@click.pass_context
@click.argument(u"project", type=click.STRING)
@click.argument(u"flow", type=click.STRING)
def fetch_jobs_from_flow(ctx, project, flow):
    """Fetch jobs of a flow"""
    __fetch_jobs_from_flow(ctx, project, flow)


@click.command(u"fetch_flow_execution")
@click.pass_context
@click.argument(u"execution_id", type=click.STRING)
def fetch_flow_execution(ctx, execution_id):
    """Fetch a flow execution"""
    __fetch_flow_execution(ctx, execution_id)


@click.command(u"fetch_executions_of_a_flow")
@click.pass_context
@click.argument(u"project", type=click.STRING)
@click.argument(u"flow", type=click.STRING)
@click.argument(u"start", type=click.INT, default=0)
@click.argument(u"length", type=click.INT, default=3)
def fetch_executions_of_a_flow(ctx, project, flow, start, length):
    """Fetch executions of a flow"""
    __fetch_executions_of_a_flow(ctx, project, flow, start, length)


@click.command(u"fetch_flow_execution_updates")
@click.pass_context
@click.argument(u"execution_id", type=click.STRING)
@click.option(
    "-lt",
    "last_update_time",
    type=click.STRING,
    default=u"-1",
    help=u"The criteria to filter by last update time",
    show_default=True,
)
def fetch_flow_execution_updates(ctx, execution_id, last_update_time):
    """Fetch flow execution updates"""
    __fetch_flow_execution_updates(ctx, execution_id, last_update_time)


@click.command(u"fetch_execution_job_log")
@click.pass_context
@click.argument(u"execution_id", type=click.STRING)
@click.argument(u"jobid", type=click.STRING)
@click.argument(u"offset", type=click.STRING)
@click.argument(u"length", type=click.STRING)
def fetch_execution_job_log(ctx, execution_id, jobid, offset, length):
    """Fetch flow execution job logs"""
    __fetch_execution_job_log(ctx, execution_id, jobid, offset, length)


@click.command(u"fetch_running_executions_of_a_flow")
@click.pass_context
@click.argument(u"project", type=click.STRING)
@click.argument(u"flow", type=click.STRING)
def fetch_running_executions_of_a_flow(ctx, project, flow):
    """ Fetch running executions of a flow"""
    _fetch_running_executions_of_a_flow(ctx, project, flow)


cli.add_command(login)
cli.add_command(logout)
cli.add_command(upload)
cli.add_command(schedule)
cli.add_command(unschedule)
cli.add_command(execute)
cli.add_command(cancel)
cli.add_command(create)
cli.add_command(delete)
cli.add_command(fetch_projects)
cli.add_command(fetch_sla)
cli.add_command(add_permission)
cli.add_command(remove_permission)
cli.add_command(change_permission)
cli.add_command(fetch_jobs_from_flow)
cli.add_command(fetch_flow_execution)
cli.add_command(fetch_flow_execution_updates)
cli.add_command(fetch_executions_of_a_flow)
cli.add_command(fetch_execution_job_log)
cli.add_command(fetch_running_executions_of_a_flow)

# Interface
# ----------------------------------------------------------------------------------------------------------------------


if __name__ == u"__main__":
    try:
        cli()

    except Exception as ex:
        logging.error(ex)

        sys.exit()
