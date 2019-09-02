#!/usr/bin/env python3

"""
The MIT License (MIT)

Copyright (c) 2019 Johan Kanflo (github.com/kanflo)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from __future__ import print_function
import argparse
import sys
import requests

port = 27532

def die(msg):
    print("Error: %s" % msg)
    sys.exit(1)


def upload_firmware(args):
    try:
        image = open(args.image, mode = 'rb').read()
        headers = {'Content-Type': 'application/octet-stream'}
        if args.name:
            headers['name'] = args.name
        if args.platform:
            headers['platform'] = args.platform.lower()
        if args.type:
            headers['node_type'] = args.type.lower()
        if args.id:
            headers['node_id'] = args.id.lower()
        if args.hwrev:
            headers['hw_rev'] = args.hwrev.lower()

        url = 'http://%s:%d/firmware' % (args.host, port)
        r = requests.post(url = url, data = image, headers = headers)
        if r.status_code == 200:
            print("Success")
        elif r.status_code == 403:
            die("firmware already exists on server")

    except FileNotFoundError:
        die("failed open %s" % args.image)
    except requests.exceptions.ConnectionError:
        die("failed to connect to %s" % args.host)


def main():
    parser = argparse.ArgumentParser(description = 'Upload firmware to the OTA server') 
    parser.add_argument('-n', '--name', type = str, help = "Name of firmware")
    parser.add_argument('-p', '--platform', type = str, help = "Platform name")
    parser.add_argument('-t', '--type', type = str, help = "Node type")
    parser.add_argument('-i', '--id', type = str, help = "Node ID")
    parser.add_argument('-r', '--hwrev', type = str, help = "Hardware revision")
    parser.add_argument('-v', '--verbose', action = 'store_true', help = "Verbose communications")
    parser.add_argument('host', help = "OTA server name")
    parser.add_argument('image', help = "Firmware image")
    args, unknown = parser.parse_known_args()

    if len(unknown) > 0:
        die("unknown argument%s: %s" % ("s" if len(unknown) > 1 else "", ", ".join(unknown)))

    if not args.type and not args.id:
        die("you need to specify at least node type (-t) or node id (-i)")

    upload_firmware(args)

if __name__ == "__main__":
    main()
