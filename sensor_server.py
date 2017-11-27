#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import argparse
# from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer #for python2
from http.server import BaseHTTPRequestHandler, HTTPServer

def get_line_sensor_data():
    with open('/dev/rtlightsensor0','r') as f:
        return map(int, f.readline().split())

def get_switch_input(swnum):
    with open('/dev/rtswitch'+str(swnum),'r') as f:
        return int(not(int(f.readline())))

class JsonResponsehandler(BaseHTTPRequestHandler):
    def __init__(self, *args):
        BaseHTTPRequestHandler.__init__(self, *args)

    def do_GET(self):
        left_end, left, right, right_end = get_line_sensor_data()
        switch = []
        for i in range(3):
            switch.append(get_switch_input(i))
        sensor_dict = {
            "line sensor": {
                "0": left_end,
                "1": left,
                "2": right,
                "3": right_end
            },
            "switch": {
                "0": switch[0],
                "1": switch[1],
                "2": switch[2],
             }
        }
        body = json.dumps(sensor_dict)
        self.send_response(200)
        self.send_header("Content-type", "text/json")
        self.send_header("Content-length", len(body))
        self.end_headers()
        self.wfile.write(body.encode("UTF-8"))
        # self.wfile.write(body)

def main():
    parser = argparse.ArgumentParser(description="usage:set JSON responce server port as '--port 5000' or '-p 5000'")
    parser.add_argument("-p", "--port", type=int, default=5000, help="define raspimouse controller's tcp port")
    args = parser.parse_args()

    server = HTTPServer(("", args.port), JsonResponsehandler)
    print("server running on port " + str(args.port))
    server.serve_forever()


if __name__ == '__main__':
    main()
