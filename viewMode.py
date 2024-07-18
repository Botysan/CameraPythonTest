from dataclasses import dataclass
import cv2
import enum

class Action(enum.Enum):
    none = 1
    up_cursor = 2
    down_cursor = 3
    left_cursor = 4
    right_cursor = 5
    zoom_In = 6
    zoom_Out = 7
    enter = 8
    cross = 9


class Mode(enum.Enum):
    none = 0
    default = 1
    ust = 2
    angle = 3
    zoom = 4
    no_signal = 5


@dataclass
class Cross:
    save: bool
    posX: int
    posY: int
    r: int
    g: int
    b: int


def paintCross(frame, posX, posY, color, thk = 2):
    cv2.line(frame, (posX, posY + 11), (posX, posY + 114), color, thickness = thk)
    cv2.line(frame, (posX, posY - 11), (posX, posY - 114), color, thickness = thk)
    cv2.line(frame, (posX + 14, posY), (posX + 126, posY), color, thickness = thk)
    cv2.line(frame, (posX - 14, posY), (posX - 126, posY), color, thickness = thk)
    cv2.circle(frame, (posX, posY), 1, color, -1)
    
def paintCrossDiag(frame, posX, posY, color, thk = 2):
    cv2.line(frame, (posX, posY - 57), (posX, posY + 57), color, thickness = thk)
    cv2.line(frame, (posX - 60, posY), (posX + 60, posY), color, thickness = thk)
    
def paintRectangle(frame, posX, posY, color, thk = 1):
    cv2.line(frame, (posX - 100, posY + 50), (posX + 100, posY + 50), color, thickness = thk)
    cv2.line(frame, (posX + 100, posY + 50), (posX + 100, posY - 50), color, thickness = thk)
    cv2.line(frame, (posX + 100, posY - 50), (posX - 100, posY - 50), color, thickness = thk)
    cv2.line(frame, (posX - 100, posY - 50), (posX - 100, posY + 50), color, thickness = thk)


class VievMode:
    def __init__(self) -> None:
        self.centerX, self.centerY = 0, 0
        self.cR, self.cG,  self.cB = 0, 0, 0
        return

    def do_action(self, frame, action):
        return frame

    def set_cursor_pos(self, x: int, y: int) -> None:
        self.centerX, self.centerX = 0, 0
        return

    def get_cursor_pos(self) -> (int, int):
        return self.centerX, self.centerX

    def set_cursor_color(self, R: int, G: int, B: int) -> None:
        self.cR, self.cG,  self.cB = R, G, B

    def get_cursor_color(self) -> (int, int, int):
        return self.cR, self.cG,  self.cB

class ustMode(VievMode):
    def __init__(self) -> None:
        self.curPosX, self.curPosY = self.centerX, self.centerY
        self.arrCross = []
        self.arrCross.append(Cross(False, 0, 0, 255, 255, 0))
        self.arrCross.append(Cross(False, 0, 0, 255, 255, 0))
        self.arrCross.append(Cross(False, 0, 0, 255, 255, 0))
        self.arrCross.append(Cross(False, 0, 0, 255, 255, 0))
        return
    
    @staticmethod
    def find_central_cross(listData) -> (int, int):
        return self.centerX, self.centerY

    def do_action(self, frame, action):
        height, width = frame.shape[:2]
        
        if action == Action.up_cursor:#TODO:: update python to > 3.10 ver and use switch/case
            self.curPosY -= 1
            if self.curPosY > height:
                self.curPosY = height
            elif self.curPosY < 0:
                self.curPosY = 0
        elif action == Action.down_cursor:
            self.curPosY += 1
            if self.curPosY > height:
                self.curPosY = height
            elif self.curPosY < 0:
                self.curPosY = 0
        elif action == Action.left_cursor:
            self.curPosX -= 1
            if self.curPosX > width:
                self.curPosX = width
            elif self.curPosX < 0:
                self.curPosX = 0
        elif action == Action.right_cursor:
            self.curPosX += 1
            if self.curPosX > width:
                self.curPosX = width
            elif self.curPosX < 0:
                self.curPosX = 0
        elif action == Action.enter:
            itter = 0
            for i in range(4):
                if self.arrCross[i].save == False:
                    self.arrCross[i].save = True
                    self.arrCross[i].posX = self.curPosX
                    self.arrCross[i].posY = self.curPosY
                    itter = itter + 1
                    break
                elif self.arrCross[i].save == True:
                    itter = itter + 1
                if itter == 4:
                    self.centerX, self.centerY = self.find_central_cross(arrCross)#TODO::findCentralCross
                    for i in range(4):
                        self.arrCross[i].save = False        

        paintCross(frame, self.curPosX, self.curPosY, (self.cB, self.cG, self.cR), 2)
        for curCross in self.arrCross:
            if curCross.save:
                paintCrossDiag(frame, curCross.posX, curCross.posY, (curCross.b, curCross.g, curCross.r))
                
        return frame


