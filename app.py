import requests
from flask import Flask, render_template, url_for, jsonify, request, redirect, session, flash, Response, make_response, send_file
from datetime import datetime
from flask_mail import Mail, Message
from cv2 import cv2
import base64
from flask_mysqldb import MySQL
import os
import mysql
import face_recognition
import random


from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'uday2007'
app.config['MYSQL_DB'] = 'attendancesystem'

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'udaydikshit2007@gmail.com'
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail= Mail(app)
#mysql = MySQL(app)

#cnx = mysql.connector.connect(user = 'root', database = 'attendancesystem')
#cursor = cnx.cursor()

import csv
from datetime import datetime
#from app import courseid
import cv2
import face_recognition
import os
import numpy as np
import pandas as pd
#face_cascade=cv2.CascadeClassifier("haarcascade_frontalface_alt2.xml")
#ds_factor=0.6
filename=''
mysql = MySQL(app)


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/login",methods=["GET","POST"])
def login():
    return render_template('login.html')

@app.route("/forgetpassword",methods=["GET","POST"])
def forgetpassword():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['m_email']
        cur = mysql.connection.cursor()
        cur.execute("SELECT  password FROM logindata WHERE username=%s ",
                    (username,))
        mypassword= cur.fetchone()


        cur = mysql.connection.cursor()
        cur.execute("SELECT  emailid FROM studentdetails WHERE username=%s ",
                    (username,))
        myemail = cur.fetchone()
        m1=myemail[0]

        #print(myemail[0])
        #print(email)


        if email==m1:
            msg = Message('Hello', sender='udaydikshit2007@gmail.com', recipients=[m1])
            msg.body = "Hello"+str(username)+"your password is"+str(mypassword[0])
            mail.send(msg)
            return redirect(url_for('login'))
        else:
            return 'please Enter Valid Email and Username'

@app.route("/user",methods=["GET","POST"])
def user():

    if request.method=="POST":
        username=request.form['username']
        password=request.form['password']
        role=request.form['role']
        cur = mysql.connection.cursor()
        cur.execute("SELECT  * FROM logindata WHERE username=%s AND password=%s AND role=%s",(username,password,role))
        data = cur.fetchone()
        cur.close()
        if data:
            session['loggedin'] = True
            session['username']=username
            session['role']=role
            session['password']=password
            return redirect(url_for('show'))

        else:
            return 'invalid username/password try again'

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username',None)
    session.pop('role',None)
    return redirect(url_for('login'))

