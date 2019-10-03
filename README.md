# Azkaban CLI
[![Build Status](https://travis-ci.com/globocom/azkaban-cli.svg?branch=master)](https://travis-ci.com/globocom/azkaban-cli)

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

```sh
$ azkaban --help
Usage: azkaban [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  add_permission        Add a group with permission in a project
  change_permission     Change a group permission in a project
  create                Create a new project
  delete                Delete a project
  execute               Execute a flow from a project
  fetch_flow_execution  Fetch a flow execution
  fetch_jobs_from_flow  Fetch jobs of a flow
  fetch_projects        Fetch all project from a user
  fetch_sla             Fetch the SLA from a schedule
  login                 Login to an Azkaban server
  logout                Logout from Azkaban session
  remove_permission     Remove group permission from a project
  schedule              Schedule a flow from a project with specified cron...
  unschedule            Unschedule a flow from a project
  upload                Generates a zip of path passed as argument and...
```

## Examples

### Making login (this login cache information and don't need to do again)

```sh
azkaban login --host https://azkaban.your_company.com
```

## Contribute

For development and contributing, please follow [Contributing Guide](https://github.com/globocom/azkaban-cli/blob/master/CONTRIBUTING.md) and ALWAYS respect the [Code of Conduct](https://github.com/globocom/azkaban-cli/blob/master/CODE_OF_CONDUCT.md)
