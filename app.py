from __future__ import unicode_literals
import os
import commands
import re
import sys
import glob
import youtube_dl
from flask import Flask, render_template, request, send_file

app = Flask(__name__)


class MyLogger(object):

    def __init__(self):
        self.download_error = None
        self.download_warning = None

    def debug(self, msg):
        pass

    def warning(self, msg):
        self.download_error = msg
        print msg

    def error(self, msg):
        self.download_error = msg
        print msg


def video_id(url):
    """ return string of video id from url; null if non-existent """
    vid_id = re.search(r'\?v=(.+)', url)
    if vid_id:
        return vid_id.group(1)


def my_hook(d):
    status = d['status']
    if status == 'downloading':
        print 'Download started'
    if status == 'finished':
        print('Done downloading, now converting ...')


def remove_files_in_directory(directory):
    """ remove files in directory if directory exists """
    if os.path.exists(directory):
        cmd = 'rm '
        for file_name in os.listdir(directory):
            cmd += os.path.join(directory, file_name)
        commands.getoutput(cmd)


def zip_file(file_name, zip_name):
    """ zip file file_name to zip_name file"""
    if os.path.exists(file_name):
        cmd = 'zip -j ' + zip_name + ' ' + file_name
        commands.getoutput(cmd)


def valid_url(url):
    """ Returns true if valid youtube video url, false otherwise """
    if re.search(r'^http(s?)://www\.youtube\.com/watch\?v=(.+)', url):
        return True
    return False


@app.route('/', methods=['GET', 'POST'])
def hello():
    error = ""
    remove_files_in_directory('videos')  # remove any already downloaded videos
    if request.method == 'POST':
        url = request.form['url']

        if valid_url(url):
            my_logger = MyLogger()
            ydl_options = {
                'outtmpl': 'videos/%(id)s.%(ext)s',
                'logger': my_logger,
                'progress_hooks': [my_hook]
            }

            try:
                with youtube_dl.YoutubeDL(ydl_options) as ydl:
                    ydl.download([url])
            except:
                return render_template('index.html', error=my_logger.download_error)

            file_name = glob.glob('videos/' + video_id(url) + '*')[0]  # find file in directory containing video id
            return send_file(file_name, as_attachment=True)

        error = "Please enter a valid YouTube url"

    return render_template('index.html', error=error)