import threading
import time

import SimpleCV
import timer


class Camera:

    def __init__(self):
        self.camera = SimpleCV.Camera()
        self.objTracker = ObjTracker(self.camera)
        self.lineTracker = LineTracker(self.camera)
        self.lineTrackerBox = LineTrackerBox(self.camera)
        self.display = False

    def _show(self, freq):

        self.display = True

        while self.display:

            t0 = time.time()

            img = self.camera.getImage()

            topCropH = 60
            img = img.resize(w=200)
            img = img.crop(0, topCropH, img.width, img.height - topCropH)
            img.show()

            dt = time.time() - t0
            if dt < 1 / freq:
                time.sleep(1 / freq - dt)

    def show(self, freq=20):
        th = threading.Thread(target=self._show, args=[freq])
        th.start()

    def stop(self):
        self.display = False


class LineTracker:

    def __init__(self, camera, display=False):
        self.camera = camera
        self.display = display
        self.active = False
        self.nbLines = 0
        self.lines = []
        self.linesHPos = []
        self.linesAreaRatio = []

    def _trackLines(self, freq):

        self.active = True

        while self.active:

            t0 = time.time()

            img = self.camera.getImage()

            # Resize and crop image (crop values pixel values apply before resize)
            topCrop = 256
            botCrop = 0
            leftCrop = 0
            rightCrop = 0
            img = img.crop(leftCrop, topCrop, img.width - leftCrop - rightCrop,
                           img.height - topCrop - botCrop)
            img = img.resize(w=200)

            # Isolate path lines (green masking tape)
            iCol = img.hueDistance(color=(40, 156, 100), minsaturation=120)
            iBin = iCol.binarize()

            # Mask center of image with black box
            contWidth = 16
            dl = iBin.dl()
            size = (iBin.width - contWidth, iBin.height - contWidth)
            center = (iBin.width / 2, iBin.height / 2)
            dl.centeredRectangle(center, size, SimpleCV.Color.BLACK, 0, True)
            iBox = iBin.applyLayers()
            iBoxContArea = float(iBox.area() - size[0] * size[1])

            self.lines = iBox.findBlobs(minsize=20)

            # Define specific locations for distance calculations
            topCtr = (iBox.width / 2, 0)
            btmCtr = (iBox.width / 2, iBox.height)
            ctrLeft = (0, iBox.height / 2)
            ctrRight = (iBox.width, iBox.height / 2)

            if self.lines is not None:
                self.nbLines = self.lines.count()
                # Find line blob at bottom center
                self.lines = self.lines.sortDistance(btmCtr)
                btmLine = self.lines[0]
                if self.nbLines > 1:
                    # Remove bottom line blob from blobs
                    self.lines.__delitem__(0)
                    # Sort remaining line blobs from left to right
                    self.lines = self.lines.sortX()

                    # For each remaining line, get and store HPos and Area
                    self.linesHPos = []
                    self.linesAreaRatio = []
                    for i in range(len(self.lines)):
                        x, y = self.lines[i].centroid()
                        self.linesHPos.append((iBox.width / 2 - x) / (iBox.width / 2))
                        area = self.lines[i].area()
                        self.linesAreaRatio.append(self.lines[i].area() / iBoxContArea)

                    # Re-insert bottom line blob at index 0
                    self.lines.insert(0, btmLine)
                    x, y = btmLine.centroid()
                    self.linesHPos.insert(0, (iBox.width / 2 - x) / (iBox.width / 2))
                    area = btmLine.area()
                    self.linesAreaRatio.insert(0, area / iBoxContArea)

            else:
                self.nbLines = 0
                self.lines = []
                self.linesHPos = []
                self.linesAreaRatio = []
                btmLine = None
                topLine = None

            # Display processed line blobs
            if self.display:
                dl = img.dl()
                if self.nbLines != 0:
                    if self.nbLines == 2:
                        topLine = self.lines[1]
                        topLine.draw(layer=dl, color=SimpleCV.Color.LIME, width=-1)
                    elif self.nbLines > 2:
                        for line in self.lines:
                            line.draw(layer=dl, color=SimpleCV.Color.GOLD, width=-1)
                    btmLine.draw(layer=dl, color=SimpleCV.Color.HOTPINK, width=-1)
                    img.applyLayers().show()
                else:
                    img.show()

            dt = time.time() - t0
            if dt < 1. / freq:
                time.sleep(1. / freq - dt)

    def trackLines(self, freq=10):
        th = threading.Thread(target=self._trackLines, args=[freq])
        th.start()

    # Change to stock actual frame x & y for blobs centroids and use get
    # functions to return HPos in relation to frame center

    def stop(self):
        self.active = False
        self.nbLines = 0
        self.lines = []
        self.linesHPos = []
        self.linesAreaRatio = []

    def getLinesHPos(self, line):
        if len(self.linesHPos) > line:
            return self.linesHPos[line]
        else:
            return 0

    def getLinesAreaRatio(self, line):
        if len(self.linesAreaRatio) > line:
            return self.linesAreaRatio[line]
        else:
            return 0

    def getNbLines(self):
        return self.nbLines

    def setDisplay(self, display):
        self.display = display

    def hasLines(self):
        if self.nbLines > 0:
            return True
        else:
            return False


