import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import copy


class BankerAlgorithmGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("银行家算法模拟系统")
        self.root.geometry("900x700")

        # 初始化变量
        self.n = 0  # 进程数量
        self.m = 0  # 资源种类数
        self.Max = []  # 最大需求矩阵
        self.Allocation = []  # 已分配矩阵
        self.Need = []  # 需求矩阵
        self.Available = []  # 可用资源向量
        self.Work = []  # 工作向量
        self.Finish = []  # 完成标记
        self.safe_sequence = []  # 安全序列

        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # 标题
        title_label = ttk.Label(main_frame, text="银行家算法模拟系统",
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 控制按钮框架
        control_frame = ttk.LabelFrame(main_frame, text="系统控制", padding="10")
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 按钮
        ttk.Button(control_frame, text="设置进程和资源",
                   command=self.setup_process_resource).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="初始化资源表",
                   command=self.initialize_data).grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="安全性检查",
                   command=self.check_safety).grid(row=0, column=2, padx=5)
        ttk.Button(control_frame, text="处理资源请求",
                   command=self.process_request).grid(row=0, column=3, padx=5)
        ttk.Button(control_frame, text="重置系统",
                   command=self.reset_system).grid(row=0, column=4, padx=5)

        # 状态显示框架
        status_frame = ttk.LabelFrame(main_frame, text="系统状态", padding="10")
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(2, weight=1)

        # 创建文本框显示状态
        self.status_text = tk.Text(status_frame, width=100, height=20, font=("Courier", 10))
        scrollbar = ttk.Scrollbar(status_frame, orient="vertical", command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)

        # 日志框架
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        self.log_text = tk.Text(log_frame, width=100, height=8, font=("Courier", 9))
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        # 初始显示
        self.log("系统已启动，请先设置进程和资源数量")

    def log(self, message):
        """添加日志信息"""
        self.log_text.insert(tk.END, f"> {message}\n")
        self.log_text.see(tk.END)

    def setup_process_resource(self):
        """设置进程和资源数量"""
        dialog = ProcessResourceDialog(self.root)
        if dialog.result:
            self.n, self.m = dialog.result
            self.log(f"已设置: {self.n}个进程, {self.m}种资源")
            self.update_status_display()

    def initialize_data(self):
        """初始化资源状态表"""
        if self.n == 0 or self.m == 0:
            messagebox.showwarning("警告", "请先设置进程和资源数量")
            return

        dialog = InitializeDataDialog(self.root, self.n, self.m)
        if dialog.result:
            self.Max, self.Allocation, self.Available = dialog.result
            self.calculate_need()
            self.log("资源状态表已初始化")
            self.update_status_display()

    def calculate_need(self):
        """计算需求矩阵 Need = Max - Allocation"""
        self.Need = []
        for i in range(self.n):
            row = []
            for j in range(self.m):
                row.append(self.Max[i][j] - self.Allocation[i][j])
            self.Need.append(row)

    def check_safety(self):
        """安全性检查"""
        if not self.Max:
            messagebox.showwarning("警告", "请先初始化资源状态表")
            return

        is_safe, safe_sequence = self.is_safe()

        if is_safe:
            self.log(f"安全性检查: 系统安全，安全序列: {[f'P{i}' for i in safe_sequence]}")
            messagebox.showinfo("安全性检查", f"系统处于安全状态\n安全序列: {[f'P{i}' for i in safe_sequence]}")
        else:
            self.log("安全性检查: 系统不安全")
            messagebox.showwarning("安全性检查", "系统处于不安全状态")

        self.update_status_display()

    def is_safe(self):
        """安全性检查算法"""
        # 初始化工作向量和完成标记
        self.Work = self.Available.copy()
        self.Finish = [False] * self.n

        safe_sequence = []
        count = 0
        changed = True

        while count < self.n and changed:
            changed = False
            for i in range(self.n):
                if not self.Finish[i]:
                    # 检查进程i的需求是否小于等于可用资源
                    can_allocate = True
                    for j in range(self.m):
                        if self.Need[i][j] > self.Work[j]:
                            can_allocate = False
                            break

                    if can_allocate:
                        # 模拟分配资源
                        for j in range(self.m):
                            self.Work[j] += self.Allocation[i][j]
                        self.Finish[i] = True
                        safe_sequence.append(i)
                        count += 1
                        changed = True

        # 检查是否所有进程都能完成
        if all(self.Finish):
            return True, safe_sequence
        else:
            return False, []

    def process_request(self):
        """处理资源请求"""
        if not self.Max:
            messagebox.showwarning("警告", "请先初始化资源状态表")
            return

        # 先进行安全性检查
        is_safe, _ = self.is_safe()
        if not is_safe:
            messagebox.showwarning("警告", "系统当前不安全，无法处理资源请求")
            return

        dialog = ResourceRequestDialog(self.root, self.n, self.m)
        if dialog.result:
            pid, request = dialog.result

            # 检查请求的合理性
            for j in range(self.m):
                if request[j] < 0:
                    self.log(f"进程 P{pid} 的资源申请不合理 (请求值不能为负数)")
                    messagebox.showwarning("资源申请", "资源申请不合理 (请求值不能为负数)")
                    return
                if request[j] > self.Need[pid][j]:
                    self.log(f"进程 P{pid} 的资源申请不合理 (请求超过需求)")
                    messagebox.showwarning("资源申请", f"进程 P{pid} 的资源申请不合理\n"
                                                  f"请求 R{j}: {request[j]} > 需求 R{j}: {self.Need[pid][j]}")
                    return

            # 检查请求是否超过可用资源
            for j in range(self.m):
                if request[j] > self.Available[j]:
                    self.log(f"进程 P{pid} 的资源申请超过最大可用资源数，资源不够分配")
                    messagebox.showwarning("资源申请", f"进程 P{pid} 的资源申请超过最大可用资源数\n"
                                                  f"请求 R{j}: {request[j]} > 可用 R{j}: {self.Available[j]}")
                    return

            # 尝试分配资源
            temp_available = self.Available.copy()
            temp_allocation = copy.deepcopy(self.Allocation)
            temp_need = copy.deepcopy(self.Need)

            # 模拟分配
            for j in range(self.m):
                temp_available[j] -= request[j]
                temp_allocation[pid][j] += request[j]
                temp_need[pid][j] -= request[j]

            # 保存当前状态
            original_available = self.Available.copy()
            original_allocation = copy.deepcopy(self.Allocation)
            original_need = copy.deepcopy(self.Need)

            # 临时更新状态进行安全性检查
            self.Available = temp_available
            self.Allocation = temp_allocation
            self.Need = temp_need

            # 进行安全性检查
            is_safe, safe_sequence = self.is_safe()

            if is_safe:
                self.log(f"进程 P{pid} 的资源申请已被满足，安全序列: {[f'P{i}' for i in safe_sequence]}")
                messagebox.showinfo("资源申请",
                                    f"资源申请已被满足\n安全序列: {[f'P{i}' for i in safe_sequence]}")
                # 永久更新状态
                self.calculate_need()  # 重新计算Need矩阵
            else:
                # 恢复原始状态
                self.Available = original_available
                self.Allocation = original_allocation
                self.Need = original_need
                self.log(f"进程 P{pid} 的资源申请不予满足 (找不到安全序列)")
                messagebox.showwarning("资源申请", "找不到安全序列，进程资源申请不予满足")

            self.update_status_display()

    def reset_system(self):
        """重置系统"""
        self.n = 0
        self.m = 0
        self.Max = []
        self.Allocation = []
        self.Need = []
        self.Available = []
        self.log("系统已重置")
        self.update_status_display()

    def update_status_display(self):
        """更新状态显示"""
        self.status_text.delete(1.0, tk.END)

        if self.n == 0 or self.m == 0:
            self.status_text.insert(tk.END, "请先设置进程和资源数量")
            return

        if not self.Max:
            self.status_text.insert(tk.END, "请先初始化资源状态表")
            return

        # 显示资源状态表
        self.status_text.insert(tk.END, "当前资源状态表:\n")
        self.status_text.insert(tk.END, "=" * 80 + "\n")

        # 表头
        header = "进程\tMax\t      Allocation\t     Need\t      Available\n"
        self.status_text.insert(tk.END, header)
        self.status_text.insert(tk.END, "-" * 80 + "\n")

        # 显示每个进程的状态
        for i in range(self.n):
            max_str = "  ".join(f"{x:2d}" for x in self.Max[i])
            alloc_str = "  ".join(f"{x:2d}" for x in self.Allocation[i])
            need_str = "  ".join(f"{x:2d}" for x in self.Need[i])

            if i == 0:
                avail_str = " ".join(f"{x:2d}" for x in self.Available)
                self.status_text.insert(tk.END, f"P{i}\t{max_str}\t  {alloc_str}\t\t  {need_str}\t\t{avail_str}\n")
            else:
                self.status_text.insert(tk.END, f"P{i}\t{max_str}\t  {alloc_str}\t\t  {need_str}\n")

        self.status_text.insert(tk.END, "-" * 80 + "\n")

        # 显示安全性检查结果
        is_safe, safe_sequence = self.is_safe()
        if is_safe:
            self.status_text.insert(tk.END, f"\n系统状态: 安全\n")
            self.status_text.insert(tk.END, f"安全序列: {[f'P{i}' for i in safe_sequence]}\n")
        else:
            self.status_text.insert(tk.END, f"\n系统状态: 不安全\n")


