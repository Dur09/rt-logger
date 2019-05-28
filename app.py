import sqlite3
from sqlite3 import Error
import json
from flask import Flask, abort,request
from flask import render_template
from flask import g
from flask import make_response
import os.path
import StringIO
import csv
import datetime

db_file = '/site/rt-logger/db/rtLogger.db'

app = Flask(__name__,template_folder='/site/rt-logger/html/')

def create_connection():
    """
    create a database connection to the SQLite database
    specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except ValueError as e:
        print(e)
    return None

def is_json(request):
    if not request.json:
        print 'Not a JSON'
        abort(400)
        return False
    return True

#DB Connection
def connect_db():
    return sqlite3.connect(DATABASE)


#@app.before_request
#def before_request():
#    g.db = connect_db()


#@app.teardown_request
#def teardown_request(exception):
#    print "Tearing Down"
#    if hasattr(g, 'db'):
#        g.db.close()


#Data handling API's
@app.route('/')
def view():
    return render_template('index.html')

@app.route("/api/v1/getUsers",methods = ['GET'])
def getUsers():
    if request.method == 'GET':
        try:
            print "Fetching users from db"
            db = create_connection()
            cursor = db.cursor()
            cursor.execute('select * from at_users')
            users = cursor.fetchall()
            convert_json = {x[0]:x[1] for x in users}
            users_list = json.dumps(convert_json)
            return users_list
        except Error as e:
            print "Failed to fetch user list from table"
            print(e)
        return None
    else:
        return False

@app.route("/api/v1/storeData",methods = ['POST'])
def storeData():
    if request.method == 'POST':
        print request
        is_json(request)
        incomingData = request.data
        print incomingData
        dataDict = json.loads(incomingData)
        print dataDict
        try:
            rt_id = dataDict['rt_id']
            ts = dataDict['ts']
            created = datetime.datetime.now()
            user_id = dataDict['user_id']
            sev_type = dataDict['sev_type']
            db = create_connection()
            cursor = db.cursor()
            cursor.execute("INSERT INTO at_rt_log (rt_id, ts, created, user_id, sev_type) values (?,?,?,?,?)",(rt_id, ts, created, user_id, sev_type))
            db.commit()
        except ValueError, e:
            print 'Failed to Push Data to Db'
            return False

    return "1"

@app.route("/api/v1/fetchReport", methods = ['GET'])
def fetchReport():
    if request.method == 'GET':
        try:
            print "Fetching Report from db"
            db = create_connection()
            cursor = db.cursor()
            cursor.execute('select count(*), rt_id from at_rt_log where sev_type = "Severity-0"')
            sev0 = cursor.fetchall()
            cursor.execute('select count(*), rt_id from at_rt_log where sev_type = "Severity-1"')
            sev1 = cursor.fetchall()
            convert_json0 = {x[0]:x[1] for x in sev0}
            convert_json1 = {x[0]:x[1] for x in sev1}
            users_list = json.dumps(convert_json0)
            users_list = json.dumps(convert_json1)
            return users_list
        except Error as e:
            print "Failed to fetch user list from table"
            print(e)
        return None
    else:
        return False

if __name__ == '__main__':
   print "Opened database successfully";
   app.run(
       host="0.0.0.0",
       port=int("3000")
   )
