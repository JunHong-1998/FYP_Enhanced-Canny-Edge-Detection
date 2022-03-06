from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import cv2

class WidgetUI(QWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)

    def imageFrame(self, size, image):
        wid = QFrame(self)
        wid.setFixedSize(size[0], size[1])
        lay = QVBoxLayout()
        lay.addWidget(image)
        wid.setLayout(lay)
        return wid

    def CanvasLabel(self, image, SizeIgnore, Scale, Align, fixedSize= None):
        canvas = QLabel(self)
        canvas.setPixmap(QPixmap(image))
        if SizeIgnore:
            canvas.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        if fixedSize:
            canvas.setFixedSize(fixedSize[0], fixedSize[1])
        canvas.setScaledContents(Scale)
        canvas.setAlignment(Align)
        return canvas

    def SpinBox(self, flag, min, max, value, width=None, ODD=None, action=None, height=None, step=None):
        if flag:
            if ODD:
                spin = SpinBox()
                spin.setSingleStep(2)
            else:
                spin = QSpinBox(self)
        else:
            spin = QDoubleSpinBox(self)
            spin.setDecimals(2)
            # spin.setSingleStep(0.1)
        if step:
            spin.setSingleStep(step)
        spin.setMinimum(min)
        if width:
            spin.setFixedWidth(width)
        if max:
            spin.setMaximum(max)
        spin.setValue(value)
        if height:
            spin.setFixedHeight(height)
        if action:
            spin.valueChanged.connect(action)
        return spin

    def LineEdit(self, text, action=None, size=None, valid=None):
        LE = QLineEdit(self)
        LE.setText(text)
        if size:
            LE.setFixedSize(size[0], size[1])
        if valid:
            LE.setValidator(valid)
        if action:
            LE.textChanged.connect(action)
        return LE

    def Label_TextOnly(self, text, font=None, color=None, align=None, border=None, height=None, width = None, fontColor=None):
        label_Text = QLabel(self)
        label_Text.setText(text)
        if font:
            label_Text.setFont(QFont(font[0], font[1]))
        if height:
            label_Text.setFixedHeight(height)
        if width:
            label_Text.setFixedWidth(width)
        if align:
            label_Text.setAlignment(align)
        if fontColor:
            label_Text.setStyleSheet('color: rgba{}'.format(fontColor))
        if color and border:
            label_Text.setStyleSheet("background-color: rgba{}".format(color)+"; border: {}px solid black".format(border))
        elif color:
            label_Text.setStyleSheet("background-color: rgba{}".format(color))
        elif border:
            label_Text.setStyleSheet("border: {}px solid black".format(border))
        return label_Text

    def PushBtnText(self, text, action, font=None, width=None, size=None):
        btn = QPushButton(self)
        btn.setText(text)
        if font:
            btn.setFont(QFont(font[0], font[1]))
        if width:
            btn.setFixedWidth(width)
        if size:
            btn.setFixedSize(size[0], size[1])
        btn.clicked.connect(action)
        return btn

    def PushBtnIcon(self, icon, action, border=None, size=None, iconSize=None, tooltip=None, checkable=False):
        btn = QPushButton(self)
        btn.setIcon(QIcon(icon))
        if not border:
            btn.setStyleSheet("background-color: transparent")
        if size:
            btn.setIconSize(QSize(size[0], size[1]))
            btn.setFixedSize(size[0], size[1])
        if iconSize:
            btn.setIconSize(QSize(iconSize[0], iconSize[1]))
        if tooltip:
            btn.setToolTip(tooltip)
            # btn.setStyleSheet('border: 0')
        if checkable:
            btn.setCheckable(True)
            btn.setChecked(False)
        if action:
            btn.clicked.connect(action)
        return btn

    def checkbox(self, name, action, checked, font=None):
        checkbox = QCheckBox(self)
        if name:
            checkbox.setText(name)
        checkbox.setChecked(checked)
        if font:
            checkbox.setFont(QFont(font[0], font[1]))
        if action:
            checkbox.clicked.connect(action)
        return checkbox

    def imageZoomDialog(self, methodName, image, text=None):
        msg = QDialog(self)
        msg.setWindowTitle(methodName)
        layout = QVBoxLayout(msg)
        viewer = PhotoViewer(self, actionAllowed=True)
        if len(image.shape)==3:
            image_RGBA = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
        else:
            image_RGBA = cv2.cvtColor(image, cv2.COLOR_GRAY2RGBA)
        QtImg = QImage(image_RGBA.data, image_RGBA.shape[1], image_RGBA.shape[0], QImage.Format_ARGB32)
        layout.addWidget(viewer)
        if text:
            layout.addWidget(self.Label_TextOnly(text, font=('Arial', 13), height=25))
        msg.setLayout(layout)
        msg.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        msg.resize(image.shape[1], image.shape[0])
        msg.show()
        viewer.setPhoto(QPixmap(QtImg))


    def cover(self):
        msg = QDialog(self)
        msg.setWindowFlag(Qt.FramelessWindowHint)

        layout = QVBoxLayout(self)
        bg = QWidget()
        bg.setStyleSheet('background-color: rgba(250,250,250,0.56)')
        bg.setFixedWidth(1950)
        bgLayout = QVBoxLayout(bg)
        bgLayout.addSpacing(45)
        bgLayout.addWidget(self.Label_TextOnly("\t\t\tSYSTEM \t : ENHANCED CANNY EDGE DETECTION", ("Times New Roman BOLD", 23), align=Qt.AlignLeft, color=(0,0,0,0)))
        bgLayout.addSpacing(20)
        bgLayout.addWidget(self.Label_TextOnly("\t\t\tMADE BY \t : LOW JUN HONG \n\t\t\t\t\t   BS18110173", ("Times New Roman BOLD", 23), align=Qt.AlignLeft, color=(0,0,0,0)))
        bgLayout.addSpacing(20)
        bgLayout.addWidget(self.Label_TextOnly("\t\t\tSUPERVISED BY : ASSOC. PROF DR ABDULLAH BADE", ("Times New Roman BOLD", 23), align=Qt.AlignLeft, color=(0,0,0,0)))
        bgLayout.addSpacing(45)
        layout.addWidget(bg)

        btn_lay = QHBoxLayout()
        layout.addSpacing(66)
        layout.addLayout(btn_lay)

        msg.setLayout(layout)
        msg.setAttribute(Qt.WA_TranslucentBackground)
        msg.move(-10, 350)
        # msg.exec_()
        return msg, btn_lay

    def QuitDialog(self, sys):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Are you sure to quit application")
        msg.setInformativeText("Reminder: Save your project before quit")
        msg.setWindowTitle("Quit")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        quit = msg.exec_()
        if quit==16384:
            sys.exit()

    def SliderWidget(self, ott, default, min, max, width, action, step=None):
        slider = QSlider(self)
        slider.setOrientation(ott)
        if step:
            slider.setSingleStep(step)
            slider.setPageStep(step)
        slider.setMinimum(min)
        slider.setMaximum(max)
        slider.setValue(default)
        slider.setFixedWidth(width)
        slider.valueChanged.connect(action)
        slider.setStyleSheet("QSlider::groove:horizontal {border: 1px solid #bbb;background: white;height: 10px;border-radius: 4px;}"
                             "QSlider::sub-page:horizontal {background: qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,stop: 0 #66e, stop: 1 #bbf);background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,stop: 0 #bbf, stop: 1 #55f);border: 1px solid #777;height: 10px;border-radius: 4px;}"
                             "QSlider::add-page:horizontal {background: #fff;border: 1px solid #777;height: 10px;border-radius: 4px;}"
                             "QSlider::handle:horizontal {background: qlineargradient(x1:0, y1:0, x2:1, y2:1,stop:0 #eee, stop:1 #ccc);border: 1px solid #777;width: 13px;margin-top: -2px;margin-bottom: -2px;border-radius: 4px;}"
                             "QSlider::handle:horizontal:hover {background: qlineargradient(x1:0, y1:0, x2:1, y2:1,stop:0 #fff, stop:1 #ddd);border: 1px solid #444;border-radius: 4px;}"
                             "QSlider::sub-page:horizontal:disabled {background: #bbb;border-color: #999;}"
                             "QSlider::add-page:horizontal:disabled {background: #eee;border-color: #999;}"
                             "QSlider::handle:horizontal:disabled {background: #eee;border: 1px solid #aaa;border-radius: 4px;}")
        return slider
