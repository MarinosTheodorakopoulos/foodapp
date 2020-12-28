import pymysql
from flask import Flask, request, jsonify,  current_app
from flask_cors import CORS, cross_origin
from datetime import timedelta
from datetime import datetime
import haversine as hs
import jwt
from flask_mail import Mail, Message


app = Flask(__name__)
mail = Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'thesis@gmail.com'
app.config['MAIL_PASSWORD'] = '1234567890'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

cors = CORS(app, supports_credentials=True)
app.config['SECRET_KEY'] = 'the random string'
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

db = pymysql.connect("localhost", "root", "", "thesis")


# db = pymysql.connect("localhost", "root", "123456789", "thesis")

@app.route("/")
def hello():
    return 'hello world'


@app.route('/checkAuth', methods=['POST', 'GET'])
@cross_origin(supports_credentials=True)
def checkAuth():
    auth_headers = request.headers.get('Authorization', '').split()
    print(auth_headers[1])
    invalid_msg = 'error'
    valid_msg = "it's valid"
    if len(auth_headers) != 2:
        print(invalid_msg)
        return jsonify(invalid_msg), 401
    try:
        token = auth_headers[1]
        print(token)
        data1 = jwt.decode(token, current_app.config['SECRET_KEY'])
        print(data1)
        return jsonify(valid_msg), 200
    except jwt.InvalidTokenError as e:
        print(e)
        print("Invalid token - JWT library")
        return jsonify(invalid_msg), 401


@app.route('/login', methods=['POST', 'GET'])
@cross_origin()
def login():
    # session.pop('userId', None)

    data = request.get_json()
    print(data)
    cursor = db.cursor()
    email = data['email']
    password = data['pass']
    print(email)
    print(password)
    query = "SELECT fname,lname,uid,cid FROM users WHERE email=%s AND password=%s;"
    cursor.execute(query, (email, password))

    rows = cursor.fetchall()
    print(len(rows))
    # print(rows[0])
    if len(rows) == 0:
        return jsonify(fname="", lname="")
    else:
        payload = []
        content = {}
        query = "SELECT COUNT(uid) FROM bannedUsers WHERE uid=%s;"
        cursor.execute(query, (rows[0][2]))
        rows1 = cursor.fetchall()
        if rows1[0][0] > 1:
            return jsonify(fname="banned", lname="banned")
        for results in rows:
            # content={'email':results[0], 'password':results[1]}
            fname = results[0]
            lname = results[1]
            uid = results[2]
            cid = results[3]
            print(cid)
            # content={}
        # session['user']=uid
        # print(session['user'])
        token = jwt.encode({
            'sub': uid,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(minutes=640)},
            current_app.config['SECRET_KEY']

        )
        return jsonify({'token': token.decode('UTF-8'), 'cid':cid})


@app.route('/signUp', methods=['POST', 'GET'])
@cross_origin(supports_credentials=True)
def signUp():
    # session.run()
    # session.pop('userId', None)
    data = request.get_json()
    print(data)
    cursor = db.cursor()
    email = data['email']
    password = data['pass']
    fname = data['firstName']
    lname = data['lastName']
    cid = data['type']
    points = "0"
    print(email)
    print(password)
    query = "SELECT * FROM users WHERE email=%s;"
    cursor.execute(query, email)
    rows = cursor.fetchall()
    print(len(rows))
    # print(rows[0])
    if len(rows) == 0:
        query = "INSERT INTO users(email,password,fname,lname,cid,points)VALUES(%s,%s,%s,%s,%s,%s);"
        cursor.execute(query, (email, password, fname, lname, int(cid), int(points)))
        db.commit()
        query = "SELECT * FROM users WHERE email=%s;"
        a = cursor.execute(query, email)
        rows = cursor.fetchall()
        uid = rows[0][0]
        print(rows[0])
        if len(rows) == 1:
            token = jwt.encode({
                'sub': uid,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(minutes=640)},
                current_app.config['SECRET_KEY']

            )
            return jsonify({'token': token.decode('UTF-8')})
        else:
            return jsonify(fname="", lname="")
    else:

        return jsonify(fname="", lname="")


