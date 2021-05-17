from django.views.decorators import gzip
from django.http import StreamingHttpResponse
import cv2
import threading
from django.shortcuts import render

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture('udpsrc port=8021  caps = "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" ! rtpjitterbuffer ! rtph264depay ! decodebin  ! videoconvert ! appsink',
            cv2.CAP_GSTREAMER)
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        image = self.frame #numpy ndarray
        # jpg didn't worked!!!!!
        _,png = cv2.imencode('.png', image)
        return png.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@gzip.gzip_page
def livefe(request):
    try:
        cam = VideoCamera()
        return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    except:  # Should Handle Error!!!!!
        pass

def index(request):
    return render(request, 'cctv/index.html')
