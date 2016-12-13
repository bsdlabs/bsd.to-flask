#
# BSD.to URL shortener
# Inspired by https://github.com/narenaryan/Pyster
#
# MIT License
# 
# Copyright (c) 2016 BSDLabs (bsdlabs.io)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 
import os
import re
import string
import base64
import sqlite3
import flask
from math import floor
from urlparse import urlparse

DBFILE = os.environ.get("BSDTO_DBFILE") or "/tmp/bsdto.db.sqlite3"
ID_EPOCH = 100

re_freebsd = re.compile(r"^http(s)?://(www\.)?freebsd\.org")

app = flask.Flask(__name__)


###############################################################################
# UTILS
###############################################################################

def base62_encode(num):
    base = string.digits + string.ascii_lowercase + string.ascii_uppercase
    r = num % 62
    res = base[r]
    q = floor(num / 62)
    while q:
        r = q % 62
        q = floor (q / 62)
        res = base[int(r)] + res
    return res


def base62_decode(num):
    base = string.digits + string.ascii_lowercase + string.ascii_uppercase
    limit = len(num)
    res = 0
    for i in range(limit):
        res = (62 * res) + base.find(num[i])
    return res


###############################################################################
# MODELS
###############################################################################

def db_init():
    sql = """
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL
        );
        """
    with sqlite3.connect(DBFILE) as conn:
        c = conn.cursor()
        c.execute(sql)


def db_insert(url):
    res = None
    sql = "INSERT INTO urls (url) VALUES (?)"
    with sqlite3.connect(DBFILE) as conn:
        c = conn.cursor()
        res = c.execute(sql, [url])
    return res.lastrowid


def db_select(url_id):
    res = None
    sql = "SELECT * FROM urls WHERE id = ?"
    with sqlite3.connect(DBFILE) as conn:
        c = conn.cursor()
        res = c.execute(sql, [url_id])
    return res.fetchone() if res else None


###############################################################################
# VIEWS
###############################################################################

@app.route("/", methods=["GET", "POST"])
def view_index():
    """ Render the base home page, and take the form POST, redirect to preview
        page. Needed to avoid rePOST on back buttons.
    """
    if flask.request.method == "POST":
        url = flask.request.form.get("url")
        if urlparse(url).scheme == "":
            url = "http://" + url

        # Limit to allowed domains only until we figure out auth
        if not re_freebsd.match(url):
            return flask.redirect(flask.url_for("view_preview_url", short="invalid"))

        url_id = db_insert(url)
        short = base62_encode(url_id + ID_EPOCH)
        return flask.redirect(flask.url_for("view_preview_url", short=short))

    return flask.render_template("index.html")


@app.route("/preview/<short>")
def view_preview_url(short):
    """ Render the URL preview page, which is the result of the shortening
        form action.
    """
    # Simple hack that doesn't require inter-page states, sessions, etc...
    if short == "invalid":
        return flask.render_template("index.html",
                                     invalid=True)

    preview_url = flask.url_for("view_url", short=short, _external=True)
    return flask.render_template("index.html",
                                 preview_url=preview_url)


@app.route("/<short>")
def view_url(short):
    """ Actual redirector from shortened URL to real URL. """
    url_id = base62_decode(short) - ID_EPOCH
    data = db_select(url_id)
    if data is None:
        flask.abort(404)
    goto_url = data[1]
    return flask.redirect(goto_url)


###############################################################################
# INIT
###############################################################################

db_init()

if __name__ == "__main__":
    app.run(debug=True)

