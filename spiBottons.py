#import spidev
import asyncio
from dataclasses import dataclass
import time

@dataclass
class Botton:
    active: bool = False
    activeTime: int = 0

@dataclass
class Bottons:
    left: Botton = Botton()
    right: Botton = Botton()
    up: Botton = Botton()
    down: Botton = Botton()
    zoomIn: Botton = Botton()
    zoomOut: Botton = Botton()
    enter: Botton = Botton()
    cross: Botton = Botton()

async def set_btn(activeFlag: bool, activeTime: int) -> Botton:
    if activeFlag:
        return Botton(True, activeTime)
    else:
        return Botton()

class SpiBottons:
    def __init__(self) -> None:
        self.__device = spidev.SpiDev()

    def connect(self, port: int, device: int) -> bool:
        try:
            self.__device.open(port, device)
        except:
            return False # use this because spiDev dont have isOpen metod
        return True
        

    def prepare(self, speed: int) -> bool:
        try:
            self.__device.max_speed_hz = speed
            self.__device.xfer2([0x40, 0x00, 0x00])#magic num see datasheet on device
            self.__device.xfer2([0x40, 0x03, 0xFF])
            self.__device.xfer2([0x40, 0x0D, 0xFF])
        except:
            return False
        return True

    async def get_current_btn(self, deltaTime: int, lastBtn: Bottons = Bottons()) -> Bottons:
        #use last bottons stete because need pushed time
        answer = spi.xfer2([0x41, 0x13, 0xFF])
        if not answer:
            print('no answer for button req')
            return Bottons()
        res = lastBtn
        curBtnState = answer[2]#TODO:: full parce answer!

        res.cross = set_btn(curBtnState & 0x40, res.cross.activeTime + deltaTime)
        res.enter = set_btn(curBtnState & 0x80, res.enter.activeTime + deltaTime)
        res.zoomOut = set_btn(curBtnState & 0x01, res.zoomOut.activeTime + deltaTime)
        res.zoomIn = set_btn(curBtnState & 0x02, res.zoomIn.activeTime + deltaTime)
        res.down = set_btn(curBtnState & 0x10, res.down.activeTime + deltaTime)
        res.up = set_btn(curBtnState & 0x20, res.up.activeTime + deltaTime)
        res.right = set_btn(curBtnState & 0x04, res.right.activeTime + deltaTime)
        res.left = set_btn(curBtnState & 0x08, res.left.activeTime + deltaTime)

        return res

    async def set_WIFI_lvl(self, lvl: int) -> None:
        if value > 75:
            spi.xfer2([0x40, 0x12, 0x0F])
        elif value > 50:
            spi.xfer2([0x40, 0x12, 0x07])
        elif value > 25:
            spi.xfer2([0x40, 0x12, 0x03])
        elif value > 0:
            spi.xfer2([0x40, 0x12, 0x01])
        elif value <= 0:
            spi.xfer2([0x40, 0x12, 0x00])
