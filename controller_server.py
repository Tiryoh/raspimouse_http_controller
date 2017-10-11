#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numbers
import json
import argparse
# import urlparse #for python2
# from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer #for python2
from urllib import parse as urlparse #for python3
from http.server import BaseHTTPRequestHandler, HTTPServer #for python3

def get_line_sensor_data():
    try:
        with open('/dev/rtlightsensor0','r') as f:
            return map(int, f.readline().split())
    except Exception as e:
        print(e)

def get_switch_input(swnum):
    try:
        with open('/dev/rtswitch'+str(swnum),'r') as f:
            return not(int(f.readline()))
    except Exception as e:
        print(e)

def set_motor_speed(left, right):
    try:
        with open('/dev/rtmotor_raw_l0','w') as lf, open('/dev/rtmotor_raw_r0','w') as rf:
            lf.write(str(int(left)))
            rf.write(str(int(right)))
    except Exception as e:
        print(e)

def set_motor_power(mode):
    try:
        with open('/dev/rtmotoren0','w') as f:
            f.write('1' if mode else '0')
    except Exception as e:
        print(e)

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
        self.wfile.write(body.encode('UTF-8'))
        # self.wfile.write(body)

    def do_POST(self):
        """
        ## sample commands
        ```
        curl -v -H "Accept: application/json" -H "Content-type: application/json" -X POST -d {JSON data} {URI}
        curl -X POST -d '{"1" : 0 , "2" : 0, "3" : 0, "4" : 0 , "5" : 0 }' http://192.168.111.90:8000\?angle
        ```
        """
        if not __debug__: print("POST method")
        uri = self.path
        uri_arg = urlparse.parse_qs(urlparse.urlparse(uri).query, keep_blank_values=True)

        body = self.rfile.read(int(self.headers["Content-Length"])).decode('UTF-8')
        try:
            data = json.loads(body)
            self.send_response(200)
        except Exception as e:
            print(e)
            self.send_response(416)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-type", "text/json")
        self.end_headers()

        try:
            if "motor_power" in uri_arg.keys():
                if "motor_power" in data.keys():
                    if not __debug__:
                        print("motor_power : ", data["motor_power"])
                    set_motor_power(data["motor_power"])
            else:
                if not __debug__:
                    print(data.keys())
                    if "motor" in data.keys():
                        print("motor_r : ", data["motor"]["r"])
                        print("motor_l : ", data["motor"]["l"])
                    if "motor_power" in data.keys():
                        print("motor_power : ", data["motor_power"])
                if "motor" in data.keys():
                    set_motor_speed(data["motor"]["l"], data["motor"]["r"])
                if "motor_power" in data.keys():
                    set_motor_power(data["motor_power"])
        except Exception as e:
            print(e)

def main():
    parser = argparse.ArgumentParser(description="usage:set JSON responce server port as '--port 5000' or '-p 5000'")
    parser.add_argument("-p", "--port", type=int, default=5000, help="define raspimouse controller's tcp port")
    args = parser.parse_args()

    httpd = HTTPServer(("", args.port), JsonResponsehandler)
    print("server running on port " + str(args.port))
    httpd.serve_forever()


if __name__ == "__main__":
    main()
