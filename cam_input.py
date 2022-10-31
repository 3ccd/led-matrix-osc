import time
from samplebase import SampleBase
from PIL import Image
import cv2


class CamInput(SampleBase):
    def __init__(self, *args, **kwargs):
        super(CamInput, self).__init__(*args, **kwargs)
        self.cap = cv2.VideoCapture(0)

    def run(self):

        double_buffer = self.matrix.CreateFrameCanvas()

        # let's scroll
        while True:
            ret, frame = self.cap.read()
            if ret is False:
                time.sleep(0.5)
                continue

            dst = cv2.resize(frame, dsize=(64, 32), interpolation=cv2.INTER_LINEAR)
            dst = cv2.cvtColor(dst, cv2.COLOR_BGR2RGB)

            pil_image = Image.fromarray(dst)

            double_buffer.SetImage(pil_image)

            double_buffer = self.matrix.SwapOnVSync(double_buffer)
            time.sleep(0.01)

# Main function
# e.g. call with
#  sudo ./image-scroller.py --chain=4
# if you have a chain of four
if __name__ == "__main__":
    image_scroller = CamInput()
    if (not image_scroller.process()):
        image_scroller.print_help()