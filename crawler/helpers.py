import os

from math import log
from sys import stdout

import time


def get_width():
    return int(os.popen('stty size', 'r').read().split()[1])


def get_browser_headers():
    return {
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,tr;q=0.6',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
    }


def truncate(s, lenght):
    s = str(s)
    if len(s) > lenght:
        return s[:lenght - 3] + "..."
    return s


def show_progress(current, total, title, completed=False):
    width = min(get_width(), 150)
    title = "[%-30s]" % truncate(title, 30)
    step = int(log(total, 10)) + 1
    counter = "[%s/%s]" % (str(current).zfill(step), total)
    # width = [square_count] counter title
    # width = 1  + square_count + 1 + 1 + counter + 1 + title + 1
    # width = (counter + title + 5) + square_count
    # square_count = width - (counter + title + 4)
    square_count = width - (len(counter) + len(title) + 5)
    progress_count = int(square_count / total) * current
    progress = (progress_count * "#").ljust(square_count, " ")
    print("[%s] %s %s" % (progress, counter, title), end="\n" if completed else "\r")
    stdout.flush()