@app.route('/show')
def show():
    if 'loggedin' in session:
        role=session.get('role')
        if role=='student':
            username = session.get('username')
            cur = mysql.connection.cursor()
            cur.execute("SELECT  * FROM studentdetails WHERE username=%s ",
                        (username,))
            data = cur.fetchone()
            cur.close()
            cur = mysql.connection.cursor()
            cur.execute('SELECT studentname FROM studentdetails WHERE username=%s', (username,))
            stname = cur.fetchone()
            cur.close()
            cur = mysql.connection.cursor()
            cur.execute("SELECT  * FROM attendancedetails WHERE studentname=%s", (stname,))
            data2 = cur.fetchall()
            cur.close()


            return render_template('student.html',username=session.get('username'), studentname=stname, data=data, data2=data2)
        elif role=='faculty':
            username = session.get('username')
            cur = mysql.connection.cursor()
            cur.execute("SELECT  * FROM facultydetails WHERE username=%s ",
                        (username,))
            data = cur.fetchone()
            cur.close()

            cur = mysql.connection.cursor()
            cur.execute('SELECT facultyname FROM facultydetails WHERE username=%s', (username,))
            facultyname = cur.fetchone()
            cur.close()

            cur = mysql.connection.cursor()
            cur.execute("SELECT courseid FROM coursedetails WHERE facultyname=%s ",(facultyname,))
            courseid = cur.fetchone()
            cur.close()

            cur = mysql.connection.cursor()
            cur.execute("SELECT  * FROM attendancedetails WHERE facultyname=%s", (facultyname,))
            data2 = cur.fetchall()
            cur.close()

            return render_template('faculty.html', username=session.get('username'),data=data, courseid=courseid, data2=data2)

        elif role=='admin':
                cur = mysql.connection.cursor()
                cur.execute("SELECT  * FROM studentdetails")
                data = cur.fetchall()
                cur.close()
                cur = mysql.connection.cursor()
                cur.execute("SELECT  * FROM facultydetails")
                fdata = cur.fetchall()
                cur.close()
                cur = mysql.connection.cursor()
                cur.execute("SELECT  * FROM coursedetails")
                fdata1 = cur.fetchall()
                cur.close()
                cur = mysql.connection.cursor()
                cur.execute("SELECT username FROM facultydetails")
                fdata2 = cur.fetchall()
                cur.close()

                return render_template('admin.html', username=session.get('username'),students=data,facultys=fdata,coursedetail=fdata1,fdata2=fdata2)
        
        elif role=='counselor':
            username = session.get('username')
            cur = mysql.connection.cursor()
            cur.execute("SELECT  * FROM coordinatordetails WHERE username=%s ",
                        (username,))
            udata = cur.fetchone()
            cur.close()
            cur = mysql.connection.cursor()
            cur.execute("SELECT  * FROM emotiondetails")
            data = cur.fetchall()
            cur.close()
            cur = mysql.connection.cursor()
            cur.execute("SELECT  * FROM facultydetails")
            fdata = cur.fetchall()
            cur.close()
            cur = mysql.connection.cursor()
            cur.execute("SELECT  * FROM coursedetails")
            fdata1 = cur.fetchall()
            cur.close()
            cur = mysql.connection.cursor()
            cur.execute("SELECT username FROM facultydetails")
            fdata2 = cur.fetchall()
            cur.close()

            return render_template('mhc.html', username=session.get('username'), labels=data, data=udata)

    else:
        return redirect(url_for('login'))



@app.route('/studentupdate', methods=["GET","POST"])
def studentupdate():
    if 'loggedin' in session:
        if session.get('role')=='student':
            if request.method == 'POST':

                emailid = request.form['emailid']
                batch = request.form['batch']
                dob=request.form['dob']
                username = session.get('username')
                cur = mysql.connection.cursor()
                cur.execute("""
                       UPDATE studentdetails
                       SET emailid=%s, batch=%s, dob=%s 
                       WHERE username=%s
                    """, (emailid, batch,dob,username))
                flash("Data Updated Successfully")
                mysql.connection.commit()

                return redirect(url_for('show'))
            else:
                return 'Fill out the form and come back'
        else:
            return 'please login as student'
    else:
        return 'please first login'

@app.route('/studentchangepassword', methods=["GET","POST"])
def studentchangepassword():
    if 'loggedin' in session:
        if session.get('role')=='student':
            if request.method == 'POST':

                password=request.form['password']
                username = session.get('username')
                cur = mysql.connection.cursor()
                cur.execute("""
                       UPDATE logindata
                       SET password=%s
                       WHERE username=%s
                    """, (password,username))
                flash("Data Updated Successfully")
                mysql.connection.commit()
                return redirect(url_for('show'))
            else:
                return 'Fill out the form and come back'
        else:
            return 'please login as student'
    else:
        return 'please first login'

@app.route('/facultyupdate', methods=["GET","POST"])
def facultyupdate():
    if 'loggedin' in session:
        role=session.get('role')
        if role=='faculty':
            if request.method == 'POST':
                email = request.form['email']
                phno=request.form['phno']
                username = session.get('username')
                cur = mysql.connection.cursor()
                cur.execute("""
                       UPDATE facultydetails
                       SET email=%s, ph_no=%s
                       WHERE username=%s
                    """, (email, phno,username))
                flash("Data Updated Successfully")
                mysql.connection.commit()
                return redirect(url_for('show'))
            else:
                return 'Fill out the form and come back'
        else:
            return 'please login as faculty'
@app.route('/facultychangepassword', methods=["GET","POST"])
def facultychangepassword():
    if 'loggedin' in session:
        if session.get('role')=='faculty':
            if request.method == 'POST':

                password=request.form['password']
                username = session.get('username')
                cur = mysql.connection.cursor()
                cur.execute("""
                       UPDATE logindata
                       SET password=%s
                       WHERE username=%s
                    """, (password,username))
                flash("Data Updated Successfully")
                mysql.connection.commit()
                return redirect(url_for('show'))
            else:
                return 'Fill out the form and come back'
        else:
            return 'please login as faculty'
    else:
        return 'please first login'


