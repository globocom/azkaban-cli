# Azkaban CLI

CLI for Azkaban 3 API access and flow upload.

[![Build Status](https://travis-ci.com/globocom/azkaban-cli.svg?branch=master)](https://travis-ci.com/globocom/azkaban-cli)

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

Actvate your virtualenv and call ```azkaban```

```sh
$ azkaban --help
Usage: azkaban [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  add_permission     Add a group with permission in a project
  change_permission  Change a group permission in a project
  create             Create a new project
  delete             Delete a project
  execute            Execute a flow from a project
  fetch_projects     Fetch all project from a user
  login              Login to an Azkaban server
  logout             Logout from Azkaban session
  remove_permission  Remove a group permission from a project
  schedule           Schedule a flow from a project with specified cron in...
  unschedule         Unschedule a flow from a project
  upload             Generates a zip of path passed as argument and uploads...
```

## Examples

### Making login (this login cache information and don't need to do again)

```sh
azkaban login --host https://azkaban.your_company.com
```

## Developing

```sh
### Install package in editable mode
pip install -e .
```

```sh
### Release package to pypi
### Update version in version.py before running this command
make release
```
