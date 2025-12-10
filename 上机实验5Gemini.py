import random
import tkinter as tk
from tkinter import ttk, scrolledtext
from collections import deque


# 1. 指令序列生成 (V2 - 确保无重复且符合规则)
def generate_instruction_sequence(length=320):
    """
    生成一个包含320条指令的、无重复的序列。
    (1) ~50%的指令是顺序执行 (m -> m+1)。
    (2) ~25%的指令是前向跳转。
    (3) ~25%的指令是后向跳转。
    """
    if length <= 0:
        return []

    # 使用集合(Set)来存储未使用的地址，以实现O(1)的快速查找和删除
    pool = set(range(length))
    sequence = []

    # 1. 随机选择一个起点
    start_addr = random.choice(list(pool))
    sequence.append(start_addr)
    pool.remove(start_addr)

    # 2. 循环生成剩余的指令
    while pool:  # 当池中还有可用的地址时
        last_instr = sequence[-1]

        # 尝试执行三种操作，直到成功一种
        # 使用随机的起始点来避免偏见 (例如总是先尝试顺序执行)
        choice = random.random()

        # 尝试顺序执行 (50% 概率)
        if choice < 0.50:
            next_sequential = last_instr + 1
            if next_sequential < length and next_sequential in pool:
                sequence.append(next_sequential)
                pool.remove(next_sequential)
                continue  # 成功，进入下一次循环

        # 尝试前向跳转 (25% 概率)
        if choice < 0.75:
            forward_options = [p for p in pool if p < last_instr]
            if forward_options:
                jump_addr = random.choice(forward_options)
                sequence.append(jump_addr)
                pool.remove(jump_addr)
                continue  # 成功，进入下一次循环

        # 尝试后向跳转 (25% 概率 + 作为其他失败情况的备选)
        backward_options = [p for p in pool if p > last_instr]
        if backward_options:
            jump_addr = random.choice(backward_options)
            sequence.append(jump_addr)
            pool.remove(jump_addr)
            continue  # 成功，进入下一次循环

        # **全局备选方案 (Fallback)**
        # 如果上述所有尝试都失败了（例如，想顺序但m+1已被用，想前向但前方无可用地址，想后向但后方也无可用地址），
        # 为了避免程序卡死，就从剩余的池中随机选一个。
        if pool:
            fallback_addr = random.choice(list(pool))
            sequence.append(fallback_addr)
            pool.remove(fallback_addr)

    return sequence


