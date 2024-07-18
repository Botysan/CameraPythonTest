import configparser
import asyncio
import time

import frameKeeper
import spiBottons
import viewMode

def create_and_init_spiBtn(port: int, device: int) -> spiBottons.SpiBottons:
    res = spiBottons.SpiBottons()
    if res.connect(port, device):
        print('spi connected!')
    else:
        print('spi not connected!')
        
    if res.prepare(1000):#TODO::move to settings
        print('spi prepared!')
    else:
        print('spi not prepared!')
        
    return res

def create_and_init_frameStream(ip: str, fps: int) -> frameKeeper.FrameKeeper:
    res = frameKeeper.FrameKeeper()
    res.init_stream(ip, fps)
    return res

def get_current_GUI_mode(modeID : viewMode.Mode) -> viewMode.VievMode: #how to set enum mode to call param?
    if modeID == viewMode.Mode.default:#TODO:: update python to > 3.10 ver and use switch/case
        return viewMode.VievMode()
    elif modeID == viewMode.Mode.ust:
        return viewMode.ustMode()
    elif modeID == viewMode.Mode.angle:
        return viewMode.angleMode()
    elif modeID == viewMode.Mode.zoom:
        return viewMode.zoomMode()
    elif modeID == viewMode.Mode.no_signal:
        return viewMode.noSignalMode()
    else:
        return viewMode.VievMode()

def check_btn(activeBtn : spiBottons.Bottons) -> (viewMode.Action, viewMode.Mode): #TODO::write this easy!
    #######KEY FOR SWITCH MODE START##############
    if activeBtn.right.active and activeBtn.up.active and activeBtn.zoomIn.active:#3 key for enter angle mode may be this line dont need?!
        if activeBtn.right.activeTime > 1000 and activeBtn.up.activeTime > 1000 and activeBtn.zoomIn.activeTime > 1000:#check btn pushed more then 1 sec
            return viewMode.Action.none, viewMode.Mode.angle

    elif activeBtn.enter.active and activeBtn.zoomOut.active:#2 key for enter default mode
        if activeBtn.enter.activeTime > 1000 and activeBtn.zoomOut.activeTime > 1000:
            return viewMode.Action.none, viewMode.Mode.default

    elif activeBtn.zoomIn.active and activeBtn.zoomOut.active:#2 key for enter zoom mode
        if activeBtn.zoomIn.activeTime > 1000 and activeBtn.zoomOut.activeTime > 1000:
            return viewMode.Action.none, viewMode.Mode.zoom

    elif activeBtn.cross.active:#1 key, BUT long for enter ust mode
        if activeBtn.cross.activeTime > 3000:
            return viewMode.Action.none, viewMode.Mode.ust
    #######KEY FOR SWITCH MODE END##############

    if activeBtn.left.activeTime > 100:#check btn pushed more then 0.1 sec
        return viewMode.Action.left_cursor, viewMode.Mode.none

    if activeBtn.right.activeTime > 100:#check btn pushed more then 0.1 sec
        return viewMode.Action.right_cursor, viewMode.Mode.none
    
    if activeBtn.down.activeTime > 100:#check btn pushed more then 0.1 sec
        return viewMode.Action.down_cursor, viewMode.Mode.none
    
    if activeBtn.up.activeTime > 100:#check btn pushed more then 0.1 sec
        return viewMode.Action.up_cursor, viewMode.Mode.none
    
    if activeBtn.zoomIn.activeTime > 1000:#check btn pushed more then 0.1 sec
        return viewMode.Action.zoom_In, viewMode.Mode.none

    if activeBtn.zoomOut.activeTime > 1000:#check btn pushed more then 0.1 sec
        return viewMode.Action.zoom_Out, viewMode.Mode.none
    
    if activeBtn.enter.activeTime > 1000:#check btn pushed more then 1 sec
        return viewMode.Action.enter, viewMode.Mode.none
    
    if activeBtn.cross.activeTime > 1000:#check btn pushed more then 1 sec
        return viewMode.Action.cross, viewMode.Mode.none

    return viewMode.Action.none, viewMode.Mode.none

async def main():
    #read param
    #check ping ?
    #create members
    #start check device event loop
    #if some event swap mode or do action
    
    config = configparser.ConfigParser()
    config.read('settings.ini')#TODO::use run key like -i path/to/file

    ip = config.get('camera', 'ip')
    fps = config.getint('camera', 'fps')
    centerX = config.getint('camera', 'centerPosX')
    centerY = config.getint('camera', 'centerPosY')
    wifiDeviceParam = config.get('WiFi', 'ip')
    spiPortParam = config.getint('spi', 'port')
    spiDeviceParam = config.getint('spi', 'device')
    
    cameraDataStream = create_and_init_frameStream(ip, fps)
    userIO = create_and_init_spiBtn(spiPortParam, spiDeviceParam)

    cv2.namedWindow('video', flags=cv2.WINDOW_GUI_EXPANDED)#view
    cv2.setWindowProperty('video', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    curViewMode = viewMode.VievMode()
    curViewMode.set_cursor_pos(centerX, centerY)
    curViewMode.set_cursor_color(255, 0, 0)
    
    curBtn = spiBottons.Bottons()
    curFrame = cv2.image()
    curTime = time.perf_counter()
    curAction = viewMode.Action.none
    curMode = viewMode.Mode.none
    
    #loopIO = asyncio.get_event_loop()#mb use loop.set_task_factory()?
    spiTask = asyncio.create_task(userIO.get_current_btn(0, curBtn))
    cameraTask = asyncio.create_task(cameraDataStream.get_current_frame())
    wifiTask = asyncio.create_task(cameraDataStream.get_WIFI_signal_lvl(wifiDeviceParam))
    
    while True:
        if spiTask.done():
            curBtn = spiTask.result()
            curAction, curMode = check_btn(curBtn)#TODO::Add swap cursor color
            spiTask = asyncio.create_task(userIO.get_current_btn(time.perf_counter() - curTime , curBtn))
            curTime = time.perf_counter()
        if cameraTask.done():
            curFrame = spiTask.result()
            cameraTask = asyncio.create_task(cameraDataStream.get_current_frame())
        if wifiTask.done():
            userIO.set_WIFI_lvl(wifiTask.result())
            wifiTask = asyncio.create_task(cameraDataStream.get_WIFI_signal_lvl(wifiDeviceParam))

        #warning! if we dont have frame need to start no_sig mode!!!!!
        if(type(curFrame).__name__ == "NoneType"):
            curMode = viewMode.Mode.no_signal

        if not curMode == viewMode.Mode.none:
            curViewMode = get_current_GUI_mode(curMode)
        imgToShow = curViewMode.do_action(curFrame, action)
        cv2.imshow('video',imgToShow)
        

asyncio.run(main())
    
