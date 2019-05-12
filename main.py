#!/usr/bin/python
# coding: utf-8

__author__ = "Benny <benny@bennythink.com>"

import os
import json
import logging
from platform import uname

from concurrent.futures import ThreadPoolExecutor
from socket import error
from tornado import web, ioloop, httpserver, gen, options
from tornado.concurrent import run_on_executor
from tornado.escape import utf8
from tornado.web import HTTPError


class BaseHandler(web.RequestHandler):
    def data_received(self, chunk):
        pass


class IndexHandler(BaseHandler):
    def get(self):
        self.render("pages/index.html")


class WeatherHandler(BaseHandler):
    executor = ThreadPoolExecutor(max_workers=20)

    @run_on_executor
    def run_request(self):
        """
        sign and return
        :return: hex and raw request in XML
        """
        # get parameter, compatibility with json


        if self.request.headers.get('Content-Type') == 'application/json' and self.request.body:
            data = json.loads(self.request.body)
            city = data.get('city')
            day = data.get('day')
        # return whole json.
        else:
            response = make_json(city)
        # set http code and response
        self.set_status(HTTP.get(response.get('code'), 418))
        return response

    @gen.coroutine
    def get(self):
        res = yield self.run_request()
        self.write(res)

    @gen.coroutine
    def post(self):
        res = yield self.run_request()
        self.write(res)


class RunServer:
    root_path = os.path.dirname(__file__)
    page_path = os.path.join(root_path, 'pages')

    handlers = [(r'/', IndexHandler),
                (r'/api/game', GameStatusHandler),
                (r'/api/web', WebStatusHandler),
                (r'/api/ss', SSStatusHandler),
                (r'/api/login', LoginHandler),
                (r'/static/(.*)', web.StaticFileHandler, {'path': root_path}),
                (r'/pages/(.*\.html|.*\.js|.*\.css|.*\.png|.*\.jpg)', web.StaticFileHandler, {'path': page_path}),
                ]
    settings = {
        "static_path": os.path.join(root_path, "static"),
        "cookie_secret": "5Li05DtnQewDZq1mDVB3HAAhFqUu2vD2USnqezkeu+M=",
        "xsrf_cookies": True,
        "autoreload": True
    }

    application = web.Application(handlers, **settings)

    @staticmethod
    def run_server(port=8888, host='127.0.0.1', **kwargs):
        tornado_server = httpserver.HTTPServer(RunServer.application, **kwargs)
        tornado_server.bind(port, host)

        if uname()[0] == 'Windows':
            tornado_server.start()
        else:
            tornado_server.start(None)

        try:
            print(f'Server is running on http://{host}:{port}')
            ioloop.IOLoop.instance().current().start()
        except KeyboardInterrupt:
            ioloop.IOLoop.instance().stop()
            print('"Ctrl+C" received, exiting.\n')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    options.define("p", default=6789, help="running port", type=int)
    options.define("h", default='127.0.0.1', help="listen address", type=str)
    options.parse_command_line()
    p = options.options.p
    h = options.options.h

    RunServer.run_server(port=p, host=h)
