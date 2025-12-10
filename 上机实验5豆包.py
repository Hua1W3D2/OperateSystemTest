import random
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.font_manager as fm

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']  # 用于正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


# 1. 生成指令序列
def generate_instructions():
    random.seed()  # 初始化随机数生成器
    instructions = [0] * 320
    m = 160  # 起始地址

    for i in range(80):
        j = i * 4
        # 顺序执行指令
        instructions[j] = m
        instructions[j + 1] = m + 1

        # 生成前地址部分指令（[0, m-1]）
        instructions[j + 2] = int(instructions[j] * random.random())
        instructions[j + 2] = max(0, min(instructions[j] - 1, instructions[j + 2]))  # 边界保护

        # 顺序执行下一条
        instructions[j + 3] = instructions[j + 2] + 1

        # 生成后地址部分指令（(a[j+3], 319]）
        next_m = instructions[j + 3] + int((319 - instructions[j + 3]) * random.random())
        m = max(instructions[j + 3] + 1, min(319, next_m))  # 边界保护

    return instructions


# 2. 转换为页地址流（每页10条指令）
def instructions_to_pages(instructions):
    return [addr // 10 for addr in instructions]


# 3. FIFO页面置换算法
def fifo(page_stream, frame_count):
    frames = []  # 按进入顺序存储页面
    page_faults = 0
    hit_miss = []  # 记录每个页面的命中状态（True=命中，False=缺页）

    for page in page_stream:
        if page not in frames:
            page_faults += 1
            hit_miss.append(False)
            if len(frames) >= frame_count:
                frames.pop(0)  # 淘汰队首页面
            frames.append(page)
        else:
            hit_miss.append(True)

    hit_rate = 1 - (page_faults / len(page_stream))
    return hit_rate, hit_miss


# 4. LRU页面置换算法
def lru(page_stream, frame_count):
    frames = {}  # {页面: 最后使用时间戳}
    page_faults = 0
    hit_miss = []
    time = 0

    for page in page_stream:
        time += 1
        if page in frames:
            frames[page] = time  # 更新最后使用时间
            hit_miss.append(True)
        else:
            page_faults += 1
            hit_miss.append(False)
            if len(frames) >= frame_count:
                # 淘汰最久未使用的页面
                lru_page = min(frames, key=frames.get)
                del frames[lru_page]
            frames[page] = time

    hit_rate = 1 - (page_faults / len(page_stream))
    return hit_rate, hit_miss


# 5. OPT页面置换算法（最佳淘汰）
def opt(page_stream, frame_count):
    frames = []
    page_faults = 0
    hit_miss = []

    for i in range(len(page_stream)):
        page = page_stream[i]
        if page in frames:
            hit_miss.append(True)
        else:
            page_faults += 1
            hit_miss.append(False)
            if len(frames) >= frame_count:
                # 找到未来最久不使用的页面
                farthest = -1
                victim = None
                for f in frames:
                    try:
                        pos = page_stream.index(f, i + 1)
                    except ValueError:
                        pos = float('inf')  # 未来不再出现
                    if pos > farthest:
                        farthest = pos
                        victim = f
                frames.remove(victim)
            frames.append(page)

    hit_rate = 1 - (page_faults / len(page_stream))
    return hit_rate, hit_miss


# 6. LFU页面置换算法（最少访问）
def lfu(page_stream, frame_count):
    frames = {}  # {页面: (访问次数, 最后使用时间)}
    page_faults = 0
    hit_miss = []
    time = 0

    for page in page_stream:
        time += 1
        if page in frames:
            count, _ = frames[page]
            frames[page] = (count + 1, time)  # 增加访问次数
            hit_miss.append(True)
        else:
            page_faults += 1
            hit_miss.append(False)
            if len(frames) >= frame_count:
                # 淘汰访问次数最少的，次数相同则淘汰最久未使用的
                victim = min(frames.items(), key=lambda x: (x[1][0], x[1][1]))[0]
                del frames[victim]
            frames[page] = (1, time)

    hit_rate = 1 - (page_faults / len(page_stream))
    return hit_rate, hit_miss


# 7. GUI界面实现
class PageReplacementSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("页面置换算法模拟器")
        self.root.geometry("1300x800")

        # 初始化数据
        self.instructions = []
        self.page_stream = []
        self.frame_count_var = tk.IntVar(value=4)  # 默认显示4页的命中情况

        # 创建界面组件
        self.create_widgets()

        # 初始运行一次
        self.run_simulation()

    def create_widgets(self):
        # 顶部控制面板
        control_panel = ttk.Frame(self.root)
        control_panel.pack(fill=tk.X, padx=10, pady=10)

        # 运行按钮
        self.run_button = ttk.Button(control_panel, text="运行/重新运行模拟", command=self.run_simulation)
        self.run_button.pack(side=tk.LEFT, padx=5)

        # 帧数选择控件
        ttk.Label(control_panel, text="查看帧数:").pack(side=tk.LEFT, padx=5)
        frame_spin = ttk.Spinbox(control_panel, from_=4, to=32, textvariable=self.frame_count_var,
                                 command=self.update_hit_display, width=10)
        frame_spin.pack(side=tk.LEFT, padx=5)

        # 左侧面板：序列展示区
        left_panel = ttk.LabelFrame(self.root, text="序列详情")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 指令序列展示
        ttk.Label(left_panel, text="指令地址序列:").pack(anchor=tk.W)
        self.inst_text = scrolledtext.ScrolledText(left_panel, height=8, width=40)
        self.inst_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 页地址序列展示
        ttk.Label(left_panel, text="页地址序列:").pack(anchor=tk.W)
        self.page_text = scrolledtext.ScrolledText(left_panel, height=8, width=40)
        self.page_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 命中情况展示
        ttk.Label(left_panel, text="FIFO命中情况 (T=命中, F=缺页):").pack(anchor=tk.W)
        self.hit_text = scrolledtext.ScrolledText(left_panel, height=8, width=40)
        self.hit_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 右侧面板：结果展示区
        right_panel = ttk.LabelFrame(self.root, text="算法结果")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 结果表格
        ttk.Label(right_panel, text="各算法命中率对比表:").pack(anchor=tk.W)
        self.result_table = ttk.Treeview(right_panel, columns=("帧数", "FIFO", "LRU", "OPT", "LFU"), show="headings")
        self.result_table.heading("帧数", text="帧数")
        self.result_table.heading("FIFO", text="FIFO")
        self.result_table.heading("LRU", text="LRU")
        self.result_table.heading("OPT", text="OPT")
        self.result_table.heading("LFU", text="LFU")
        self.result_table.column("帧数", width=80)
        self.result_table.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 结果图表
        ttk.Label(right_panel, text="命中率趋势图:").pack(anchor=tk.W)
        self.fig = plt.Figure(figsize=(8, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_panel)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def run_simulation(self):
        """运行/重新运行整个模拟过程"""
        try:
            # 生成新的指令序列和页地址流
            self.instructions = generate_instructions()
            self.page_stream = instructions_to_pages(self.instructions)

            # 更新显示
            self.update_sequence_display()
            self.update_hit_display()
            self.calculate_all_results()

            messagebox.showinfo("成功", "模拟运行完成！")
        except Exception as e:
            messagebox.showerror("错误", f"运行过程中出现错误：{str(e)}")

    def update_sequence_display(self):
        """更新指令序列和页地址序列的显示"""
        self.inst_text.delete(1.0, tk.END)
        self.inst_text.insert(tk.END, " ".join(map(str, self.instructions)))

        self.page_text.delete(1.0, tk.END)
        self.page_text.insert(tk.END, " ".join(map(str, self.page_stream)))

    def update_hit_display(self):
        """更新命中情况的显示"""
        if not self.page_stream:
            return

        frame_count = self.frame_count_var.get()
        _, hit_miss = fifo(self.page_stream, frame_count)
        hit_str = " ".join(["T" if h else "F" for h in hit_miss])
        self.hit_text.delete(1.0, tk.END)
        self.hit_text.insert(tk.END, hit_str)

    def calculate_all_results(self):
        """计算所有算法在不同帧数下的结果"""
        # 计算4-32页的所有算法结果
        self.frame_list = list(range(4, 33))
        self.fifo_rates = []
        self.lru_rates = []
        self.opt_rates = []
        self.lfu_rates = []

        # 清空表格
        for item in self.result_table.get_children():
            self.result_table.delete(item)

        # 计算并填充数据
        for fc in self.frame_list:
            fifo_rate, _ = fifo(self.page_stream, fc)
            lru_rate, _ = lru(self.page_stream, fc)
            opt_rate, _ = opt(self.page_stream, fc)
            lfu_rate, _ = lfu(self.page_stream, fc)

            self.fifo_rates.append(round(fifo_rate, 4))
            self.lru_rates.append(round(lru_rate, 4))
            self.opt_rates.append(round(opt_rate, 4))
            self.lfu_rates.append(round(lfu_rate, 4))

            # 插入表格
            self.result_table.insert("", tk.END, values=(fc, round(fifo_rate, 4), round(lru_rate, 4),
                                                         round(opt_rate, 4), round(lfu_rate, 4)))

        # 绘制趋势图（使用中文标签）
        self.ax.clear()
        self.ax.plot(self.frame_list, self.fifo_rates, marker='o', label='FIFO', linestyle='-')
        self.ax.plot(self.frame_list, self.lru_rates, marker='s', label='LRU', linestyle='-')
        self.ax.plot(self.frame_list, self.opt_rates, marker='^', label='OPT', linestyle='-')
        self.ax.plot(self.frame_list, self.lfu_rates, marker='*', label='LFU', linestyle='-')

        self.ax.set_xlabel("实存页数")
        self.ax.set_ylabel("命中率")
        self.ax.set_title("页面置换算法命中率对比")
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw()


# 主程序入口
if __name__ == "__main__":
    root = tk.Tk()
    app = PageReplacementSimulator(root)
    root.mainloop()