.. Azkaban CLI documentation master file, created by
   sphinx-quickstart on Thu Mar 14 14:47:18 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.



Azkaban CLI
===========


.. image:: https://travis-ci.com/globocom/azkaban-cli.svg?branch=master
   :target: https://travis-ci.com/globocom/azkaban-cli
   :alt: Build Status


CLI for Azkaban 3 API access and flow upload.

Installation
------------

Please virtualenv or conda env on this, example as follows

.. code-block:: sh

   ### Building virtualenv
   virtualenv azkaban_cli

   ### Activating virtualenv
   source azkaban_cli/bin/activate

   ### Installing Azkaban CLI
   pip install azkaban_cli

Usage
-----

Activate your virtualenv and call ``azkaban``

.. code-block:: sh

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

Examples
--------

Making Login
^^^^^^^^^^^^
This command will login cache information and then won't need to be run again


.. code-block:: sh

   azkaban login --host https://azkaban.your_company.com

Contribute
----------

For development and contributing, please follow `Contributing Guide <https://github.com/globocom/azkaban-cli/blob/master/CONTRIBUTING.md>`_ and ALWAYS respect the `Code of Conduct <https://github.com/globocom/azkaban-cli/blob/master/CODE_OF_CONDUCT.md>`_


API Methods
===========

login
-----
.. code-block:: sh
   
   classazkaban_cli.azkaban.Azkaban.login
   
Login command, intended to make the request to Azkaban and treat the response properly

This method validate the host, make the request to Azkaban, and evaluate the response. If host, user or password is wrong or could not connect to host, it returns false and do not change the host and session_id attribute from the class. If everything is fine, saves the new session_id and corresponding host as attributes in the class and returns True



- Parameters

  - **host** (str) - Azkaban Hostname

  - **user** (str) - Username to login

  - **password** (str) - Password from user
  

- Raises

  - **loginError** – when Azkaban api returns error in response


logout
------
.. code-block:: sh
   
   classazkaban_cli.azkaban.Azkaban.logout

Logout command, intended to clear the host, user and session_id attributes from the instance


upload
------
.. code-block:: sh
   
   classazkaban_cli.azkaban.Azkaban.upload

Upload command, intended to make the request to Azkaban and treat the response properly

This method receives a path to a directory that contains all the files that should be in the Azkaban project, zip this path (as Azkaban expects it zipped), make the upload request to Azkaban, deletes the zip that was created and evaluate the response.

If project name is not passed as argument, it will be assumed that the project name is the basename of the path passed. If zip name is not passed as argument, the project name will be used for the zip.

If project or path is wrong or if there is no session_id, it returns false. If everything is fine, returns True.

- Parameters

  - **path** (str) – path to be zipped and uploaded

  - **project** (str) – Project name on Azkaban, optional.

  - **zip_name** (str) – Zip name that will be created and uploaded, optional.


- Raises

  - **UploadError** – when Azkaban api returns error in response

create
------
.. code-block:: sh

   classazkaban_cli.azkaban.Azkaban.create
   
Create command, intended to make the request to Azkaban and treat the response properly.

This method receives the project name and the description, make the execute request to create the project and evaluate the response.

- Parameters

  - **project** (str) – Project name on Azkaban

  - **description** (str) – Description for the project


delete
------
.. code-block:: sh

   classazkaban_cli.azkaban.Azkaban.delete

Delete command, intended to make the request to Azkaban and treat the response properly.

This method receives the project name, make the execute request to delete the project and evaluate the response.

- Parameters

  - **project** (str) – Project name on Azkaban

add_permission
--------------
.. code-block:: sh

   classazkaban_cli.azkaban.Azkaban.add_permission
   
Add permission command, intended to make the request to Azkaban and treat the response properly.

This method receives the project name, the group name, and the permission options and execute request to add a group permission to the project and evaluate the response.

- Parameters

  - **project** (str) – Project name on Azkaban

  - **group** (str) – Group name on Azkaban

  - **permission_options** (Dictionary) – The group permissions in the project on Azkaban

change_permission
-----------------

.. code-block:: sh

   classazkaban_cli.azkaban.Azkaban.change_permission
   
Change permission command, intended to make the request to Azkaban and treat the response properly.

