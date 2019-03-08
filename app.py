from flask import Flask,url_for, flash, redirect, render_template, request, session, abort,g
from flask import request
from werkzeug import secure_filename
import pandas as pd
import re
import subprocess
import sys
import requests
import sqlite3

DATABASE = 'database.db'

app = Flask(__name__)

@app.route('/main/<name>')
def mainPage(name=None):
    return render_template('main.html', name=name)

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
   f = open(".\\static\\lyrics\\"+ txtPath, encoding='utf-8')
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
   isLyrics =  request.form['isLyrics']
   # if the lyrics part is not null, then insert the record and refresh to next song
   if (lyrics != ''):
      conn = sqlite3.connect('database.db')
      params = (index, singer, songName, start, end, lyrics, isLyrics)
      conn.execute('INSERT INTO record ( index_id , singer, songName, start, end, lyrics, isLyrics) VALUES (?, ?, ?, ?, ?, ?, ?)' ,params)
      conn.commit()
      conn.close()
   return "This is checking response"


# conn.execute('CREATE TABLE record (' +
#   'id INTEGER PRIMARY KEY AUTOINCREMENT,'+
#   'singer TEXT NOT NULL,'+
#   'songName TEXT NOT NULL,'+
#   'start FLOAT NOT NULL,'+
#   'end FLOAT NOT NULL,'+
#   'lyrics TEXT NOT NULL,'+
#   'isLyrics BOOLEAN NOT NULL)')

# def cutSong(df):
   # AUDIO_FOLDER ='D:\\song\\audio\\'
   # REFORMAT_FOLDER = 'C:\\Users\\terry\\Desktop\\flask\\static\\songs_reformat\\'
   # OUTPUT_FOLDER = 'C:\\Users\\terry\\Desktop\\flask\\static\\songs_gen\\'
   # songNames = result['songNames']
   # singers = result['singers']
   
   # # ffmpeg -i Superstar_1.mp3 -acodec copy -ss 3.22 -to 4.634 output.mp3
   # input_path = AUDIO_FOLDER + singers +"\\" + songNames + "." + rawFormat
   # output_path = OUTPUT_FOLDER + str(index) +'.wav'
   # reformat_path = REFORMAT_FOLDER + str(index) +'.wav'
   # # reformat the audio to .wav first 
   # reformat_command = ['ffmpeg','-i',str(input_path),str(reformat_path)]
   # split_command = ['ffmpeg','-i',str(reformat_path), '-acodec','copy','-ss',
   #                str(startTimes),'-to',str(endTimes),str(output_path)]
   # print(reformat_command)
   # print(split_command)
   # subprocess.run(reformat_command)
   # subprocess.run(split_command)
   # subprocess.run(['ffmpeg,','-i',str(input_path), '-acodec','copy','-ss',
   #                str(startTimes),'-to',str(endTimes),str(output_path)])
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