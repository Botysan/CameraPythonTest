# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import cv2
import numpy as np
import spidev
import array as arr
from dataclasses import dataclass
import time
import configparser
import socket
import http.client
import platform
import subprocess
from concurrent.futures import ThreadPoolExecutor
import copy

@dataclass
class Cross:
    save: bool
    posX: int
    posY: int
    r: int
    g: int
    b: int
    
@dataclass
class Bottons:
    left: bool = False
    leftItter: int = 0
    right: bool = False
    rightItter: int = 0
    up: bool = False
    upItter: int = 0
    down: bool = False
    downItter: int = 0
    zoomIn: bool = False
    zoomInItter: int = 0
    zoomOut: bool = False
    zoomOutItter: int = 0
    enter: bool = False
    enterItter: int = 0
    cross: bool = False
    crossItter: int = 0
    
def ping(ip):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    cmd = ['ping', param, '1', ip]
    return subprocess.call(cmd) == 0
    
def paintCross2(img, posX, posY, color, thk = 2):
    cv2.line(img, (posX, posY + 11), (posX, posY + 114), color, thickness = thk)
    cv2.line(img, (posX, posY - 11), (posX, posY - 114), color, thickness = thk)
    cv2.line(img, (posX + 14, posY), (posX + 126, posY), color, thickness = thk)
    cv2.line(img, (posX - 14, posY), (posX - 126, posY), color, thickness = thk)
    cv2.circle(img, (posX, posY), 1, color, -1)
    
def paintCross(img, posX, posY, color, thk = 2):
    cv2.line(img, (posX, posY - 57), (posX, posY + 57), color, thickness = thk)
    cv2.line(img, (posX - 60, posY), (posX + 60, posY), color, thickness = thk)
    
def paintRectangle(img, posX, posY, color, thk = 1):
    cv2.line(img, (posX - 100, posY + 50), (posX + 100, posY + 50), color, thickness = thk)
    cv2.line(img, (posX + 100, posY + 50), (posX + 100, posY - 50), color, thickness = thk)
    cv2.line(img, (posX + 100, posY - 50), (posX - 100, posY - 50), color, thickness = thk)
    cv2.line(img, (posX - 100, posY - 50), (posX - 100, posY + 50), color, thickness = thk)
    
def prepareSPI(spi):
    spi.max_speed_hz = 10000
    spi.xfer2([0x40, 0x00, 0x00])
    spi.xfer2([0x40, 0x03, 0xFF])
    spi.xfer2([0x40, 0x0D, 0xFF])
    
def getBottons(spi, prevBtn, time):
    activateBnt = prevBtn;
    answer = spi.xfer2([0x41, 0x13, 0xFF])
    if not answer:
        print('no answer for button req')
        return Bottons()
        
    if answer[2] & 0x40:
        activateBnt.cross = True
        activateBnt.crossItter += time 
        #print('cross presed')
        #print(activateBnt.crossItter)
    else:
        activateBnt.cross = False
        #activateBnt.crossItter = 0
        
    if answer[2] & 0x80:
        activateBnt.enter = True
        activateBnt.enterItter += time
        #print('enter presed')
        #print(activateBnt.enterItter)
    else:
        activateBnt.enter = False
        activateBnt.enterItter = 0 
        
    if answer[2] & 0x20:
        activateBnt.up = True
        activateBnt.upItter += time
        #print('up presed')
        #print(activateBnt.upItter)
    else:
        activateBnt.up = False
        activateBnt.upItter = 0 
        
    if answer[2] & 0x10:
        activateBnt.down = True
        activateBnt.downItter += time
        #print('down presed')
        #print(activateBnt.downItter)
    else:
        activateBnt.down = False
        activateBnt.downItter = 0 
        
    if answer[2] & 0x02:
        activateBnt.zoomIn = True
        activateBnt.zoomInItter += time
        #print('zoomIn presed')
        #print(activateBnt.zoomInItter)
    else:
        activateBnt.zoomIn = False
        activateBnt.zoomInItter = 0 
        
    if answer[2] & 0x01:
        activateBnt.zoomOut = True
        activateBnt.zoomOutItter += time
        #print('zoomOut presed')
        #print(activateBnt.zoomOutItter)
    else:
        activateBnt.zoomOut = False
        activateBnt.zoomOutItter = 0 
        
    if answer[2] & 0x04:
        activateBnt.right = True
        activateBnt.rightItter += time
        #print('right presed')
        #print(activateBnt.rightItter)
    else:
        activateBnt.right = False
        activateBnt.rightItter = 0 
        
    if answer[2] & 0x08:
        activateBnt.left = True
        activateBnt.leftItter += time
        #print('left presed')
        #print(activateBnt.leftItter)
    else:
        activateBnt.left = False
        activateBnt.leftItter = 0 
        
    return activateBnt
    