This method receives the project name, the group name, and the permission options and execute request to change a existing group permission in a project and evaluate the response.

- Parameters

  - **project** (str) – Project name on Azkaban

  - **group** (str) – Group name on Azkaban

  - **permission_options** (Dictionary) – The group permissions in the project on Azkaban

remove_permission
-----------------

.. code-block:: sh
   
   classazkaban_cli.azkaban.Azkaban.remove_permission
   
Remove permission command, intended to make the request to Azkaban and treat the response properly.

This method receives the project name and the group name and execute request to remove a group permission from the project and evaluate the response.

- Parameters

  - **project** (str) – Project name on Azkaban

  - **group** (str) – Group name on Azkaban

execute
-------
.. code-block:: sh

   classazkaban_cli.azkaban.Azkaban.execute
   
Execute command, intended to make the request to Azkaban and treat the response properly.

This method receives the project and the flow, make the execute request to execute the flow and evaluate the response.

If project or flow is wrong or if there is no session_id, it returns false. If everything is fine, returns True.

- Parameters

  - **project** (str) – Project name on Azkaban

  - **flow** (str) – Flow name on Azkaban

- Raises

  - **ExecuteError** – when Azkaban api returns error in response

fetch_projects
--------------
.. code-block:: sh

   classazkaban_cli.azkaban.Azkaban.fetch_projects

Fetch all projects command, intended to make the request to Azkaban and treat the response properly. This method makes the fetch projects request to fetch all the projects and evaluates the response.

fetch_sla
---------
.. code-block:: sh

   classazkaban_cli.azkaban.Azkaban.fetch_sla

Fetch SLA command, intended to make the request to Azkaban and treat the response properly. Given a schedule id, this API call fetches the SLA.

- Parameters

  - **schedule_id** (str) – Schedule ID on Azkaban (Find on fetch_schedule)

fetch_flow_execution
--------------------
.. code-block:: sh

   classazkaban_cli.azkaban.Azkaban.fetch_flow_execution
   
Fetch a flow execution command, intended to make the request to Azkaban and treat the response properly.

This method receives the execution id, makes the fetch a flow execution request to fetch the flow execution details and evaluates the response.

Returns the json response from the request.

- Parameters

  - **execution_id** (str) – Execution id on Azkaban

- Raises

  - **FetchFlowExecutionError** – when Azkaban api returns error in response

fetch_jobs_from_flow
--------------------
.. code-block:: sh

   classazkaban_cli.azkaban.Azkaban.fetch_jobs_from_flow
   
Fetch jobs of a flow command, intended to make the request to Azkaban and return the response.

This method receives the project name and flow id, makes the fetch jobs of a flow request to fetch the jobs of a flow and evaluates the response.

Returns the json response from the request.

- Parameters

  - **project** (str) – project name on Azkaban

  - **flow** (str) – flow id on Azkaban

- Raises

  - **FetchJobsFromFlowError** – when Azkaban api returns error in response

schedule
--------
.. code-block:: sh

   classazkaban_cli.azkaban.Azkaban.schedule
   
Schedule command, intended to make the request to Azkaban and treat the response properly.

This method receives the project, the flow, the cron expression in quartz format and optional execution options, make the schedule request to schedule the flow with the cron specified and evaluate the response.

If project, flow or cron is wrong or if there is no session_id, it returns false. If everything is fine, returns True.

- Parameters

  - **project** (str) – Project name on Azkaban

  - **flow** (str) – Flow name on Azkaban

  - **cron** (str) – Cron expression, in quartz format [Eg.: ‘0*/10*?**’ -> Every 10 minutes]

- Raises

  - **ScheduleError** – when Azkaban api returns error in response

unschedule
----------
.. code-block:: sh

   classazkaban_cli.azkaban.Azkaban.unschedule
   
Unschedule command, intended to make the request to Azkaban and treat the response properly.

This method receives the schedule id and optional execution options, makes the unschedule request to unschedule the flow and evaluates the response.

If schedule_id is wrong or there is no session_id, it returns false. If everything is fine, returns True.

- Parameters

  - **schedule_id** (str) – Schedule id on Azkaban

- Raises

  - **UnscheduleError** – when Azkaban api returns error in response