# 2. 转换为页地址流 (无变化)
def convert_to_page_stream(instructions, instructions_per_page=10):
    return [instr // instructions_per_page for instr in instructions]


# 3. 页面调度算法实现 (无变化)
def simulate_fifo(page_stream, frame_count):
    """先进先出算法 (FIFO)"""
    memory = deque()
    page_faults = 0
    hit_miss_sequence = []

    for page in page_stream:
        if page not in memory:
            page_faults += 1
            if len(memory) == frame_count:
                memory.popleft()
            memory.append(page)
            hit_miss_sequence.append('MISS')
        else:
            hit_miss_sequence.append('HIT')

    return page_faults, hit_miss_sequence


def simulate_lru(page_stream, frame_count):
    """最近最少使用算法 (LRU)"""
    memory = []
    page_faults = 0
    hit_miss_sequence = []

    for page in page_stream:
        if page not in memory:
            page_faults += 1
            if len(memory) == frame_count:
                memory.pop(0)
            memory.append(page)
            hit_miss_sequence.append('MISS')
        else:
            memory.remove(page)
            memory.append(page)
            hit_miss_sequence.append('HIT')

    return page_faults, hit_miss_sequence


def simulate_opt(page_stream, frame_count):
    """最佳淘汰算法 (OPT)"""
    memory = []
    page_faults = 0
    hit_miss_sequence = []

    for i, page in enumerate(page_stream):
        if page not in memory:
            page_faults += 1
            if len(memory) < frame_count:
                memory.append(page)
            else:
                future_uses = {}
                for mem_page in memory:
                    try:
                        next_use_index = page_stream[i + 1:].index(mem_page)
                        future_uses[mem_page] = next_use_index
                    except ValueError:
                        future_uses[mem_page] = float('inf')

                page_to_replace = max(future_uses, key=future_uses.get)
                memory[memory.index(page_to_replace)] = page
            hit_miss_sequence.append('MISS')
        else:
            hit_miss_sequence.append('HIT')

    return page_faults, hit_miss_sequence


def simulate_lfu(page_stream, frame_count):
    """最少访问页面算法 (LFU)"""
    memory = {}  # page -> [frequency, entry_time]
    page_faults = 0
    hit_miss_sequence = []

    for t, page in enumerate(page_stream):
        if page in memory:
            memory[page][0] += 1  # 增加频率
            hit_miss_sequence.append('HIT')
        else:
            page_faults += 1
            if len(memory) < frame_count:
                memory[page] = [1, t]
            else:
                # 找到最不常用的页 (LFU)
                # 如果频率相同，则找最早进入的页 (FIFO tie-breaker)
                lfu_page = min(memory.keys(), key=lambda p: (memory[p][0], memory[p][1]))
                del memory[lfu_page]
                memory[page] = [1, t]
            hit_miss_sequence.append('MISS')

    return page_faults, hit_miss_sequence


# 4. GUI 界面 (无变化)
class PageReplacementSimulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("页面调度算法模拟器")
        self.geometry("1000x750")

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill="both", expand=True)

        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill="x", pady=5)

        ttk.Label(control_frame, text="内存容量(k):").pack(side="left", padx=(0, 5))
        self.k_var = tk.IntVar(value=4)
        self.k_spinbox = ttk.Spinbox(control_frame, from_=4, to=32, textvariable=self.k_var, width=5)
        self.k_spinbox.pack(side="left", padx=5)

        self.run_button = ttk.Button(control_frame, text="1. 生成序列并开始模拟", command=self.run_simulation)
        self.run_button.pack(side="left", padx=10)

        self.show_trace_button = ttk.Button(control_frame, text="2. 查看选中容量的命中序列",
                                            command=self.show_hit_miss_trace)
        self.show_trace_button.pack(side="left", padx=10)
        self.show_trace_button['state'] = 'disabled'

        paned_window = ttk.PanedWindow(main_frame, orient='horizontal')
        paned_window.pack(fill='both', expand=True, pady=10)

        left_pane = ttk.Frame(paned_window, width=300)
        paned_window.add(left_pane, weight=1)

        ttk.Label(left_pane, text="生成的指令序列 (320条, 无重复)").pack(anchor='w')
        self.instr_text = scrolledtext.ScrolledText(left_pane, height=10, wrap=tk.WORD, state='disabled')
        self.instr_text.pack(fill='both', expand=True, pady=(0, 10))

        ttk.Label(left_pane, text="转换的页地址流 (320个)").pack(anchor='w')
        self.page_text = scrolledtext.ScrolledText(left_pane, height=10, wrap=tk.WORD, state='disabled')
        self.page_text.pack(fill='both', expand=True)

        right_pane = ttk.Frame(paned_window)
        paned_window.add(right_pane, weight=2)

        ttk.Label(right_pane, text="不同内存容量下的命中率结果").pack(anchor='w')
        cols = ("k (页框数)", "FIFO", "LRU", "OPT", "LFU")
        self.tree = ttk.Treeview(right_pane, columns=cols, show='headings')
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='center')
        self.tree.pack(fill='both', expand=True)

        trace_frame = ttk.Frame(main_frame)
        trace_frame.pack(fill='both', expand=True, pady=5)
        ttk.Label(trace_frame, text="命中/缺页(Hit/Miss)详细序列").pack(anchor='w')
        self.trace_text = scrolledtext.ScrolledText(trace_frame, height=10, wrap=tk.WORD, state='disabled')
        self.trace_text.pack(fill='both', expand=True)

        self.full_results = {}

    def display_in_text_widget(self, widget, content):
        widget.config(state='normal')
        widget.delete('1.0', tk.END)
        widget.insert(tk.END, content)
        widget.config(state='disabled')

    def run_simulation(self):
        instructions = generate_instruction_sequence()
        page_stream = convert_to_page_stream(instructions)
        self.page_stream_data = page_stream

        self.display_in_text_widget(self.instr_text, str(instructions))
        self.display_in_text_widget(self.page_text, str(page_stream))

        for item in self.tree.get_children():
            self.tree.delete(item)
        self.full_results = {}

        for k in range(4, 33):
            fifo_faults, fifo_trace = simulate_fifo(page_stream, k)
            fifo_rate = 1 - fifo_faults / len(page_stream)
            lru_faults, lru_trace = simulate_lru(page_stream, k)
            lru_rate = 1 - lru_faults / len(page_stream)
            opt_faults, opt_trace = simulate_opt(page_stream, k)
            opt_rate = 1 - opt_faults / len(page_stream)
            lfu_faults, lfu_trace = simulate_lfu(page_stream, k)
            lfu_rate = 1 - lfu_faults / len(page_stream)

            self.tree.insert("", "end", values=(
                k, f"{fifo_rate:.4f}", f"{lru_rate:.4f}", f"{opt_rate:.4f}", f"{lfu_rate:.4f}"
            ))
            self.full_results[k] = {
                'FIFO': fifo_trace, 'LRU': lru_trace, 'OPT': opt_trace, 'LFU': lfu_trace
            }

        self.show_trace_button['state'] = 'normal'
        self.display_in_text_widget(self.trace_text, "模拟完成！请在上方选择内存容量(k)并点击按钮查看详细命中序列。")

    def show_hit_miss_trace(self):
        k = self.k_var.get()
        if not self.full_results or k not in self.full_results:
            self.display_in_text_widget(self.trace_text, f"没有容量为 {k} 的模拟数据，请先运行模拟。")
            return

        results_for_k = self.full_results[k]

        trace_output = f"--- 内存容量 k = {k} 时的详细命中序列 ---\n\n"
        trace_output += f"页地址流: {str(self.page_stream_data)}\n\n"
        trace_output += f"FIFO 序列: {' '.join(results_for_k['FIFO'])}\n\n"
        trace_output += f"LRU  序列: {' '.join(results_for_k['LRU'])}\n\n"
        trace_output += f"OPT  序列: {' '.join(results_for_k['OPT'])}\n\n"
        trace_output += f"LFU  序列: {' '.join(results_for_k['LFU'])}\n"

        self.display_in_text_widget(self.trace_text, trace_output)


if __name__ == "__main__":
    app = PageReplacementSimulator()
    app.mainloop()