from multiprocessing import Process
import platform
import cv2

# This module is used to handle the stream from the cameras


class CameraStream(Process):
    def __init__(self, index, pipe_end):
        super(CameraStream, self).__init__()
        self.index = index
        self.pipe_end = pipe_end

    def run(self):
        camera = self.open_camera()
        try:
            if camera:
                while True:
                    ret, frame = camera.read()
                    if ret:
                        self.pipe_end.send(frame)

        except Exception as Error:
            print(Error)
            pass
        except KeyboardInterrupt:
            camera.release()

    def open_camera(self):
        system = platform.system()

        # Use cv2.CAP_DSHOW only for Windows
        capture_flag = cv2.CAP_DSHOW if system == "Windows" else 0
        camera = cv2.VideoCapture(self.index, capture_flag)

        # Check if the camera opened successfully
        if not camera.isOpened():
            print('Camera with index number:', self.index, 'is not connected')
            return None

        return camera
