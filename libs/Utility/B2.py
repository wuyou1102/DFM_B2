# -*- encoding:UTF-8 -*-
import requests
import re
import time
from bs4 import BeautifulSoup

token_pattern = re.compile(r"data:{'token':'(.*?)'")
version_pattern = re.compile(r"Products\(Current Version：(.*?)\)")
login_url = "http://{address}/login.php"
login_check_url = "http://{address}/login_check.php"

TYF_CONFIG = {
    1: (4, 3, 1),
    2: (4, 3, 3),
    3: (4, 3, 5),
    4: (4, 4, 5),
    5: (4, 5, 5),
    6: (17, 3, 5),
    7: (17, 4, 5),
    8: (17, 5, 5),
    9: (7, 3, 5),
    10: (7, 4, 5),
    11: (7, 5, 5),
    12: (12, 3, 5),
    13: (12, 4, 5),
    14: (12, 5, 5),
}


class WebSever(object):
    def __init__(self, address):
        self._address = address
        self._token = ""
        self._session = requests.Session()

    def __post(self, url, data):
        resp = self._session.post(url=url, data=data)
        return resp

    def __get(self, url):
        resp = self._session.get(url=url)
        return resp

    def __get_token(self):
        resp = self.__get(url=login_url.format(address=self._address))
        if resp.status_code == 200:
            token = re.findall(token_pattern, resp.content)[0]
            return token
        else:
            raise IOError("Can not reach the web server: %s " % resp.status_code)

    def __login(self):
        if not self._token:
            if not self.Login():
                raise IOError("Can not login the server")
        return True

    def Login(self):
        token = self.__get_token()
        url = login_check_url.format(address=self._address)
        data = {
            'token': token,
            'password': '666666',
        }
        resp = self.__post(url=url, data=data)
        if resp.status_code == 200 and resp.content == '{"code":"0","message":"Login success","data":"Array"}':
            self._token = token
            return True
        self._token = ''
        return False

    def SetAsBS(self, NW_ID, TYF):
        self.__login()
        url = "http://{address}/write_txt.php".format(address=self._address)
        data = {
            'USR_ID': 0,
            'NW_NUM': 1,
            'NW_ID': NW_ID,
            'NW_ID0': NW_ID,
            'NW_ID1': NW_ID + 1,
            'NW_ID2': NW_ID + 2,
            'NW_ID3': NW_ID + 3,
            'FN_INDEX': TYF_CONFIG[TYF][0],
            'DEV_TYPE': 0,
            'BAND': 2,
            'UL_BW': TYF_CONFIG[TYF][1],
            'UL_MCS': TYF_CONFIG[TYF][2],
            'RF_PWR': 15,
            'FERQ': 0,
            'token': self._token,
            'time': int(time.time())
        }
        resp = self.__post(url=url, data=data)
        if resp.status_code == 200 and resp.content == '{"code":"0","message":"success"}':
            return True
        return False

    def SetAsND(self, USR_ID, NW_ID, NW_NUM=1, NW_ID1=None, NW_ID2=None, NW_ID3=None):
        self.__login()
        NW_ID1 = NW_ID1 if NW_ID1 is not None else NW_ID + 1
        NW_ID2 = NW_ID2 if NW_ID2 is not None else NW_ID + 2
        NW_ID3 = NW_ID3 if NW_ID3 is not None else NW_ID + 3
        url = "http://{address}/write_txt.php".format(address=self._address)
        data = {
            'USR_ID': USR_ID,
            'NW_NUM': NW_NUM,
            'NW_ID0': NW_ID,
            'NW_ID1': NW_ID1,
            'NW_ID2': NW_ID2,
            'NW_ID3': NW_ID3,
            'FN_INDEX': 4,
            'DEV_TYPE': 1,
            'BAND': 2,
            'UL_BW': 3,
            'UL_MCS': 1,
            'RF_PWR': 15,
            'FERQ': 0,
            'token': self._token,
            'time': int(time.time())
        }
        resp = self.__post(url=url, data=data)
        if resp.status_code == 200 and resp.content == '{"code":"0","message":"success"}':
            return True
        return False

    def RebootDevice(self):
        url = "http://{address}/upload.php?signal=9".format(address=self._address)
        try:
            self.__get(url=url)
        except requests.exceptions.ChunkedEncodingError:
            return True
        except requests.exceptions.ConnectionError:
            return True
        finally:
            self._token = ""

    def GetVersion(self):
        self.__login()
        url = "http://{address}/index.php".format(address=self._address)
        resp = self.__get(url=url)
        if resp.status_code == 200:
            version = re.findall(version_pattern, resp.content)[0]
            return version
        return ""

    def GetConfig(self):
        self.__login()
        url = "http://{address}/index.php".format(address=self._address)
        resp = self.__get(url=url)
        soup = BeautifulSoup(resp.content, "html.parser")
        count = 0
        for a in soup.find_all('option'):
            try:
                d = a.get('value').split('_')
                if len(d) == 3:
                    count += 1
                    z = [int(x) for x in d]
                    print '%s:%s,' % (count, tuple(z))
            except Exception:
                pass

    def isStart(self):
        try:
            resp = self._session.request(method='get', url='http://{address}/login.php'.format(address=self._address),
                                         timeout=1)
            if resp.status_code == 200:
                return True
            return False
        except requests.ConnectTimeout:
            return False
        except requests.ReadTimeout:
            return False
        except requests.ConnectionError:
            return False


if __name__ == '__main__':
    ws = WebSever('192.168.1.1')
    # ws.Login()
    ws.SetAsBS(4444, 5)

    # ws.Login()
    # ws.Set(USR_ID=0, NW_ID=1, FN_INDEX=7, DEV_TYPE=1, BAND=2, UL_BW=4, UL_MCS=5, FERQ=0)
    # ws.RebootDevice()
    # while True:
