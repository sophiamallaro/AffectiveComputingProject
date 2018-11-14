import os
from pydub import AudioSegment

audio_directory = "../affcom-project/data/deam/MEMD_audio/"
feature_directory = "features/"
opensmile = "../opensmile-2.3.0/inst/bin/SMILExtract"
config = "IS13_ComParE_lld-func.conf"

for file_name in os.listdir(audio_directory):
    song_id = file_name.split(".")[0]
    mp3_file_path = audio_directory + file_name
    mp3_file = AudioSegment.from_mp3(mp3_file_path)
    temp_wav = mp3_file.export("temp.wav", format="wav")
    output_csv = feature_directory + song_id + ".csv"
    os.system("{} -C {} -I temp.wav -O {}".format(opensmile, config, output_csv))
    os.system("rm temp.wav")
    print("{} done...\n\n\n".format(song_id))