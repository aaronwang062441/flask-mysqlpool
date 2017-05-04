#-*- coding: utf-8 -*-
import logging

from flask import Flask
from flask_mysqlpool import MySQLPool


logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config.from_pyfile('hello.cfg')
db = MySQLPool(app)


@app.route('/')
def index():
    conn = db.connection
    cur = conn.cursor()
    cur.execute('Select 1')
    rows = cur.fetchone()
    print rows
    cur.close()
    return 'OK'

if __name__ == '__main__':
    app.run()

