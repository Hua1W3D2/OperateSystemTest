import sys, threading, time, random
from itertools import count
from PyQt5.QtCore import QObject, pyqtSignal, QPoint, QPropertyAnimation, QEasingCurve, Qt
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QSpacerItem, QSizePolicy, QFrame
from PyQt5.QtGui import QPixmap

# ---------------- communication ----------------
class Communicator(QObject):
    request_animation = pyqtSignal(str, str, bool, int)

# ---------------- plate ----------------
class Plate:
    def __init__(self, capacity=2):
        self.capacity = capacity
        self.contents = [None] * capacity  # (fruit_type, owner_name) or None

    def next_free_slot(self):
        for i, v in enumerate(self.contents):
            if v is None:
                return i
        return None

    def find_fruit_slot(self, fruit_type):
        for i, v in enumerate(self.contents):
            if v is not None and v[0] == fruit_type:
                return i
        return None

# ---------------- worker ----------------
class ActorThread(threading.Thread):
    def __init__(self, name, role, fruit_type, comm, plate, cond, stop_event, event_registry, event_id_counter):
        super().__init__(daemon=True)
        self.name = name
        self.role = role
        self.fruit_type = fruit_type
        self.comm = comm
        self.plate = plate
        self.cond = cond
        self.stop_event = stop_event
        self.event_registry = event_registry
        self.event_id_counter = event_id_counter

    def new_event_id(self):
        return next(self.event_id_counter)

    def run(self):
        while not self.stop_event.is_set():
            time.sleep(random.uniform(0,0.5))  # 自然随机延迟
            if self.role == 'producer':
                with self.cond:
                    slot = self.plate.next_free_slot()
                    if slot is not None:
                        self.plate.contents[slot] = (self.fruit_type, self.name)
                eid = self.new_event_id()
                self.event_registry[eid] = threading.Event()
                self.comm.request_animation.emit(self.name, f"{self.fruit_type}.png", True, eid)
                self.event_registry[eid].wait()
                self.event_registry.pop(eid, None)
                with self.cond:
                    if slot is not None:
                        self.cond.notify_all()
            else:  # consumer
                with self.cond:
                    slot = self.plate.find_fruit_slot(self.fruit_type)
                    if slot is not None:
                        self.plate.contents[slot] = None
                eid = self.new_event_id()
                self.event_registry[eid] = threading.Event()
                self.comm.request_animation.emit(self.name, f"{self.fruit_type}.png", False, eid)
                self.event_registry[eid].wait()
                self.event_registry.pop(eid, None)
                with self.cond:
                    if slot is not None:
                        self.cond.notify_all()

