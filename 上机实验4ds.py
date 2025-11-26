import tkinter as tk
from tkinter import ttk, messagebox
import random


class PCB:
    def __init__(self, name, priority, run_time):
        self.name = name
        self.priority = priority
        self.run_time = run_time
        self.status = "R"  # 初始状态为就绪
        self.next = None  # 指向下一个PCB的指针

    def clone(self):
        """创建PCB的副本"""
        return PCB(self.name, self.priority, self.run_time)


class ProcessScheduler:
    def __init__(self):
        self.processes = []
        self.initial_processes = []  # 保存初始进程状态
        self.head = None
        self.current_process = None
        self.step_count = 0
        self.is_auto_running = False
        self.auto_speed = 1000  # 自动执行速度（毫秒）

    def initialize_processes(self, process_data):
        """初始化进程"""
        self.processes = []
        for name, priority, run_time in process_data:
            self.processes.append(PCB(name, priority, run_time))

        # 保存初始进程状态
        self.initial_processes = [p.clone() for p in self.processes]

        # 按优先数从大到小排序并连接队列
        self.processes.sort(key=lambda p: p.priority, reverse=True)

        # 连接队列
        for i in range(len(self.processes) - 1):
            self.processes[i].next = self.processes[i + 1]

        if self.processes:
            self.head = self.processes[0]

        self.step_count = 0

    def get_queue_info(self):
        """获取队列信息"""
        queue_info = []
        current = self.head
        while current:
            queue_info.append({
                "name": current.name,
                "priority": current.priority,
                "run_time": current.run_time,
                "status": current.status,
                "next": current.next.name if current.next else "0"
            })
            current = current.next
        return queue_info

    def get_initial_processes_info(self):
        """获取初始进程信息"""
        initial_info = []
        for p in self.initial_processes:
            initial_info.append({
                "name": p.name,
                "priority": p.priority,
                "run_time": p.run_time,
                "status": p.status
            })
        return initial_info

    def schedule_step(self):
        """执行一步调度"""
        if not self.head:
            return False, "所有进程已执行完毕！"

        # 选择队首进程运行
        self.current_process = self.head

        # 记录调度信息
        step_info = f"第{self.step_count + 1}次调度: 选中进程 {self.current_process.name}\n"
        step_info += f"  运行前: 优先数={self.current_process.priority}, 要求运行时间={self.current_process.run_time}\n"

        # 模拟进程运行：优先数-1，要求运行时间-1
        self.current_process.priority -= 1
        self.current_process.run_time -= 1

        step_info += f"  运行后: 优先数={self.current_process.priority}, 要求运行时间={self.current_process.run_time}\n"

        # 如果要求运行时间为0，则结束进程
        if self.current_process.run_time <= 0:
            self.current_process.status = "E"
            step_info += f"  进程 {self.current_process.name} 执行完毕，状态改为结束(E)\n"

            # 从队列中移除该进程
            if self.head == self.current_process:
                self.head = self.current_process.next
            else:
                prev = self.head
                while prev and prev.next != self.current_process:
                    prev = prev.next
                if prev:
                    prev.next = self.current_process.next
        else:
            # 将进程重新插入队列（按优先数大小）
            step_info += f"  进程 {self.current_process.name} 重新插入队列\n"

            # 从队列中移除当前进程
            if self.head == self.current_process:
                self.head = self.current_process.next
            else:
                prev = self.head
                while prev and prev.next != self.current_process:
                    prev = prev.next
                if prev:
                    prev.next = self.current_process.next

            # 按优先数重新插入
            self.current_process.next = None

            if not self.head:
                self.head = self.current_process
            else:
                # 如果当前进程的优先数大于等于队首进程，则插入队首
                if self.current_process.priority >= self.head.priority:
                    self.current_process.next = self.head
                    self.head = self.current_process
                else:
                    # 寻找插入位置
                    prev = self.head
                    current = self.head.next

                    while current and current.priority > self.current_process.priority:
                        prev = current
                        current = current.next

                    prev.next = self.current_process
                    self.current_process.next = current

        self.step_count += 1

        # 获取队列变化信息
        queue_info = self.get_queue_info()
        step_info += "  队列变化: "
        for p in queue_info:
            step_info += f"{p['name']}(P:{p['priority']}, T:{p['run_time']}, S:{p['status']}) -> "
        step_info += "NULL\n"

        return True, step_info

    def reset(self):
        """重置调度器"""
        self.head = None
        self.current_process = None
        self.step_count = 0
        self.is_auto_running = False


class ProcessSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("进程调度模拟 - 动态优先数调度算法")
        self.root.geometry("900x700")

        self.scheduler = ProcessScheduler()

        self.setup_ui()
        self.set_default_processes()

    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)

        # 标题
        title_label = ttk.Label(main_frame, text="进程调度模拟程序", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        # 进程设置区域
        setup_frame = ttk.LabelFrame(main_frame, text="进程设置", padding="5")
        setup_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        setup_frame.columnconfigure(1, weight=1)

        # 默认进程按钮
        ttk.Button(setup_frame, text="使用默认进程", command=self.set_default_processes).grid(row=0, column=0,
                                                                                              padx=(0, 10))

        # 手动输入进程按钮
        ttk.Button(setup_frame, text="手动输入进程", command=self.manual_input_dialog).grid(row=0, column=1,
                                                                                            padx=(0, 10))

        # 显示初始进程按钮
        ttk.Button(setup_frame, text="显示初始进程", command=self.show_initial_processes).grid(row=0, column=2,
                                                                                               padx=(0, 10))

        # 进程表格框架
        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        table_frame.columnconfigure(0, weight=1)
        table_frame.columnconfigure(1, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # 当前进程队列表格
        ttk.Label(table_frame, text="当前进程队列", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W)
        columns = ("进程名", "优先数", "要求运行时间", "状态")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=5)
        self.tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        # 设置列标题
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        # 初始进程表格
        ttk.Label(table_frame, text="初始进程设置", font=("Arial", 10, "bold")).grid(row=0, column=1, sticky=tk.W)
        self.initial_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=5)
        self.initial_tree.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 设置列标题
        for col in columns:
            self.initial_tree.heading(col, text=col)
            self.initial_tree.column(col, width=100)

        # 控制区域
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        control_frame.columnconfigure(1, weight=1)

        # 单步执行按钮
        ttk.Button(control_frame, text="单步执行", command=self.step_execution).grid(row=0, column=0, padx=(0, 10))

        # 自动执行按钮
        self.auto_btn = ttk.Button(control_frame, text="开始自动执行", command=self.toggle_auto_execution)
        self.auto_btn.grid(row=0, column=1, padx=(0, 10))

        # 速度控制
        speed_frame = ttk.Frame(control_frame)
        speed_frame.grid(row=0, column=2, padx=(0, 10))
        ttk.Label(speed_frame, text="速度:").grid(row=0, column=0)
        self.speed_var = tk.StringVar(value="中速")
        speed_combo = ttk.Combobox(speed_frame, textvariable=self.speed_var,
                                   values=["慢速", "中速", "快速"], state="readonly", width=8)
        speed_combo.grid(row=0, column=1)
        speed_combo.bind("<<ComboboxSelected>>", self.on_speed_change)

        # 字体大小控制
        font_frame = ttk.Frame(control_frame)
        font_frame.grid(row=0, column=3, padx=(0, 10))
        ttk.Label(font_frame, text="字体大小:").grid(row=0, column=0)
        self.font_size_var = tk.StringVar(value="12")
        font_combo = ttk.Combobox(font_frame, textvariable=self.font_size_var,
                                  values=["10", "12", "14", "16", "18"], state="readonly", width=5)
        font_combo.grid(row=0, column=1)
        font_combo.bind("<<ComboboxSelected>>", self.on_font_size_change)

        # 重置按钮
        ttk.Button(control_frame, text="重置", command=self.reset_scheduler).grid(row=0, column=4)

        # 输出区域
        output_frame = ttk.LabelFrame(main_frame, text="调度过程输出", padding="5")
        output_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

        # 输出文本框 - 设置默认字体大小
        self.output_text = tk.Text(output_frame, wrap=tk.WORD, height=15, font=("宋体", 12))
        scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)

        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

    def on_font_size_change(self, event):
        """改变字体大小"""
        font_size = int(self.font_size_var.get())
        # 直接设置文本框的字体
        self.output_text.configure(font=("宋体", font_size))

    def set_default_processes(self):
        """设置默认进程"""
        default_processes = [
            ("P1", random.randint(1, 10), random.randint(1, 5)),
            ("P2", random.randint(1, 10), random.randint(1, 5)),
            ("P3", random.randint(1, 10), random.randint(1, 5)),
            ("P4", random.randint(1, 10), random.randint(1, 5)),
            ("P5", random.randint(1, 10), random.randint(1, 5))
        ]

        self.scheduler.initialize_processes(default_processes)
        self.update_process_table()
        self.update_initial_table()
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "已设置默认进程，点击单步执行开始调度。\n")

    def manual_input_dialog(self):
        """手动输入进程对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("手动输入进程参数")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        # 创建输入框架
        input_frame = ttk.Frame(dialog, padding="10")
        input_frame.pack(fill=tk.BOTH, expand=True)

        # 表头
        ttk.Label(input_frame, text="进程名").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(input_frame, text="优先数").grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(input_frame, text="要求运行时间").grid(row=0, column=2, padx=5, pady=5)

        # 输入框
        entries = []
        for i in range(5):
            ttk.Label(input_frame, text=f"P{i + 1}").grid(row=i + 1, column=0, padx=5, pady=5)

            priority_var = tk.StringVar(value=str(random.randint(1, 10)))
            priority_entry = ttk.Entry(input_frame, textvariable=priority_var, width=10)
            priority_entry.grid(row=i + 1, column=1, padx=5, pady=5)

            run_time_var = tk.StringVar(value=str(random.randint(1, 5)))
            run_time_entry = ttk.Entry(input_frame, textvariable=run_time_var, width=10)
            run_time_entry.grid(row=i + 1, column=2, padx=5, pady=5)

            entries.append((priority_var, run_time_var))

        # 按钮框架
        button_frame = ttk.Frame(dialog, padding="10")
        button_frame.pack(fill=tk.X)

        def confirm():
            process_data = []
            for i in range(5):
                try:
                    priority = int(entries[i][0].get())
                    run_time = int(entries[i][1].get())
                    if priority <= 0 or run_time <= 0:
                        raise ValueError("数值必须为正整数")
                    process_data.append((f"P{i + 1}", priority, run_time))
                except ValueError as e:
                    messagebox.showerror("输入错误", f"进程P{i + 1}的参数无效: {e}")
                    return

            self.scheduler.initialize_processes(process_data)
            self.update_process_table()
            self.update_initial_table()
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "已设置手动输入进程，点击单步执行开始调度。\n")
            dialog.destroy()

        ttk.Button(button_frame, text="确认", command=confirm).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)

    def update_process_table(self):
        """更新进程表格"""
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 添加进程数据
        queue_info = self.scheduler.get_queue_info()
        for p in queue_info:
            self.tree.insert("", tk.END, values=(
                p["name"], p["priority"], p["run_time"], p["status"]
            ))

    def update_initial_table(self):
        """更新初始进程表格"""
        # 清空表格
        for item in self.initial_tree.get_children():
            self.initial_tree.delete(item)

        # 添加初始进程数据
        initial_info = self.scheduler.get_initial_processes_info()
        for p in initial_info:
            self.initial_tree.insert("", tk.END, values=(
                p["name"], p["priority"], p["run_time"], p["status"]
            ))

    def show_initial_processes(self):
        """显示初始进程对话框"""
        if not self.scheduler.initial_processes:
            messagebox.showinfo("初始进程", "没有初始进程数据")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("初始进程设置")
        dialog.geometry("500x300")
        dialog.transient(self.root)

        # 创建表格
        columns = ("进程名", "初始优先数", "初始要求运行时间", "初始状态")
        tree = ttk.Treeview(dialog, columns=columns, show="headings", height=5)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 设置列标题
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        # 添加初始进程数据
        initial_info = self.scheduler.get_initial_processes_info()
        for p in initial_info:
            tree.insert("", tk.END, values=(
                p["name"], p["priority"], p["run_time"], p["status"]
            ))

    def step_execution(self):
        """单步执行调度"""
        if self.scheduler.is_auto_running:
            return

        success, info = self.scheduler.schedule_step()
        self.output_text.insert(tk.END, info + "\n")
        self.output_text.see(tk.END)
        self.update_process_table()

        if not success:
            messagebox.showinfo("调度完成", info + "\n\n调度过程已完成，您可以在左侧查看初始进程设置。")

    def toggle_auto_execution(self):
        """切换自动执行状态"""
        if self.scheduler.is_auto_running:
            self.scheduler.is_auto_running = False
            self.auto_btn.config(text="开始自动执行")
        else:
            self.scheduler.is_auto_running = True
            self.auto_btn.config(text="停止自动执行")
            self.auto_execution()

    def auto_execution(self):
        """自动执行调度"""
        if not self.scheduler.is_auto_running:
            return

        def run_step():
            success, info = self.scheduler.schedule_step()
            self.output_text.insert(tk.END, info + "\n")
            self.output_text.see(tk.END)
            self.update_process_table()

            if success and self.scheduler.is_auto_running:
                self.root.after(self.scheduler.auto_speed, run_step)
            else:
                self.scheduler.is_auto_running = False
                self.auto_btn.config(text="开始自动执行")
                if not success:
                    messagebox.showinfo("调度完成", info + "\n\n调度过程已完成，您可以在左侧查看初始进程设置。")

        run_step()

    def on_speed_change(self, event):
        """改变自动执行速度"""
        speed = self.speed_var.get()
        if speed == "慢速":
            self.scheduler.auto_speed = 2000
        elif speed == "中速":
            self.scheduler.auto_speed = 1000
        elif speed == "快速":
            self.scheduler.auto_speed = 500

    def reset_scheduler(self):
        """重置调度器"""
        self.scheduler.reset()
        self.update_process_table()
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "调度器已重置，请设置进程参数后开始调度。\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = ProcessSchedulerApp(root)
    root.mainloop()