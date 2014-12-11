for i in *.ogv; do
    avconv -i "${i%.ogv}.ogv" -acodec aac -strict experimental "${i%.ogv}.mp4"
done

for i in *.3gp; do
    avconv -i "${i}" -r 29.97 -vcodec libx264 -acodec aac -strict experimental "${i%.3gp}.mp4"
done

for i in *.mp4; do
    avconv -i "${i}" -acodec pcm_s16le -ac 1 -ar 16000 "${i%.mp4}.wav"
done

for i in *.mp4; do
    avconv -i "${i}" -r 30 "mma_${i}" 
done