@app.route('/map', methods=['POST', 'GET'])
@cross_origin(supports_credentials=True)
def map():
    auth_headers = request.headers.get('Authorization', ' ').split()
    invalid_msg = 'error'
    try:
        token = auth_headers[1]
        print(token)
        data1 = jwt.decode(token, current_app.config['SECRET_KEY'])
        print(data1)
    except jwt.InvalidTokenError as e:
        print(e)
        print("Invalid token - JWT library")
        return jsonify(invalid_msg), 401
    data = request.get_json()
    print(data)
    cursor = db.cursor()
    lat = data['lat']
    lon = data['lon']
    address = data['addr']
    uid = data1['sub']
    query = "UPDATE users SET lon=%s, lat=%s , address=%s WHERE uid=%s;"
    cursor.execute(query, (lon, lat, address, uid))
    db.commit()
    query = "SELECT cid FROM users WHERE uid=%s;"
    cursor.execute(query, (uid))
    rows = cursor.fetchall()
    cid = rows[0][0]
    return jsonify(cid=cid)


@app.route('/points', methods=['POST', 'GET'])
def points():
    cursor = db.cursor()
    query = "SELECT points FROM users WHERE uid=%s;"
    cursor.execute(query, ("8"))
    rows = cursor.fetchall()
    return jsonify(points=rows[0])


@app.route('/insertfood', methods=['POST', 'GET'])
@cross_origin(supports_credentials=True)
def insertfood():
    auth_headers = request.headers.get('Authorization', '').split()
    invalid_msg = 'error'
    print(auth_headers)
    if len(auth_headers) != 2:
        print(invalid_msg)
        return jsonify(invalid_msg), 401
    try:
        token = auth_headers[1]
        print(token)
        data1 = jwt.decode(token, current_app.config['SECRET_KEY'])
        print(data1)
    except jwt.InvalidTokenError as e:
        print(e)
        print("Invalid token - JWT library")
        return jsonify(invalid_msg), 40
    print(data1['sub'])
    uid = data1['sub']
    data = request.get_json()
    print(data)
    cursor = db.cursor()
    #uid = data1['uid']
    portions = data['nofood']
    #datefrom = 0
    dateto = str(data['time'])
    print(dateto)
    dateTimeObj = datetime.now()
    cdate = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
    datefrom=str(cdate)
    print('Current Timestamp : ', datefrom)


    # cid=data['type']
    query = "INSERT INTO food(uid,portions,datefrom,dateto)VALUES(%s,%s,%s,%s);"
    cursor.execute(query, (uid, portions, datefrom, dateto))
    db.commit()
    query = "SELECT * FROM food;"
    a = cursor.execute(query)
    print(a)
    rows = cursor.fetchall()
    print(rows[0])
    if len(rows) == 0:
        return 'error'
    else:
        return 'success'


@app.route('/showUser', methods=['POST', 'GET'])
@cross_origin(supports_credentials=True)
def showUser():
    auth_headers = request.headers.get('Authorization', '').split()
    invalid_msg = 'error'
    print(auth_headers)
    if len(auth_headers) != 2:
        print(invalid_msg)
        return jsonify(invalid_msg), 401
    try:
        token = auth_headers[1]
        print(token)
        data = jwt.decode(token, current_app.config['SECRET_KEY'])
        print(data)
    except jwt.InvalidTokenError as e:
        print(e)
        print("Invalid token - JWT library")
        return jsonify(invalid_msg), 40
    print(data['sub'])
    uid = data['sub']
    cursor = db.cursor()
    query = "SELECT * FROM users WHERE uid=%s;"
    a = cursor.execute(query, uid)
    rows = cursor.fetchall()

    print(rows)
    return jsonify(email=rows[0][1], password=rows[0][2], fname=rows[0][3], lname=rows[0][4], cid=rows[0][5])


