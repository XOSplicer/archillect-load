#!/usr/bin/env python2

import sys
import os
import errno
import requests

ARCHILLECT_URL = "http://archillect.com/api/"
DEFAULT_FOLDER = "img"
DEFAULT_IMG_PREFIX = "archillect"
ALLOWED_FORMATS = ["jpg"]
LAST_NUM_FILE = "last"
DEFAULT_LINK = "archillect.jpg"
MAX_RETRIES = 30

def main():
    if len(sys.argv) > 3 or '--help' in sys.argv or '-h' in sys.argv:
        print 'Usage: {} [-h | --help] [-v | --verbose]'.format(sys.argv[0])
        exit(1)
    if not os.path.isfile(LAST_NUM_FILE):
        with open(LAST_NUM_FILE, 'w') as last_file:
            last_file.write('0')
    with open(LAST_NUM_FILE, 'r+') as last_file:
        num = int(last_file.read())
        retries = MAX_RETRIES
        while retries > 0:
            try:
                num = num + 1
                retries = retries - 1
                api_url = '{}{}'.format(ARCHILLECT_URL, num)
                log('calling API: {}'.format(api_url))
                api_req = requests.get(api_url)
                if not api_req.ok:
                    log('API call failed: {} {}'.format(api_req.url, api_req.reason))
                    continue
                api_req_json = api_req.json()
                if 'error' in api_req_json:
                    log('API call failed: {} {}'.format(api_req.url, api_req_json['error']))
                    continue
                if 'post' not in api_req_json \
                    or 'big' not in api_req_json["post"] \
                    or not isinstance(api_req_json['post']['big'], basestring):
                    log('API response invalid')
                    continue
                img_url = api_req_json["post"]["big"]
                extension = img_url.split('.')[-1]
                if extension not in ALLOWED_FORMATS:
                    log('Format not allowed: {}'.format(extension))
                    continue
                log("Loading imgage: {}".format(img_url))
                img_req = requests.get(img_url)
                if not img_req.ok:
                    log('Image request failed: {} {}'.format(img_req.url, img_req.reason))
                    continue
                img_name = '{}.{}.{}'.format(DEFAULT_IMG_PREFIX, num, extension)
                out_path = os.path.join(DEFAULT_FOLDER, img_name)
                if not os.path.exists(DEFAULT_FOLDER):
                    os.makedirs(DEFAULT_FOLDER)
                with open(out_path, 'wb') as out_file:
                    out_file.write(img_req.content)
                symlink_force(out_path, DEFAULT_LINK)
                last_file.seek(0)
                last_file.write("{}".format(num))
                last_file.truncate()
                break # FINISHED
            except requests.ConnectionError:
                log('failed connection, retry next')

def symlink_force(target, link_name):
    try:
        os.symlink(target, link_name)
    except OSError, e:
        if e.errno == errno.EEXIST:
            os.remove(link_name)
            os.symlink(target, link_name)
        else:
            raise e

def log(msg):
    if '-v' in sys.argv or '--verbose' in sys.argv:
        print msg

if __name__ == '__main__':
    main()