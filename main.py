import threading
import time

import numpy as np

from PIL import Image

from pythonosc import dispatcher
from pythonosc import osc_server

from rgbmatrix import RGBMatrix, RGBMatrixOptions


class FrameGrabber:

    def __init__(self, ip, port=9000):
        self.dp = dispatcher.Dispatcher()
        self.dp.map("/frame/red/upper", self.conversion, 'red_u')
        self.dp.map("/frame/red/lower", self.conversion, 'red_l')
        self.dp.map("/frame/blue/upper", self.conversion, "blue_u")
        self.dp.map("/frame/blue/lower", self.conversion, "blue_l")
        self.dp.map("/frame/green/upper", self.conversion, "green_u")
        self.dp.map("/frame/green/lower", self.conversion, "green_l")
        self.dp.map("/ping", print)

        self.ip = ip
        self.port = port
        self.server = None

        self.callback = None

        self.frame = np.zeros((32, 64, 3), dtype=np.uint8)

    def start(self):
        print("Starting Server")
        self.server = osc_server.ThreadingOSCUDPServer(
            (self.ip, self.port), self.dp)
        print("Serving on {}".format(self.server.server_address))
        thread = threading.Thread(target=self.server.serve_forever)
        thread.start()

    def conversion(self, arg, ch_list, *args):
        ch = ch_list[0]

        if len(args) < 1024:
            print('Less data received {}'.format(len(args)))
        else:
            # print('data received {}'.format(ch))
            pass

        receive_data = np.array(args, dtype=np.uint8)
        tmp = receive_data.reshape([16, 64])

        if ch == 'red_u':
            self.frame[:16, :, 0] = tmp
        elif ch == 'red_l':
            self.frame[16:, :, 0] = tmp
            if self.callback is not None:
                self.callback(self.frame)
        elif ch == 'green_u':
            self.frame[:16, :, 1] = tmp
        elif ch == 'green_l':
            self.frame[16:, :, 1] = tmp
        elif ch == 'blue_u':
            self.frame[:16, :, 2] = tmp
        elif ch == 'blue_l':
            self.frame[16:, :, 2] = tmp

    def set_callback(self, cb):
        self.callback = cb


class Display(threading.Thread):
    def __init__(self):
        super().__init__()
        self.frame = np.zeros((32, 64, 3), dtype=np.uint8)

        options = RGBMatrixOptions()
        options.rows = 32
        options.cols = 64
        options.chain_length = 1
        options.parallel = 1
        options.hardware_mapping = 'adafruit-hat'
        options.disable_hardware_pulsing = True
        options.drop_privileges = False
        self.matrix = RGBMatrix(options=options)

        self.running = True

    def test(self):
        test_frame = np.zeros([32, 64, 3], dtype=np.uint8)
        color = np.full([32, 64], 255, dtype=np.uint8)

        test_frame[:, :, 0] = color
        pil_image = Image.fromarray(test_frame)
        self.matrix.SetImage(pil_image)
        time.sleep(1)
        test_frame[:, :, :] = 0
        test_frame[:, :, 1] = color
        pil_image = Image.fromarray(test_frame)
        self.matrix.SetImage(pil_image)
        time.sleep(1)
        test_frame[:, :, :] = 0
        test_frame[:, :, 2] = color
        pil_image = Image.fromarray(test_frame)
        self.matrix.SetImage(pil_image)
        time.sleep(1)

    def set_frame(self, frame):
        self.frame = frame.copy()

    def run(self):
        while self.running:
            pil_image = Image.fromarray(self.frame)
            self.matrix.Clear()
            self.matrix.SetImage(pil_image)
            time.sleep(0.1)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    fg = FrameGrabber('192.168.1.121')
    dis = Display()
    fg.set_callback(dis.set_frame)
    dis.test()
    fg.start()
    dis.start()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
