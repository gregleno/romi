import io
import time
from picamera import PiCamera
import threading


class Camera(object):
    thread = None
    frame = None
    last_access = 0

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
            camera.resolution = (320, 240)
            camera.rotation = 180
            camera.framerate = 5

            time.sleep(2)

            stream = io.BytesIO()
            for foo in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                stream.seek(0)
                cls.frame = stream.read()
                stream.seek(0)
                stream.truncate()

                if time.time() - cls.last_access > 10:
                    break
        cls.thread = None
