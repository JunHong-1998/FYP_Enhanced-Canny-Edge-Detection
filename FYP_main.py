import sys
import os
from FYP_GUI import*
from FYP_DIP import*

class FYP_CED(QMainWindow):
    def __init__(self):
        self.tool_ori = -1
        self.tool_ehc = -1
        self.confirmation = [False, False]
        self.size = (300,300)
        super(FYP_CED, self).__init__()
        self.setWindowTitle("Enhanced Canny Edge Detection Using Integrated Filters and Edge-Chain Filtering Technique by LOW JUN HONG (BS18110173)")
        self.showMaximized()
        self.setStyleSheet("""QToolTip {
                                   background-color: black;
                                   color: white;
                                   border: 0
                                   }""")
        self.UI = WidgetUI(self)
        self.inputImage = PhotoViewer(self, (125,230,125), tooltip='Input image')
        self.inputImage.photoClicked.connect(lambda : self.zoomImage((True, -1)))
        self.outputImage = [PhotoViewer(self, (230,125,0), tooltip='Gaussian Filtered Image'),
                            PhotoViewer(self, (230,125,0), tooltip='Gradient Image'),
                            PhotoViewer(self, (230,125,0), tooltip='Thinned Image'),
                            PhotoViewer(self, (230,125,0), tooltip='Thresholded Image'),
                            PhotoViewer(self, (230,125,0), tooltip='Hysteresis Image'),
                            PhotoViewer(self, (230,125,0), tooltip='Classic Edge Map'),

                            PhotoViewer(self, (230, 0, 180), tooltip='GABF Image'),
                            PhotoViewer(self, (230, 0, 125), tooltip='Gradient Image'),
                            PhotoViewer(self, (230, 0, 125), tooltip='Thinned Image'),
                            PhotoViewer(self, (230, 0, 125), tooltip='Thresholded Image'),
                            PhotoViewer(self, (230, 0, 125), tooltip='Hysteresis Image'),
                            PhotoViewer(self, (230, 0, 180), tooltip='EC Formation Image'),
                            PhotoViewer(self, (230, 0, 180), tooltip='EC Filtering Image'),
                            PhotoViewer(self, (230, 0, 125), tooltip='Enhanced Edge Map')
                            ]
        for i,output in enumerate(self.outputImage):
            if i<=5:
                output.photoClicked.connect(lambda x=i : self.zoomImage((True, x)))
            else:
                output.photoClicked.connect(lambda x=i-6 : self.zoomImage((False, x)))
        self.initUI()
        self.CV = DIP()
        self.oriCED = [None, None, None, None, None, None, None]
        self.enhCED = [None, None, None, None, None, None, None, None, None, None, None]

    def initUI(self):
        mainBG = self.UI.CanvasLabel("FYP/mainBG.png", True, True, Qt.AlignCenter)
        mainLay = QVBoxLayout()
        mainLay.addLayout(self.titleBAR())

        mainBG.setLayout(mainLay)
        self.setCentralWidget(mainBG)
        cover = self.UI.cover()
        cover[1].addWidget(self.UI.PushBtnIcon("FYP/start.png", lambda : self.exitCover(cover[0]), size=(250,100)))
        cover[0].exec_()      ###################### cover please reopen !!

        bottomLay = QHBoxLayout()
        bottomLay.addWidget(self.Controls())
        bottomLay.addWidget(self.Intermediate())
        bottomLay.addLayout(self.FinalOutput())
        empty = QWidget()
        empty.setFixedWidth(5)
        bottomLay.addWidget(empty)
        bottomLay.addLayout(self.benchmark())
        bottomLay.addWidget(empty)
        mainLay.addLayout(bottomLay)

    def titleBAR(self):
        lay = QHBoxLayout()
        lay.addWidget(self.UI.CanvasLabel("FYP/UMSlogo.png", True, True, Qt.AlignLeft, fixedSize=(350,120)))
        lay.addWidget(self.UI.Label_TextOnly("ENHANCED CANNY EDGE DETECTION USING INTEGRATED FILTERS\nAND EDGE-CHAIN FILTERING TECHNIQUE", ("Times New Roman BOLD", 20), align=Qt.AlignCenter))
        lay.addWidget(self.UI.CanvasLabel("FYP/MCGlogo.png", True, True, Qt.AlignRight, fixedSize=(230,120)))
        lay.setAlignment(Qt.AlignTop)
        return lay

    def exitCover(self, msg):
        msg.close()

    def Controls(self):
        leftWDG = QWidget()
        leftWDG.setFixedWidth(490)
        lay = QHBoxLayout()
        namelay = QVBoxLayout()
        namelay.addWidget(self.UI.CanvasLabel("FYP/CLASSICAL.png", True, True, Qt.AlignCenter, fixedSize=(44,302)))
        namelay.addWidget(self.UI.CanvasLabel("FYP/ENHANCED.png", True, True, Qt.AlignCenter, fixedSize=(44,302)))

        self.slider_params = [self.UI.SliderWidget(Qt.Horizontal, 5, 3, 15, 150, lambda : self.update_params(1, 0), step=2),
                              self.UI.SliderWidget(Qt.Horizontal, 150, 0, 5000, 150, lambda : self.update_params(1, 1, deci=True), step=1),
                              self.UI.SliderWidget(Qt.Horizontal, 90, 0, 255, 150, lambda : self.update_params(1, 2), step=1),
                              self.UI.SliderWidget(Qt.Horizontal, 35, 0, 255, 150, lambda : self.update_params(1, 3), step=1),

                              self.UI.SliderWidget(Qt.Horizontal, 5, 3, 15, 150, lambda : self.update_params(1, 4), step=2),
                              self.UI.SliderWidget(Qt.Horizontal, 150, 0, 5000, 150, lambda : self.update_params(1, 5, deci=True), step=1),
                              self.UI.SliderWidget(Qt.Horizontal, 65, 0, 255, 150, lambda: self.update_params(1, 6), step=1),
                              self.UI.SliderWidget(Qt.Horizontal, 48, 0, 255, 150, lambda: self.update_params(1, 7), step=1),
                              self.UI.SliderWidget(Qt.Horizontal, 18, 0, 255, 150, lambda: self.update_params(1, 8), step=1),
                              # self.UI.SliderWidget(Qt.Horizontal, 120, 100, 300, 150, lambda: self.update_params(1, 7, deci=True), step=1),
                              self.UI.SliderWidget(Qt.Horizontal, 55, 0, 100, 150, lambda: self.update_params(1, 9, deci=True), step=1),
                              self.UI.SliderWidget(Qt.Horizontal, 0, 0, 100, 150, lambda: self.update_params(1, 10, deci=True), step=1)
                              ]
        self.spinner_params = [self.UI.SpinBox(True, 3,15,5,ODD=True, width=50, action=lambda : self.update_params(2,0)),
                               self.UI.SpinBox(False, 0,50,1.5, width=50, action=lambda : self.update_params(2, 1, deci=True), step=0.05),
                               self.UI.SpinBox(True, 0,255,90, width=50, action=lambda : self.update_params(2, 2)),
                               self.UI.SpinBox(True, 0,255,35, width=50, action=lambda : self.update_params(2, 3)),

                               self.UI.SpinBox(True, 3,15,5,ODD=True, width=50, action=lambda : self.update_params(2,4)),
                               self.UI.SpinBox(False, 0,50,1.5, width=50, action=lambda : self.update_params(2, 5, deci=True), step=0.05),
                               self.UI.SpinBox(True, 0, 255, 65, width=50, action=lambda: self.update_params(2, 6)),

                               self.UI.SpinBox(True, 0, 255, 48, width=50, action=lambda: self.update_params(2, 7)),
                               self.UI.SpinBox(True, 0, 255, 18, width=50, action=lambda: self.update_params(2, 8)),
                               # self.UI.SpinBox(False, 1.0, 3.0, 1.2, width=50, action=lambda: self.update_params(2, 7, deci=True), step=0.05),
                               self.UI.SpinBox(False, 0, 1.0, 0.55, width=50, action=lambda: self.update_params(2, 9, deci=True), step=0.01),
                               self.UI.SpinBox(False, 0, 1.0, 0, width=50, action=lambda: self.update_params(2, 10, deci=True), step=0.01)
                               ]
        controlLay = QVBoxLayout()
        controlLay.addStretch(2)
        controlLay.addLayout(self.paramController("Gaussian Kernel", self.slider_params[0], self.spinner_params[0]))
        controlLay.addLayout(self.paramController("Gauss. Spatial \u03C3\u209B", self.slider_params[1], self.spinner_params[1]))
        controlLay.addLayout(self.paramController("High Threshold", self.slider_params[2], self.spinner_params[2]))
        controlLay.addLayout(self.paramController("Low Threshold", self.slider_params[3], self.spinner_params[3]))
        controlLay.addWidget(QWidget())
        controlLay.addLayout(self.paramController("", QWidget(), QWidget()))

        LeftCentreLay = QHBoxLayout()
        ToolLay = QVBoxLayout()
        ToolLay.addWidget(self.UI.PushBtnIcon("FYP/Open.png", self.openDialog, size=(45,45), tooltip='Open Image'))
        ToolLay.addWidget(self.UI.PushBtnIcon("FYP/Detect.png", lambda: self.update_tools(2), size=(45, 45), tooltip='Detect Edge'))
        self.compareImgBtn = self.UI.PushBtnIcon("FYP/Compare.png", lambda: self.update_tools(3), size=(50, 45), checkable=True, tooltip='Compare ground')

        ToolLay.addWidget(self.compareImgBtn)
        ToolLay.addWidget(self.UI.PushBtnIcon("FYP/Save.png", lambda: self.update_tools(4), size=(45, 45), tooltip='Save Image'))
        LeftCentreLay.addLayout(ToolLay)
        LeftCentreLay.addWidget(self.UI.imageFrame((330,330), self.inputImage))

        controlLay.addLayout(LeftCentreLay)
        controlLay.addStretch(1)

        controlLay.addLayout(self.paramController("GABF Kernel", self.slider_params[4], self.spinner_params[4]))
        controlLay.addLayout(self.paramController("Gauss. Spatial \u03C3\u209B", self.slider_params[5], self.spinner_params[5]))
        controlLay.addLayout(self.paramController("Gauss. Range \u03C3r", self.slider_params[6], self.spinner_params[6]))
        controlLay.addLayout(self.paramController("High Threshold", self.slider_params[7], self.spinner_params[7]))
        controlLay.addLayout(self.paramController("Low Threshold", self.slider_params[8], self.spinner_params[8]))
        controlLay.addLayout(self.paramController("GradientMean k1", self.slider_params[9], self.spinner_params[9]))
        controlLay.addLayout(self.paramController("ChainMean k2", self.slider_params[10], self.spinner_params[10]))
        controlLay.addStretch(2)

        lay.addLayout(namelay)
        lay.addLayout(controlLay)
        leftWDG.setLayout(lay)
        return leftWDG

    def paramController(self, name, slider, spinner):
        lay = QHBoxLayout()
        lay.addWidget(self.UI.Label_TextOnly(name, ("Times New Roman", 15), align=Qt.AlignLeft, width=180))
        lay.addWidget(slider)
        lay.addWidget(spinner)
        return lay

    def ver_Plane(self, topName, topImage, botName, botImage):
        lay = QVBoxLayout()
        lay.addWidget(self.UI.Label_TextOnly(topName, ("Times New Roman BOLD", 15), align=Qt.AlignCenter))
        lay.addWidget(topImage)
        lay.addSpacing(5)
        lay.addWidget(botImage)
        lay.addWidget(self.UI.Label_TextOnly(botName, ("Times New Roman BOLD", 15), align=Qt.AlignCenter))
        return lay

    def benchmark(self):
        self.result = []
        self.compare = []

        lay = QVBoxLayout()
        lay.addSpacing(10)
        lay.addWidget(self.UI.Label_TextOnly("Benchmark Test\n", ("Times New Roman BOLD", 15), align=Qt.AlignCenter))

        testName = ["Precision",
                "Recall",
                "F-measure",

                "Precision",
                "Recall",
                "F-measure",
                #Super final
                "Precision",
                "Recall",
                "F-measure",
                ]
        for i,test in enumerate(testName):
            if i==0:
                lay.addWidget(self.UI.Label_TextOnly('CLASSICAL', ("Times New Roman BOLD", 14), align=Qt.AlignCenter, border=2, color=(230, 125, 0, 0.7), height=40))
            elif i==3:
                lay.addSpacing(75)
                lay.addWidget(self.UI.Label_TextOnly('ENHANCED', ("Times New Roman BOLD", 14), align=Qt.AlignCenter, border=2, color=(230, 0, 125, 0.7), height=40))
                lay.addWidget(self.UI.Label_TextOnly('Gaussian-Adaptive Bilateral Filtering', ("Times New Roman ", 11), align=Qt.AlignCenter, fontColor=(33,33,33,0.7)))
                lay.addWidget(HLine())
            elif i==6:
                lay.addWidget(self.UI.Label_TextOnly('Edge-Chain Filtering', ("Times New Roman ", 11), align=Qt.AlignCenter, fontColor=(33, 33, 33, 0.7)))
                lay.addWidget(HLine())
            testWidget = QWidget()
            testLay = QHBoxLayout(testWidget)

            if i>=3:
                testLay.addWidget(self.UI.Label_TextOnly(test, ("Times New Roman ", 13), align=Qt.AlignLeft, width=160))
                self.compare.append((self.UI.CanvasLabel("", True, True, Qt.AlignCenter, fixedSize=(20,20)),
                                     self.UI.Label_TextOnly("", ("Times New Roman", 12), align=Qt.AlignRight, width=60)))
                testLay.addWidget(self.compare[i-3][1])
                testLay.addWidget(self.compare[i-3][0])
            else:
                testLay.addWidget(self.UI.Label_TextOnly(test, ("Times New Roman ", 13), align=Qt.AlignLeft, width=180))
                testLay.addWidget(self.UI.Label_TextOnly("", ("Times New Roman", 12), align=Qt.AlignRight, width=40))
                testLay.addWidget(self.UI.CanvasLabel("", True, True, Qt.AlignCenter, fixedSize=(20,20)))

            self.result.append(self.UI.Label_TextOnly("-", ("Times New Roman", 12), align=Qt.AlignRight, width=80, border=1))
            testLay.addWidget(self.result[i])
            testWidget.setLayout(testLay)
            lay.addWidget(testWidget)

        lay.addStretch(3)
        return lay

    def Intermediate(self):
        scroll = QScrollArea()
        scroll.setStyleSheet('background-color: transparent; border: 0')
        scroll.setFixedWidth(660)
        scroll_content = QWidget()
        scroll_Lay = QHBoxLayout(scroll_content)

        lay1 = self.ver_Plane("Gaussian\nFiltering", self.UI.imageFrame((320,320), self.outputImage[0]),
                              "Gaussian-Adaptive\nBilateral Filtering", self.UI.imageFrame((320,320), self.outputImage[6]))     #############
        lay2 = self.ver_Plane("Gradient \nComputation", self.UI.imageFrame((320, 320), self.outputImage[1]),
                              "Gradient \nComputation", self.UI.imageFrame((320, 320), self.outputImage[7]))
        lay3 = self.ver_Plane("Non-Maxima\nSuppression", self.UI.imageFrame((320, 320), self.outputImage[2]),
                              "Non-Maxima\nSuppression", self.UI.imageFrame((320, 320), self.outputImage[8]))
        lay4 = self.ver_Plane("Double\nThresholding", self.UI.imageFrame((320, 320), self.outputImage[3]),
                              "Double\nThresholding", self.UI.imageFrame((320, 320), self.outputImage[9]))
        lay5 = self.ver_Plane("\nHysteresis", self.UI.imageFrame((320, 320), self.outputImage[4]),
                              "Hysteresis\n", self.UI.imageFrame((320, 320), self.outputImage[10]))
        empty = QWidget()
        empty.setFixedSize(320,320)
        lay6 = self.ver_Plane("\n", empty,
                              "Edge Chain\nFormation", self.UI.imageFrame((320, 320), self.outputImage[11]))  ##################
        lay7 = self.ver_Plane("\n", empty,
                              "Edge Chain\nFiltering", self.UI.imageFrame((320, 320), self.outputImage[12]))             ##################

        scroll_Lay.addLayout(lay1)
        scroll_Lay.addLayout(lay2)
        scroll_Lay.addLayout(lay3)
        scroll_Lay.addLayout(lay4)
        scroll_Lay.addLayout(lay5)
        scroll_Lay.addLayout(lay6)
        scroll_Lay.addLayout(lay7)
        scroll.setWidget(scroll_content)
        return scroll

    def FinalOutput(self):
        resultLay = QVBoxLayout()
        resultLay.addWidget(self.UI.Label_TextOnly("Classical Output", ("Times New Roman BOLD", 15), align=Qt.AlignCenter))
        resultLay.addWidget(self.UI.imageFrame((350, 350), self.outputImage[5]))
        resultLay.addWidget(self.UI.imageFrame((350, 350), self.outputImage[13]))
        resultLay.addWidget(self.UI.Label_TextOnly("Enhanced Output", ("Times New Roman BOLD", 15), align=Qt.AlignCenter))
        resultLay.addSpacing(40)
        return resultLay

    def update_params(self, flag, ind, deci=None):
        if flag==1:
            if deci:
                self.spinner_params[ind].setValue(self.slider_params[ind].value()/100)
            else:
                self.spinner_params[ind].setValue(self.slider_params[ind].value())

        elif flag==2:
            self.slider_params[ind].blockSignals(True)
            if deci:
                self.slider_params[ind].setValue(int(round(self.spinner_params[ind].value()*100)))
            else:
                self.slider_params[ind].setValue(self.spinner_params[ind].value())
            self.slider_params[ind].blockSignals(False)

        if 0<=ind<=1:
            self.tool_ori = 1
        elif 2<=ind<=3 and self.tool_ori==0:
            self.tool_ori = 2
        elif 4<=ind<=6:
            self.tool_ehc = 1
        elif 7<=ind<=8 and self.tool_ehc == 0:
            self.tool_ehc = 2
        elif 9<=ind<=10 and self.tool_ehc == 0:
            self.tool_ehc = 3

    def openDialog(self):
        allConfirmed = False
        if all(self.confirmation):
            allConfirmed = True
        self.confirmation = [False, False]
        msg = QDialog(self)
        msg.setWindowFlag(Qt.FramelessWindowHint)
        lay = QVBoxLayout()
        textLay = QHBoxLayout()
        textLay.addWidget(self.UI.Label_TextOnly("Test Image", ("Times New Roman", 12), align=Qt.AlignCenter, border=2, width=300))
        textLay.addWidget(self.UI.Label_TextOnly("Ground Truth", ("Times New Roman", 12), align=Qt.AlignCenter, border=2, width=300))
        lay.addLayout(textLay)
        btnLay = QHBoxLayout()
        self.openImage = [self.UI.PushBtnIcon('FYP/image.png', lambda : self.update_tools(0), size=(300,300), border=1), self.UI.PushBtnIcon('FYP/image.png', lambda: self.update_tools(1), size=(300,300), border=1)]
        btnLay.addWidget(self.openImage[0])
        btnLay.addWidget(self.openImage[1])
        lay.addLayout(btnLay)

        def confirm():
            if not all(self.confirmation) or self.groundImg.shape[0]!=self.ori.shape[0] or self.groundImg.shape[1]!=self.ori.shape[1]:
                return
            # if both image obtained, then can close else return
            self.Render(self.ori.copy(), self.inputImage)
            if len(self.ori.shape)==3:
                self.input = self.CV.cvtGreyscale(self.ori.copy())
            else:
                self.input = self.ori.copy()
            self.tool_ori = self.tool_ehc = -1
            self.compareImgBtn.setChecked(False)
            msg.close()
        def cancel():
            if allConfirmed:
                self.confirmation = [True, True]
            msg.close()

        btnLayBottom = QHBoxLayout()
        btnLayBottom.addStretch()
        btnLayBottom.addWidget(self.UI.PushBtnText('Confirm', confirm, width=80))
        btnLayBottom.addWidget(self.UI.PushBtnText('Cancel', cancel, width=80))
        lay.addLayout(btnLayBottom)
        msg.setLayout(lay)

        msg.exec_()

    def update_ParamValue(self, filename):
        print(filename, " updating params value ...")
        if filename=='21077':
            params = (5, 1.35, 90, 30, 5, 1.05, 44, 52, 11, 0.46, 0.15)
        elif filename=='24077':
            params = (5, 3, 97, 41, 5, 2.65, 71, 54, 18, 0.5, 0.15)
        elif filename=='67079':
            params = (5, 2.6, 79, 37, 5, 2.65, 54, 36, 10, 0.60, 0.05)
        elif filename=='69020':
            params = (5, 1.55, 66, 36, 5, 1.5, 37, 43, 17, 0.69, 0.11)
        elif filename=='100075':
            params = (5, 2.9, 79, 36, 5, 3.2, 73, 50, 30, 0.67, 0.09)
        elif filename=='113044':
            params = (5, 1.35, 94, 46, 5, 1.35, 64, 40, 22, 0.72, 0.18)
        elif filename=='299086':
            params = (5, 1.4, 64, 28, 5, 1.55, 70, 31, 15, 0.55, 0.12)
        elif filename=='323016':
            params = (7, 1.1, 70, 40, 7, 0.8, 88, 56, 25, 0.57, 0.07)
        elif filename=='187071':
            params = (7, 1.45, 105, 41, 7, 1.3, 75, 55, 24, 0.64, 0.08)
        elif filename=='368078':
            params = (5, 1.35, 96, 33, 5, 1.3, 88, 58, 12, 0.44, 0.1)
        else:
            print('not matched, resetting params value')
            params = (5, 1.5, 90, 35, 5, 1.5, 65, 48, 18, 0.55, 0)
        for i,spin in enumerate(self.spinner_params):
            spin.setValue(params[i])

    def update_tools(self, flag, groundPath=None):
        if flag==0 or flag==1:
            if groundPath:
                file = groundPath
            else:
                filter = "Images (*.png *.jpg *.tif *.tiff)"
                if flag==0:
                    pathSuggest = f'./FYP/Image'
                else:
                    pathSuggest = f'./FYP/Ground'
                file, _ = QFileDialog.getOpenFileName(self, "File Directory", pathSuggest, filter)
            if file == (""):
                return
            else:
                img = self.CV.read(file)
                if flag==0:
                    self.ori = img.copy()

                if flag ==1:
                    self.groundImg = img.copy()
                self.confirmation[flag] = True
                self.Render(img.copy(), self.openImage[flag], icon=True)
                if flag==0:
                    groundPath = f'./FYP/Ground/'+str(os.path.basename(file).split('.')[0])+'.png'
                    if os.path.isfile(groundPath):
                        self.update_tools(1, groundPath)
                        self.update_ParamValue(str(os.path.basename(file).split('.')[0]))

        elif flag==2 and all(self.confirmation):
            #################### Classic ##########################
            if self.tool_ori==1 or self.tool_ori==-1:
                print(np.average(np.abs(np.average(self.input.copy())-self.input.copy()))*255)
                gaussFltr = self.CV.gaussianFilter(self.input.copy(), self.spinner_params[0].value(), self.spinner_params[1].value())
                self.oriCED[0] = gaussFltr.copy()*255

                grad2x2, ang2x2 = self.CV.gradient2x2(gaussFltr.copy())
                self.oriCED[1] = grad2x2.copy()*255

                self.oriCED[2] = self.CV.nonMax_Supp(grad2x2.copy(), ang2x2.copy())
                self.tool_ori = 2

                for i in range(3):
                    self.Render(self.oriCED[i].copy(), self.outputImage[i])

            if self.tool_ori==2:
                self.oriCED[3] = self.CV.thresholding(self.oriCED[2].copy(), self.spinner_params[2].value(), self.spinner_params[3].value())

                self.oriCED[4],_ = self.CV.hysteresis(self.oriCED[3].copy())

                for i in range(3, 5):
                    self.Render(self.oriCED[i].copy(), self.outputImage[i])
                self.Render(self.oriCED[4].copy(), self.outputImage[5])

            #################### Enhanced ##########################
            if self.tool_ehc==1 or self.tool_ehc==-1:
                GABFfilter = self.CV.gabf(self.input.copy(), self.spinner_params[4].value(), self.spinner_params[5].value(), float(self.spinner_params[6].value()/255.0))
                self.enhCED[0] = GABFfilter.copy()*255

                gradENH, angENH = self.CV.gradient2x2(GABFfilter.copy())
                self.enhCED[1] = gradENH.copy()*255

                self.enhCED[2] = self.CV.nonMax_Supp(gradENH.copy(), angENH.copy())
                self.tool_ehc = 2

                for i in range(3):
                    self.Render(self.enhCED[i].copy(), self.outputImage[i+6])
            if self.tool_ehc==2:

                self.enhCED[3] = self.CV.thresholding(self.enhCED[2].copy(), self.spinner_params[7].value(), self.spinner_params[8].value())

                self.enhCED[4], nms_e = self.CV.hysteresis(self.enhCED[3].copy(), self.enhCED[2].copy())

                self.enhCED[5], self.enhCED[6], self.chainInfo = self.CV.chainFormation(self.enhCED[4].copy(), nms_e.copy())
                self.tool_ehc = 3
                for i in range(3, 6):
                    self.Render(self.enhCED[i].copy(), self.outputImage[i+6])
            if self.tool_ehc==3:


                self.enhCED[7], self.enhCED[10] = self.CV.chainFiltering(self.enhCED[6].copy(), self.chainInfo, self.spinner_params[9].value(), self.spinner_params[10].value())

                self.Render(self.enhCED[7].copy(), self.outputImage[12])
                self.Render(self.enhCED[7].copy(), self.outputImage[13])

            ########  benchmark  ###############
            result1 = [0,0,0]
            result2 = [0,0,0,0,0,0]
            print("Ori: w={}; \u03C3\u209B={}; TH={}; TL={}".format(self.spinner_params[0].value(), round(self.spinner_params[1].value(),2), self.spinner_params[2].value(), self.spinner_params[3].value()))

            result1[0], result1[1], result1[2], self.oriCED[5] = self.CV.getConfusionMat(self.groundImg.copy(), self.oriCED[4].copy())

            self.result[0].setText(str(round(result1[0], 4)))
            self.result[1].setText(str(round(result1[1], 4)))
            self.result[2].setText(str(round(result1[2], 4)))

            print("Enh: w={}; s={}; r={}; TH={}; TL={}".format(self.spinner_params[4].value(), round(self.spinner_params[5].value(),2), round(self.spinner_params[6].value(),2), round(self.spinner_params[7].value(),2), round(self.spinner_params[8].value(),2)))
            result2[0], result2[1], result2[2], self.enhCED[8] = self.CV.getConfusionMat(self.groundImg.copy(), self.enhCED[4].copy())

            self.result[3].setText(str(round(result2[0], 4)))
            self.result[4].setText(str(round(result2[1], 4)))
            self.result[5].setText(str(round(result2[2], 4)))
            result2[3], result2[4], result2[5], self.enhCED[9] = self.CV.getConfusionMat(self.groundImg.copy(), self.enhCED[7].copy())
            self.result[6].setText(str(round(result2[3], 4)))
            self.result[7].setText(str(round(result2[4], 4)))
            self.result[8].setText(str(round(result2[5], 4)))

            ### comparison ####
            for ind,myResult in enumerate(result2):

                if ind>=3:
                    percent = (round(myResult, 4) - round(result1[ind-3], 4)) * 100
                else:
                    percent = (round(myResult, 4) - round(result1[ind], 4))*100
                if percent==0:
                    self.compare[ind][0].setPixmap(QPixmap(''))
                    self.compare[ind][1].setText('')
                elif percent>0:
                    self.compare[ind][0].setPixmap(QPixmap('FYP/up.png'))
                    self.compare[ind][1].setText(str(round(percent, 2)) + '%')
                    self.compare[ind][1].setStyleSheet('color: rgb(0,150,0)')
                else:
                    self.compare[ind][0].setPixmap(QPixmap('FYP/down.png'))
                    self.compare[ind][1].setText(str(round(percent, 2)) + '%')
                    self.compare[ind][1].setStyleSheet('color: rgb(180,0,0)')

            print('_______________________________________')

            self.tool_ori = self.tool_ehc = 0       # reset
        elif flag == 3 and self.tool_ehc!=-1 and self.tool_ori!=-1:
            if self.compareImgBtn.isChecked():
                self.Render(self.oriCED[5], self.outputImage[4])
                self.Render(self.oriCED[5], self.outputImage[5])
                self.Render(self.enhCED[8], self.outputImage[10])
                self.Render(self.enhCED[10], self.outputImage[12])
                self.Render(self.enhCED[9], self.outputImage[13])
                self.Render(self.groundImg.copy(), self.inputImage)
            else:
                self.Render(self.oriCED[4], self.outputImage[4])
                self.Render(self.oriCED[4], self.outputImage[5])
                self.Render(self.enhCED[4], self.outputImage[10])
                self.Render(self.enhCED[7], self.outputImage[12])
                self.Render(self.enhCED[7], self.outputImage[13])
                self.Render(self.ori.copy(), self.inputImage)
        elif flag==4 and self.tool_ehc!=-1 and self.tool_ori!=-1:
            folder = QFileDialog.getExistingDirectory(self, ("Save Output"), QDir.currentPath())
            if folder == (""):
                return
            else:
                self.CV.save(folder+'/GaussianFiltering.tif', self.oriCED[0].astype(np.uint8))
                self.CV.save(folder + '/Gradient.tif', self.oriCED[1].astype(np.uint8))
                self.CV.save(folder + '/NMS.tif', self.oriCED[2])
                self.CV.save(folder + '/Thresholded.tif', self.oriCED[3])
                self.CV.save(folder+'/ClassicOutput.tif', self.oriCED[4])
                self.CV.save(folder + '/ClassicGround.tif', cv2.cvtColor(self.oriCED[5], cv2.COLOR_BGR2RGB))

                self.CV.save(folder+'/01GABF.tif', self.enhCED[0].astype(np.uint8))
                self.CV.save(folder + '/02Gradient_enh.tif', self.enhCED[1].astype(np.uint8))
                self.CV.save(folder + '/03NMS_enh.tif', self.enhCED[2])
                self.CV.save(folder + '/04Thresholded_enh.tif', self.enhCED[3])
                self.CV.save(folder + '/05Hysteresis_enh.tif', self.enhCED[4])
                self.CV.save(folder + '/06EC_formation.tif', self.enhCED[5])
                self.CV.save(folder + '/07EnhancedOutput.tif', self.enhCED[7])
                self.CV.save(folder + '/08HysteresisGround.tif', cv2.cvtColor(self.enhCED[8], cv2.COLOR_BGR2RGB))
                self.CV.save(folder + '/09EnhancedGround.tif', cv2.cvtColor(self.enhCED[9], cv2.COLOR_BGR2RGB))
                self.CV.save(folder + '/10ECF_comp.tif', cv2.cvtColor(self.enhCED[10], cv2.COLOR_BGR2RGB))

    def zoomImage(self, flag):
        if not all(self.confirmation):
            return
        if flag[0]:    #ori
            if flag[1]==0:
                text = "Ori_Gaussian Filtering: w ={}; \u03C3\u209B = {}".format(self.spinner_params[0].value(), round(self.spinner_params[1].value(),2))
            elif flag[1]==1:
                text = "Ori_Gradient Computation"
            elif flag[1]==2:
                text = "Ori_Non-Maxima Suppression"
            elif flag[1]==3:
                text = "Ori_Double Thresholding: TH = {}; TL = {}".format(self.spinner_params[2].value(), self.spinner_params[3].value())
            elif flag[1] == 4:
                text = "Ori_Hysteresis: TH = {}; TL = {}".format(self.spinner_params[2].value(), self.spinner_params[3].value())
            elif flag[1]==5:
                text = "Ori: w={}; \u03C3\u209B={}; TH={}; TL={}".format(self.spinner_params[0].value(), round(self.spinner_params[1].value(),2), self.spinner_params[2].value(), self.spinner_params[3].value())
                self.UI.imageZoomDialog(text, self.oriCED[4])
                self.UI.imageZoomDialog(text, self.oriCED[5])
                return
            image = self.oriCED[flag[1]]
            if flag[1]==-1:
                self.UI.imageZoomDialog("Ground Truth", self.groundImg.copy())
                grey = self.input.copy()*255
                self.UI.imageZoomDialog("Greyscale", grey.astype(np.uint8))
                self.UI.imageZoomDialog("Original Input", self.ori.copy())
                return
        else:       #enh
            if flag[1] == 0:
                text = "Enh_GABF: kernel = {}; \u03C3\u209B = {}; \u03C3r = {}".format(self.spinner_params[4].value(), round(self.spinner_params[5].value(),2), round(self.spinner_params[6].value(),2))
            elif flag[1] == 1:
                text = "Enh_Gradient Computation"
            elif flag[1] == 2:
                text = "Enh_Non-Maxima Suppression"
            elif flag[1] == 3:
                text = "Enh_Double Thresholding: TH={}; TL={}".format(round(self.spinner_params[7].value(),2), round(self.spinner_params[8].value(),2))
            elif flag[1] == 4:
                text = "Enh_Hysteresis: w={}; s={}; r={}; TH={}; TL={}".format(self.spinner_params[4].value(), round(self.spinner_params[5].value(),2), round(self.spinner_params[6].value(),2), round(self.spinner_params[7].value(),2), round(self.spinner_params[8].value(),2))
                self.UI.imageZoomDialog(text, self.enhCED[4])
                self.UI.imageZoomDialog(text, self.enhCED[8])
                return
            elif flag[1] == 5:
                text = "Enh_Edge Chain Formation"
            elif flag[1] == 6:
                text = "Enh_Edge Chain Filtering"
                self.UI.imageZoomDialog(text, self.enhCED[7])
                self.UI.imageZoomDialog(text, self.enhCED[10])
                return
            elif flag[1] == 7:      #########3
                text = "Enh: w={}; s={}; r={}; TH={}; TL={}".format(self.spinner_params[4].value(), round(self.spinner_params[5].value(),2), round(self.spinner_params[6].value(),2), round(self.spinner_params[7].value(),2), round(self.spinner_params[8].value(),2))
                self.UI.imageZoomDialog(text, self.enhCED[7])
                self.UI.imageZoomDialog(text, self.enhCED[9])
                return
                # return
            image = self.enhCED[flag[1]]
        self.UI.imageZoomDialog(text, image.astype(np.uint8))

    def Render(self, image, canvas, icon=False):
        image = image.astype(np.uint8)
        image = cv2.resize(image, dsize=(self.size[0], self.size[1]))
        if len(image.shape)==3:
            image_RGBA = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
        else:
            image_RGBA = cv2.cvtColor(image, cv2.COLOR_GRAY2RGBA)
        QtImg = QImage(image_RGBA.data, image_RGBA.shape[1], image_RGBA.shape[0], QImage.Format_ARGB32)
        if not icon:
            canvas.setPhoto(QPixmap(QtImg))
        else:
            canvas.setIcon(QIcon(QPixmap.scaled(QPixmap.fromImage(QtImg), image.shape[1], image.shape[0], Qt.KeepAspectRatio, Qt.SmoothTransformation)))

def main():
    app = QApplication(sys.argv)
    win = FYP_CED()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()