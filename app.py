from flask import Flask,url_for, flash, redirect, render_template, request, session, abort,g
from flask import request
from flask import send_file
from werkzeug import secure_filename
import pandas as pd
import re
import os
import subprocess
import sys
import requests
import sqlite3
import json
import pymysql
from flask_sqlalchemy import SQLAlchemy
import datetime
import sqlalchemy

# 
DATABASE = "database.db"
app = Flask(__name__)
# Environment variables are defined in app.yaml.
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:sochioncarry@127.0.0.1:3306/db"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# engine = sqlalchemy.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
# engine.connect()

@app.route('/main/<name>')
def mainPage(name=None):
    return render_template('main.html', name=name)

@app.route('/select/<name>')
def select(name=None):
   results = engine.execute("SELECT * FROM SongInfo where index_id=" + str(name))
   songPath = ""
   singers = ""
   songNames = ""
   singers_zh = ""
   songNames_zh=""
   startTime = ""
   endTime = ""
   duration = ""
   rawFormat = ""
   index = ""
   for result in results:
      songPath = result['fullNames']
      singers = result['singers']
      songNames = result['songNames']
      singers_zh = result['singers_zh']
      songNames_zh = result['songNames_zh']
      startTime = result['startTimes'] 
      endTime =  result['endTimes']
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
      line = line.replace(")","").replace("(","").replace("：","").replace("&lt;","").replace("&gt;","")
      for letter in line:
         letter = re.sub('[a-zA-Z]', '',letter)
         letter = re.sub('[=&!@#$-/]', '', letter)
         letter = re.sub('\ |\?|\.|\!|\/|\;|\:', '', letter)
         formatted_lyrics += letter

      audioSource = "https://storage.googleapis.com/audio-data-u3519936/audio_raw_cutted_5_compressed_mp3/"+str(index)+'.mp3'
      if len(formatted_lyrics) > 0 and formatted_lyrics !='\n' :
         lyrics.append(formatted_lyrics.replace("\n",""))

   return render_template('main_admin.html',
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

@app.route('/')
def index():
   results = engine.execute("SELECT * FROM SongInfo where isDone = 0 ORDER BY RAND() LIMIT 1")
   songPath = ""
   singers = ""
   songNames = ""
   singers_zh = ""
   songNames_zh=""
   startTime = ""
   endTime = ""
   duration = ""
   rawFormat = ""
   index = ""
   for result in results:
      songPath = result['fullNames']
      singers = result['singers']
      songNames = result['songNames']
      singers_zh = result['singers_zh']
      songNames_zh = result['songNames_zh']
      startTime = result['startTimes'] 
      endTime = result['endTimes'] 
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
      line = line.replace(")","").replace("(","").replace("：","").replace("&lt;","").replace("&gt;","")
      for letter in line:
         letter = re.sub('[a-zA-Z]', '',letter)
         letter = re.sub('[=&!@#$-/]', '', letter)
         letter = re.sub('\ |\?|\.|\!|\/|\;|\:', '', letter)
         formatted_lyrics += letter

      audioSource = "https://storage.googleapis.com/audio-data-u3519936/audio_raw_cutted_5_compressed_mp3/"+str(index)+'.mp3'
      if len(formatted_lyrics) > 0 and formatted_lyrics !='\n' :
         lyrics.append(formatted_lyrics.replace("\n",""))

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
   # conn = sqlite3.connect('database.db')
   index =  int(request.form['index'])
   singer =  request.form['singer']
   songName =  request.form['songName']
   start =  request.form['start']
   end =  request.form['end']
   lyrics =  (request.form['lyrics'])
   isNotLyrics =  request.form['isNotLyrics']
   if isNotLyrics == 'false':
      isNotLyrics = str(0)
   else:
      isNotLyrics = str(1)
   submitDate =  request.form['submitDate']
   # print("lyrics")
   # print(len(lyrics))

   if (len(lyrics) == 0 and isNotLyrics == str(0) ):
      print("Not valid record")
   else:
      # if the lyrics part is not null, then insert the record and refresh to next song
      query = 'UPDATE SongInfo SET isDone=1 WHERE index_id=' + str(index)
      results_1 = engine.execute(query)

      # Insert the record
      query_2 = 'INSERT INTO record ( index_id , singer, songName, start, end, lyrics, isNotLyrics,submitDate) '  +'VALUES ('+ str(index)  + ',"' + singer+ '","' + songName+ '",' + start+ ',' + end+ ',"' + lyrics+ '",' + isNotLyrics+ ',"' + submitDate + '");'
      results_2 = engine.execute(query_2)

   # Query and get random song info
   results = engine.execute("SELECT * FROM SongInfo  where isDone = 0 ORDER BY RAND() LIMIT 1")
   songPath = ""
   singers = ""
   songNames = ""
   singers_zh = ""
   songNames_zh=""
   startTime = ""
   endTime = ""
   duration = ""
   rawFormat = ""
   index = ""
   for result in results:
      songPath = result['fullNames']
      singers = result['singers']
      songNames = result['songNames']
      singers_zh = result['singers_zh']
      songNames_zh = result['songNames_zh']
      startTime = result['startTimes'] 
      endTime = result['endTimes']
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
      line = line.replace(")","").replace("(","").replace("：","").replace("&lt;","").replace("&gt;","")
      for letter in line:
         letter = re.sub('[a-zA-Z]', '',letter)
         letter = re.sub('[=&!@#$-/]', '', letter)
         letter = re.sub('\ |\?|\.|\!|\/|\;|\:', '', letter)
         formatted_lyrics += letter

      audioSource = "https://storage.googleapis.com/audio-data-u3519936/audio_raw_cutted_5_compressed_mp3/"+str(index)+'.mp3'
      if len(formatted_lyrics) > 0 and formatted_lyrics !='\n' :
         lyrics.append(formatted_lyrics.replace("\n",""))
         
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

@app.route('/adminPage')
def index_adminPage():
   results = engine.execute("SELECT * FROM SongInfo where isDone = 0 ORDER BY RAND() LIMIT 1")
   songPath = ""
   singers = ""
   songNames = ""
   singers_zh = ""
   songNames_zh=""
   startTime = ""
   endTime = ""
   duration = ""
   rawFormat = ""
   index = ""
   for result in results:
      songPath = result['fullNames']
      singers = result['singers']
      songNames = result['songNames']
      singers_zh = result['singers_zh']
      songNames_zh = result['songNames_zh']
      startTime = result['startTimes'] 
      endTime = result['endTimes'] 
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
      line = line.replace(")","").replace("(","").replace("：","").replace("&lt;","").replace("&gt;","")
      for letter in line:
         letter = re.sub('[a-zA-Z]', '',letter)
         letter = re.sub('[=&!@#$-/]', '', letter)
         letter = re.sub('\ |\?|\.|\!|\/|\;|\:', '', letter)
         formatted_lyrics += letter

      audioSource = "https://storage.googleapis.com/audio-data-u3519936/audio_raw_cutted_5_compressed_mp3/"+str(index)+'.mp3'
      if len(formatted_lyrics) > 0 and formatted_lyrics !='\n' :
         lyrics.append(formatted_lyrics.replace("\n",""))

   return render_template('main_admin.html',
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

@app.route('/submit_data_2', methods=['POST'])
def submit_data_2():
   # conn = sqlite3.connect('database.db')
   index =  int(request.form['index'])
   singer =  request.form['singer']
   songName =  request.form['songName']
   start =  request.form['start']
   end =  request.form['end']
   lyrics =  (request.form['lyrics'])
   isNotLyrics =  request.form['isNotLyrics']
   if isNotLyrics == 'false':
      isNotLyrics = str(0)
   else:
      isNotLyrics = str(1)
   submitDate =  request.form['submitDate']
   # print("lyrics")
   # print(len(lyrics))

   if (len(lyrics) == 0 and isNotLyrics == str(0) ):
      print("Not valid record")
   else:
      # if the lyrics part is not null, then insert the record and refresh to next song
      query = 'UPDATE SongInfo SET isDone=1 WHERE index_id=' + str(index)
      results_1 = engine.execute(query)

      # Insert the record
      query_2 = 'INSERT INTO record ( index_id , singer, songName, start, end, lyrics, isNotLyrics,isValidate,submitDate) '  +'VALUES ('+ str(index)  + ',"' + singer+ '","' + songName+ '",' + start+ ',' + end+ ',"' + lyrics+ '",' + isNotLyrics+ ', 1 ,"' + submitDate + '");'
      results_2 = engine.execute(query_2)

   # Query and get random song info
   results = engine.execute("SELECT * FROM SongInfo  where isDone = 0 ORDER BY RAND() LIMIT 1")
   songPath = ""
   singers = ""
   songNames = ""
   singers_zh = ""
   songNames_zh=""
   startTime = ""
   endTime = ""
   duration = ""
   rawFormat = ""
   index = ""
   for result in results:
      songPath = result['fullNames']
      singers = result['singers']
      songNames = result['songNames']
      singers_zh = result['singers_zh']
      songNames_zh = result['songNames_zh']
      startTime = result['startTimes'] 
      endTime = result['endTimes']
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
      line = line.replace(")","").replace("(","").replace("：","").replace("&lt;","").replace("&gt;","")
      for letter in line:
         letter = re.sub('[a-zA-Z]', '',letter)
         letter = re.sub('[=&!@#$-/]', '', letter)
         letter = re.sub('\ |\?|\.|\!|\/|\;|\:', '', letter)
         formatted_lyrics += letter

      audioSource = "https://storage.googleapis.com/audio-data-u3519936/audio_raw_cutted_5_compressed_mp3/"+str(index)+'.mp3'
      if len(formatted_lyrics) > 0 and formatted_lyrics !='\n' :
         lyrics.append(formatted_lyrics.replace("\n",""))
         
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


@app.route('/validate/<name>')
def validate(name=None):
   result = pd.read_excel('record_20190327_0130.xlsx', sheetname='ws1')
   name = int(name)
   singers = result['singers'][name]
   songNames = result['songNames'][name]
   singers_zh = result['singers'][name]
   songNames_zh = result['songNames'][name]
   startTime = result['startTimes'][name]
   endTime = result['endTimes'][name]
   duration = result['audioDuration'][name]
   index = result['index_id'][name]

   # read the text file
   txtPath = singers + "_" + songNames  + ".txt"
   f = open("./static/lyrics/"+ txtPath, encoding='utf-8')
   lyrics = []
   for line in f:
      formatted_lyrics =''
      line = line.replace(")","").replace("(","").replace("：","").replace("&lt;","").replace("&gt;","")
      for letter in line:
         letter = re.sub('[a-zA-Z]', '',letter)
         letter = re.sub('[=&!@#$-/]', '', letter)
         letter = re.sub('\ |\?|\.|\!|\/|\;|\:', '', letter)
         formatted_lyrics += letter

      audioSource = "https://storage.googleapis.com/audio-data-u3519936/audio_raw_cutted_5_compressed/"+str(index)+'.wav'
      if len(formatted_lyrics) > 0 and formatted_lyrics !='\n' :
         lyrics.append(formatted_lyrics.replace("\n",""))

   return render_template('main_validate.html',
                           index = index,
                           singers=singers,
                           singers_zh =singers_zh,
                           songNames=songNames,
                           songNames_zh = songNames_zh,
                           lyrics=lyrics,
                           audioSource =audioSource,
                           startTime =startTime,
                           endTime =endTime,
                           duration =duration,
                        )

if __name__ == '__main__':
   app.run()

# @app.route('/submit_data', methods=['POST'])
# def submit_data():
#    # conn = sqlite3.connect('database.db')
#    index =  int(request.form['index'])
#    singer =  request.form['singer']
#    songName =  request.form['songName']
#    start =  request.form['start']
#    end =  request.form['end']
#    lyrics =  request.form['lyrics']
#    isNotLyrics =  request.form['isNotLyrics']
#    submitDate =  request.form['submitDate']


#    # read the text file
#    txtPath = singers + "_" + songNames  + ".txt"
#    f = open("./static/lyrics/"+ txtPath, encoding='utf-8')
#    lyrics = []
#    for line in f:
#       formatted_lyrics =''
#       line = line.replace(")","").replace("(","").replace("：","").replace("&lt;","").replace("&gt;","")
#       for letter in line:
#          letter = re.sub('[a-zA-Z]', '',letter)
#          letter = re.sub('[=&!@#$-/]', '', letter)
#          letter = re.sub('\ |\?|\.|\!|\/|\;|\:', '', letter)
#          formatted_lyrics += letter

#       audioSource = "https://storage.googleapis.com/audio-data-u3519936/audio_raw_cutted/"+str(index)+'.wav'
#       if len(formatted_lyrics) > 0 and formatted_lyrics !='\n' :
#          lyrics.append(formatted_lyrics)
         
#    a = {
#          'index':index, 
#          'singers': singers, 
#          'singers_zh': singers_zh ,
#          'songNames':songNames, 
#          'songNames_zh': songNames_zh, 
#          'lyrics':lyrics, 
#          'audioSource': audioSource, 
#          'startTime': startTime ,
#          'endTime':endTime, 
#          'duration': duration
#       }
#    thisObject = json.dumps(a)

#    return thisObject

# def get_db():
#     db = getattr(g, '_database', None)
#     if db is None:
#         db = g._database = sqlite3.connect(DATABASE)
#     print("Getting db......")
#     db.row_factory = make_dicts
#     return db

# def query_db(query, args=(), one=False):
#     cur = get_db().execute(query, args)
#     rv = cur.fetchall()
#     cur.close()
#     return (rv[0] if rv else None) if one else rv

# def make_dicts(cursor, row):
#     return dict((cursor.description[idx][0], value)
#                 for idx, value in enumerate(row))


# @app.teardown_appcontext
# def close_connection(exception):
#     db = getattr(g, '_database', None)
#     if db is not None:
#         db.close()

# if __name__ == '__main__':
#    app.run()

