#!Anaconda/anaconda/python
# coding: utf-8

"""
从视屏中识别人脸，并实时标出面部特征点
"""

import numpy as np  # 数据处理的库numpy
import cv2  # 图像处理的库OpenCv
import wx  # 构造显示界面的GUI

COVER = 'camera.png'


class face_emotion(wx.Frame):

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(600, 600))
        self.panel = wx.Panel(self)
        self.Center()

        # 封面图片

        # 显示图片在panel上
        self.bmp = wx.StaticBitmap(self.panel, -1, wx.EmptyBitmap(400,300))

        start_button = wx.Button(self.panel, label='Start')
        close_button = wx.Button(self.panel, label='Close')

        self.Bind(wx.EVT_BUTTON, self.learning_face, start_button)
        self.Bind(wx.EVT_BUTTON, self.close_face, close_button)

        # 基于GridBagSizer的界面布局
        # 先实例一个对象
        self.grid_bag_sizer = wx.GridBagSizer(hgap=5, vgap=5)
        # 注意pos里面是先纵坐标后横坐标
        self.grid_bag_sizer.Add(self.bmp, pos=(0, 0), flag=wx.ALL | wx.EXPAND, span=(4, 4), border=5)
        self.grid_bag_sizer.Add(start_button, pos=(4, 1), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, span=(1, 1), border=5)
        self.grid_bag_sizer.Add(close_button, pos=(4, 2), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, span=(1, 1), border=5)

        self.grid_bag_sizer.AddGrowableCol(0, 1)
        # grid_bag_sizer.AddGrowableCol(0,2)

        self.grid_bag_sizer.AddGrowableRow(0, 1)
        # grid_bag_sizer.AddGrowableRow(0,2)

        self.panel.SetSizer(self.grid_bag_sizer)
        # 界面自动调整窗口适应内容
        self.grid_bag_sizer.Fit(self)

        """dlib的初始化调用"""
        # 使用人脸检测器get_frontal_face_detector

    def _learning_face(self, event):
        # 建cv2摄像头对象，这里使用电脑自带摄像头，如果接了外部摄像头，则自动切换到外部摄像头
        self.cap = cv2.VideoCapture('rtsp://admin:Password01!@192.168.1.243:554')
        # 设置视频参数，propId设置的视频参数，value设置的参数值
        self.cap.set(3, 480)
        # 截图screenshoot的计数器
        self.cnt = 0

        # cap.isOpened（） 返回true/false 检查初始化是否成功
        while (self.cap.isOpened()):

            # cap.read()
            # 返回两个值：
            #    一个布尔值true/false，用来判断读取视频是否成功/是否到视频末尾
            #    图像对象，图像的三维矩阵
            flag, im_rd = self.cap.read()
            # 每帧数据延时1ms，延时为0读取的是静态帧
            self.k = cv2.waitKey(1)

            # 待会要显示在屏幕上的字体

            height, width = im_rd.shape[:2]
            image1 = cv2.cvtColor(im_rd, cv2.COLOR_BGR2RGB)
            pic = wx.Bitmap.FromBuffer(width, height, image1)
            # 显示图片在panel上
            self.bmp.SetBitmap(pic)
            self.grid_bag_sizer.Fit(self)

        # 释放摄像头
        self.cap.release()
        # 删除建立的窗口
        # cv2.destroyAllWindows()

    def learning_face(self, event):
        """使用多线程，子线程运行后台的程序，主线程更新前台的UI，这样不会互相影响"""
        import _thread
        # 创建子线程，按钮调用这个方法，
        _thread.start_new_thread(self._learning_face, (event,))

    def close_face(self, event):
        """关闭摄像头，显示封面页"""
        self.cap.release()
        self.bmp.SetBitmap(wx.Bitmap(self.image_cover))
        self.grid_bag_sizer.Fit(self)


class main_app(wx.App):
    # OnInit 方法在主事件循环开始前被wxPython系统调用，是wxpython独有的
    def OnInit(self):
        self.frame = face_emotion(parent=None, title="Face")
        self.frame.Show(True)
        return True


if __name__ == "__main__":
    app = main_app()
    app.MainLoop()
