
from io import StringIO
from flask import Flask, request, render_template,session
import os
import csv
import sqlite3
import datetime

from werkzeug.utils import redirect

app = Flask(__name__)
app.secret_key = os.urandom(32)
answer = []
answernum = 0
con = sqlite3.connect("database.db",check_same_thread=False)
 

@app.route('/')
def index():
  if "username" not in session:
    return redirect('login')
  c = con.cursor()
  c.execute("select * from log order by score desc, time")
  rows = c.fetchall();
  return render_template('index.html', rows=rows)

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    session['username'] = request.form['name']
    return redirect('/')
  return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
  session.pop('username', None)
  return redirect('/login')

@app.route('/fileupload', methods=['POST'])
def fileupload():
  cnt =0
  name = session['username']
  try :
    paramfile = StringIO(request.files['file'].read().decode())
    reader = csv.reader(paramfile,delimiter=",")
    next(reader,None)
    i=0
    for row in reader:
      if answer[i] == row[1]:
        cnt+=1
  except:
     return render_template("fileerror.html")
  c = con.cursor()
  c.execute("select * from log where name = ? and score = ?", (name,str(round(cnt/answernum,5))))
  data = c.fetchall()
  if len(data) == 0:
    c.execute("INSERT INTO log (name,score,time) VALUES (?,?,?)",(name,str(round(cnt/answernum,5)),str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))) )
    con.commit()
  return render_template("result.html", score=str(round(cnt/answernum,5)))


if __name__=="__main__":
  c = con.cursor()
  c.execute('CREATE TABLE IF NOT EXISTS log (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, score text, time text)')
  with open('submission.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    next(spamreader,None)
    for row in spamreader:
      answer.append(row[1])
      answernum+=1
  app.run(debug=True, host="0.0.0.0")
  # host 등을 직접 지정하고 싶다면
  # app.run(host="127.0.0.1", port="5000", debug=True)
