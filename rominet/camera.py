import io
import time
import threading
import os.path

try:
    from picamera import PiCamera
except ImportError:
    picamera = None


class Camera(object):
    thread = None
    frame = open(os.path.join(os.path.dirname(__file__), 'images/black.jpg'), 'rb').read()
    last_access = 0
    resolution = (320, 240)

    def get_camera_frame(self):
        Camera.last_access = time.time()
        self.initialize()
        return self.frame

    def initialize(self):
        if Camera.thread is None:
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()
            while self.frame is None:
                time.sleep(0.1)

    @classmethod
    def _thread(cls):
        with PiCamera() as camera:
            camera.resolution = cls.resolution
            camera.rotation = 180
            camera.framerate = 5

            time.sleep(2)

            stream = io.BytesIO()
            for _ in camera.capture_continuous(stream, 'jpeg',
                                               use_video_port=True):
                stream.seek(0)
                cls.frame = stream.read()
                stream.seek(0)
                stream.truncate()

                if time.time() - cls.last_access > 10:
                    break
        cls.thread = None
