# Azkaban CLI

Projeto criado para facilitar o uso do Azkaban, permitindo usar a API de forma fácil e fornecendo uma alternativa ao uso da interface gráfica.

## Instalação

Para instalar, crie uma virtualenv e instale o módulo via pip
```sh
# Criando a virtualenv
virtualenv azkaban_cli

# Ativando ela
source azkaban_cli/bin/activate

# Instalando o Azkaban CLI
pip install azkaban_cli --index-url=https://artifactory.globoi.com/artifactory/api/pypi/pypi-all/simple
```

## Uso

Feito a instalação, sempre que for usar, basta ativar a virtualenv e chamar o comando ```azkaban```

```sh
# Ativando a virtualenv
source azkaban_cli/bin/activate

# Usando a CLI
azkaban [OPTIONS] COMMAND [ARGS]

# Fazendo login no azkaban (Este comando efetua um cache da sua autenticação para evitar o login repetido)
azkaban login --host https://azkaban.globoi.com
```

## Exemplos

```sh
$ azkaban --help
Usage: azkaban [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  schedule  Schedule a flow from a project with specified...
  upload    Generates a zip of path passed as argument...
```

### Comandos

Todas os comandos e seu funcionamento podem ser obtidos usando o ```--help``` após o nome do comando

* **upload**: Recebe como argumento o path para o projeto. Se encarrega de gerar um arquivo ```.zip``` e de fazer o upload. Caso não seja especificado o nome do projeto, será usado o nome do diretório passado. 

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

* **schedule**: Recebe como argumento o nome do projeto, nome do flow e o cron do agendamento. 

```sh
$ azkaban schedule --help
Usage: azkaban schedule [OPTIONS] PROJECT FLOW CRON

  Schedule a flow from a project with specified cron

Options:
  --host TEXT  Azkaban hostname with protocol.
  --help       Show this message and exit.
```

## Desenvolvendo

Após o desenvolvimento, a geração de pacote deve ser feita atualizando a versão no ```setup.py``` e no módulo principal. Logo após, pode ser usado o comando do Makefile.

* make dist

Gera o pacote no diretório dist, permitindo a instalação local

```sh
# Gera o pacote no diretório dist
make dist

# Instala o pacote
pip install dist/<module-name>-<version>.tar.gz
```

* make release

Envia o pacote para o artifactory. Necessário alterar a versão em ```setup.py```. Se nunca tiver feito deploy para o artifactory, verificar a seção [Configurações para artifactory](#configurações-para-artifactory)

```sh
# Gera a dist e envia para o artifactory
make release
```

### Configurações para artifactory

[Google Doc](https://docs.google.com/document/d/1zgbYfdU0KPF3IeK9udVk7FKXqFCD8swhfXLSyzmyIIw)