class ProcessResourceDialog:
    """进程和资源设置对话框"""

    def __init__(self, parent):
        self.parent = parent
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("设置进程和资源")
        self.dialog.geometry("300x150")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)

        self.setup_ui()

        # 等待对话框关闭
        self.parent.wait_window(self.dialog)

    def setup_ui(self):
        """设置对话框UI"""
        frame = ttk.Frame(self.dialog, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 进程数量
        ttk.Label(frame, text="进程数量:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.process_var = tk.StringVar(value="5")
        process_entry = ttk.Entry(frame, textvariable=self.process_var, width=10)
        process_entry.grid(row=0, column=1, sticky=tk.W, pady=5)

        # 资源种类数
        ttk.Label(frame, text="资源种类数:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.resource_var = tk.StringVar(value="3")
        resource_entry = ttk.Entry(frame, textvariable=self.resource_var, width=10)
        resource_entry.grid(row=1, column=1, sticky=tk.W, pady=5)

        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="确定", command=self.ok).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="取消", command=self.cancel).grid(row=0, column=1, padx=5)

    def ok(self):
        """确定按钮处理"""
        try:
            n = int(self.process_var.get())
            m = int(self.resource_var.get())

            if n <= 0 or m <= 0:
                messagebox.showwarning("输入错误", "进程数量和资源种类数必须大于0")
                return

            self.result = (n, m)
            self.dialog.destroy()
        except ValueError:
            messagebox.showwarning("输入错误", "请输入有效的整数")

    def cancel(self):
        """取消按钮处理"""
        self.dialog.destroy()


class InitializeDataDialog:
    """初始化数据对话框"""

    def __init__(self, parent, n, m):
        self.parent = parent
        self.n = n
        self.m = m
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("初始化资源状态表")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)

        self.setup_ui()

        # 等待对话框关闭
        self.parent.wait_window(self.dialog)

    def setup_ui(self):
        """设置对话框UI"""
        frame = ttk.Frame(self.dialog, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(frame, text="选择初始化方式:").grid(row=0, column=0, columnspan=2, pady=10)

        # 按钮
        ttk.Button(frame, text="随机生成",
                   command=self.random_initialize).grid(row=1, column=0, padx=10, pady=10)
        ttk.Button(frame, text="手动输入",
                   command=self.manual_initialize).grid(row=1, column=1, padx=10, pady=10)
        ttk.Button(frame, text="安全测试数据",
                   command=self.safe_test_data).grid(row=2, column=0, padx=10, pady=5)
        ttk.Button(frame, text="不安全测试数据",
                   command=self.unsafe_test_data).grid(row=2, column=1, padx=10, pady=5)
        ttk.Button(frame, text="取消",
                   command=self.cancel).grid(row=3, column=0, columnspan=2, pady=10)

    def random_initialize(self):
        """随机初始化"""
        # 生成最大需求矩阵
        Max = []
        for i in range(self.n):
            row = []
            for j in range(self.m):
                row.append(random.randint(1, 10))
            Max.append(row)

        # 生成已分配矩阵
        Allocation = []
        for i in range(self.n):
            row = []
            for j in range(self.m):
                max_val = Max[i][j]
                row.append(random.randint(0, max_val * 7 // 10))
            Allocation.append(row)

        # 生成可用资源向量
        Available = []
        total_resources = [0] * self.m
        allocated_resources = [0] * self.m

        # 计算总资源和已分配资源
        for i in range(self.n):
            for j in range(self.m):
                total_resources[j] += Max[i][j]
                allocated_resources[j] += Allocation[i][j]

        # 可用资源 = 总资源 - 已分配资源 + 额外资源
        for j in range(self.m):
            available = max(total_resources[j] - allocated_resources[j], random.randint(1, 5))
            Available.append(available)

        self.result = (Max, Allocation, Available)
        self.dialog.destroy()

    def manual_initialize(self):
        """手动初始化"""
        dialog = ManualInputDialog(self.parent, self.n, self.m)
        if dialog.result:
            self.result = dialog.result
            self.dialog.destroy()

    def safe_test_data(self):
        """安全测试数据"""
        if self.n == 5 and self.m == 3:
            # 安全状态测试数据
            Max = [
                [7, 5, 3],
                [3, 2, 2],
                [9, 0, 2],
                [2, 2, 2],
                [4, 3, 3]
            ]
            Allocation = [
                [0, 1, 0],
                [2, 0, 0],
                [3, 0, 2],
                [2, 1, 1],
                [0, 0, 2]
            ]
            Available = [3, 3, 2]
            self.result = (Max, Allocation, Available)
            self.dialog.destroy()
        else:
            messagebox.showwarning("测试数据", "安全测试数据仅适用于5个进程3种资源的情况")

    def unsafe_test_data(self):
        """不安全测试数据"""
        if self.n == 5 and self.m == 3:
            # 不安全状态测试数据
            Max = [
                [7, 5, 3],
                [3, 2, 2],
                [9, 0, 2],
                [2, 2, 2],
                [4, 3, 3]
            ]
            Allocation = [
                [0, 1, 0],
                [2, 0, 0],
                [3, 0, 2],
                [2, 1, 1],
                [0, 0, 2]
            ]
            Available = [1, 0, 0]  # 可用资源不足，导致系统不安全
            self.result = (Max, Allocation, Available)
            self.dialog.destroy()
        else:
            messagebox.showwarning("测试数据", "不安全测试数据仅适用于5个进程3种资源的情况")

    def cancel(self):
        """取消按钮处理"""
        self.dialog.destroy()


class ManualInputDialog:
    """手动输入对话框"""

    def __init__(self, parent, n, m):
        self.parent = parent
        self.n = n
        self.m = m
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("手动输入资源状态表")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.setup_ui()

        # 等待对话框关闭
        self.parent.wait_window(self.dialog)

    def setup_ui(self):
        """设置对话框UI"""
        # 创建主框架和滚动条
        main_frame = ttk.Frame(self.dialog)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 配置网格权重
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # 输入框架
        input_frame = ttk.Frame(self.scrollable_frame, padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 最大需求矩阵
        ttk.Label(input_frame, text="最大需求矩阵 (Max):", font=("Arial", 10, "bold")).grid(
            row=0, column=0, columnspan=self.m + 2, sticky=tk.W, pady=(0, 10))

        # 表头 - 第一列是进程标签，后面是资源列
        ttk.Label(input_frame, text="进程\\资源").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        for j in range(self.m):
            ttk.Label(input_frame, text=f"R{j}").grid(row=1, column=j + 1, padx=5, pady=2)

        self.max_entries = []
        for i in range(self.n):
            # 进程标签
            ttk.Label(input_frame, text=f"P{i}").grid(row=i + 2, column=0, padx=5, pady=2, sticky=tk.W)

            # 资源输入框
            row_entries = []
            for j in range(self.m):
                entry = ttk.Entry(input_frame, width=8)
                entry.grid(row=i + 2, column=j + 1, padx=2, pady=2)
                row_entries.append(entry)
            self.max_entries.append(row_entries)

        # 已分配矩阵
        ttk.Label(input_frame, text="\n已分配矩阵 (Allocation):", font=("Arial", 10, "bold")).grid(
            row=self.n + 3, column=0, columnspan=self.m + 1, sticky=tk.W, pady=(20, 10))

        # 表头
        ttk.Label(input_frame, text="进程").grid(row=self.n + 4, column=0, padx=5, pady=2)
        for j in range(self.m):
            ttk.Label(input_frame, text=f"R{j}").grid(row=self.n + 4, column=j + 1, padx=5, pady=2)

        self.allocation_entries = []
        for i in range(self.n):
            row_entries = []
            ttk.Label(input_frame, text=f"P{i}").grid(row=self.n + 5 + i, column=0, padx=5, pady=2)
            for j in range(self.m):
                entry = ttk.Entry(input_frame, width=5)
                entry.grid(row=self.n + 5 + i, column=j + 1, padx=5, pady=2)
                row_entries.append(entry)
            self.allocation_entries.append(row_entries)

        # 可用资源向量
        ttk.Label(input_frame, text="\n可用资源向量 (Available):", font=("Arial", 10, "bold")).grid(
            row=2 * self.n + 6, column=0, columnspan=self.m + 1, sticky=tk.W, pady=(20, 10))

        self.available_entries = []
        for j in range(self.m):
            ttk.Label(input_frame, text=f"R{j}").grid(row=2 * self.n + 7, column=j, padx=5, pady=2)
            entry = ttk.Entry(input_frame, width=5)
            entry.grid(row=2 * self.n + 8, column=j, padx=5, pady=2)
            self.available_entries.append(entry)

        # 按钮
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=2 * self.n + 9, column=0, columnspan=self.m + 1, pady=20)

        ttk.Button(button_frame, text="确定", command=self.ok).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="取消", command=self.cancel).grid(row=0, column=1, padx=10)

        # 配置滚动区域
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

    def ok(self):
        """确定按钮处理"""
        try:
            # 读取最大需求矩阵
            Max = []
            for i in range(self.n):
                row = []
                for j in range(self.m):
                    value = int(self.max_entries[i][j].get())
                    if value < 0:
                        raise ValueError("数值不能为负")
                    row.append(value)
                Max.append(row)

            # 读取已分配矩阵
            Allocation = []
            for i in range(self.n):
                row = []
                for j in range(self.m):
                    value = int(self.allocation_entries[i][j].get())
                    if value < 0:
                        raise ValueError("数值不能为负")
                    if value > Max[i][j]:
                        raise ValueError(f"进程 P{i} 的资源 R{j} 已分配数超过最大需求")
                    row.append(value)
                Allocation.append(row)

            # 读取可用资源向量
            Available = []
            for j in range(self.m):
                value = int(self.available_entries[j].get())
                if value < 0:
                    raise ValueError("数值不能为负")
                Available.append(value)

            self.result = (Max, Allocation, Available)
            self.dialog.destroy()

        except ValueError as e:
            messagebox.showwarning("输入错误", f"请输入有效的正整数: {e}")

    def cancel(self):
        """取消按钮处理"""
        self.dialog.destroy()


class ResourceRequestDialog:
    """资源请求对话框"""

    def __init__(self, parent, n, m):
        self.parent = parent
        self.n = n
        self.m = m
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("处理资源请求")
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)

        self.setup_ui()

        # 等待对话框关闭
        self.parent.wait_window(self.dialog)

    def setup_ui(self):
        """设置对话框UI"""
        frame = ttk.Frame(self.dialog, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 选择进程
        ttk.Label(frame, text="选择进程:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.process_var = tk.StringVar()
        process_combo = ttk.Combobox(frame, textvariable=self.process_var,
                                     values=[f"P{i}" for i in range(self.n)], state="readonly")
        process_combo.grid(row=0, column=1, sticky=tk.W, pady=5)
        process_combo.current(0)

        # 资源请求向量
        ttk.Label(frame, text="资源请求向量:").grid(row=1, column=0, sticky=tk.W, pady=5)

        self.request_entries = []
        for j in range(self.m):
            ttk.Label(frame, text=f"R{j}").grid(row=2, column=j, padx=5, pady=2)
            entry = ttk.Entry(frame, width=5)
            entry.grid(row=3, column=j, padx=5, pady=2)
            entry.insert(0, "0")
            self.request_entries.append(entry)

        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=self.m, pady=20)

        ttk.Button(button_frame, text="确定", command=self.ok).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="取消", command=self.cancel).grid(row=0, column=1, padx=10)

    def ok(self):
        """确定按钮处理"""
        try:
            # 获取进程ID
            pid_str = self.process_var.get()
            if not pid_str:
                messagebox.showwarning("输入错误", "请选择进程")
                return

            pid = int(pid_str[1:])  # 去掉"P"前缀

            # 获取请求向量
            request = []
            for j in range(self.m):
                value = int(self.request_entries[j].get())
                if value < 0:
                    raise ValueError("请求值不能为负")
                request.append(value)

            self.result = (pid, request)
            self.dialog.destroy()

        except ValueError as e:
            messagebox.showwarning("输入错误", f"请输入有效的数值: {e}")

    def cancel(self):
        """取消按钮处理"""
        self.dialog.destroy()


def main():
    """主函数"""
    root = tk.Tk()
    app = BankerAlgorithmGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()