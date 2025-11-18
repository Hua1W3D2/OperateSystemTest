import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets

class CarWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, area_size=(300,200), car_img_path="car.png"):
        super().__init__(parent)
        self.area_w, self.area_h = area_size
        self.setFixedSize(self.area_w, self.area_h)
        self.setMinimumSize(200, 120)
        self.car_pix = QtGui.QPixmap(car_img_path)

        # 如果没有图片，绘制一个替代的“简易小车”尺寸
        self.car_w = self.car_pix.width()
        self.car_h = self.car_pix.height()

        # if self.car_pix is not None:
        #     self.car_w = self.car_pix.width()
        #     self.car_h = self.car_pix.height()

        # 小车起点与移动向量（从左上到右下）
        self.reset_position()

    def reset_position(self):
        # 从左上角（允许少量内边距）开始
        self.x = 0
        self.y = 0
        self.update()

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)

        # 背景（只在演示中画浅色背景）
        painter.fillRect(self.rect(), QtGui.QColor(245, 245, 245))

        # 画运动区域边框
        pen = QtGui.QPen(QtGui.QColor(200, 200, 200))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRect(0, 0, self.area_w-1, self.area_h-1)


        painter.drawPixmap(int(self.x), int(self.y), self.car_pix)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("移动的小车（左上 → 右下）")
        self.setWindowIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon))

        # 中央区域和小车绘制区大小（可以调整）
        area_size = (1200,800)
        self.car_widget = CarWidget(area_size=area_size, car_img_path="car.png")

        # Timer 与速度参数
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.on_timeout)
        self.timer_interval_ms = 60  # 固定tick间隔
        self.timer.setInterval(self.timer_interval_ms)

        # 速度表示： 每个tick的小车位移（像素）
        # 通过按钮改动 step（示例提供两档：慢 1 px/tick、快 4 px/tick），同时提供滑块调节
        self.base_step = 1.0
        self.dx = self.base_step
        self.dy = self.base_step

        # UI 控件：两个按钮（慢/快），滑块，重置按钮
        slow_btn = QtWidgets.QPushButton("慢速")
        fast_btn = QtWidgets.QPushButton("快速")
        stop_btn = QtWidgets.QPushButton("暂停/继续")
        reset_btn = QtWidgets.QPushButton("重置位置")
        self.speed_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(20)
        self.speed_slider.setValue(4)  # 初始倍率
        self.speed_label = QtWidgets.QLabel("速度倍率: 4")

        slow_btn.clicked.connect(self.set_slow)
        fast_btn.clicked.connect(self.set_fast)
        stop_btn.clicked.connect(self.toggle_pause)
        reset_btn.clicked.connect(self.reset_position)
        self.speed_slider.valueChanged.connect(self.on_slider_change)

        controls = QtWidgets.QHBoxLayout()
        controls.addWidget(slow_btn)
        controls.addWidget(fast_btn)
        controls.addWidget(stop_btn)
        controls.addWidget(reset_btn)
        controls.addStretch()
        controls.addWidget(self.speed_label)
        controls.addWidget(self.speed_slider)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.car_widget)
        main_layout.addLayout(controls)

        central = QtWidgets.QWidget()
        central.setLayout(main_layout)
        self.setCentralWidget(central)

        # 计算总轨迹（对角线）目标位置
        self.update_bounds()

        # 托盘图标与菜单
        self.tray = None
        self.create_tray_icon()

        # 启动移动
        self.running = True
        self.timer.start()

    def update_bounds(self):
        area_w, area_h = self.car_widget.area_w, self.car_widget.area_h
        car_w, car_h = self.car_widget.car_w, self.car_widget.car_h
        self.min_x = 0
        self.min_y = 0
        # 使小车右下角能贴到区域右下角
        self.max_x = max(0, area_w - car_w)
        self.max_y = max(0, area_h - car_h)
        # 按对角线方向移动，dx,dy 比例
        self.set_step_from_slider()

    def set_step_from_slider(self):
        # 基于滑块值决定每tick移多少像素（保留对角线比例）
        v = self.speed_slider.value()
        # 基础步长乘以倍率
        step = float(v) * 0.5  # 你可以调整映射关系
        # 以对角线方向均匀移动：dx = dy
        self.dx = step
        self.dy = step
        self.speed_label.setText(f"速度倍率: {v}")

    def set_slow(self):
        self.speed_slider.setValue(2)
        self.set_step_from_slider()

    def set_fast(self):
        self.speed_slider.setValue(12)
        self.set_step_from_slider()

    def on_slider_change(self, val):
        self.set_step_from_slider()

    def toggle_pause(self):
        if self.running:
            self.timer.stop()
            self.running = False
        else:
            self.timer.start()
            self.running = True

    def reset_position(self):
        self.car_widget.reset_position()

    def on_timeout(self):
        # 每次tick按 dx,dy 移动，沿对角线
        new_x = self.car_widget.x + self.dx
        new_y = self.car_widget.y + self.dy

        # 到达边界时循环回到起点（也可以改成停在终点）
        # 为满足“从左上到右下”的视觉效果，这里在到达终点后回到起点继续
        if new_x > self.max_x or new_y > self.max_y:
            new_x = 0
            new_y = 0

        self.car_widget.set_position(new_x, new_y)

    def closeEvent(self, event):
        # 覆盖窗口关闭：隐藏到托盘，但保持后台运行
        # 如果没有系统托盘支持，则退出
        if self.tray is None:
            event.accept()
            return

        # 隐藏窗口并显示托盘信息
        event.ignore()  # 阻止真正的关闭
        self.hide()
        self.tray.showMessage("程序已最小化到托盘",
                              "程序继续在后台运行，小车仍在移动（不可见）。右键托盘图标可恢复或退出。",
                              QtWidgets.QSystemTrayIcon.Information,
                              3000)

    def create_tray_icon(self):
        if not QtWidgets.QSystemTrayIcon.isSystemTrayAvailable():
            QtWidgets.QMessageBox.critical(None, "错误", "系统托盘不可用！")
            self.tray = None
            return

        self.tray = QtWidgets.QSystemTrayIcon(self)
        # 选择一个图标（优先程序图标）
        icon = self.windowIcon()
        self.tray.setIcon(icon)
        self.tray.setVisible(True)

        # 托盘菜单
        menu = QtWidgets.QMenu()

        restore_action = menu.addAction("恢复")
        exit_action = menu.addAction("退出")

        restore_action.triggered.connect(self.on_restore)
        exit_action.triggered.connect(self.on_exit)

        # 右键菜单绑定
        self.tray.setContextMenu(menu)

        # 双击或左键单击也可以恢复
        self.tray.activated.connect(self.on_tray_activated)

    def on_restore(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def on_exit(self):
        # 停止计时器并退出
        if self.timer.isActive():
            self.timer.stop()
        QtCore.QCoreApplication.quit()

    def on_tray_activated(self, reason):
        # 鼠标双击或触发激活时恢复窗口（根据平台不同会有不同触发）
        if reason in (QtWidgets.QSystemTrayIcon.Trigger, QtWidgets.QSystemTrayIcon.DoubleClick):
            self.on_restore()

def main():
    app = QtWidgets.QApplication(sys.argv)


    app.setQuitOnLastWindowClosed(False)

    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
