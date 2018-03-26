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
```

Para fazer requests para o Azkaban, deve-se fornecer o AC raiz da globo.com. Ele está disponível no projeto, em [glb_ca_root/ca_root.pem](glb_ca_root/ca_root.pem). Existem duas formas de usar:

* Passando como uma option

```sh
azkaban --ca-root /path/to/ca_root.pem COMMAND [ARGS]
```

* Exportando como a variável de ambiente ```AZKABAN_CA_ROOT```

```sh
export AZKABAN_CA_ROOT=/path/to/ca_root.pem

azkaban COMMAND [ARGS]
```

### Funções

* #### upload

Recebe como argumento o path para o projeto. Se encarrega de gerar um arquivo ```.zip``` e de fazer o upload. Caso não seja especificado o nome do projeto, será usado o nome do diretório passado. 

Outras opções, descritas pelo ```--help```:

```sh
$ azkaban upload --help
Usage: azkaban upload [OPTIONS] PATH

Options:
  --host TEXT      Azkaban hostname with protocol.
  --user TEXT      Login user.
  --password TEXT  Login password.
  --project TEXT   Project name in Azkaban, default value is the dirname
                   specified in path argument.
  --zip-name TEXT  Zip file name that will be uploaded to Azkaban. Default
                   value is project name.
  --help           Show this message and exit.
```


## Desenvolvendo

Após o desenvolvimento, a geração de pacote deve ser feita atualizando a versão no ```setup.py``` e no módulo principal. Logo após, pode ser usado o comando do Makefile.

* #### make dist

Gera o pacote no diretório dist, permitindo a instalação local

```sh
# Gera o pacote no diretório dist
make dist

# Instala o pacote
pip install dist/<module-name>-<version>.tar.gz
```

* #### make release

Envia o pacote para o artifactory. Necessário alterar a versão em ```setup.py```. Se nunca tiver feito deploy para o artifactory, verificar a seção [Configurações para artifactory](#configuracoes-para-artifactory)

```sh
# Gera a dist e envia para o artifactory
make release
```

### Configurações para artifactory

[Google Doc](https://docs.google.com/document/d/1zgbYfdU0KPF3IeK9udVk7FKXqFCD8swhfXLSyzmyIIw)