class HLine(QFrame):
    def __init__(self):
        super(HLine, self).__init__()
        self.setFrameShape(self.HLine|self.Sunken)

class SpinBox(QSpinBox):
    # Replaces the valueChanged signal
    newValueChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super(SpinBox, self).__init__(parent=parent)

        self.valueChanged.connect(self.onValueChanged)
        self.before_value = self.value()

    def onValueChanged(self, i):
        if not self.isValid(i):
            self.setValue(self.before_value)
        else:
            self.newValueChanged.emit(i)
            self.before_value = i

    def isValid(self, value):
        if (value % self.singleStep()) == 0:
            return False
        return True

class PhotoViewer(QGraphicsView):
    photoClicked = pyqtSignal()

    def __init__(self, parent, color=None, tooltip=None, actionAllowed=False):
        self.actionAllowed = actionAllowed
        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(self)
        self._photo = QGraphicsPixmapItem()
        if tooltip:
            self._photo.setToolTip(tooltip)
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(55, 55, 55)))
        if color:
            self.setStyleSheet('border-radius: 5px ;border: 4px solid rgb{}'.format(color))
        self.setFrameShape(QFrame.NoFrame)

    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QGraphicsView.NoDrag)
            self._photo.setPixmap(QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
        if self.hasPhoto() and self.actionAllowed:
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def toggleDragMode(self):
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            self.setDragMode(QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event):

        if self._photo.isUnderMouse():
            if not self.actionAllowed:
                self.photoClicked.emit()

            else:
                super(PhotoViewer, self).mousePressEvent(event)

