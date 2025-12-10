import random
import tkinter as tk
from tkinter import ttk, scrolledtext
from collections import deque, OrderedDict
import time


class PageReplacementSimulator:
    def __init__(self):
        self.available_even_addresses = []
        self.instructions = []
        self.page_stream = []

    def generate_instructions(self):
        self.instructions = []

        available_addresses = set(range(320))

        available_even_addresses = [addr for addr in range(0, 320, 2) if addr in available_addresses]

        if available_even_addresses:
            m = random.choice(available_even_addresses)
        else:
            m = None

        for i in range(80):
            if m is None or m not in available_addresses:
                available_even_addresses = [addr for addr in range(0, 320, 2) if addr in available_addresses]
                if available_even_addresses:
                    m = random.choice(available_even_addresses)
                else:
                    break

            if m in available_addresses:
                self.instructions.append(m)
                available_addresses.remove(m)

            odd_addr = m + 1
            if odd_addr <= 319 and odd_addr in available_addresses:
                self.instructions.append(odd_addr)
                available_addresses.remove(odd_addr)

            available_even_addresses = [addr for addr in range(0, 320, 2) if addr in available_addresses]
            prev_even_addresses = [addr for addr in available_even_addresses if addr < m]

            if prev_even_addresses:
                m_prime = random.choice(prev_even_addresses)
            elif available_even_addresses:
                m_prime = random.choice(available_even_addresses)
            else:
                break

            if m_prime in available_addresses:
                self.instructions.append(m_prime)
                available_addresses.remove(m_prime)

            odd_prime_addr = m_prime + 1
            if odd_prime_addr <= 319 and odd_prime_addr in available_addresses:
                self.instructions.append(odd_prime_addr)
                available_addresses.remove(odd_prime_addr)

            available_even_addresses = [addr for addr in range(0, 320, 2) if addr in available_addresses]
            after_even_addresses = [addr for addr in available_even_addresses if addr > m_prime]

            if after_even_addresses:
                m = random.choice(after_even_addresses)
            elif available_even_addresses:
                m = random.choice(available_even_addresses)
            else:
                m = None

        if len(self.instructions) == 320:
            return self.instructions

        remaining_addresses = list(available_addresses)
        random.shuffle(remaining_addresses)
        self.instructions.extend(remaining_addresses)

        if len(self.instructions) > 320:
            self.instructions = self.instructions[:320]

        return self.instructions
            

    def convert_to_page_stream(self):
        """将指令序列转换为页地址流"""
        self.page_stream = [addr // 10 for addr in self.instructions]
        return self.page_stream

    def fifo_algorithm(self, memory_size):
        """先进先出页面置换算法"""
        memory = deque(maxlen=memory_size)
        page_faults = 0
        hit_miss_sequence = []  # 记录每次访问是命中还是缺页

        for page in self.page_stream:
            if page not in memory:
                page_faults += 1
                hit_miss_sequence.append('M')
                if len(memory) == memory_size:
                    memory.popleft()
                memory.append(page)
            else:
                hit_miss_sequence.append('H')

        hit_rate = 1 - page_faults / len(self.page_stream)
        return hit_rate, hit_miss_sequence, memory

    def lru_algorithm(self, memory_size):
        """最近最少使用页面置换算法"""
        memory = OrderedDict()
        page_faults = 0
        hit_miss_sequence = []

        for page in self.page_stream:
            if page not in memory:
                page_faults += 1
                hit_miss_sequence.append('M')
                if len(memory) == memory_size:
                    memory.popitem(last=False)
                memory[page] = True
            else:
                hit_miss_sequence.append('H')
                memory.move_to_end(page)

        hit_rate = 1 - page_faults / len(self.page_stream)
        return hit_rate, hit_miss_sequence, list(memory.keys())

    def opt_algorithm(self, memory_size):
        """最佳淘汰页面置换算法"""
        memory = set()
        page_faults = 0
        hit_miss_sequence = []

        for i, page in enumerate(self.page_stream):
            if page not in memory:
                page_faults += 1
                hit_miss_sequence.append('M')
                if len(memory) == memory_size:
                    farthest_use = -1
                    page_to_remove = None

                    for mem_page in memory:
                        found = False
                        for j in range(i + 1, len(self.page_stream)):
                            if self.page_stream[j] == mem_page:
                                if j > farthest_use:
                                    farthest_use = j
                                    page_to_remove = mem_page
                                found = True
                                break

                        if not found:
                            page_to_remove = mem_page
                            break

                    if page_to_remove is not None:
                        memory.remove(page_to_remove)
                    else:
                        memory.remove(next(iter(memory)))

                memory.add(page)
            else:
                hit_miss_sequence.append('H')

        hit_rate = 1 - page_faults / len(self.page_stream)
        return hit_rate, hit_miss_sequence, list(memory)

    def lfu_algorithm(self, memory_size):
        """最少访问页面算法"""
        memory = {}
        page_faults = 0
        hit_miss_sequence = []

        for page in self.page_stream:
            for mem_page in memory:
                if mem_page != page:
                    memory[mem_page] = (memory[mem_page][0], memory[mem_page][1] + 1)

            if page not in memory:
                page_faults += 1
                hit_miss_sequence.append('M')
                if len(memory) == memory_size:
                    min_freq = float('inf')
                    page_to_remove = None

                    for mem_page, (freq, age) in memory.items():
                        if freq < min_freq or (
                                freq == min_freq and age > (memory[page_to_remove][1] if page_to_remove else 0)):
                            min_freq = freq
                            page_to_remove = mem_page

                    if page_to_remove is not None:
                        del memory[page_to_remove]

                memory[page] = [1, 0]
            else:
                hit_miss_sequence.append('H')
                memory[page] = [memory[page][0] + 1, 0]

        hit_rate = 1 - page_faults / len(self.page_stream)
        return hit_rate, hit_miss_sequence, list(memory.keys())


class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("页面置换算法模拟器")
        self.root.geometry("1000x700")

        self.simulator = PageReplacementSimulator()
        self.current_memory_size = 4
        self.current_algorithm = "FIFO"
        self.is_batch_running = False
        self.font_size = 10

        self.create_widgets()

    def create_widgets(self):
        # 控制框架
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)

        ttk.Button(control_frame, text="生成指令序列", command=self.generate_instructions).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="转换为页地址流", command=self.convert_to_pages).pack(side=tk.LEFT, padx=5)

        # 算法选择
        algo_frame = ttk.Frame(control_frame)
        algo_frame.pack(side=tk.LEFT, padx=20)

        ttk.Label(algo_frame, text="算法:").pack(side=tk.LEFT)
        self.algo_var = tk.StringVar(value="FIFO")
        algo_combo = ttk.Combobox(algo_frame, textvariable=self.algo_var,
                                  values=["FIFO", "LRU", "OPT", "LFU"], state="readonly")
        algo_combo.pack(side=tk.LEFT, padx=5)

        # 内存容量选择
        memory_frame = ttk.Frame(control_frame)
        memory_frame.pack(side=tk.LEFT, padx=20)

        ttk.Label(memory_frame, text="内存容量(页):").pack(side=tk.LEFT)
        self.memory_var = tk.StringVar(value="4")
        memory_combo = ttk.Combobox(memory_frame, textvariable=self.memory_var,
                                    values=[str(i) for i in range(4, 33)], state="readonly")
        memory_combo.pack(side=tk.LEFT, padx=5)

        # 字体大小选择
        font_frame = ttk.Frame(control_frame)
        font_frame.pack(side=tk.LEFT, padx=20)

        ttk.Label(font_frame, text="字体大小:").pack(side=tk.LEFT)
        self.font_var = tk.StringVar(value="10")
        font_combo = ttk.Combobox(font_frame, textvariable=self.font_var,
                                  values=["8", "9", "10", "11", "12", "14", "16", "18"], state="readonly")
        font_combo.pack(side=tk.LEFT, padx=5)
        font_combo.bind('<<ComboboxSelected>>', self.change_font_size)

        ttk.Button(control_frame, text="运行算法", command=self.run_algorithm).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="批量运行(4-32页)", command=self.run_batch).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="暂停/继续", command=self.toggle_pause).pack(side=tk.LEFT, padx=5)

        self.progress = ttk.Progressbar(control_frame, orient=tk.HORIZONTAL, length=200, mode='determinate')
        self.progress.pack(side=tk.LEFT, padx=10)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.instructions_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.instructions_tab, text="指令序列")

        self.instructions_text = scrolledtext.ScrolledText(
            self.instructions_tab,
            width=120,
            height=15,
            font=("Courier", self.font_size)
        )
        self.instructions_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.pages_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.pages_tab, text="页地址流")

        self.pages_text = scrolledtext.ScrolledText(
            self.pages_tab,
            width=120,
            height=15,
            font=("Courier", self.font_size)
        )
        self.pages_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.hits_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.hits_tab, text="命中情况")

        self.hits_text = scrolledtext.ScrolledText(
            self.hits_tab,
            width=120,
            height=15,
            font=("Courier", self.font_size)
        )
        self.hits_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.results_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.results_tab, text="批量运行结果")

        self.results_text = scrolledtext.ScrolledText(
            self.results_tab,
            width=120,
            height=15,
            font=("Courier", self.font_size)
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def change_font_size(self, event=None):
        try:
            self.font_size = int(self.font_var.get())
            for text_widget in [self.instructions_text, self.pages_text,
                                self.hits_text, self.results_text]:
                text_widget.configure(font=("Courier", self.font_size))
        except ValueError:
            pass

    def generate_instructions(self):
        self.simulator.generate_instructions()
        self.display_instructions()

    def convert_to_pages(self):
        self.simulator.convert_to_page_stream()
        self.display_pages()

    def run_algorithm(self):
        algorithm = self.algo_var.get()
        memory_size = int(self.memory_var.get())

        if algorithm == "FIFO":
            hit_rate, hit_miss_sequence, memory = self.simulator.fifo_algorithm(memory_size)
        elif algorithm == "LRU":
            hit_rate, hit_miss_sequence, memory = self.simulator.lru_algorithm(memory_size)
        elif algorithm == "OPT":
            hit_rate, hit_miss_sequence, memory = self.simulator.opt_algorithm(memory_size)
        elif algorithm == "LFU":
            hit_rate, hit_miss_sequence, memory = self.simulator.lfu_algorithm(memory_size)

        self.display_hit_miss(hit_miss_sequence, algorithm, memory_size, hit_rate, memory)
        self.update_results(algorithm, memory_size, hit_rate)

    def run_batch(self):
        self.is_batch_running = True
        algorithm = self.algo_var.get()

        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"批量运行 {algorithm} 算法 (4-32页)\n")
        self.results_text.insert(tk.END, "=" * 50 + "\n\n")

        self.progress['maximum'] = 29
        self.progress['value'] = 0

        for memory_size in range(4, 33):
            if not self.is_batch_running:
                break

            if algorithm == "FIFO":
                hit_rate, hit_miss_sequence, memory = self.simulator.fifo_algorithm(memory_size)
            elif algorithm == "LRU":
                hit_rate, hit_miss_sequence, memory = self.simulator.lru_algorithm(memory_size)
            elif algorithm == "OPT":
                hit_rate, hit_miss_sequence, memory = self.simulator.opt_algorithm(memory_size)
            elif algorithm == "LFU":
                hit_rate, hit_miss_sequence, memory = self.simulator.lfu_algorithm(memory_size)

            result_line = f"{algorithm}算法, {memory_size:2d}页内存: 命中率 = {hit_rate:.3f}\n"
            self.results_text.insert(tk.END, result_line)
            self.results_text.see(tk.END)
            self.results_text.update()

            if memory_size == 32:
                self.display_hit_miss(hit_miss_sequence, algorithm, memory_size, hit_rate, memory)

            self.progress['value'] = memory_size - 4
            self.root.update()

            time.sleep(0.1)

        self.progress['value'] = 0
        self.is_batch_running = False

    def toggle_pause(self):
        self.is_batch_running = not self.is_batch_running
        if self.is_batch_running:
            self.run_batch()

    def display_instructions(self):
        self.instructions_text.delete(1.0, tk.END)
        self.instructions_text.insert(tk.END, "生成的320条指令序列:\n\n")

        for i in range(0, len(self.simulator.instructions), 16):
            line = " ".join(f"{addr:3d}" for addr in self.simulator.instructions[i:i + 16])
            self.instructions_text.insert(tk.END, line + "\n")

        self.instructions_text.insert(tk.END, f"\n总指令数: {len(self.simulator.instructions)}")
        self.instructions_text.insert(tk.END,
                                      f"\n指令地址范围: {min(self.simulator.instructions)} - {max(self.simulator.instructions)}")

    def display_pages(self):
        self.pages_text.delete(1.0, tk.END)
        self.pages_text.insert(tk.END, "页地址流 (每10条指令对应1页):\n\n")

        for i in range(0, len(self.simulator.page_stream), 20):
            line = " ".join(f"{page:2d}" for page in self.simulator.page_stream[i:i + 20])
            self.pages_text.insert(tk.END, line + "\n")

        self.pages_text.insert(tk.END, f"\n总页数: {len(self.simulator.page_stream)}")
        self.pages_text.insert(tk.END, f"\n使用的不同页数: {len(set(self.simulator.page_stream))}")
        self.pages_text.insert(tk.END,
                               f"\n页地址范围: {min(self.simulator.page_stream)} - {max(self.simulator.page_stream)}")

    def display_hit_miss(self, hit_miss_sequence, algorithm, memory_size, hit_rate, memory):
        self.hits_text.delete(1.0, tk.END)
        self.hits_text.insert(tk.END, f"算法: {algorithm}, 内存容量: {memory_size}页, 命中率: {hit_rate:.3f}\n\n")
        self.hits_text.insert(tk.END, "命中情况 (H:命中, M:缺页):\n\n")

        hits = hit_miss_sequence.count('H')
        misses = hit_miss_sequence.count('M')

        # 显示命中序列
        for i in range(0, len(hit_miss_sequence), 50):
            line = " ".join(hit_miss_sequence[i:i + 50])
            self.hits_text.insert(tk.END, line + "\n")

        self.hits_text.insert(tk.END, f"\n统计信息:")
        self.hits_text.insert(tk.END, f"\n命中次数: {hits}")
        self.hits_text.insert(tk.END, f"\n缺页次数: {misses}")
        self.hits_text.insert(tk.END, f"\n总访问次数: {len(hit_miss_sequence)}")
        self.hits_text.insert(tk.END, f"\n命中率: {hit_rate:.3f} ({hits}/{len(hit_miss_sequence)})")
        self.hits_text.insert(tk.END, f"\n最终内存中的页面: {sorted(memory)}")

    def update_results(self, algorithm, memory_size, hit_rate):
        self.results_text.insert(tk.END, f"{algorithm}算法, {memory_size:2d}页内存: 命中率 = {hit_rate:.3f}\n")


def main():
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()