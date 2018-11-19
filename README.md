# Azkaban CLI

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

Actvate your virtualenv and call ```azkaban```

### Using CLI
azkaban [OPTIONS] COMMAND [ARGS]

### Making login (this login cache information and don't need to do again)

azkaban login --host https://azkaban.your_company.com
```

## Examples

```sh
$ azkaban --help
Usage: azkaban [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  execute   Execute a flow from a project
  login     Login to an Azkaban server
  logout    Logout from Azkaban session
  schedule  Schedule a flow from a project with specified...
  upload    Generates a zip of path passed as argument...
```

### Commands


```sh
$ azkaban upload --help
Usage: azkaban upload [OPTIONS] PATH

  Generates a zip of path passed as argument and uploads it to Azkaban.

Options:
  --host TEXT      Azkaban hostname with protocol.
  --project TEXT   Project name in Azkaban, default value is the dirname
                   specified in path argument.
  --zip-name TEXT  If you wanna specify Zip file name that will be generated
                   and uploaded to Azkaban. Default value is project name.
  --help           Show this message and exit.
```


```sh
$ azkaban schedule --help
Usage: azkaban schedule [OPTIONS] PROJECT FLOW CRON

  Schedule a flow from a project with specified cron

Options:
  --host TEXT  Azkaban hostname with protocol.
  --help       Show this message and exit.
```

## Developing

Update version in setup.py

```sh
### Make package on dist
make dist

### Install package
pip install dist/<module-name>-<version>.tar.gz
```

```sh
### Release package to pypi
make release
```
