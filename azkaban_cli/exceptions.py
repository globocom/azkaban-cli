# -*- coding: utf-8 -*-

class NotLoggedOnError(Exception):
    pass

class SessionError(Exception):
    pass

class LoginError(Exception):
    pass

class UploadError(Exception):
    pass

class ExecuteError(Exception):
    pass

class CancelError(Exception):
    pass

class ScheduleError(Exception):
    pass

class FetchFlowsError(Exception):
    pass

class FetchScheduleError(Exception):
    pass

class FetchSLAError(Exception):
    pass

class UnscheduleError(Exception):
    pass

class CreateError(Exception):
    pass

class FetchProjectsError(Exception):
    pass

class AddPermissionError(Exception):
    pass

class RemovePermissionError(Exception):
    pass

class ChangePermissionError(Exception):
    pass

class FetchFlowExecutionError(Exception):
    pass

class FetchJobsFromFlowError(Exception):
    pass

class FetchFlowExecutionUpdatesError(Exception):
    pass

class FetchExecutionsOfAFlowError(Exception):
    pass

class FetchExecutionJobsLogError(Exception):
    pass

class ResumeFlowExecutionError(Exception):
    pass

class FetchRunningExecutionsOfAFlowError(Exception):
    pass
