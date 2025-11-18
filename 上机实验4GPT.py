import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os, datetime

class PCB:
    def __init__(self, name, priority, time):
        self.name = name
        self.priority = priority
        self.time = time
        self.status = "R"  # R=就绪, E=结束

class SchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("进程调度模拟程序（动态优先数 + 日志记录）")
        self.root.geometry("800x600")
        self.pcbs = []

        # ==== 输入区 ====
        frame_input = ttk.LabelFrame(root, text="初始设置", padding=10)
        frame_input.pack(fill="x", padx=10, pady=5)

        self.entries = []
        for i in range(5):
            row = tk.Frame(frame_input)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"P{i+1} 优先数:").pack(side="left", padx=5)
            e1 = tk.Entry(row, width=5)
            e1.insert(0, str(5-i))
            e1.pack(side="left")
            tk.Label(row, text=" 运行时间:").pack(side="left")
            e2 = tk.Entry(row, width=5)
            e2.insert(0, str(i+1))
            e2.pack(side="left")
            self.entries.append((e1, e2))

        self.btn_start = ttk.Button(frame_input, text="开始调度", command=self.start)
        self.btn_start.pack(pady=5)

        # ==== 输出区 ====
        frame_output = ttk.LabelFrame(root, text="运行结果", padding=10)
        frame_output.pack(fill="both", expand=True, padx=10, pady=5)

        self.label_current = tk.Label(frame_output, text="当前执行：", font=("微软雅黑", 12))
        self.label_current.pack(anchor="w")

        self.label_queue = tk.Label(frame_output, text="就绪队列：", font=("微软雅黑", 12))
        self.label_queue.pack(anchor="w")

        # PCB表
        columns = ("name", "priority", "time", "status")
        self.tree = ttk.Treeview(frame_output, columns=columns, show="headings", height=6)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(fill="x", pady=5)

        # ==== 日志显示区 ====
        frame_log = ttk.LabelFrame(root, text="调度日志", padding=5)
        frame_log.pack(fill="both", expand=True, padx=10, pady=5)
        self.log_box = scrolledtext.ScrolledText(frame_log, wrap="word", height=10, font=("Consolas", 10))
        self.log_box.pack(fill="both", expand=True)

        # 日志文件路径
        os.makedirs("logs", exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_path = f"logs/schedule_log_{timestamp}.txt"
        self.log_file = open(self.log_path, "w", encoding="utf-8")

        self.step_delay = 1000
        self.step_idx = 0
        self.queue = []

    # === 写入日志到界面和文件 ===
    def log(self, text):
        self.log_box.insert(tk.END, text + "\n")
        self.log_box.see(tk.END)

    def start(self):
        try:
            self.pcbs = []
            for i in range(5):
                prio = int(self.entries[i][0].get())
                time = int(self.entries[i][1].get())
                self.pcbs.append(PCB(f"P{i+1}", prio, time))
        except ValueError:
            messagebox.showerror("错误", "请输入整数！")
            return

        self.log_box.delete(1.0, tk.END)
        self.step_idx = 0
        self.log(f"==== 进程调度模拟开始 ====")
        self.schedule_loop()

    def schedule_loop(self):
        ready = [p for p in self.pcbs if p.status == "R"]
        if not ready:
            self.log("所有进程均已结束。调度完成。")
            self.label_current.config(text="调度完成！")
            self.label_queue.config(text="所有进程状态：结束")
            self.log_file.write("\n==== 调度结束 ====\n")
            self.log_file.close()
            return

        ready.sort(key=lambda x: (-x.priority, x.name))
        current = ready[0]
        self.step_idx += 1

        self.label_current.config(text=f"步骤 {self.step_idx}: 当前执行 {current.name}")
        self.label_queue.config(text="就绪队列: " + " -> ".join(p.name for p in ready))
        self.log(f"[步骤 {self.step_idx}] 执行进程 {current.name}: priority={current.priority}, time={current.time}")

        # 模拟执行一次
        current.priority -= 1
        current.time -= 1
        if current.time <= 0:
            current.status = "E"
            self.log(f"→ {current.name} 已完成，状态置为 E。")
        else:
            self.log(f"→ {current.name} 执行后: priority={current.priority}, 剩余时间={current.time}")

        # 刷新PCB表格
        for i in self.tree.get_children():
            self.tree.delete(i)
        for p in self.pcbs:
            self.tree.insert("", "end", values=(p.name, p.priority, p.time, p.status))

        # 下一步
        if any(p.status == "R" for p in self.pcbs):
            self.root.after(self.step_delay, self.schedule_loop)
        else:
            self.schedule_loop()  # 结束处理

if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerGUI(root)
    root.mainloop()