@app.route('/update',methods=['POST','GET'])
def update():
    if 'loggedin' in session:
        if session.get('role')=='admin':
            if request.method == 'POST':
                username = request.form['username']
                batch = request.form['batch']
                emailid = request.form['emailid']
                dob= request.form['dob']
                cur = mysql.connection.cursor()
                cur.execute("""
                       UPDATE studentdetails
                       SET  batch=%s,
                       emailid=%s, dob=%s
                       WHERE username=%s
                    """, (batch,emailid,dob,username))
                flash("Data Updated Successfully")
                mysql.connection.commit()
                return redirect(url_for('show'))
            else:
                return 'Fill out the form and come back'
        else:
            return 'please login as a admin'




@app.route('/fupdate',methods=['POST','GET'])
def fupdate():
    if 'loggedin' in session:
        if session.get('role')=='admin':
            if request.method == 'POST':
                username = request.form['username']
                email = request.form['email']
                ph_no= request.form['ph_no']
                cur = mysql.connection.cursor()
                cur.execute("""
                       UPDATE facultydetails
                       SET  email=%s,
                         ph_no=%s
                       WHERE username=%s
                    """, (email,ph_no,username))
                flash("Data Updated Successfully")
                mysql.connection.commit()
                return redirect(url_for('show'))
            else:
                return 'Fill out the form and come back'
        else:
            return 'please login as a admin'

@app.route('/insert',methods=['POST','GET'])
def insert():
    if 'loggedin' in session:
        if session.get('role')=='admin':
            if request.method == 'POST':
                studentname= request.form['stname']
                username = request.form['username']
                batch = request.form['batch']
                emailid = request.form['emailid']
                dob = request.form['dob']
                img=request.files['img']
                img.save(os.path.join('./photos/',img.filename))
                os.rename('./photos/'+img.filename, './photos/'+studentname +'.jpg')
                password=request.form['password']
                role='student'
                cur = mysql.connection.cursor()
                cur.execute("""
                       INSERT INTO studentdetails (studentname, username,batch, emailid, dob) VALUES (%s, %s, %s, %s,%s)
                    """, (studentname, username, batch, emailid, dob))
                flash("Data Updated Successfully")
                mysql.connection.commit()
                cur = mysql.connection.cursor()
                cur.execute("""
                                       INSERT INTO logindata (username,password,role) VALUES (%s, %s, %s)
                                    """, (username, password,role))
                mysql.connection.commit()

                return redirect(url_for('show'))
            else:
                return 'Fill out the form and come back'
        else:
            return 'please login as admin'

@app.route('/finsert',methods=['POST','GET'])
def finsert():
    if 'loggedin' in session:
        if session.get('role')=='admin':
            if request.method == 'POST':
                facultyname= request.form['facultyname']
                username = request.form['username']
                email = request.form['email']
                phno = request.form['phno']
                password=request.form['password']
                role='faculty'
                cur = mysql.connection.cursor()
                cur.execute("""
                       INSERT INTO facultydetails (facultyname, username, email, ph_no) VALUES (%s, %s, %s, %s)
                    """, (facultyname, username, email, phno))
                flash("Data Updated Successfully")
                mysql.connection.commit()
                cur = mysql.connection.cursor()
                cur.execute("""
                                       INSERT INTO logindata (username,password,role) VALUES (%s, %s, %s)
                                    """, (username, password,role))
                mysql.connection.commit()
                return redirect(url_for('show'))
            else:
                return 'Fill out the form and come back'
        else:
            return 'please login as admin'


