from flask import Flask,url_for, flash, redirect, render_template, request, session, abort,g
from flask import request
from flask import send_file
from werkzeug import secure_filename
import pandas as pd
import re
import subprocess
import sys
import requests
import sqlite3
import json

DATABASE = 'database.db'

app = Flask(__name__)

@app.route('/main/<name>')
def mainPage(name=None):
    return render_template('main.html', name=name)

@app.route('/downloadData/<name>')
def downloadData(name=None):
   if(name=="sochioncarry"):
      path = "./database.db"
      return send_file(path, as_attachment=True)
   else:
      return name

@app.route('/checkData/<name>')
def checkData(name=None):
   if(name=="sochioncarry"):
      count_result = query_db('SELECT COUNT(id) FROM record')
      result = query_db('SELECT * FROM record')
      return render_template('checkData.html',
                              count_result=count_result,
                              result = result)
   else:
      return ""

@app.route('/')
def index():
   # Query and get random song info
   result = query_db('SELECT * FROM SongInfo ' +
                     'WHERE if_lyrics_exists=? ORDER BY RANDOM()',
                     ['TRUE'],
                     one=True)

   songPath = result['fullNames']
   singers = result['singers']
   songNames = result['songNames']
   singers_zh = result['singers_zh']
   songNames_zh = result['songNames_zh']
   startTime = result['startTimes'] < 3 and result['startTimes'] or result['startTimes'] -3
   endTime = (result['audioDuration'] - result['endTimes']) < 3 and result['endTimes'] or result['endTimes'] +3
   duration = result['audioDuration'] 
   rawFormat = result['rawFormat']
   index = result['index_id']



   # read the text file
   txtPath = singers + "_" + songNames  + ".txt"
   # f = open("/home/vmagent/app/static/lyrics/"+ txtPath, encoding='utf-8')
   f = open("./static/lyrics/"+ txtPath, encoding='utf-8')
   lyrics = []
   for line in f:
      formatted_lyrics =''
      line = line.replace(")","").replace("(","").replace("：","")
      for letter in line:
         letter = re.sub('[a-zA-Z]', '',letter)
         formatted_lyrics += letter

      audioSource = "https://storage.googleapis.com/audio-data-u3519936/audio_raw_cutted/"+str(index)+'.wav'
      if len(formatted_lyrics) > 0 and formatted_lyrics !='\n' :
         lyrics.append(formatted_lyrics)

   return render_template('main.html',
                           index = index,
                           singers=singers,
                           singers_zh =singers_zh,
                           songNames=songNames,
                           songNames_zh = songNames_zh,
                           songPath=songPath,
                           lyrics=lyrics,
                           audioSource =audioSource,
                           startTime =startTime,
                           endTime =endTime,
                           duration =duration,
                        )

@app.route('/submit_data', methods=['POST'])
def submit_data():
   index =  int(request.form['index'])
   singer =  request.form['singer']
   songName =  request.form['songName']
   start =  request.form['start']
   end =  request.form['end']
   lyrics =  request.form['lyrics']
   isNotLyrics =  request.form['isNotLyrics']
   submitDate =  request.form['submitDate']
   # if the lyrics part is not null, then insert the record and refresh to next song
   if (lyrics != ''):
      conn = sqlite3.connect('database.db')
      # Insert the record
      params = (index, singer, songName, start, end, lyrics, isNotLyrics,submitDate)
      conn.execute('INSERT INTO record ( index_id , singer, songName, start, end, lyrics, isNotLyrics,submitDate) VALUES (?, ?, ?, ?, ?, ?, ?,?)' ,params)
      conn.commit()
      # update Song Info
      test=("True",index)
      conn.execute('UPDATE SongInfo SET isDone=? WHERE index_id=?' ,test)
      conn.commit()
      conn.close()


   # Query and get random song info
   result = query_db('SELECT * FROM SongInfo ' +
                     'WHERE if_lyrics_exists=? ORDER BY RANDOM()',
                     ['TRUE'],
                     one=True)

   songPath = result['fullNames']
   singers = result['singers']
   songNames = result['songNames']
   singers_zh = result['singers_zh']
   songNames_zh = result['songNames_zh']
   startTime = result['startTimes'] < 3 and result['startTimes'] or result['startTimes'] -3
   endTime = (result['audioDuration'] - result['endTimes']) < 3 and result['endTimes'] or result['endTimes'] +3
   duration = result['audioDuration'] 
   rawFormat = result['rawFormat']
   index = result['index_id']

   # read the text file
   txtPath = singers + "_" + songNames  + ".txt"
   # f = open("/home/vmagent/app/static/lyrics/"+ txtPath, encoding='utf-8')
   f = open("./static/lyrics/"+ txtPath, encoding='utf-8')
   lyrics = []
   for line in f:
      formatted_lyrics =''
      line = line.replace(")","").replace("(","").replace("：","")
      for letter in line:
         letter = re.sub('[a-zA-Z]', '',letter)
         formatted_lyrics += letter

      audioSource = "https://storage.googleapis.com/audio-data-u3519936/audio_raw_cutted/"+str(index)+'.wav'
      if len(formatted_lyrics) > 0 and formatted_lyrics !='\n' :
         lyrics.append(formatted_lyrics)
         
   a = {
         'index':index, 
         'singers': singers, 
         'singers_zh': singers_zh ,
         'songNames':songNames, 
         'songNames_zh': songNames_zh, 
         'songPath': songPath ,
         'lyrics':lyrics, 
         'audioSource': audioSource, 
         'startTime': startTime ,
         'endTime':endTime, 
         'duration': duration
      }
   thisObject = json.dumps(a)

   return thisObject

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    print("Getting db......")
    db.row_factory = make_dicts
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
   app.run()

