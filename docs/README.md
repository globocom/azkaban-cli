# Documentation process

The methods who are beeen documented here are the ones that the user uses to interact with the api. Those methoods belogs to the Azkaban object described in ``azkaban.py``

## How to build the documentation locally

Make sure to have a ``virtualenv`` active and simply download Sphinx by typing ``pip install sphinx``. Once installed run ``make html`` within the folder with the ``Makefile`` to build your local version of the documentation inside ``build/html/index.html``.

## How to document a new method.

Once have added a new API call method inside azkaban.py and made sure to had written the appropriate docstring, go to the ``index.srt`` and add:

````
your method's name
-------------------

.. autoclass:: azkaban_cli.azkaban.Azkaban.your_method_name
````

to the end of the file.

It will automatically generate the documentation from that particular method based upon the docstring you wrote.

Keep in mind that sphinx interprets your documentation as python code, so any code lying outside a method or a class may be called by the sphinx builder including the import statements. You may have to pip install some of those before being able to correctly build your documentation file.