def setWFPower(spi, value):
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
        
def circleApprox(x1, y1, x2, y2, x3, y3):
    cX = -1000.0
    cY = -1000.0

    da1 = y2 - y1
    ma1 = x2 - x1
    db1 = y3 - y2
    mb1 = x3 - x2
    if ma1 != 0 and mb1 != 0:
        ma = da1 / ma1
        mb = db1 / mb1
        if ma != mb:
            cX = (ma * mb * (y1 - y3) + mb * (x1 + x2) - ma * (x2 + x3)) / (2 * (mb - ma));
            if ma != 0:
                cY = -(1 / ma) * (cX - (x1 + x2) / 2) + (y1 + y2) / 2
            if mb != 0:
                cY = -(1 / mb) * (cX - (x2 + x3) / 2) + (y2 + y3) / 2

    da2 = y3 - y2
    ma2 = x3 - x2
    db2 = y1 - y3
    mb2 = x1 - x3
    if ma2 != 0 and mb2 != 0:
        ma = da2 / ma2
        mb = db2 / mb2
        if ma != mb:
            cX = (ma * mb * (y2 - y1) + mb * (x2 + x3) - ma * (x3 + x1)) / (2 * (mb - ma))
            if ma != 0:
                cY = -(1 / ma) * (cX - (x2 + x3) / 2) + (y2 + y3) / 2
            if mb != 0:
                cY = -(1 / mb) * (cX - (x3 + x1) / 2) + (y3 + y1) / 2
                
    da3 = y1 - y3
    ma3 = x1 - x3
    db3 = y2 - y1
    mb3 = x2 - x1
    if ma3 != 0 and mb3 != 0:
        ma = da3 / ma3
        mb = db3 / mb3
        if ma != mb:
            cX = (ma * mb * (y3 - y2) + mb * (x3 + x1) - ma * (x1 + x2)) / (2 * (mb - ma))
            if ma != 0:
                cY = -(1 / ma) * (cX - (x3 + x1) / 2) + (y3 + y1) / 2
            if mb != 0:
                cY = -(1 / mb) * (cX - (x1 + x2) / 2) + (y1 + y2) / 2

    return cX, cY
        
def findCentralCross(arrCross):
    x, y = [], []
    tmpX, tmpY = circleApprox(arrCross[0].posX, arrCross[0].posY, arrCross[1].posX, arrCross[1].posY, arrCross[2].posX, arrCross[2].posY)
    x.append(tmpX)
    y.append(tmpY)
    tmpX, tmpY = circleApprox(arrCross[1].posX, arrCross[1].posY, arrCross[2].posX, arrCross[2].posY, arrCross[3].posX, arrCross[3].posY)
    x.append(tmpX)
    y.append(tmpY)
    tmpX, tmpY = circleApprox(arrCross[2].posX, arrCross[2].posY, arrCross[3].posX, arrCross[3].posY, arrCross[0].posX, arrCross[0].posY)
    x.append(tmpX)
    y.append(tmpY)
    tmpX, tmpY = circleApprox(arrCross[3].posX, arrCross[3].posY, arrCross[0].posX, arrCross[0].posY, arrCross[1].posX, arrCross[1].posY)
    x.append(tmpX)
    y.append(tmpY)
    cX, cY, itter = 0, 0, 0
    for i in range(0, 4):
        if x[i] != -1000.0 and y[i] != -1000.0:
            cX += x[i]
            cY += y[i]
            itter += 1
    if itter != 0:
        cX = int(cX / itter)
        cY = int(cY / itter)
    else:
        cX = arrCross[0].posX
        cY = arrCross[0].posY

    return cX, cY
    