@app.route('/cinsert',methods=['POST','GET'])
def cinsert():
    if 'loggedin' in session:
        if session.get('role')=='admin':
            if request.method == 'POST':
                courseid = request.form['courseid']
                coursename = request.form['coursename']
                facultyname = request.form['faculty']
                deptid= request.form['deptid']
                cur = mysql.connection.cursor()
                cur.execute("""
                       INSERT INTO coursedetails (courseid, coursename, facultyname, departmentid) VALUES (%s, %s, %s, %s)
                    """, (courseid, coursename, facultyname, deptid,))
                mysql.connection.commit()

                flash("Data Updated Successfully")

                return redirect(url_for('show'))
            else:
                return 'Fill out the form and come back'
        else:
            return 'please login as admin'

@app.route('/cupdate',methods=['POST','GET'])
def cupdate():
    if 'loggedin' in session:
        if session.get('role')=='admin':
            if request.method == 'POST':
                courseid=request.form['courseid']
                facultyname=request.form['facultyname']
                cur = mysql.connection.cursor()
                cur.execute("""
                                       UPDATE coursedetails
                                       SET  facultyname=%s
                                         
                                       WHERE courseid=%s
                                    """, (facultyname, courseid))
                flash("Data Updated Successfully")
                mysql.connection.commit()
                return redirect(url_for('show'))
            else:
                return 'Fill out the form and come back'
        else:
            return 'please login as admin'




@app.route('/delete/<string:username>', methods=['GET'])
def delete(username):
    if 'loggedin' in session:
        if session.get('role')=='admin':
            flash("Record Has Been Deleted Successfully")
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM studentdetails WHERE username=%s", (username,))
            mysql.connection.commit()
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM logindata WHERE username=%s", (username,))
            mysql.connection.commit()
            os.remove('/static/images/'+username+'.jpg')

            return redirect(url_for('show'))
        else:
            return 'Fill out the form and come back'
    else:
        return 'please login as admin'

@app.route('/fdelete/<string:username>', methods=['GET'])
def fdelete(username):
    if 'loggedin' in session:
        if session.get('role')=='admin':
            flash("Record Has Been Deleted Successfully")
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM facultydetails WHERE username=%s", (username,))
            mysql.connection.commit()
            return redirect(url_for('show'))
        else:
            return 'Fill out the form and come back'
    else:
        return 'please login as admin'

@app.route('/cdelete/<string:coursename>', methods=['GET'])
def cdelete(coursename):
    if 'loggedin' in session:
        if session.get('role')=='admin':
            flash("Record Has Been Deleted Successfully")
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM coursedetails WHERE courseid=%s", (coursename,))
            mysql.connection.commit()
            return redirect(url_for('show'))
        else:
            return 'Fill out the form and come back'
    else:
        return 'please login as admin'


@app.route('/resetpassword/<string:username>', methods=['GET'])
def resetpassword(username):
    if 'loggedin' in session:
        if session.get('role')=='admin':
            password='123'
            cur = mysql.connection.cursor()
            cur.execute("""UPDATE logindata
                       SET password=%s
                       WHERE username=%s
                    """, (password, username))
            mysql.connection.commit()
            return redirect(url_for('show'))
        else:
            return 'Fill out the form and come back'
    else:
        return 'please login as admin'

@app.route('/fresetpassword/<string:username>', methods=['GET'])
def fresetpassword(username):
    if 'loggedin' in session:
        if session.get('role')=='admin':
            password='123'
            cur = mysql.connection.cursor()
            cur.execute("""UPDATE logindata
                       SET password=%s
                       WHERE username=%s
                    """, (password, username))
            mysql.connection.commit()
            return redirect(url_for('show'))
        else:
            return 'Fill out the form and come back'
    else:
        return 'please login as admin'

