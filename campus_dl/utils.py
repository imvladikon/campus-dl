#!/usr/bin/env python
# -*- coding: utf-8 -*-
from functools import lru_cache

# This module contains generic functions, ideally useful to any other module
from six.moves.urllib.request import urlopen, Request
import sys

if sys.version_info[0] >= 3:
    import html
else:
    from six.moves import html_parser

    html = html_parser.HTMLParser()

import errno
import json
import logging
import os
import string
import subprocess
import requests


def get_filename_from_prefix(target_dir, filename_prefix):
    """
    Return the basename for the corresponding filename_prefix.
    """
    # This whole function is not the nicest thing, but isolating it makes
    # things clearer. A good refactoring would be to get the info from the
    # video_url or the current output, to avoid the iteration from the
    # current dir.
    filenames = os.listdir(target_dir)
    for name in filenames:  # Find the filename of the downloaded video
        if name.startswith(filename_prefix):
            basename, _ = os.path.splitext(name)
            return basename
    return None


def execute_command(cmd, args):
    """
    Creates a process with the given command cmd.
    """
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        if args.ignore_errors:
            logging.warn('External command error ignored: %s', e)
        else:
            raise e


def has_hebrew(initial_name):
    """
    Check if a string contains Hebrew characters
    """
    return any(u"\u0590" <= c <= u"\u05EA" for c in initial_name)


def directory_name(initial_name):
    """
    Transform the name of a directory into an ascii version
    """
    result = clean_filename(initial_name)
    return result if result != "" else "course_folder"


def get_page_contents(url, headers):
    """
    Get the contents of the page at the URL given by url. While making the
    request, we use the headers given in the dictionary in headers.
    """
    result = urlopen(Request(url, None, headers))
    try:
        # for python3
        charset = result.headers.get_content_charset(failobj="utf-8")
    except:
        charset = result.info().getparam('charset') or 'utf-8'
    return result.read().decode(charset)


def get_page_contents_as_json(url, headers):
    """
    Makes a request to the url and immediately parses the result asuming it is
    formatted as json
    """
    json_string = get_page_contents(url, headers)
    json_object = json.loads(json_string)
    return json_object


def remove_duplicates(orig_list, seen=set()):
    """
    Returns a new list based on orig_list with elements from the (optional)
    set seen and elements of orig_list removed.

    The function tries to maintain the order of the elements in orig_list as
    much as possible, only "removing" a given element if it appeared earlier
    in orig_list or if it was already a member of seen.

    This function does *not* modify any of its input parameters.
    """
    new_list = []
    new_seen = set(seen)

    for elem in orig_list:
        if elem not in new_seen:
            new_list.append(elem)
            new_seen.add(elem)

    return new_list, new_seen


# The next functions come from coursera-dl/coursera
def mkdir_p(path, mode=0o777):
    """
    Create subdirectory hierarchy given in the paths argument.
    """
    try:
        os.makedirs(path, mode)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class GoogleTranslate:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.make_header())
        self.session.verify = False
        self.url = "https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl={}&tl={}&q={}"

    def make_header(self):
        headers = dict()
        headers["Accept"] = "*/*"
        headers["Host"] = "clients5.google.com"
        headers["Connection"] = "keep-alive"
        headers["Upgrade-Insecure-Requests"] = "1"
        headers[
            "User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36"
        headers["Content-Encoding"] = "gzip"
        headers["Accept-Language"] = "en-US,en;q=0.9,ru;q=0.8,he;q=0.7"
        headers["Content-Type"] = "application/json; charset=UTF-8"
        return headers

    @lru_cache(maxsize=100)
    def translate(self, text, target='en', source='auto'):
        url = self.url.format(source, target, text)
        response = self.session.get(url)
        response.encoding = response.apparent_encoding
        json = response.json()
        try:
            # check if it's list of lists or list of strings
            if isinstance(json[0], list):
                return "\n".join(map(lambda p: p[0], json)).strip()
            else:
                return "\n".join(json).strip()
        except:
            pass
        return text


def clean_filename(s, minimal_change=False):
    """
    Sanitize a string to be used as a filename.
    If minimal_change is set to true, then we only strip the bare minimum of
    characters that are problematic for filesystems (namely, ':', '/' and
    '\x00', '\n').
    """
    if has_hebrew(s):
        s = GoogleTranslate().translate(s, target='en', source='he')

    # First, deal with URL encoded strings
    h = html
    s = h.unescape(s)

    # strip paren portions which contain trailing time length (...)
    s = (
        s.replace(':', '-')
        .replace('/', '-')
        .replace('\x00', '-')
        .replace('\n', '')
    )

    if minimal_change:
        return s

    s = s.replace('(', '').replace(')', '')
    s = s.rstrip('.')  # Remove excess of trailing dots

    s = s.strip().replace(' ', '_')
    valid_chars = '-_.()%s%s' % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)
    s = s.lower()
    return s