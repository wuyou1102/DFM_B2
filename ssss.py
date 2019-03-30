import wx
from PIL import Image
import cv2

video = cv2.VideoCapture('rtsp://admin:Password01!@192.168.1.243:554')
print video.isOpened()

SIZE = (600, 400)


def get_image():
    # Put your code here to return a PIL image from the camera.
    ret, img = video.read()
    a = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    a = a.resize(SIZE)

    return a


def pil_to_wx(image):
    width, height = image.size
    buffer = image.convert('RGB').tobytes()
    bitmap = wx.Bitmap.FromBuffer(width, height, buffer)
    return bitmap


class Panel(wx.Panel):
    def __init__(self, parent):
        super(Panel, self).__init__(parent, -1)
        self.SetSize(SIZE)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.update()

    def update(self):
        self.Refresh()
        self.Update()
        wx.CallLater(15, self.update)

    def create_bitmap(self):
        image = get_image()
        bitmap = pil_to_wx(image)
        return bitmap

    def on_paint(self, event):
        bitmap = self.create_bitmap()
        dc = wx.AutoBufferedPaintDC(self)
        dc.DrawBitmap(bitmap, 0, 0)


class Frame(wx.Frame):
    def __init__(self):
        style = wx.DEFAULT_FRAME_STYLE & ~wx.RESIZE_BORDER & ~wx.MAXIMIZE_BOX
        super(Frame, self).__init__(None, -1, 'Camera Viewer', style=style)
        panel = Panel(self)
        self.Fit()


def main():
    app = wx.App()
    frame = Frame()
    frame.Center()
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
