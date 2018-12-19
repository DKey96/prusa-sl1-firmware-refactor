# part of SL1 firmware
# 2014-2018 Futur3d - www.futur3d.net
# 2018 Prusa Research s.r.o. - www.prusa3d.com

import os
import logging
import threading, Queue
import pygame.display
import pygame.image
import pygame.mouse
import pygame.surfarray
import pygame.font
import numpy
import zipfile
from cStringIO import StringIO
from subprocess import call

import defines

class ImagePreloader(threading.Thread):

    def __init__(self, source, overlays, workQueue, resultQueue):
        super(ImagePreloader, self).__init__()
        self.logger = logging.getLogger(__name__)
        try:
            self.zf = zipfile.ZipFile(source, 'r')
        except Exception as e:
            self.logger.exception("zip read exception:")
        #endtry
        self.overlays = overlays
        self.workQueue = workQueue
        self.resultQueue = resultQueue
        self.stoprequest = threading.Event()
    #enddef

    def run(self):
        #self.logger.debug("thread started")
        while not self.stoprequest.isSet():
            try:
                (filename, overlayName) = self.workQueue.get(timeout = 0.1)
                #self.logger.debug("preload of %s started", filename)
                filedata = self.zf.read(filename)
                filedata_io = StringIO(filedata)
                obr = pygame.image.load(filedata_io, filename).convert()
                overlay = self.overlays.get(overlayName, None)
                if overlay:
                    obr.blit(overlay, (0,0))
                #endif
                overlay = self.overlays.get('mask', None)
                if overlay:
                    obr.blit(overlay, (0,0))
                #endif
                #self.logger.debug("pixelcount of %s started", filename)
                pixels = pygame.surfarray.pixels3d(obr)
                hist = numpy.histogram(pixels, [0, 51, 102, 153, 204, 255])
                del pixels
                whitePixels = (hist[0][1] * 0.25 + hist[0][2] * 0.5 + hist[0][3] * 0.75 + hist[0][4]) / 3
                #self.logger.debug("pixelcount of %s done, whitePixels: %f", filename, whitePixels)
                self.resultQueue.put((obr, whitePixels))
                #self.logger.debug("preload of %s done", filename)
            except Queue.Empty:
                continue
            except Exception:
                self.logger.exception("ImagePreloader exception")
                self.resultQueue.put((None, None, None))
                break
            #endtry
        #endwhile
        self.zf.close()
        #self.logger.debug("thread ended")
    #enddef

    def join(self, timeout = None):
        self.stoprequest.set()
        super(ImagePreloader, self).join(timeout)
    #enddef

#endclass