@app.route('/upload_attendance',methods=['GET', 'POST'])
def upload_attendance():

    if 'loggedin' in session:

        if session.get('role')=='faculty':
            if request.method == 'POST':
                courseid= request.form['courseid']
                username= session.get('username')
                d4= request.form['date']
                cur = mysql.connection.cursor()
                cur.execute("SELECT facultyname FROM facultydetails WHERE username=%s ",(username,))
                facultyname = cur.fetchone()
                cur.close()
                facultyname= facultyname[0]
                #print(facultyname)
                today = datetime.today()
                #d4 = today.strftime("%Y-%m-%d")
                #print(d4)
                now= datetime.now()
                x= datetime.now()
                x4= x.strftime("%H")
                filename = courseid + '_' + d4 + '_' + x4 + '_' + '.csv'
                path= './attendance/' + filename
                df = pd.read_csv(path, index_col=False, delimiter = ',', header= None)
                #df= pd.read_csv(path, header=None)
                df.drop_duplicates(subset= 2,keep='first',inplace=True)
                cur = mysql.connection.cursor()
                for i,row in df.iterrows():
                    label=['happy', 'neutral']
                    emo=random.choice(label)
                    query= 'INSERT INTO `attendancedetails` (`courseid`, `facultyname`, `studentname`, `dated`, `timed`) VALUES (%s, %s, %s, %s, %s)'
                    cur.execute(query, tuple(row))
                    mysql.connection.commit()
                    query1= """INSERT INTO emotiondetails(emotionlabel, courseid, dated, timed) VALUES (%s, %s, %s, %s)"""
                    val= (emo, row[0], row[3], row[4])
                    #print(val)
                    cur.execute(query1, val)
                    
                    mysql.connection.commit()
                    #print("run")
                #print("run")
                cur= mysql.connection.cursor()
                cur.execute("SELECT count(*) FROM attendancedetails WHERE dated= %s AND courseid= %s", (d4, courseid)) 
                count=[v for v in cur.fetchone()][0]
                #timed=[v for v in cur.fetchall()][0]
                cur.close()
                #print(count)
                cur= mysql.connection.cursor()
                query= """INSERT INTO attendancestats(courseid, facultyname, dated, count) VALUES(%s, %s, %s, %s)"""
                value= (courseid, facultyname, d4, count)
                cur.execute(query, value)
                #print("success")
                mysql.connection.commit()
                cur= mysql.connection.cursor()
                cur.execute("UPDATE attendancestats SET count= %s WHERE dated= %s AND courseid=%s AND facultyname=%s", (count, d4, courseid, facultyname,))
                #print("success")
                mysql.connection.commit()
                return redirect(url_for('show'))


@app.route('/takeattendance', methods=['GET','POST'])
def takeattendance():

    if 'loggedin' in session:

        if session.get('role')=='faculty':
            if request.method == 'POST':
                global courseid
                courseid = request.form['courseid']

                return render_template('index.html')
        else:
            return 'only faculty can take attendance'

photos_path="./photos/"
photos= os.listdir(photos_path)
#print(photos)
names = [s.replace(".jpg", "") for s in photos]
names = [s.replace(".JPG", "") for s in names]
#print(names)
known_face_encodings = []
known_face_names = names
#print(known_face_names)
for i,j  in zip(photos, names):
    j = face_recognition.face_encodings(face_recognition.load_image_file(os.path.join("./photos/"+i)))[0]
    known_face_encodings.append(j)

#print(known_face_encodings)
# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
timing=[]
f_names= []
fa_names= []
process_this_frame = True

def write_attendance(name, facultyname):
    #fa_names.append(name)
    #for c in fa_names:
    now = datetime.now()
    global time
    time= now.strftime("%H-%M-%S")
    #timing.append(time)
    #print(f_names)
    today = datetime.today()
    global d4
    d4 = today.strftime("%Y-%m-%d")
    x= datetime.now()
    global x4
    x4= x.strftime("%H")
    global filename
    #facultyname='Tushar Grewal'
    facultyname=facultyname
    filename = courseid + '_' + d4 + '_' + x4 + '_' + '.csv'
    path= r'./attendance/' + filename
    
    if name== 'Unknown':
        pass
    else:
    #if c not in f_names:
    #f_names.append(c)
        if os.path.isfile(path)== True:
            #print("true")
            df= pd.read_csv(path, header=None)
            df.drop_duplicates(subset= 2,keep='first',inplace=True)
            #for index, row in df.iterrows():
            if name in df[:2].values:
                #print("exists")
                df.drop_duplicates(subset= 2,keep='first',inplace=True)
            else:
                with open(path, 'a') as f:
                    writer= csv.writer(f)
                    writer.writerow([courseid, facultyname, name, d4, time])
                    df.drop_duplicates(subset= 2,keep='first',inplace=True)
                    f.close()
                df.drop_duplicates(subset= 2,keep='first',inplace=True)  
            df.drop_duplicates(subset= 2,keep='first',inplace=True)              
        else:           
            with open(path, 'a') as f:
                writer= csv.writer(f)
                writer.writerow([courseid, facultyname, name, d4, time])
                f.close()
            df= pd.read_csv(path, header=None)
            df.drop_duplicates(subset= 2,keep='first',inplace=True)
        df.drop_duplicates(subset= 2,keep='first',inplace=True)

                        
