import sys
from PyQt5 import QtWidgets, QtGui, QtCore

class CarWidget(QtWidgets.QWidget):
    def __init__(self, car_path="car.png", area=(600,500)):
        super().__init__()
        self.setFixedSize(*area)
        self.car = QtGui.QPixmap(car_path)
        self.car_x, self.car_y = 0, 0
        self.area_w, self.area_h = area

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor(245, 245, 245))
        painter.drawRect(0, 0, self.area_w - 1, self.area_h - 1)
        painter.drawPixmap(int(self.car_x), int(self.car_y), self.car)

    def reset(self):
        self.car_x, self.car_y = 0, 0
        self.update()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置标题
        self.setWindowTitle("移动的小车")

        # 小车显示区域
        self.car_widget = CarWidget()

        # 按钮
        self.btn_pause = QtWidgets.QPushButton("暂停/继续")
        self.btn_reset = QtWidgets.QPushButton("重置位置")
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.label_speed = QtWidgets.QLabel("速度: 1")


        # 按钮布局
        layout_btn = QtWidgets.QHBoxLayout()
        layout_btn.addWidget(self.btn_pause)
        layout_btn.addWidget(self.btn_reset)
        layout_btn.addWidget(self.label_speed)
        layout_btn.addWidget(self.slider)

        # 界面布局
        layout_main = QtWidgets.QVBoxLayout()
        layout_main.addWidget(self.car_widget)
        layout_main.addLayout(layout_btn)
        container = QtWidgets.QWidget()
        container.setLayout(layout_main)
        self.setCentralWidget(container)

        # 速度控制
        self.slider.setRange(1, 20)
        # 初始速度为4
        self.slider.setValue(1)
        self.speed = 1 * 0.5
        # 连接按钮功能和滑块功能
        self.btn_pause.clicked.connect(self.pause)
        self.btn_reset.clicked.connect(self.car_widget.reset)
        self.slider.valueChanged.connect(self.change_speed)

        # 定时器
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.move_car)
        self.timer.start(10)
        self.running = True

        # 边界计算
        self.max_x = self.car_widget.area_w - self.car_widget.car.width() + 1
        self.max_y = self.car_widget.area_h - self.car_widget.car.height() + 1

        # 托盘图标
        self.create_tray_icon()

    def change_speed(self, val):
        self.speed = val * 0.5
        self.label_speed.setText(f"速度: {val}")

    def pause(self):
        if self.running:
            self.timer.stop()
        else:
            self.timer.start()
        self.running = not self.runningzan


    def move_car(self):
        c = self.car_widget
        c.car_x += self.speed
        c.car_y += self.speed
        if c.car_x > self.max_x or c.car_y > self.max_y:
            c.reset()
        c.update()

    def create_tray_icon(self):
        self.tray = QtWidgets.QSystemTrayIcon(self)
        self.tray.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon))
        self.tray.setVisible(True)

        menu = QtWidgets.QMenu()
        act_restore = menu.addAction("恢复窗口")
        act_quit = menu.addAction("退出程序")
        act_restore.triggered.connect(self.show)
        act_quit.triggered.connect(QtWidgets.qApp.quit)
        self.tray.setContextMenu(menu)

    def closeEvent(self, e):
        self.hide()
        e.ignore()

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
