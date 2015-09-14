from __future__ import unicode_literals
import os
import commands
import re
import sys
import glob
import youtube_dl
from flask import Flask, render_template, request, send_file

app = Flask(__name__)


def video_id(url):
    """return string of video id from url; null if non-existent"""
    vid_id = re.search(r'\?v=(.+)', url)
    if vid_id:
        return vid_id.group(1)


def remove_file(file_name):
    """ remove file if exists """
    if os.path.exists(file_name):
        cmd = 'rm ' + file_name
        commands.getoutput(cmd)


def zip_file(file_name, zip_name):
    """ zip file file_name to zip_name file"""
    if os.path.exists(file_name):
        cmd = 'zip -j ' + zip_name + ' ' + file_name
        commands.getoutput(cmd)



@app.route('/', methods=['GET', 'POST'])
def hello():

    if request.method == 'POST':
        url = request.form['url']
        if url:
            ydl_options = {}
            with youtube_dl.YoutubeDL(ydl_options) as ydl:
                ydl.download([url])
            file_name = glob.glob('*' + video_id(url) + '.*')[0]  # find file in directory containing video id
            return send_file(file_name, as_attachment=True)

    return render_template('index.html')