class Screen(object):

    def __init__(self, hwConfig, source):
        self.logger = logging.getLogger(__name__)
        os.environ['SDL_NOMOUSE'] = '1'
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        call(['/usr/sbin/fbset', '-fb', '/dev/fb0 1440x2560-0'])
        pygame.display.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((1440,2560), pygame.FULLSCREEN, 32)
        self.screen.set_alpha(None)
        pygame.mouse.set_visible(False)
        self.getImgBlack()
        self.font = pygame.font.SysFont(None, int(5 / hwConfig.pixelSize))
        self.basepath = source
        di = pygame.display.Info()
        self.width = di.current_w
        self.height = di.current_h
        #self.logger.debug("screen size is %dx%d pixels", self.width, self.height)
        self.overlays = dict()
        self.imagePreloaderStarted = False
    #enddef

    def __del__(self):
        self.exit()
    #enddef

    def exit(self):
        if self.imagePreloaderStarted:
            self.imagePreloader.join()
        #endif
        pygame.quit()
    #enddef

    def startPreloader(self):
        self.workQueue = Queue.Queue()
        self.resultQueue = Queue.Queue()
        self.imagePreloader = ImagePreloader(self.basepath, self.overlays, self.workQueue, self.resultQueue)
        self.imagePreloader.start()
        self.imagePreloaderStarted = True
    #enddef

    def getImgBlack(self):
        self.screen.fill((0,0,0))
        pygame.display.flip()
        self.writefb()
    #enddef

    def fillArea(self, area, color = (0,0,0)):
        pygame.display.update(self.screen.fill(color, area))
    #enddef

    def writefb(self):
        with open('/dev/fb0', 'wb') as fb:
            fb.write(self.screen.get_buffer())
    #enddef

    def getImg(self, filename, base = None):
        # obrazky jsou rozbalene nebo zkopirovane do ramdisku
        if base is None:
            base = self.basepath
        #endif
        #self.logger.debug("view of %s started", base + filename)
        obr = pygame.image.load(os.path.join(base, filename)).convert()
        self.screen.blit(obr, (0,0))
        pygame.display.flip()
        self.writefb()
        #self.logger.debug("view of %s done", base + filename)
    #enddef

    def preloadImg(self, filename, overlayName):
        self.workQueue.put((filename, overlayName))
    #enddef

    def blitImg(self):
        (obr, whitePixels) = self.resultQueue.get()
        if obr is None:
            raise Exception("ImagePreloader exception")
        #endif

        #self.logger.debug("blit started")
        self.screen.blit(obr, (0,0))
        pygame.display.flip()
        self.writefb()
        #self.logger.debug("blit done")
        return whitePixels
    #enddef

    def inverse(self):
        pixels = pygame.surfarray.pixels3d(self.screen)
        pixels ^= 2 ** 32 - 1
        del pixels
        pygame.display.flip()
        self.writefb()
    #enddef

    def createMask(self):
        try:
            zf = zipfile.ZipFile(self.basepath, 'r')
        except Exception as e:
            self.logger.exception("zip read exception:")
            return
        #endtry
        try:
            filedata = zf.read(defines.maskFilename)
        except KeyError as e:
            self.logger.info("No mask picture in the project")
            return
        #endtry
        filedata_io = StringIO(filedata)
        self.overlays['mask'] = pygame.image.load(filedata_io, defines.maskFilename).convert_alpha()
    #enddef

    def createCalibrationOverlay(self, areas, baseTime, timeStep):
        self.overlays['calibPad'] = pygame.Surface((self.width, self.height), pygame.SRCALPHA).convert_alpha()
        self.overlays['calib'] = pygame.Surface((self.width, self.height), pygame.SRCALPHA).convert_alpha()
        spacingX = 1.5
        spacingY = 1.5
        for area in areas:
            text = "%.2f" % baseTime
            surf = pygame.transform.flip(self.font.render(text, True, (255,255,255)), True, False).convert_alpha()
            rect = surf.get_rect()
            padX = rect.w * spacingX
            padY = rect.h * spacingY
            ofsetX = int((padX - rect.w) / 2)
            ofsetY = int((padY - rect.h) / 2)
            #self.logger.debug("rectW:%d rectH:%d", rect.w, rect.h)
            #self.logger.debug("padX:%d padY:%d", padX, padY)
            #self.logger.debug("ofsetX:%d ofsetY:%d", ofsetX, ofsetY)
            startX = int(area[0][0] + ((area[1][0] - padX) / 2))
            startY = area[0][1]
            #self.logger.debug("startX:%d startY:%d", startX, startY)
            self.overlays['calibPad'].fill((255,255,255), ((startX, startY), (padX, padY)))
            self.overlays['calib'].blit(surf, (startX + ofsetX, startY + ofsetY))
            baseTime += timeStep
        #endfor
    #enddef

    def testBlit(self, obr, overlayName = None):
        self.screen.blit(obr, (0,0))
        overlay = self.overlays.get(overlayName, None)
        if overlay:
            self.screen.blit(overlay, (0,0))
        #endif
        pygame.display.flip()
        self.writefb()
    #enddef

#endclass