@app.route('/edit', methods=['POST', 'GET'])
@cross_origin(supports_credentials=True)
def edit():
    auth_headers = request.headers.get('Authorization', '').split()
    token = auth_headers[1]
    print(token)
    data1 = jwt.decode(token, current_app.config['SECRET_KEY'])
    data = request.get_json()
    print(data)
    cursor = db.cursor()
    points = 0
    email = data['email']
    password = data['pass']
    fname = data['firstName']
    lname = data['lastName']
    cid = data['type']
    uid = data1['sub']
    print(email)
    print(password)
    query = "UPDATE users SET email=%s,password=%s,fname=%s,lname=%s,cid=%s,points=%s WHERE uid=%s;"
    cursor.execute(query, (email, password, fname, lname, cid, points, uid))
    db.commit()
    return jsonify(cid=cid)


@app.route('/logout', methods=['POST', 'GET'])
@cross_origin(supports_credentials=True)
def logout():
    return "ok"


@app.route('/foodMap', methods=['POST', 'GET'])
@cross_origin()
def foodMap():
    auth_headers = request.headers.get('Authorization', '').split()
    token = auth_headers[1]
    print(token)
    data1 = jwt.decode(token, current_app.config['SECRET_KEY'])
    data = request.get_json()
    print(data)
    cursor = db.cursor()
    fid = data['fid']
    print(fid)
    query = "SELECT lat,lon FROM users,food WHERE users.uid=food.uid AND fid=%s;"
    #cursor.execute(query, fid)
    a = cursor.execute(query, fid)
    print(a)
    rows = cursor.fetchall()
    print(rows)
    return jsonify(rows)


@app.route('/showFood', methods=['POST', 'GET'])
@cross_origin(supports_credentials=True)
def showFood():
    auth_headers = request.headers.get('Authorization', '').split()
    invalid_msg = 'error'
    print(auth_headers)
    if len(auth_headers) != 2:
        print(invalid_msg)
        return jsonify(invalid_msg), 401
    try:
        token = auth_headers[1]
        print(token)
        data = jwt.decode(token, current_app.config['SECRET_KEY'])
        print(data)
    except jwt.InvalidTokenError as e:
        print(e)
        print("Invalid token - JWT library")
        return jsonify(invalid_msg), 40
    print(data['sub'])
    uid = data['sub']
    timestampNow = datetime.now().strftime("%y-%m-%d %H:%M:%S")
    # timestampNow=data['timestampNow']



    cursor = db.cursor()
    query = "SELECT * FROM users WHERE users.uid=%s;"
    cursor.execute(query,uid)
    rows = cursor.fetchall()
    print(len(rows))
    print(rows)
    loc1 =(rows[0][7],rows[0][8])
    dateTimeObj = datetime.now()
    cdate = dateTimeObj.strftime("%Y-%b-%d (%H:%M:%S.%f)")
    datefrom = str(cdate)
    query = "SELECT * FROM food,users WHERE users.uid=food.uid AND DATE(datefrom)<=DATE(%s);"
    cursor.execute(query,datefrom)
    rows1 = cursor.fetchall()
    rows2=[]
    for x in rows1:
        loc2 = (x[13], x[14])
        ms = hs.haversine(loc1, loc2)
        print(ms, 'km')
        if ms<=4.0:
            rows2.append(x)

    print(len(rows2))
    print(rows2)
    return jsonify(rows2)

@app.route('/showPortion', methods=['POST', 'GET'])
@cross_origin(supports_credentials=True)
def showPortion():
    auth_headers = request.headers.get('Authorization', '').split()
    invalid_msg = 'error'
    print(auth_headers)
    if len(auth_headers) != 2:
        print(invalid_msg)
        return jsonify(invalid_msg), 401
    try:
        token = auth_headers[1]
        print(token)
        data = jwt.decode(token, current_app.config['SECRET_KEY'])
        print(data)
    except jwt.InvalidTokenError as e:
        print(e)
        print("Invalid token - JWT library")
        return jsonify(invalid_msg), 40
    print(data['sub'])
    uid = data['sub']
    data1 = request.get_json()
    fid=data1['fid']
    print(fid)
    timestampNow = datetime.now().strftime("%y-%m-%d %H:%M:%S")
    # timestampNow=data['timestampNow']
    cursor = db.cursor()
    query = "SELECT * FROM food WHERE fid=%s;"
    cursor.execute(query ,fid)
    rows = cursor.fetchall()
    print(len(rows))
    print(rows)
    return jsonify(portions=rows[0][2])


