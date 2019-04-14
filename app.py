from flask import Flask, render_template, request, jsonify, session
from flaskext import mysql
from flask_cors import CORS, cross_origin
import pymysql
from typing import Any

app = Flask(__name__)
CORS(app)

db = pymysql.connect("localhost", "root", "", "thesis")

@app.route("/")
def hello():
   # return render_template('/home/marinos/testapp/www/index.html')
    return 'hello world'


@app.route('/login', methods=['POST'])
def login():


    data = request.get_json()
    print(data)
    cursor = db.cursor()
    email = data['email']
    password = data['pass']
    print(email)
    print(password)
    query="SELECT fname,lname,uid,cid FROM users WHERE email=%s AND password=%s;"
    cursor.execute(query,(email,password))

    rows=cursor.fetchall()
    print(len(rows))
    #print(rows[0])
    if len(rows)==0:
        return jsonify(fname="",lname="")
    else:
        payload = []
        content = {}
        for results in rows:
            content={'email':results[0], 'password':results[1]}
            fname=results[0]
            lname=results[1]
            uid=results[2]
            cid=results[3]
            content={}
        session['user']=uid
        print(session['user'])
        return jsonify(fname=fname,lname=lname,cid=cid)



@app.route('/signUp', methods=['POST'])
def signUp():

        data = request.get_json()
        print(data)
        cursor = db.cursor()
        email = data['email']
        password = data['pass']
        fname=data['firstName']
        lname=data['lastName']
        cid=data['type']
        points="0"
        print(email)
        print(password)
        query = "SELECT * FROM users WHERE email=%s;"
        cursor.execute(query, email)
        rows = cursor.fetchall()
        print(len(rows))
        # print(rows[0])
        if len(rows) == 0:
            query = """INSERT INTO users(email,password,fname,lname,cid,points)VALUES(%s,%s,%s,%s,%s,%s);"""
            cursor.execute(query, (email,password,fname,lname,int(cid),int(points)))
            db.commit()
            query = "SELECT * FROM users WHERE email=%s;"
            a=cursor.execute(query, email)
            print(a)
            rows = cursor.fetchall()
            print(rows[0])
            if len(rows) == 1:
                session['user']=rows[0]
                return jsonify(fname=fname, lname=lname,cid=cid)
            else:
                return jsonify(fname="", lname="")
        else:

            return jsonify(fname="", lname="")

@app.route('/points', methods=['POST','GET'])
def points():
    cursor = db.cursor()
    query = "SELECT points FROM users WHERE uid=%s;"
    cursor.execute(query, ("8"))
    rows = cursor.fetchall()
    return jsonify(points=rows[0])


if __name__ == "__main__":
    app.secret_key = 'super_secret_key'
    app.run(debug=True)