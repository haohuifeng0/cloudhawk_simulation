# -*- coding: utf-8 -*-
import logging
import os

import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import define, options

from handler.graphqlhandler import GraphiQLHandler, GQHandler
from libs.confhelper import ConfHelper

define('conf', default="./global.conf")
define('mode', default="INFO")
define('tracker', default=dict())


class Application(tornado.web.Application):
    def __init__(self, debug=False):
        handlers = [
            (r'/graphql', GQHandler, None, GQHandler.__name__),
            (r'/*', GraphiQLHandler, {'endpoint': '/graphql'})
        ]

        settings = dict(
            debug=debug,
        )

        tornado.web.Application.__init__(self, handlers, **settings)


def shutdown(server):
    try:
        # old version of tornado does not support stop
        if server:
            if hasattr(server, 'stop'):
                server.stop()
            tornado.ioloop.IOLoop.instance().stop
    except:
        pass


if __name__ == '__main__':
    tornado.options.parse_command_line()
    os.environ.setdefault("CONFIG_FILE", options.conf)

    if options.mode.lower() == "debug":
        debug_mode = True
    else:
        debug_mode = False

    http_server = None
    try:
        ConfHelper.load(options.conf)
        application = Application(debug=debug_mode)
        http_server = tornado.httpserver.HTTPServer(application, xheaders=True)

        http_server.listen(int(ConfHelper.LOCAL_CONF.port))
        logging.warning("[SERVER] running on: localhost:%s", ConfHelper.LOCAL_CONF.port)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        logging.error("Ctrl-C is pressed.")
    except:
        logging.exception("[SERVER] exit exception")
    finally:
        logging.warning("[SERVER] shutdown...")
        if http_server:
            shutdown(http_server)
        logging.warning("[SERVER] Stopped. Bye!")