@app.route('/takeportions', methods=['POST', 'GET'])
@cross_origin(supports_credentials=True)
def takeportions():
    auth_headers = request.headers.get('Authorization', '').split()
    invalid_msg = 'error'
    print(auth_headers)
    if len(auth_headers) != 2:
        print(invalid_msg)
        return jsonify(invalid_msg), 401
    try:
        token = auth_headers[1]
        print(token)
        data = jwt.decode(token, current_app.config['SECRET_KEY'])
        print(data)
    except jwt.InvalidTokenError as e:
        print(e)
        print("Invalid token - JWT library")
        return jsonify(invalid_msg), 40
    print(data['sub'])
    uid = data['sub']
    data1 = request.get_json()
    print(data)
    #uid = data['uid']
    fid = data1['fid']
    portions = data1['nofood']
    now = datetime.now()
    date = now.strftime("%d/%m/%Y %H:%M:%S")
    cursor = db.cursor()
    query = "INSERT INTO transaction(uid,fid,portions,date)VALUES(%s,%s,%s,%s);"

    cursor.execute(query, (uid, fid, portions, date))
    db.commit()


    return jsonify("ok")


@app.route('/history', methods=['POST', 'GET'])
@cross_origin(supports_credentials=True)
def history():
    auth_headers = request.headers.get('Authorization', '').split()
    invalid_msg = 'error'
    print(auth_headers)
    if len(auth_headers) != 2:
        print(invalid_msg)
        return jsonify(invalid_msg), 401
    try:
        token = auth_headers[1]
        print(token)
        data = jwt.decode(token, current_app.config['SECRET_KEY'])
        print(data)
    except jwt.InvalidTokenError as e:
        print(e)
        print("Invalid token - JWT library")
        return jsonify(invalid_msg), 40
    print(data['sub'])
    uid = data['sub']
    cursor = db.cursor()
    query="SELECT cid FROM users WHERE uid=%s;"
    cursor.execute(query, uid)
    rows = cursor.fetchall()
    if rows[0]==1:
        query = "SELECT c.fname,c.lname,t.trid,t.date, t.fid,t.portions, s.fname,s.lname, l.type FROM transaction as t, food as f, users as c, users as s, typeLocation as l WHERE t.fid=f.fid AND t.uid=c.uid AND f.uid=s.uid AND f.fid=l.tid AND t.uid=%s;"
    else:
        query = "SELECT c.fname,c.lname,t.trid,t.date, t.fid,t.portions, s.fname,s.lname, l.type FROM transaction as t, food as f, users as c, users as s, typeLocation as l WHERE t.fid=f.fid AND t.uid=c.uid AND f.uid=s.uid AND f.fid=l.tid AND s.uid=%s;"
    cursor.execute(query, uid)
    rows = cursor.fetchall()
    print(rows)
    return jsonify(rows)

@app.route('/transaction', methods=['POST', 'GET'])
@cross_origin(supports_credentials=True)
def transaction():
    auth_headers = request.headers.get('Authorization', '').split()

    invalid_msg = 'error'
    print(auth_headers)
    if len(auth_headers) != 2:
        print(invalid_msg)
        return jsonify(invalid_msg), 401
    try:
        token = auth_headers[1]
        print(token)
        data = jwt.decode(token, current_app.config['SECRET_KEY'])
        print(data)
    except jwt.InvalidTokenError as e:
        print(e)
        print("Invalid token - JWT library")
        return jsonify(invalid_msg), 40
    data1 = request.get_json()

    print(data['sub'])
    trid = data1['trid']
    print(trid)
    cursor = db.cursor()
    query = "SELECT c.fname,c.lname,t.trid,t.date, t.fid,t.portions, s.fname,s.lname, l.type FROM transaction as t, food as f, users as c, users as s, typeLocation as l WHERE t.fid=f.fid AND t.uid=c.uid AND f.uid=s.uid AND f.tid=l.tid AND t.trid=%s;"
    cursor.execute(query, trid)
    rows = cursor.fetchall()
    print(rows)
    return jsonify(rows)