# ---------------- main window ----------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("水果盘子并发仿真（逻辑动画同步）")
        self.setFixedSize(1000,650)

        central = QWidget()
        self.setCentralWidget(central)
        vbox = QVBoxLayout(central)

        # 控件
        ctrl = QHBoxLayout()
        self.btn_start = QPushButton("Start")
        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setEnabled(False)
        ctrl.addWidget(self.btn_start)
        ctrl.addWidget(self.btn_stop)
        ctrl.addSpacerItem(QSpacerItem(20,10,QSizePolicy.Expanding,QSizePolicy.Minimum))
        ctrl.addWidget(QLabel("动画时长(ms)"))
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(100)
        self.slider.setMaximum(2000)
        self.slider.setValue(700)
        self.slider.setFixedWidth(300)
        ctrl.addWidget(self.slider)
        vbox.addLayout(ctrl)

        # 画布
        self.canvas = QFrame()
        self.canvas.setStyleSheet("background:#F0F8FF;")
        self.canvas.setFixedSize(980,560)
        vbox.addWidget(self.canvas)

        # 载入 pixmap
        def load_pix(path):
            p = QPixmap(path)
            if p.isNull():
                print(f"Warning: can't load {path}")
            return p

        self.pix = {k: load_pix(f"{k}.png") for k in ['dad','mom','son','daughter','apple','orange','plate']}

        # actor 初始位置
        self.actor_pos = {
            'Dad': QPoint(60,40),
            'Mom': QPoint(800,40),
            'Son': QPoint(800,360),
            'Daughter': QPoint(60,360)
        }

        # actor labels
        self.actor_labels = {}
        for name,pos in self.actor_pos.items():
            lbl = QLabel(self.canvas)
            pix = self.pix.get(name.lower())
            if pix and not pix.isNull():
                lbl.setPixmap(pix.scaled(120,120,Qt.KeepAspectRatio,Qt.SmoothTransformation))
            else:
                lbl.setText(name)
                lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedSize(120,120)
            lbl.move(pos)
            lbl.show()
            self.actor_labels[name] = lbl

        # plate label
        self.plate_label = QLabel(self.canvas)
        plate_pix = self.pix['plate']
        if plate_pix and not plate_pix.isNull():
            self.plate_label.setPixmap(plate_pix.scaled(240,140,Qt.KeepAspectRatio,Qt.SmoothTransformation))
        else:
            self.plate_label.setText("Plate")
            self.plate_label.setAlignment(Qt.AlignCenter)
        self.plate_label.setFixedSize(240,140)
        self.plate_pos = QPoint(370,210)
        self.plate_label.move(self.plate_pos)
        self.plate_label.show()

        # slots
        self.slot_offsets = [QPoint(45,40), QPoint(150,40)]
        self.plate_fruit_widgets = [None,None]

        # communication
        self.comm = Communicator()
        self.comm.request_animation.connect(self.handle_request_animation)
        self.event_registry = {}
        self.event_id_counter = count(1)

        # synchronization
        self.cond = threading.Condition()
        self.plate = Plate()
        self.stop_event = threading.Event()
        self.threads = []
        self.active_anims = []

        # connections
        self.btn_start.clicked.connect(self.start_simulation)
        self.btn_stop.clicked.connect(self.stop_simulation)
        self.slider.valueChanged.connect(self.on_slider_changed)
        self.animation_duration = self.slider.value()

    def on_slider_changed(self, v):
        self.animation_duration = v

    def start_simulation(self):
        self.stop_event.clear()
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        # reset plate visuals
        self.plate = Plate()
        for w in self.plate_fruit_widgets:
            if w: w.hide()
        self.plate_fruit_widgets = [None,None]
        # create threads
        self.threads = [
            ActorThread('Dad','producer','apple',self.comm,self.plate,self.cond,self.stop_event,self.event_registry,self.event_id_counter),
            ActorThread('Mom','producer','orange',self.comm,self.plate,self.cond,self.stop_event,self.event_registry,self.event_id_counter),
            ActorThread('Son','consumer','orange',self.comm,self.plate,self.cond,self.stop_event,self.event_registry,self.event_id_counter),
            ActorThread('Daughter','consumer','apple',self.comm,self.plate,self.cond,self.stop_event,self.event_registry,self.event_id_counter)
        ]
        for t in self.threads:
            t.start()

    def stop_simulation(self):
        self.stop_event.set()
        with self.cond: self.cond.notify_all()
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)

    def slot_global_pos(self, idx):
        return self.plate_pos + self.slot_offsets[idx]

    def find_plate_slot_by_mark(self, fruit_type):
        for i,v in enumerate(self.plate.contents):
            if v is not None and v[0]==fruit_type:
                return i
        return None

    def handle_request_animation(self, actor_name, fruit_img_path, is_putting, event_id):
        event = self.event_registry.get(event_id)
        if event is None:
            event = threading.Event()
            self.event_registry[event_id] = event
        actor_lbl = self.actor_labels[actor_name]
        fruit_type = fruit_img_path.split('.')[0]

        # determine slot
        slot_idx = self.find_plate_slot_by_mark(fruit_type) if (is_putting==False) else self.plate.next_free_slot()
        if slot_idx is None: slot_idx = -1

        # actor move animation
        start_pos = actor_lbl.pos()
        plate_target = self.slot_global_pos(slot_idx) if slot_idx!=-1 else self.plate_pos + QPoint(90,40)
        anim_actor = QPropertyAnimation(actor_lbl,b"pos")
        anim_actor.setDuration(self.animation_duration)
        anim_actor.setStartValue(start_pos)
        anim_actor.setEndValue(plate_target - QPoint(60,60))
        anim_actor.setEasingCurve(QEasingCurve.OutCubic)
        self.active_anims.append(anim_actor)

        # fruit widget
        fruit_lbl = None
        if is_putting:
            if slot_idx!=-1:
                fruit_lbl = QLabel(self.canvas)
                fruit_pix = self.pix['apple'] if fruit_type=='apple' else self.pix['orange']
                fruit_lbl.setPixmap(fruit_pix.scaled(48,48,Qt.KeepAspectRatio,Qt.SmoothTransformation))
                fruit_lbl.setFixedSize(48,48)
                fruit_lbl.move(start_pos)
                fruit_lbl.show()
        else:
            if slot_idx!=-1 and self.plate_fruit_widgets[slot_idx]:
                fruit_lbl = self.plate_fruit_widgets[slot_idx]

        def after_actor_move():
            # move fruit
            if fruit_lbl:
                anim_fruit = QPropertyAnimation(fruit_lbl,b"pos")
                anim_fruit.setDuration(self.animation_duration)
                anim_fruit.setStartValue(fruit_lbl.pos())
                anim_fruit.setEndValue(self.slot_global_pos(slot_idx) if is_putting else actor_lbl.pos()+QPoint(60,60))
                anim_fruit.setEasingCurve(QEasingCurve.OutCubic)
                self.active_anims.append(anim_fruit)
                def after_fruit_move():
                    if is_putting:
                        self.plate_fruit_widgets[slot_idx] = fruit_lbl
                    else:
                        fruit_lbl.hide()
                        self.plate_fruit_widgets[slot_idx] = None
                    self.active_anims.remove(anim_fruit)
                anim_fruit.finished.connect(after_fruit_move)
                anim_fruit.start()

            # move actor back
            anim_back = QPropertyAnimation(actor_lbl,b"pos")
            anim_back.setDuration(self.animation_duration)
            anim_back.setStartValue(actor_lbl.pos())
            anim_back.setEndValue(start_pos)
            anim_back.setEasingCurve(QEasingCurve.InOutCubic)
            self.active_anims.append(anim_back)
            anim_back.finished.connect(lambda: (event.set(), self.active_anims.remove(anim_back)))
            anim_back.start()
            self.active_anims.remove(anim_actor)

        anim_actor.finished.connect(after_actor_move)
        anim_actor.start()

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__=="__main__":
    main()
