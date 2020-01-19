# -*- coding: utf-8 -*-
from tornado.web import HTTPError


class AppError(HTTPError):

    def __init__(self, status, data=None, message=None,
                 log_message=None, *args, **kwargs):
        if message is None:
            message = MESSAGE[status] \
                if status in MESSAGE else "Unknown status."
        super(AppError, self).__init__(200, reason=message,
                                       log_message=log_message,
                                       *args, **kwargs)
        self.app_status_code = status
        self.data = data


def fmt_response(code):
    return code, MESSAGE[code]


# 请求被成功响应
OK = 200
# 请求格式错误，参数错误
ILLEGAL_FORMAT = 400
# 服务器错误
SERVER_ERROR = 500

TRACKER_EXISTS = 600
TRACKER_NOT_EXISTS = 700

MESSAGE = {
    OK: u"Operation is successful.",
    ILLEGAL_FORMAT: u"Invalid request data format.",
    SERVER_ERROR: u"Server error.",
    TRACKER_EXISTS: u'Tracker is already exists',
    TRACKER_NOT_EXISTS: u'Tracker is not exists',
}