class LineTrackerBox:

    def __init__(self, camera, display=False):
        self.camera = camera
        self.active = False
        self.btm = False
        self.btmHPos = []
        self.btmAreaRatio = []
        self.top = False
        self.topAreaRatio = []
        self.left = False
        self.right = False
        self.intersection = []

    def _trackLines(self, freq):

        self.active = True
        lTimer = Timer()

        while self.active:

            img = self.camera.getImage()

            # Resize and crop image (crop values pixel values apply before resize)
            topCrop = 256
            botCrop = 0
            leftCrop = 0
            rightCrop = 0
            # Crop before resize to avoid SimpleCV bug
            img = img.crop(leftCrop, topCrop, img.width - leftCrop - rightCrop,
                           img.height - topCrop - botCrop)
            img = img.resize(w=256)

            # Isolate path lines (green masking tape)
            iBin = img.hueDistance(color=(40, 156, 100), minsaturation=120).binarize()

            # Isolate zone images
            cWidth = 8
            imgTop = iBin.crop((cWidth, 0), (img.width - cWidth, cWidth))
            imgBtm = iBin.crop((0, img.height - cWidth), (img.width, img.height))
            imgLeft = iBin.crop((0, 0), (cWidth, img.height - cWidth))
            imgRight = iBin.crop((img.width - cWidth, 0), (img.width, img.height - cWidth))

            # Reset intersection configuration
            intersection = 0

            # Analyse bottom image
            blobsBtm = imgBtm.findBlobs(minsize=20)
            if blobsBtm is not None:
                blobsBtm = blobsBtm.sortArea()
                self.btm = True
                x, y = blobsBtm[0].centroid()
                self.btmHPos = (imgBtm.width / 2. - x) / (imgBtm.width / 2.)
                self.btmAreaRatio = blobsBtm[0].area() / float(imgBtm.area())
            else:
                self.btm = False
                self.btmHPos = []
                self.btmAreaRatio = []

            # Analyse top image
            blobsTop = imgTop.findBlobs(minsize=20)
            if blobsTop is not None:
                blobsTop = blobsTop.sortArea()
                self.top = True
                self.topAreaRatio = blobsTop[0].area() / float(imgTop.area())
                intersection += 2
            else:
                self.top = False
                self.topAreaRatio = []

            # Analyse left image
            blobsLeft = imgLeft.findBlobs(minsize=20)
            if blobsLeft is not None:
                self.left = True
                intersection += 1
            else:
                self.left = False

            # Analyse right image
            blobsRight = imgRight.findBlobs(minsize=20)
            if blobsRight is not None:
                self.Right = True
                intersection += 4
            else:
                self.Right = False

            blobs = iBin.findBlobs()
            if blobs is not None:
                blobs = blobs.sortArea()
                if (blobs[0].area() / iBin.area()) > .5:
                    intersection = 8

            self.intersection = intersection

            lTimer.sleepToElapsed(1. / freq)

    def trackLines(self, freq=20):
        th = threading.Thread(target=self._trackLines, args=[freq])
        th.start()

    def stop(self):
        self.active = False
        self.btm = False
        self.btmHPos = []
        self.btmAreaRatio = []
        self.top = False
        self.topAreaRatio = []
        self.left = False
        self.right = False
        self.intersection = []

    def getBtmHPos(self):
        if self.btm:
            return self.btmHPos
        else:
            return 0

    def getBtmAreaRatio(self):
        return self.btmAreaRatio

    def getTopAreaRatio(self):
        return self.topAreaRatio

    def getIntersection(self):
        if self.btm:
            return self.intersection
        else:
            return -1


class ObjTracker:

    def __init__(self, camera, display=False):
        self.camera = camera
        self.display = display
        self.active = False
        self.nbObj = 0
        self.objHPos = []
        self.objAreaRatio = []

    def _trackObjByHue(self, hue, freq):

        self.active = True

        while self.active:

            t0 = time.time()

            img = self.camera.getImage()

            topCropH = 60
            img = img.resize(w=200)
            img = img.crop(0, topCropH, img.width, img.height - topCropH)

            col = SimpleCV.Color.hueToBGR(hue)
            iBin = img.hueDistance(color=col, minsaturation=120).binarize(50)

            blobs = iBin.findBlobs()

            if blobs is not None:
                self.nbObj = 1
                blobs.sortArea()
                obj = blobs[0]
                x, y = obj.centroid()
                self.objHPos = (img.width / 2 - x) / (img.width / 2)
                self.objAreaRatio = obj.area() / img.area()
                if self.display:
                    dl = img.dl()
                    obj.drawRect(layer=dl, color=(0, 255, 0), width=2)
            else:
                self.nbObj = 0
                self.objHPos = []
                self.objAreaRatio = []

            if self.display:
                img.show()

            dt = time.time() - t0
            if dt < 1. / freq:
                time.sleep(1. / freq - dt)

    def trackObjByHue(self, hue, freq=10):
        th = threading.Thread(target=self._trackObjByHue, args=(hue, freq))
        th.start()

    def stop(self):
        self.active = False
        self.nbObj = 0
        self.objHPos = []
        self.objVPos = []
        self.objAreaRatio = []

    def hasObj(self):
        if self.nbObj > 0:
            return True
        else:
            return False

    def getObjHPos(self):
        return self.objHPos

    def getObjVPos(self):
        return self.objVPos

    def getObjAreaRatio(self):
        return self.objAreaRatio

    def setDisplay(self, display):
        self.display = display