class zoomMode(VievMode):
    def __init__(self) -> None:
        self.zoom = 1
        return
    
    @staticmethod
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
    
    def do_action(self, frame, action):
        if action == Action.zoom_In:
            self.zoom *= 1.1
        elif action == Action.zoom_Out:
            self.zoom /= 0.9
                
        return self.zoom_frame(frame, zoom)


class angleMode(VievMode):
    def __init__(self) -> None:
        self.curPosX, self.curPosY = self.centerX, self.centerY
        self.angModeItter = 0
        self.angCross = []
        self.angCross.append(Cross(False, 0, 0, 255, 255, 0))
        self.angCross.append(Cross(False, 0, 0, 0, 255, 0))
        return

    def do_action(self, frame, action):
        size = len(self.angCross)
        
        if action == Action.up_cursor:#TODO:: update python to > 3.10 ver and use switch/case
            self.curPosY -= 1
            if self.curPosY > height:
                self.curPosY = height
            elif self.curPosY < 0:
                self.curPosY = 0
        elif action == Action.down_cursor:
            self.curPosY += 1
            if self.curPosY > height:
                self.curPosY = height
            elif self.curPosY < 0:
                self.curPosY = 0
        elif action == Action.left_cursor:
            self.curPosX -= 1
            if self.curPosX > width:
                self.curPosX = width
            elif self.curPosX < 0:
                self.curPosX = 0
        elif action == Action.right_cursor:
            self.curPosX += 1
            if self.curPosX > width:
                self.curPosX = width
            elif self.curPosX < 0:
                self.curPosX = 0
        elif action == Action.enter:
            self.angCross[angModeItter % size].save = True
            self.angCross[angModeItter % size].posX = self.curPosX
            self.angCross[angModeItter % size].posY = self.curPosY
            self.angModeItter += 1

        paintCrossDiag(frame, centerX, centerY, (cB, cG, cR))
        paintCross2(frame, curPosX, curPosY, (cB, cG, cR), 2)
        
        for i in range(len(self.angCross)):
            curCross = self.angCross[i]
            if curCross.save:
                paintCross(frame, curCross.posX, curCross.posY, (curCross.b, curCross.g, curCross.r))
                dX = curCross.posX - self.centerX#(curCross.posX / scalefactorX - self.centerX) * angleKoefX
                dY = curCross.posY - self.centerY#(curCross.posY / scalefactorY - self.centerY) * angleKoefY
                cv2.putText(frame, f'dX={dX:.3f} dY={dY:.3f}', (20, 30 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0,  (curCross.b, curCross.g, curCross.r), 2, cv2.LINE_AA)
                
        return frame

class noSignalMode(VievMode):
    def __init__(self) -> None:
        return
    
    def do_action(self, frame, action):                
        return cv2.imread('nowifi.jpg')

    
