import ffmpeg

vid = ffmpeg.probe('naruto.mp4')
print(vid['streams'])