@app.route('/rate', methods=['POST', 'GET'])
@cross_origin(supports_credentials=True)
def rate():
    data = request.get_json()
    print(data)
    trid = data['trid']
    rate = data['rate']
    cursor = db.cursor()
    query = "SELECT food.uid,transaction.uid FROM transaction INNER JOIN food ON transaction.fid=food.fid WHERE transaction.trid=%s;"
    cursor.execute(query, trid)
    rows = cursor.fetchall()
    print(len(rows))
    print(rows)
    query = "INSERT INTO rating(uid,rate)VALUES(%s,%s);"
    cursor.execute(query, (rows[0][0], rate))
    db.commit()
    query = "INSERT INTO rating(uid,rate)VALUES(%s,%s);"
    cursor.execute(query, (rows[0][1], rate))
    db.commit()

    return "ok"


@app.route('/myrating', methods=['POST', 'GET'])
@cross_origin(supports_credentials=True)
def myrating():
    auth_headers = request.headers.get('Authorization', '').split()
    invalid_msg = 'error'
    print(auth_headers)
    if len(auth_headers) != 2:
        print(invalid_msg)
        return jsonify(invalid_msg), 401
    try:
        token = auth_headers[1]
        print(token)
        data = jwt.decode(token, current_app.config['SECRET_KEY'])
        print(data)
    except jwt.InvalidTokenError as e:
        print(e)
        print("Invalid token - JWT library")
        return jsonify(invalid_msg), 40
    print(data['sub'])
    uid = data['sub']
    cursor = db.cursor()
    query = "SELECT fname, lname,AVG(rate),COUNT(rate) FROM users,rating WHERE users.uid=rating.uid AND users.uid=%s;"
    cursor.execute(query, uid)
    rows = cursor.fetchall()
    print(len(rows))
    print(rows)
    return jsonify(rows)


@app.route('/leaderboard', methods=['POST', 'GET'])
@cross_origin(supports_credentials=True)
def leaderboard():
    data = request.get_json()
    print(data)
    uid = data['uid']
    cursor = db.cursor()
    query = "SELECT fname, lname,AVG(rate),COUNT(rate) FROM users,rating WHERE users.uid=rating.uid GROUP BY rating.uid;"
    cursor.execute(query)
    rows = cursor.fetchall()
    print(len(rows))
    print(rows)
    return "ok"


@app.route('/report', methods=['POST', 'GET'])
@cross_origin(supports_credentials=True)
def report():
    auth_headers = request.headers.get('Authorization', '').split()
    invalid_msg = 'error'
    print(auth_headers)
    if len(auth_headers) != 2:
        print(invalid_msg)
        return jsonify(invalid_msg), 401
    try:
        token = auth_headers[1]
        print(token)
        data = jwt.decode(token, current_app.config['SECRET_KEY'])
        print(data)
    except jwt.InvalidTokenError as e:
        print(e)
        print("Invalid token - JWT library")
        return jsonify(invalid_msg), 40
    print(data['sub'])
    uid = data['sub']
    data1 = request.get_json()
    print(data1)
    reason = data1['reason']
    trid = data1['trid']
    #uid = data['uid']
    cursor = db.cursor()
    query = "SELECT food.uid,transaction.uid FROM transaction INNER JOIN food ON transaction.fid=food.fid WHERE transaction.trid=%s;"
    cursor.execute(query, trid)
    rows = cursor.fetchall()
    print(len(rows))
    print(rows)
    if uid == rows[0][0]:
        query = "INSERT INTO bannedUsers(uid,reason)VALUES(%s,%s);"
        cursor.execute(query, (rows[0][1], reason))
        db.commit()
    else:
        query = "INSERT INTO bannedUsers(uid,reason)VALUES(%s,%s);"
        cursor.execute(query, (rows[0][0], reason))
        db.commit()

    return "ok"


if __name__ == "__main__":
    app.secret_key = 'super_secret_key'
    app.run(debug=True)
