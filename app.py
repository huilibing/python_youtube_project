from __future__ import unicode_literals
import os
import commands
import re
import sys
import glob
import tempfile
import shutil
import youtube_dl
from flask import Flask, render_template, request, send_file, redirect

app = Flask(__name__)


class TemporaryDirectory(object):
    """ Context manager to make and remove temporary folder to contain downloaded video """

    def __init__(self, directory):
        self.directory = directory

    def __enter__(self):
        self.name = tempfile.mkdtemp(dir=self.directory)
        return self.name

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self.name)


class MyLogger(object):
    """ logger object for youtube-dl """
    def __init__(self):
        self.download_error = None

    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        self.download_error = msg


def video_id(url):
    """ return string of video id from url if present """
    vid_id = re.search(r'\?v=(.+)', url)
    if vid_id:
        return vid_id.group(1)


def my_hook(d):
    """ check download status for debugging """
    status = d['status']
    if status == 'finished':
        print('Done downloading, now converting ...')


def valid_url(url):
    """ Returns true if valid youtube video url, false otherwise """
    if re.search(r'^http(s?)://www\.youtube\.com/watch\?v=(.+)', url):
        return True
    return False


@app.route('/', methods=['GET', 'POST'])
def hello():
    error = ""

    if request.method == 'POST':
        url = request.form['url']

        if valid_url(url):
            with TemporaryDirectory('videos') as temp_dir:
                my_logger = MyLogger()
                ydl_options = {
                    'outtmpl': temp_dir + '/%(id)s.%(ext)s',
                    'logger': my_logger,
                    'progress_hooks': [my_hook]
                }
                try:
                    with youtube_dl.YoutubeDL(ydl_options) as ydl:
                        ydl.download([url])
                except:
                    return render_template('index.html', error=my_logger.download_error)
                file_name = glob.glob(temp_dir + '/' + video_id(url) + '*')[0]
                return send_file(file_name, as_attachment=True)

        error = "Please enter a valid YouTube url"

    return render_template('index.html', error=error)
