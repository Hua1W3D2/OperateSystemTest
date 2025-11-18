# -*- coding: utf-8 -*-
"""
可视化并发同步示例（PyQt5）
场景：盘子最多2个水果，爸爸放苹果，妈妈放橘子，儿子吃橘子，女儿吃苹果。

使用说明：
  1) 把dad.png,mom.png,son.png,daughter.png,apple.png,orange.png,plate.png
     放在与该脚本相同的目录下。
  2) 需要 Python3 和 PyQt5： pip install PyQt5
  3) 运行： python fruit_sync_pyqt.py

实现要点：
  - PlateModel 用 threading.Condition 控制生产/消费，容量2。
  - 每个角色使用 QThread，线程在串行地调用 PlateModel.put/take（这些方法会阻塞直到操作可进行）。
  - 动画由主线程执行（QPropertyAnimation），线程在发出动画请求后使用 threading.Event 等待动画完成信号，避免在主线程中阻塞。
  - 通过信号/槽跨线程传递动画请求并在动画结束后通知对应线程继续。
  - 通过一个速度滑动条调整动画时长。

为避免死锁：只有一个条件变量和一个锁；生产者只在盘子满时等待，消费者只在盘子中没有他们想要的水果时等待；每次修改状态后都会 notify_all()，因此不会发生循环等待。
"""

import sys
import os
import threading
import time
from PyQt5 import QtCore, QtGui, QtWidgets

# ---------------------- Plate (model with synchronization) ----------------------
class PlateModel:
    def __init__(self, capacity=2):
        self.capacity = capacity
        self.slots = [None] * capacity  # None or 'apple'/'orange'
        self.lock = threading.Lock()
        self.cond = threading.Condition(self.lock)

    def put(self, fruit_type):
        """放入一个水果，阻塞直到有空位。返回放入的 slot index."""
        with self.cond:
            while all(slot is not None for slot in self.slots):
                self.cond.wait()
            # find first empty slot
            for i in range(self.capacity):
                if self.slots[i] is None:
                    self.slots[i] = fruit_type
                    slot_index = i
                    break
            self.cond.notify_all()
            return slot_index

    def take(self, fruit_type):
        """取出一个指定类型的水果，阻塞直到有可取的水果。返回被取的 slot index."""
        with self.cond:
            while True:
                for i, val in enumerate(self.slots):
                    if val == fruit_type:
                        self.slots[i] = None
                        slot_index = i
                        self.cond.notify_all()
                        return slot_index
                # 没有找到想要的水果，等待
                self.cond.wait()

# ---------------------- Actor threads ----------------------
class ActorThread(QtCore.QThread):
    # signals to request animations from GUI thread
    request_put_anim = QtCore.pyqtSignal(str, str, int)   # actor_name, fruit_type, slot_index
    request_take_anim = QtCore.pyqtSignal(str, str, int)  # actor_name, fruit_type, slot_index

    def __init__(self, name, role, plate: PlateModel, parent=None):
        super().__init__(parent)
        self.name = name
        self.role = role  # 'producer' or 'consumer'
        self.plate = plate
        self.running = False
        self._stop_requested = False
        self.action_event = threading.Event()  # used to wait for animation to finish
        # role specific
        if name == 'Dad':
            self.fruit = 'apple'
        elif name == 'Mom':
            self.fruit = 'orange'
        elif name == 'Son':
            self.fruit = 'orange'
        elif name == 'Daughter':
            self.fruit = 'apple'
        else:
            self.fruit = 'apple'

    def run(self):
        self.running = True
        # small initial pause so GUI can finish setup
        time.sleep(0.2)
        while not self._stop_requested:
            if self.role == 'producer':
                # try to put a fruit (this blocks until space available)
                slot = self.plate.put(self.fruit)
                # request animation, then wait for it to finish
                self.action_event.clear()
                self.request_put_anim.emit(self.name, self.fruit, slot)
                self.action_event.wait()
            else:
                # consumer
                slot = self.plate.take(self.fruit)
                self.action_event.clear()
                self.request_take_anim.emit(self.name, self.fruit, slot)
                self.action_event.wait()
            # small delay to avoid tight loop (doesn't control order)
            time.sleep(0.15)
        self.running = False

    def stop(self):
        self._stop_requested = True

    @QtCore.pyqtSlot()
    def notify_animation_done(self):
        # called from GUI thread when animation finishes
        try:
            self.action_event.set()
        except Exception:
            pass

