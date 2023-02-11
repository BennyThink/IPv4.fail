#!/usr/bin/python
# coding: utf-8

__author__ = "Benny <benny@bennythink.com>"

import logging
import os
import re
from platform import uname

import dns.resolver
from concurrent.futures import ThreadPoolExecutor
from tornado import web, ioloop, httpserver, gen, options
from tornado.concurrent import run_on_executor
from tornado.log import enable_pretty_logging

from IPs import ip_query

enable_pretty_logging()


class BaseHandler(web.RequestHandler):
    def data_received(self, chunk):
        pass


class IndexHandler(BaseHandler):
    executor = ThreadPoolExecutor(max_workers=20)

    @run_on_executor
    def run_request(self):
        user_ip = self.request.headers.get("X-Real-IP", "") or self.request.remote_ip
        location = ip_query.simple_query(user_ip)
        if self.request.method == 'GET' and 'Mozilla' not in self.request.headers.get('User-Agent'):
            return '\nIP: %s  %s' % (user_ip, location)
        else:
            return self.render_string('pages/index.html', ip=user_ip, location=location)

    @gen.coroutine
    def get(self):
        res = yield self.run_request()
        self.write(res)

    @gen.coroutine
    def post(self):
        yield self.run_request()
        return self.redirect('/')


class IPQueryHandler(BaseHandler):
    executor = ThreadPoolExecutor(max_workers=20)

    @run_on_executor
    def run_request(self):
        if self.request.method == 'GET':
            user_input = self.get_query_argument('ip', None)
            return self.process(user_input)
        elif self.request.method == 'POST':
            user_input = self.get_argument('ip', None)
            return self.process(user_input)

    @gen.coroutine
    def get(self):
        res = yield self.run_request()
        self.write(res)

    @gen.coroutine
    def post(self):
        res = yield self.run_request()
        self.write(res)

    def process(self, user_content):
        ip = None

        if not user_content:
            self.set_status(400)
            return {"status": "fail", "message": "need ip arguments."}

        if re.findall(r'[0-9]+(?:\.[0-9]+){3}', user_content):
            ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', user_content)[0]
        elif ":" in user_content:
            ip = user_content
        else:
            # TODO: AAAA, CNAME
            try:
                self_server = dns.resolver.Resolver()
                query = self_server.query(user_content)
                for i in query.response.answer:
                    for x in i.items:
                        ip = x.address
            except Exception as e:
                self.set_status(400)
                resp = {"status": "fail", "message": str(e),
                        "IP": "", "domain": user_content, "result": ""}
                return resp

            # self_server = dns.resolver.Resolver()
            # self_server.nameservers = ['2620:0:ccc::2', '2400:da00::6666']
            # query = self_server.query(user_content, dns.rdatatype.AAAA)
            # for i in query.response.answer:
            #     for x in i.items:
            #         ipv6 = x.address

        if not ip:
            self.set_status(400)
            return {"status": "fail", "message": "Bad IP"}

        try:
            location = ip_query.simple_query(ip)
            resp = {"status": "success", "message": "success", "IP": ip, "result": location}
        except ValueError as e:
            self.set_status(400)
            resp = {"status": "fail", "message": str(e),
                    "IP": user_content, "domain": "", "result": ""}
        return resp


class RunServer:
    root_path = os.path.dirname(__file__)
    page_path = os.path.join(root_path, 'pages')

    handlers = [(r'/', IndexHandler),
                (r'/api/query', IPQueryHandler),
                (r'/static/(.*)', web.StaticFileHandler, {'path': root_path}),
                (r'/pages/(.*\.html|.*\.js|.*\.css|.*\.png|.*\.jpg)', web.StaticFileHandler, {'path': page_path}),
                ]
    settings = {
        "static_path": os.path.join(root_path, "static"),
        "cookie_secret": "5Li05DtnQewDZq1mDVB3HAAhFqUu2vD2USnqezkeu+M=",
        "xsrf_cookies": False,
        "autoreload": True
    }

    application = web.Application(handlers, **settings)

    @staticmethod
    def run_server(port=8888, host='127.0.0.1', **kwargs):
        tornado_server = httpserver.HTTPServer(RunServer.application, **kwargs, xheaders=True)
        tornado_server.bind(port, host)

        if uname()[0] == 'Windows':
            tornado_server.start()
        else:
            tornado_server.start(1)

        try:
            print('Server is running on http://{host}:{port}'.format(host=host, port=port))
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

    if not os.environ.get('dev'):
        logging.getLogger('tornado.access').disabled = True

    RunServer.run_server(port=p, host=h)
