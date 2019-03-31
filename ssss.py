import cv2

a = cv2.VideoCapture("rtsp://admin:Password01!@192.168.1.243:554")
print a.isOpened()
print(a.read())

# SIZE = (600, 400)
# from libs.Utility import Timeout
# def check_thread
#
# class Panel(wx.Panel):
#     def __init__(self, parent):
#         super(Panel, self).__init__(parent, -1)
#         self.video = cv2.VideoCapture('rtsp://admin:Password01!@192.168.1.243:554')
#         self.SetSize(SIZE)
#         self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
#         self.Bind(wx.EVT_PAINT, self.on_paint)
#         self.update()
#
#     def update(self):
#         from libs.Utility import ThreadManager
#         thread = ThreadManager.append_thread(self.play)
#
#
#     def play(self):
#         while True:
#             print self.video.isOpened()
#             import time
#             time.sleep(0.015)
#             bitmap = self.create_bitmap()
#             self.set_value(bitmap=bitmap)
#             self.Refresh()
#             self.Update()
#
#     def pil_to_wx(self, image):
#         width, height = image.size
#         buffer = image.convert('RGB').tobytes()
#         bitmap = wx.Bitmap.FromBuffer(width, height, buffer)
#         return bitmap
#
#     def get_image(self):
#         # return
#         # Put your code here to return a PIL image from the camera.
#         ret, img = self.video.read()
#         if img is None:
#             self.video = cv2.VideoCapture('rtsp://admin:Password01!@192.168.1.243:554')
#             return Image.new("RGB", tuple(self.GetSize()), color='black')
#         a = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
#         return a.resize(self.GetSize())
#
#     @Timeout.timeout(1)
#     def create_bitmap(self):
#         image = self.get_image()
#         bitmap = self.pil_to_wx(image)
#         return bitmap
#
#     def set_value(self, bitmap):
#         self.bitmap = bitmap
#
#     def on_paint(self, event):
#         dc = wx.AutoBufferedPaintDC(self)
#         dc.DrawBitmap(self.bitmap, 0, 0)
#
#
# class Frame(wx.Frame):
#     def __init__(self):
#         super(Frame, self).__init__(None, -1, 'Camera Viewer')
#         panel = Panel(self)
#         self.Fit()
#
#
# def main():
#     app = wx.App()
#     frame = Frame()
#     frame.Center()
#     frame.Show()
#     app.MainLoop()
#
#
# if __name__ == '__main__':
#     main()
