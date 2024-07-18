import cv2
import http.client
import platform
import subprocess

class FrameKeeper:
    def __init__(self) -> None:
        self.__capture = VideoCapture()

    def init_stream(self, ip: str, fps: int) -> bool:
        self.__capture = cv2.VideoCapture(ip)
        self.__capture.set(cv2.CAP_PROP_FPS, fps)

    async def get_current_frame(self):#return?
        ret, frame = self.__capture.read()
        return frame

    @staticmethod
    def ping_camera_addres(ip: str) -> bool:
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        cmd = ['ping', param, '1', ip]
        return subprocess.call(cmd) == 0

    @staticmethod
    async def get_WIFI_signal_lvl(deviceAdr: str) -> int:#TODO::parce response
        conn = http.client.HTTPSConnection(deviceAdr)
        conn.request("GET", "/status.cgi/", headers={"Host": deviceAdr})
        res = conn.getresponse()
        print(res.status, res.reason)
        #another way
        #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #sock.connect(("192.168.0.26", 443))
        #sock.send(b"https://192.168.0.26//status.cgi")
        #response = sock.recv(4096)
        #sock.close()
        #print(response.decode())
        return 73


