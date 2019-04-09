# -*- encoding:UTF-8 -*-
import wx

COMMON_1 = wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL)
COMMON_1_BOLD = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD)
COMMON_1_LARGE = wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL)
COMMON_1_LARGE_BOLD = wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD)
COMMON_1_ITALIC_BOLD = wx.Font(10, wx.SWISS, wx.ITALIC, wx.BOLD)
COMMON_1_SLANT_BOLD = wx.Font(10, wx.SWISS, wx.SLANT, wx.BOLD)

TEST_TITLE = wx.Font(30, wx.SWISS, wx.NORMAL, wx.BOLD)
DESC = wx.Font(22, wx.SWISS, wx.NORMAL, wx.BOLD)
REPORT_LARGE = wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL)
NORMAL_14 = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
NORMAL_20 = wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
NORMAL_20_BOLD = wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.BOLD)

# family用于快速指定一个字体而无需知道该字体的实际的名字.字体的准确选择依赖于系统和具体可用的字体.你所得到的精确的字体将依赖于你的系统。字体类别如下:
# wx.DECORATIVE：一个正式的，老的英文样式字体。
# wx.DEFAULT：系统默认字体。
# wx.MODERN：一个单间隔（固定字符间距）字体。
# wx.ROMAN：serif字体，通常类似于Times New Roman。
# wx.SCRIPT：手写体或草写体
# wx.SWISS：sans-serif字体，通常类似于Helvetica或Arial。
# style参数指明字体的是否倾斜，它的值有：
# wx.NORMAL,
# wx.SLANT,
# wx.ITALIC
# weight参数指明字体的醒目程度，他的值有:
# wx.NORMAL,
# wx.LIGHT,
# wx.BOLD
# underline参数仅工作在Windows系统下，如果取值为True，则加下划线，False为无下划线。
# faceName参数指定字体名。
# encoding参数允许你在几个编码中选择一个，它映射内部的字符和字本显示字符。编码不是Unicode编码，只是用于wxPython的不同的8位编码。大多数情况你可以使用默认编码。


def customize(*args):
    return wx.Font(*args)
