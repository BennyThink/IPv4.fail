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

from IPs import ip_query


class BaseHandler(web.RequestHandler):
    def data_received(self, chunk):
        pass


class IndexHandler(BaseHandler):
    executor = ThreadPoolExecutor(max_workers=20)

    @run_on_executor
    def run_request(self):
        if self.request.method == 'GET' and 'Mozilla' not in self.request.headers.get('User-Agent'):
            user_ip = self.request.headers.get("X-Real-IP", "") or self.request.remote_ip
            return '\nIP: %s  %s' % (user_ip, ip_query.simple_query(user_ip))
        else:
            return self.render_string('pages/index.html')

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
        ipv4 = ipv6 = None

        if not user_content:
            self.set_status(400)
            return {"status": "fail", "message": "need ip arguments."}

        if re.findall(r'[0-9]+(?:\.[0-9]+){3}', user_content):
            ipv4 = re.findall(r'[0-9]+(?:\.[0-9]+){3}', user_content)[0]
        elif re.findall(r'^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))'
                        r'|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|'
                        r'((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d))'
                        r'{3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})'
                        r'|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d))'
                        r'{3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|'
                        r'((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)'
                        r'(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}'
                        r'(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:'
                        r'((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d))'
                        r'{3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|'
                        r'((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)'
                        r'(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}'
                        r'(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:'
                        r'((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d))'
                        r'{3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|'
                        r'((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)'
                        r'(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\s*$', user_content):
            # TODO: IPv6
            ipv6 = user_content
        else:
            # TODO: AAAA
            try:
                self_server = dns.resolver.Resolver()
                query = self_server.query(user_content)
                for i in query.response.answer:
                    for x in i.items:
                        ipv4 = x.address
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

        # TODO: API format
        if ipv4:
            location = ip_query.simple_query(ipv4)
            resp = {"status": "success", "message": "success",
                    "IP": ipv4, "domain": "", "result": location}
            return resp
        if ipv6:
            pass

        try:
            location = ip_query.simple_query(ipv4)
            resp = {"status": "success", "message": "success",
                    "IP": ipv4, "domain": "", "result": location}
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
            tornado_server.start(None)

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