def findAngle(x1, y1, x2, y2):
    angle = np.arctan(np.absolute(y1-y2) / np.absolute(x1-x2))    
    return angle

def zoom_frame(frame, zoom_factor):
    height, width = frame.shape[:2]
    new_height = int(height * zoom_factor)
    new_width = int(width * zoom_factor)

    resized_frame = cv2.resize(frame, (new_width, new_height))
    
    roi_x = int((new_width - width) / 2)
    roi_y = int((new_height - height) / 2)
    roi_width = width
    roi_height = height

    zoomed_frame = resized_frame[roi_y:roi_y+roi_height, roi_x:roi_x+roi_width]

    return zoomed_frame
    
def getWFSignal():
    host = "192.168.0.26"
    conn = http.client.HTTPSConnection(host)
    conn.request("GET", "/status.cgi/", headers={"Host": host})
    res = conn.getresponse()
    print(res.status, res.reason)
    #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #sock.connect(("192.168.0.26", 443))
    #sock.send(b"https://192.168.0.26//status.cgi")
    #response = sock.recv(4096)
    #sock.close()
    #print(response.decode())
    
def readNextFrame(cap):
    ret, frame = cap.read()
    return frame

if __name__ == '__main__':
    
    config = configparser.ConfigParser()
    config.read('settings.ini')
    
    ip = config.get('camera', 'ip')
    centerX = config.getint('camera', 'centerPosX')
    centerY = config.getint('camera', 'centerPosY')
    pingParam = config.get('camera', 'ping')
    minX = config.getint('camera', 'minX')
    maxX = config.getint('camera', 'maxX')
    minY = config.getint('camera', 'minY')
    maxY = config.getint('camera', 'maxY')
    angleKoefX = config.getfloat('camera', 'angleKoefX')
    angleKoefY = config.getfloat('camera', 'angleKoefY')
    scalefactorX = config.getfloat('camera', 'scalefactorX')
    scalefactorY = config.getfloat('camera', 'scalefactorY')
    cR = 255
    cG = 0
    cB = 0
    
    #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #sock.connect(("www.example.com", 80))
    #sock.send(b"GET / HTTP/1.1\r\nHost:www.example.com\r\n\r\n")
    #response = sock.recv(4096)
    #sock.close()
    #print(response.decode())
    
    curPosX = centerX
    curPosY = centerY
    
    arrCross = []
    arrCross.append(Cross(False, 0, 0, 255, 255, 0))
    arrCross.append(Cross(False, 0, 0, 255, 255, 0))
    arrCross.append(Cross(False, 0, 0, 255, 255, 0))
    arrCross.append(Cross(False, 0, 0, 255, 255, 0))
    
    angCross = []
    angCross.append(Cross(False, 0, 0, 255, 255, 0))
    angCross.append(Cross(False, 0, 0, 0, 255, 0))
    
    bus = 0
    device = 0
    spi = spidev.SpiDev()
    spi.open(bus, device)
    
    prepareSPI(spi)
    
    prevTime = time.perf_counter()
    
    zoomVal = 1
    pwrWF = 10
    
    btn = Bottons()
    angModeItter = 0
    
    ustMode = False
    tecnicalUstMode = False
    angleMode = False
    zoomed = True#False
    
    cv2.namedWindow('NoWF', flags=cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('NoWF', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    findWFDevice = False
    setWFPower(spi, 0)
    noWFImg = cv2.imread('nowifi.jpg')
    noWFImg[0:720, 0:986] = noWFImg[0:720, 147:1133]
    
    while(not findWFDevice):
        if  not findWFDevice:
            cv2.imshow('NoWF',noWFImg)
            cv2.waitKey(1000)
        findWFDevice = ping(pingParam)
    
    setWFPower(spi, 73)
    
    cap = cv2.VideoCapture(ip)
    cap.set(cv2.CAP_PROP_FPS, 50)
    pool = ThreadPoolExecutor(3)
    
    ret, curFrame = cap.read()
    future = pool.submit(readNextFrame, (cap))
    
    cv2.destroyAllWindows()
    
    cv2.namedWindow('video', flags=cv2.WINDOW_GUI_EXPANDED)
    cv2.setWindowProperty('video', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN) 
       
    while(True): 
        if(future.done()):
            curFrame = future.result()
            future = pool.submit(readNextFrame, (cap))
        frame = copy.copy(curFrame)
        if(type(frame).__name__ != "NoneType"):
            frame[0:720, 0:986] = frame[0:720, 147:1133]
        checkBtn = False
        curTime = time.perf_counter()
        if curTime - prevTime > 0.02:
            btn = getBottons(spi, btn, int((curTime - prevTime)*1000))
            checkBtn = True
            prevTime = curTime

        if ustMode:
            paintCross2(frame, curPosX, curPosY, (cB, cG, cR), 2)
            for i in range(0, 4):
                if arrCross[i].save == True:
                    paintCross(frame, arrCross[i].posX, arrCross[i].posY, (arrCross[i].b, arrCross[i].g, arrCross[i].r))
        elif tecnicalUstMode:
            paintCross(frame, centerX, centerY, (cB, cG, cR))
            paintRectangle(frame, curPosX, curPosY, (cB, cG, cR))
        elif angleMode:
            paintCross(frame, centerX, centerY, (cB, cG, cR))
            paintCross2(frame, curPosX, curPosY, (cB, cG, cR), 2)
            if angCross[0].save:
                paintCross(frame, angCross[0].posX, angCross[0].posY, (angCross[0].b, angCross[0].g, angCross[0].r))
                dX = (angCross[0].posX / scalefactorX - centerX) * angleKoefX
                dY = (angCross[0].posY / scalefactorY - centerY) * angleKoefY
                cv2.putText(frame, f'dX={dX:.3f} dY={dY:.3f}', (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0,  (angCross[0].b, angCross[0].g, angCross[0].r), 2, cv2.LINE_AA)
            if angCross[1].save:
                paintCross(frame, angCross[1].posX, angCross[1].posY, (angCross[1].b, angCross[1].g, angCross[1].r))
                dX = (angCross[1].posX / scalefactorX - centerX) * angleKoefX
                dY = (angCross[1].posY / scalefactorY - centerY) * angleKoefY
                cv2.putText(frame, f'dX={dX:.3f} dY={dY:.3f}', (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0,  (angCross[1].b, angCross[1].g, angCross[1].r), 2, cv2.LINE_AA)
        elif zoomed:
            paintCross(frame, centerX, centerY, (cB, cG, cR))
        else:
            paintRectangle(frame, centerX, centerY, (cB, cG, cR))
            
        try:
            cv2.imshow('video',frame)
        except cv2.error as e:
            findWFDevice = True
            setWFPower(spi, 0)
            cv2.namedWindow('NoWF', flags=cv2.WINDOW_NORMAL)
            cv2.setWindowProperty('NoWF', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            while(not findWFDevice):
                if cv2.getWindowProperty('video', cv2.WND_PROP_VISIBLE) > 0:
                    cv2.destroyWindow('video')
                cv2.namedWindow('NoWF', flags=cv2.WINDOW_NORMAL)
                cv2.setWindowProperty('NoWF', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                cv2.imshow('NoWF',noWFImg)
                cv2.waitKey(1000)
                findWFDevice = ping(pingParam)
            
            if cv2.getWindowProperty('NoWF', cv2.WND_PROP_VISIBLE) > 0:
                cv2.destroyWindow('NoWF')
                cap = cv2.VideoCapture(ip)
                cv2.namedWindow('video', flags=cv2.WINDOW_GUI_EXPANDED)
                cv2.setWindowProperty('video', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN) 
            setWFPower(spi, 73)
        
        if checkBtn:
            if btn.cross and btn.up and btn.zoomIn:
                if btn.crossItter > 1000 and btn.upItter > 1000 and btn.zoomInItter > 1000: 
                    if not ustMode and not angleMode:
                        tecnicalUstMode = False#True
            elif btn.right and btn.up and zoomed:
                if btn.rightItter > 1000 and btn.upItter > 1000:
                    if not ustMode and not tecnicalUstMode:
                        angleMode = True
                        angCross[0].save = False
                        angCross[1].save = False
                        angModeItter = 0
            elif btn.enter and btn.zoomOut:
                if btn.enterItter > 1000 and btn.zoomOutItter > 1000:
                    ustMode = False
                    tecnicalUstMode = False
                    angleMode = False
                    zoomed = True#False
                    for i in range(0, 4):
                        arrCross[i].save = False
                    curPosX = centerX
                    curPosY = centerY
                    angModeItter = 0
                    btn.crossItter = 0
            elif btn.cross and not ustMode:
                if btn.crossItter > 2000 and zoomed:
                    ustMode = True
                    btn.crossItter = 0
            elif not btn.cross and not ustMode and btn.crossItter > 500 and btn.crossItter < 2000:
                if cR == 255 and cG == 0 and cB == 0:
                    cR, cG, cB = 0, 0, 0
                elif cR == 0 and cG == 0 and cB == 0:
                    cR, cG, cB = 255, 255, 255
                elif cR == 255 and cG == 255 and cB == 255:
                    cR, cG, cB = 255, 0, 0
                btn.crossItter = 0
            if btn.enter and btn.enterItter > 2000 :
                btn.enterItter = 0
                if ustMode:
                    itter = 0
                    for i in range(0, 4):
                        if arrCross[i].save == False:
                            arrCross[i].save = True
                            arrCross[i].posX = curPosX
                            arrCross[i].posY = curPosY
                            itter = itter + 1
                            break
                        elif arrCross[i].save == True:
                            itter = itter + 1
                    if itter == 4:
                        ustMode = False#do something save from file and calc center
                        centerX, centerY = findCentralCross(arrCross)
                        config.set('camera', 'centerPosX', str(centerX))
                        config.set('camera', 'centerPosY', str(centerY))
                        with open('settings.ini', 'w') as configfile: 
                            config.write(configfile)
                        for i in range(0, 4):
                            arrCross[i].save = False
                        curPosX, curPosY = centerX, centerY
                        angleMode = False
                    btn.crossItter = 0
                elif angleMode:
                    angCross[angModeItter % 2].save = True
                    angCross[angModeItter % 2].posX = curPosX
                    angCross[angModeItter % 2].posY = curPosY
                    angModeItter = angModeItter + 1
                elif tecnicalUstMode:
                    zoomVal += 1
                    print(str(zoomVal))
            if btn.left:
                inc = 1
                if btn.leftItter > 1000:
                    inc = 3
                if ustMode or angleMode or tecnicalUstMode:
                    curPosX = curPosX - inc
                if curPosX > maxX:
                    curPosX = maxX
                elif curPosX < minX:
                    curPosX = minX
            if btn.right:
                inc = 1
                if btn.rightItter > 1000:
                    inc = 3
                if ustMode or angleMode or tecnicalUstMode:
                    curPosX = curPosX + inc
                    if curPosX > maxX:
                        curPosX = maxX
                    elif curPosX < minX:
                        curPosX = minX
            if btn.up:
                inc = 1
                if btn.upItter > 1000:
                    inc = 3
                if ustMode or angleMode or tecnicalUstMode:
                    curPosY = curPosY - inc
                    if curPosY > maxY:
                        curPosY = maxY
                    elif curPosY < minY:
                        curPosY = minY
            if btn.down:
                inc = 1
                if btn.downItter > 1000:
                    inc = 3
                if ustMode or angleMode or tecnicalUstMode:
                    curPosY = curPosY + inc
                    if curPosY > maxY:
                        curPosY = maxY
                    elif curPosY < minY:
                        curPosY = minY
            if btn.zoomIn and btn.zoomInItter > 2000:
                print("zoomIn")
                #zoomed = True
            if btn.zoomOut and btn.zoomOutItter > 2000:
                #zoomed = False
                print("zoomOut")
                print(curPosY)
                print(curPosX)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

