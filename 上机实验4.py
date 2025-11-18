import random


class PCB:
    def __init__(self, name, priority, run_time):
        self.name = name
        self.priority = priority
        self.run_time = run_time
        self.state = 'R'  # R:就绪, E:结束
        self.next = None

    def __str__(self):
        return f"{self.name}\t{self.priority}\t{self.run_time}\t{self.state}"


class ProcessScheduler:
    def __init__(self):
        self.head = None
        self.processes = []

    def create_processes(self):
        """创建五个进程，随机生成优先数和运行时间"""
        names = ['P1', 'P2', 'P3', 'P4', 'P5']
        for name in names:
            priority = random.randint(1, 10)
            run_time = random.randint(1, 6)
            self.processes.append(PCB(name, priority, run_time))

        # 按优先数从大到小排序并构建队列
        self.processes.sort(key=lambda x: x.priority, reverse=True)

        # 构建链表
        if self.processes:
            self.head = self.processes[0]
            current = self.head
            for i in range(1, len(self.processes)):
                current.next = self.processes[i]
                current = current.next

    def display_queue(self, step):
        """显示当前进程队列状态"""
        print(f"\n=== 第{step}次调度后的进程队列 ===")
        print("进程名\t优先数\t运行时间\t状态")
        print("-" * 40)

        current = self.head
        while current:
            print(current)
            current = current.next
        print()

    def schedule(self):
        """执行进程调度"""
        step = 0
        self.display_queue(step)  # 显示初始状态

        while self.head:
            step += 1

            # 选择队首进程运行
            current_process = self.head
            print(f"第{step}次调度选中的进程: {current_process.name}")

            # 模拟进程运行：优先数-1，运行时间-1
            current_process.priority -= 1
            current_process.run_time -= 1

            # 检查进程是否结束
            if current_process.run_time == 0:
                current_process.state = 'E'
                print(f"进程{current_process.name}运行结束!")
                # 从队列中移除结束的进程
                self.head = self.head.next
            else:
                # 进程未结束，重新插入队列
                self.head = self.head.next
                self.insert_into_queue(current_process)

            # 显示调度后的队列状态
            self.display_queue(step)

    def insert_into_queue(self, process):
        """将进程按优先数大小插入队列"""
        # 如果队列为空或进程优先数大于队首
        if not self.head or process.priority > self.head.priority:
            process.next = self.head
            self.head = process
            return

        # 寻找插入位置
        current = self.head
        while current.next and current.next.priority >= process.priority:
            current = current.next

        # 插入进程
        process.next = current.next
        current.next = process

    def run_simulation(self):
        """运行完整的调度模拟"""
        print("=" * 50)
        print("          进程调度模拟程序")
        print("=" * 50)
        print("初始进程信息:")
        print("进程名\t优先数\t运行时间\t状态")
        print("-" * 40)

        self.create_processes()

        # 显示初始进程信息
        for process in self.processes:
            print(process)

        print("\n开始调度模拟...")
        self.schedule()

        print("所有进程都已运行结束！")


def main():
    # 设置随机种子以便重现结果
    random.seed(42)

    # 创建调度器并运行模拟
    scheduler = ProcessScheduler()
    scheduler.run_simulation()


if __name__ == "__main__":
    main()