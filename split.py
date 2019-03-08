import pandas as pd
import re
import subprocess
import os
AUDIO_FOLDER ='D:\\song\\audio\\'
REFORMAT_FOLDER = 'D:\\song\\done\\audio_reformat\\'
OUTPUT_FOLDER = 'D:\\song\\done\\audio_raw_cutted\\'

df =pd.read_csv('MatchingList_done.csv')
for index, row in df.iterrows():
   songPath = row['fullNames']
   singers = row['singers']
   songNames = row['songNames']
   startTimes = row['startTimes'] < 3 and row['startTimes'] or row['startTimes'] -3
   endTimes = (row['audioDuration'] - row['endTimes']) < 3 and row['endTimes'] or row['endTimes'] +3
   rawFormat = row['rawFormat']
   index = row['index']

   # # ffmpeg -i Superstar_1.mp3 -acodec copy -ss 3.22 -to 4.634 output.mp3
   input_path = AUDIO_FOLDER + singers +"\\" + songNames + "." + rawFormat
   output_path = OUTPUT_FOLDER + str(index) +'.wav'
   reformat_path = REFORMAT_FOLDER + str(index) +'.wav'
   # reformat the audio to .wav first 
   if not(os.path.isfile(str(reformat_path))):
      print("Reformatting:  " + str(reformat_path))
      subprocess.call(['ffmpeg,','-i',str(input_path),str(reformat_path)])

   subprocess.call(['ffmpeg,','-i',str(reformat_path), '-acodec','copy','-ss',
                  str(startTimes),'-to',str(endTimes),str(output_path)])
   # print(reformat_command)
   # print(split_command)
# subprocess.run(split_command)
# subprocess.run(['ffmpeg,','-i',str(input_path), '-acodec','copy','-ss',
#                str(startTimes),'-to',str(endTimes),str(output_path)])

