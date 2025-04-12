import whisper
import re
import cv2
from transformers import pipeline
from moviepy.editor import VideoFileClip
from nudenet import NudeDetector

detector = NudeDetector()
classifier = pipeline("text-classification", model="unitary/toxic-bert")
model = whisper.load_model("large")

def img_filter(image_path):
    result = detector.detect(image_path)
    if result and result[0]['label'] == 'unsafe' and result[0]['unsafe'] >= 0.7:
        return True
    return False

def vid_filter(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_interval = 30
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if int(cap.get(cv2.CAP_PROP_POS_FRAMES)) % frame_interval == 0:
            tmp_path = "temp_frame.jpg"
            cv2.imwrite(tmp_path, frame)
            result = detector.detect(tmp_path)
            if result and result[0]['label'] == 'unsafe' and result[0]['unsafe'] >= 0.7:
                return True
    cap.release()
    return False

def aud_filter(video_path):
    video = VideoFileClip(video_path)
    audio_path = "temp_audio.wav"
    video.audio.write_audiofile(audio_path)
    result = model.transcribe(audio_path, language="en")
    text = result.get("text", "")
    if not text:
        return False
    results = classifier(text)
    foul_labels = ['toxic', 'obscene', 'insult', 'threat']
    for res in results:
        if res['label'].lower() in foul_labels and res['score'] > 0.1:
            return True
    return False

def txt_filter(text):
    pattern = r"\b(badword1|badword2|badword3)\b"
    return re.sub(pattern, "****", text, flags=re.IGNORECASE)