# Azkaban CLI
[![Build Status](https://img.shields.io/travis/com/globocom/azkaban-cli?style=flat-square&labelColor=black&logo=travis&logoColor=white?branch=master)](https://travis-ci.com/globocom/azkaban-cli)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

CLI for Azkaban 3 API access and flow upload.

## Install

Use virtualenv or conda env
```sh
### Building virtualenv
virtualenv azkaban_cli

### Activating virtualenv
source azkaban_cli/bin/activate

### Installing Azkaban CLI
pip install azkaban_cli
```

## Usage

Activate your virtualenv and call ```azkaban```

```
$ azkaban --help
Usage: azkaban [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  add_permission                      Add a group with permission in a project
  change_permission                   Change a group permission in a project
  create                              Create a new project
  delete                              Delete a project
  execute                             Execute a flow from a project
  cancel                              Cancel a flow execution
  fetch_running_executions_of_a_flow  Fetch the running executions of a flow
  fetch_flow_execution                Fetch a flow execution
  fetch_flow_execution_updates        Fetch flow execution updates
  fetch_execution_of_a_flow           Fetch all execution of a given flow
  fetch_jobs_from_flow                Fetch jobs of a flow
  fetch_execution_job_log             Fetches the correponding job logs
  fetch_projects                      Fetch all project from a user
  fetch_sla                           Fetch the SLA from a schedule
  login                               Login to an Azkaban server
  logout                              Logout from Azkaban session
  remove_permission                   Remove group permission from a project
  schedule                            Schedule a flow from a project with specified cron...
  unschedule                          Unschedule a flow from a project
  upload                              Generates a zip of path passed as argument and...
```

## Environment setting

User session files are saved by default in the directory "$HOME/.azkaban_cli" directory.
This directory can be changed setting the environment variable AZKABAN_CLI_PATH .

## Examples

### Making login (this login cache information and don't need to do again)

```sh
azkaban login --host https://azkaban.your_company.com
```

## Contribute

For development and contributing, please follow [Contributing Guide](https://github.com/globocom/azkaban-cli/blob/master/CONTRIBUTING.md) and ALWAYS respect the [Code of Conduct](https://github.com/globocom/azkaban-cli/blob/master/CODE_OF_CONDUCT.md)