# ---------------------- Main GUI ----------------------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('水果放取同步演示')
        self.setFixedSize(1000, 600)
        self.central = QtWidgets.QWidget()
        self.setCentralWidget(self.central)

        # load images (assume in same folder)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        def load(name):
            p = os.path.join(self.base_dir, name)
            if not os.path.exists(p):
                print('Missing:', p)
            return QtGui.QPixmap(p)

        self.pix_dad = load('dad.png')
        self.pix_mom = load('mom.png')
        self.pix_son = load('son.png')
        self.pix_daughter = load('daughter.png')
        self.pix_apple = load('apple.png')
        self.pix_orange = load('orange.png')
        self.pix_plate = load('plate.png')

        # create canvas area
        self.canvas = QtWidgets.QFrame(self.central)
        self.canvas.setGeometry(0, 0, 1000, 520)
        self.canvas.setStyleSheet('background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #f2f6ff, stop:1 #ffffff);')

        # actor positions
        self.positions = {
            'Dad': QtCore.QPoint(50, 100),
            'Mom': QtCore.QPoint(50, 320),
            'Son': QtCore.QPoint(820, 100),
            'Daughter': QtCore.QPoint(820, 320),
        }

        # hand offsets (start positions for fruits)
        self.hand_offset = QtCore.QPoint(80, 40)

        # place character labels
        self.char_labels = {}
        self._place_character('Dad', self.pix_dad, self.positions['Dad'])
        self._place_character('Mom', self.pix_mom, self.positions['Mom'])
        self._place_character('Son', self.pix_son, self.positions['Son'])
        self._place_character('Daughter', self.pix_daughter, self.positions['Daughter'])

        # plate
        self.plate_label = QtWidgets.QLabel(self.canvas)
        self.plate_label.setPixmap(self.pix_plate)
        self.plate_label.setScaledContents(True)
        self.plate_label.resize(220, 140)
        self.plate_label.move(390, 190)

        # plate slot centers (two slots)
        plate_geom = self.plate_label.geometry()
        slot_a = plate_geom.topLeft() + QtCore.QPoint(55, 40)
        slot_b = plate_geom.topLeft() + QtCore.QPoint(135, 40)
        self.slot_positions = [slot_a, slot_b]

        # place empty placeholders for fruits on plate
        self.plate_slots_widgets = [QtWidgets.QLabel(self.canvas), QtWidgets.QLabel(self.canvas)]
        for w in self.plate_slots_widgets:
            w.setVisible(False)
            w.setScaledContents(True)
            w.resize(48, 48)

        # control panel
        self.start_btn = QtWidgets.QPushButton('Start', self.central)
        self.start_btn.setGeometry(40, 540, 80, 30)
        self.start_btn.clicked.connect(self.start_sim)
        self.stop_btn = QtWidgets.QPushButton('Stop', self.central)
        self.stop_btn.setGeometry(140, 540, 80, 30)
        self.stop_btn.clicked.connect(self.stop_sim)
        self.stop_btn.setEnabled(False)

        self.speed_label = QtWidgets.QLabel('Animation ms:', self.central)
        self.speed_label.setGeometry(260, 540, 90, 30)
        self.speed_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self.central)
        self.speed_slider.setGeometry(360, 545, 200, 20)
        self.speed_slider.setRange(200, 1600)
        self.speed_slider.setValue(700)

        # Plate model
        self.plate_model = PlateModel(capacity=2)

        # threads
        self.threads = {}
        self._make_threads()

    def _make_threads(self):
        # create actor threads but don't start
        self.threads['Dad'] = ActorThread('Dad', 'producer', self.plate_model)
        self.threads['Mom'] = ActorThread('Mom', 'producer', self.plate_model)
        self.threads['Son'] = ActorThread('Son', 'consumer', self.plate_model)
        self.threads['Daughter'] = ActorThread('Daughter', 'consumer', self.plate_model)
        # connect signals
        for name, t in self.threads.items():
            t.request_put_anim.connect(self.on_request_put)
            t.request_take_anim.connect(self.on_request_take)

    def _place_character(self, name, pixmap, pos: QtCore.QPoint):
        lbl = QtWidgets.QLabel(self.canvas)
        lbl.setPixmap(pixmap)
        lbl.setScaledContents(True)
        lbl.resize(140, 140)
        lbl.move(pos)
        lbl.show()
        self.char_labels[name] = lbl

    def start_sim(self):
        # hide any plate slot widgets
        for w in self.plate_slots_widgets:
            w.setVisible(False)
        # reset model and threads
        self.plate_model = PlateModel(capacity=2)
        for t in self.threads.values():
            t.stop()
        # small wait then recreate
        time.sleep(0.05)
        self._make_threads()

        # start threads
        self.threads['Dad'].start()
        self.threads['Mom'].start()

        # 等待一下，确保盘子至少有水果
        QtCore.QTimer.singleShot(500, lambda: self._start_consumers())

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def _start_consumers(self):
        self.threads['Son'].start()
        self.threads['Daughter'].start()

    def stop_sim(self):
        for t in self.threads.values():
            t.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    # ------------------ Animation handlers ------------------
    @QtCore.pyqtSlot(str, str, int)
    def on_request_put(self, actor_name, fruit_type, slot_index):
        # create a floating fruit at actor hand -> animate to plate slot
        start = self._actor_hand_pos(actor_name)
        end = self.slot_positions[slot_index] + QtCore.QPoint(0, 0)
        pix = self.pix_apple if fruit_type == 'apple' else self.pix_orange
        moving = QtWidgets.QLabel(self.canvas)
        moving.setPixmap(pix)
        moving.setScaledContents(True)
        moving.resize(48, 48)
        moving.move(start)
        moving.show()

        dur = self.speed_slider.value()
        anim = QtCore.QPropertyAnimation(moving, b'pos')
        anim.setDuration(dur)
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setEasingCurve(QtCore.QEasingCurve.InOutQuad)

        def on_finished():
            # place fruit on plate (slot widget)
            slot_w = self.plate_slots_widgets[slot_index]
            slot_w.setPixmap(pix)
            slot_w.move(end)
            slot_w.setVisible(True)
            moving.deleteLater()
            # notify corresponding thread animation done
            self._notify_actor(actor_name)

        anim.finished.connect(on_finished)
        anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

    @QtCore.pyqtSlot(str, str, int)
    def on_request_take(self, actor_name, fruit_type, slot_index):
        # find the plate slot widget and animate it to actor hand then hide
        slot_w = self.plate_slots_widgets[slot_index]
        if not slot_w.isVisible():
            # shouldn't happen, but guard
            self._notify_actor(actor_name)
            return
        start = slot_w.pos()
        end = self._actor_hand_pos(actor_name)
        anim = QtCore.QPropertyAnimation(slot_w, b'pos')
        anim.setDuration(self.speed_slider.value())
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setEasingCurve(QtCore.QEasingCurve.InOutQuad)

        def on_finished_take():
            slot_w.setVisible(False)
            # optionally show a short disappearing animation at actor (not necessary)
            # notify thread
            self._notify_actor(actor_name)

        anim.finished.connect(on_finished_take)
        anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

    def _actor_hand_pos(self, actor_name):
        # compute a reasonable hand start/end position relative to character label
        lbl = self.char_labels.get(actor_name)
        if not lbl:
            return QtCore.QPoint(0, 0)
        pos = lbl.pos() + self.hand_offset
        return pos

    def _notify_actor(self, actor_name):
        t = self.threads.get(actor_name)
        if t is not None:
            # call the thread's notify slot (cross-thread safe)
            t.notify_animation_done()

# ---------------------- run ----------------------
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