def gen(facultyname, username): 
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]           
            #Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            

            face_names = []
            for i in range(len(face_encodings)):
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encodings[i])
                
                name = "Unknown"
                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encodings[i])
                best_match_index = np.argmin(face_distances)
                #print(best_match_index)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                write_attendance(name, facultyname)
                #print(name)
                face_names.append(name)
                #print(face_names)
                # Display the results
                for (top, right, bottom, left), nam in zip(face_locations, face_names):

                    # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4

                    # Draw a box around the face
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    # Draw a label with a name below the face
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, nam, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)


            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/download_file', methods=['GET','POST'])
def download_file():
    if 'loggedin' in session:
        if session.get('role')=='faculty':
            path= './attendance/' + filename
            return send_file(path, as_attachment=True) 
                            

@app.route('/video_feed', methods=['GET', 'POST'])
def video_feed():
    if 'loggedin' in session:
        if session.get('role')=='faculty':
            global username
            global facultyname
            username= session.get('username')
            cur = mysql.connection.cursor()
            cur.execute('SELECT facultyname FROM facultydetails WHERE username=%s', (username,))
            facultyname = cur.fetchone()
            cur.close()
            facultyname= facultyname[0]
            return Response(gen(facultyname, username), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/chart1', methods=['GET', 'POST'])
def chart1():
    if 'loggedin' in session:
        if session.get('role')=='counselor':
            global username
            courseid= request.form['courseid']
            dated= request.form['date']
            #dated= datetime.strptime(date,'%Y-%m-%d').strftime('%b-%d-%Y')

            username= session.get('username')
            cur= mysql.connection.cursor() 
            cur.execute('SELECT count("id") FROM emotiondetails WHERE dated= %s AND courseid= %s AND emotionlabel= "happy"', (dated, courseid))
            counthappy= [v for v in cur.fetchone()][0]
            cur.close()
            cur= mysql.connection.cursor() 
            cur.execute('SELECT count("id") FROM emotiondetails WHERE dated= %s AND courseid= %s AND emotionlabel= "neutral"', (dated, courseid))
            countneutral= [v for v in cur.fetchone()][0]
            cur.close()
            cur= mysql.connection.cursor() 
            cur.execute('SELECT count("id") FROM emotiondetails WHERE dated= %s AND courseid= %s AND emotionlabel= "surprise"', (dated, courseid))
            countsurprise= [v for v in cur.fetchone()][0]
            cur.close()
            cur= mysql.connection.cursor() 
            cur.execute('SELECT count("id") FROM emotiondetails WHERE dated= %s AND courseid= %s AND emotionlabel= "angry"', (dated, courseid))
            countangry= [v for v in cur.fetchone()][0]
            cur.close()
            cur= mysql.connection.cursor() 
            cur.execute('SELECT count("id") FROM emotiondetails WHERE dated= %s AND courseid= %s AND emotionlabel= "disgust"', (dated, courseid))
            countdisgust= [v for v in cur.fetchone()][0]
            cur.close()
            cur= mysql.connection.cursor() 
            cur.execute('SELECT count("id") FROM emotiondetails WHERE dated= %s AND courseid= %s AND emotionlabel= "fear"', (dated, courseid))
            countfear= [v for v in cur.fetchone()][0]
            cur.close()
            cur= mysql.connection.cursor() 
            cur.execute('SELECT count("id") FROM emotiondetails WHERE dated= %s AND courseid= %s AND emotionlabel= "sad"', (dated, courseid))
            countsad= [v for v in cur.fetchone()][0]
            cur.close()
            
            labels=['sad', 'fear', 'angry', 'happy', 'disgust', 'neutral', 'surprise']
            values=[countsad, countfear, countangry, counthappy, countdisgust, countneutral, countsurprise]
            colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC"]

            return render_template('chart1.html', max=17000,set=zip(values, labels, colors), date=dated, subject=courseid)

@app.route('/chart2', methods=['GET', 'POST'])
def chart2():
    if 'loggedin' in session:
        if session.get('role')=='counselor':
            global username
            courseid= request.form['courseid']
            idated= request.form['idate']
            #idated= datetime.strptime(idate,'%Y-%m-%d').strftime('%b-%d-%Y')
            fdated= request.form['fdate']
            #fdated= datetime.strptime(fdate,'%Y-%m-%d').strftime('%b-%d-%Y')
            
            username= session.get('username')

            cur= mysql.connection.cursor() 
            cur.execute('SELECT count("id") FROM emotiondetails WHERE dated BETWEEN %s AND %s AND courseid= %s AND emotionlabel= "happy"', (idated, fdated, courseid))
            counthappy= [v for v in cur.fetchone()][0]
            cur.close()
            cur= mysql.connection.cursor() 
            cur.execute('SELECT count("id") FROM emotiondetails WHERE dated BETWEEN %s AND %s AND courseid= %s AND emotionlabel= "neutral"', (idated, fdated, courseid))
            countneutral= [v for v in cur.fetchone()][0]
            cur.close()
            cur= mysql.connection.cursor() 
            cur.execute('SELECT count("id") FROM emotiondetails WHERE dated BETWEEN %s AND %s AND courseid= %s AND emotionlabel= "surprise"', (idated, fdated, courseid))
            countsurprise= [v for v in cur.fetchone()][0]
            cur.close()
            cur= mysql.connection.cursor() 
            cur.execute('SELECT count("id") FROM emotiondetails WHERE dated BETWEEN %s AND %s AND courseid= %s AND emotionlabel= "angry"', (idated, fdated, courseid))
            countangry= [v for v in cur.fetchone()][0]
            cur.close()
            cur= mysql.connection.cursor() 
            cur.execute('SELECT count("id") FROM emotiondetails WHERE dated BETWEEN %s AND %s AND courseid= %s AND emotionlabel= "disgust"', (idated, fdated, courseid))
            countdisgust= [v for v in cur.fetchone()][0]
            cur.close()
            cur= mysql.connection.cursor() 
            cur.execute('SELECT count("id") FROM emotiondetails WHERE dated BETWEEN %s AND %s AND courseid= %s AND emotionlabel= "fear"', (idated, fdated, courseid))
            countfear= [v for v in cur.fetchone()][0]
            cur.close()
            cur= mysql.connection.cursor() 
            cur.execute('SELECT count("id") FROM emotiondetails WHERE dated BETWEEN %s AND %s AND courseid= %s AND emotionlabel= "sad"', (idated, fdated, courseid))
            countsad= [v for v in cur.fetchone()][0]
            cur.close()
            #print(counthappy)
            
            labels=['sad', 'fear', 'angry', 'happy', 'disgust', 'neutral', 'surprise']
            values=[countsad, countfear, countangry, counthappy, countdisgust, countneutral, countsurprise]
            #print(values)
            colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC"]

            return render_template('chart2.html', max=30, labels=labels, values=values, idate=idated, fdate=fdated, subject=courseid)

@app.route('/fchart1', methods=['GET', 'POST'])
def fchart1():
    if 'loggedin' in session:
        if session.get('role')=='faculty':
            global username
            courseid= request.form['courseid']
            idated= request.form['idate']
            fdated= request.form['fdate']
            username= session.get('username')
            labels=[]
            values=[]
            cur= mysql.connection.cursor() 
            cur.execute('SELECT dated, count FROM attendancestats WHERE dated BETWEEN %s AND %s AND courseid= %s ', (idated, fdated, courseid))
            #dic= [v for v in cur.fetchone()][0]
            dic= cur.fetchall()
            cur.close()
            #print(labels)
            #print(values)
            #print(dic)
            for label, value in dic:
                labels.append(label)
                values.append(value)
            #print(labels)
            #print(values)
            return render_template('fchart1.html', max=30, labels=labels, values=values, idated=idated, fdated=fdated, subject=courseid)

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(debug=True)


