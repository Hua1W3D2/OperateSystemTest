import pygame
import threading
import time
import random
import sys
import os

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("上机实验2")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

try:
    dad_img = pygame.image.load("dad.png")
    mom_img = pygame.image.load("mom.png")
    son_img = pygame.image.load("son.png")
    daughter_img = pygame.image.load("daughter.png")
    apple_img = pygame.image.load("apple.png")
    orange_img = pygame.image.load("orange.png")
    plate_img = pygame.image.load("plate.png")

    dad_img = pygame.transform.scale(dad_img, (80, 120))
    mom_img = pygame.transform.scale(mom_img, (80, 120))
    son_img = pygame.transform.scale(son_img, (80, 120))
    daughter_img = pygame.transform.scale(daughter_img, (80, 120))
    apple_img = pygame.transform.scale(apple_img, (50, 50))
    orange_img = pygame.transform.scale(orange_img, (50, 50))
    plate_img = pygame.transform.scale(plate_img, (100, 60))
except:
    print("图片加载失败，请确保所有图片文件都在当前目录下")
    sys.exit()

def get_chinese_font():
    font_paths = [
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
    ]

    for path in font_paths:
        if os.path.exists(path):
            try:
                return pygame.font.Font(path, 24)
            except:
                continue

    print("警告：未找到中文字体，中文可能显示异常")
    return pygame.font.SysFont(None, 24)

font = get_chinese_font()

plate_lock = threading.Lock()
plate_empty = threading.Semaphore(2)
apple_available = threading.Semaphore(0)
orange_available = threading.Semaphore(0)

plate_fruits = []

dad_original_pos = [100, 400]
mom_original_pos = [700, 400]
son_original_pos = [100, 100]
daughter_original_pos = [700, 100]
plate_pos = [350, 250]

dad_pos = [100, 400]
mom_pos = [700, 400]
son_pos = [100, 100]
daughter_pos = [700, 100]

dad_state = "空闲"
mom_state = "空闲"
son_state = "空闲"
daughter_state = "空闲"
dad_fruit_pos = [dad_pos[0] + 40, dad_pos[1] - 30]
mom_fruit_pos = [mom_pos[0] + 40, mom_pos[1] - 30]
son_fruit_pos = [son_pos[0] + 40, son_pos[1] - 30]
daughter_fruit_pos = [daughter_pos[0] + 40, daughter_pos[1] - 30]


class Person(threading.Thread):
    def __init__(self, name, role, speed, original_pos):
        super().__init__()
        self.name = name
        self.role = role
        self.speed = speed
        self.original_pos = original_pos.copy()
        self.running = True
        self.daemon = True

    def run(self):
        while self.running:

            time.sleep(random.uniform(1, 3))

            if self.role == "dad":
                self.dad_behavior()
            elif self.role == "mom":
                self.mom_behavior()
            elif self.role == "son":
                self.son_behavior()
            elif self.role == "daughter":
                self.daughter_behavior()

    def dad_behavior(self):
        global dad_state, dad_fruit_pos, plate_fruits, dad_pos

        dad_state = "前往盘子"

        self.move_to_plate(dad_pos, dad_fruit_pos)

        if plate_empty.acquire(blocking=False):

            dad_state = "放苹果"
            time.sleep(0.1)

            with plate_lock:
                plate_fruits.append("apple")
                apple_available.release()

            dad_fruit_pos = [dad_pos[0] + 40, dad_pos[1] - 30]

            dad_state = "返回"
            self.return_to_original(dad_pos, dad_fruit_pos, self.original_pos)
            dad_state = "空闲"
        else:
            dad_state = "带水果返回"
            self.return_to_original(dad_pos, dad_fruit_pos, self.original_pos)
            dad_state = "空闲"

    def mom_behavior(self):
        global mom_state, mom_fruit_pos, plate_fruits, mom_pos

        mom_state = "前往盘子"
        self.move_to_plate(mom_pos, mom_fruit_pos)

        if plate_empty.acquire(blocking=False):
            mom_state = "放橘子"
            time.sleep(0.1)

            with plate_lock:
                plate_fruits.append("orange")
                orange_available.release()

            mom_fruit_pos = [mom_pos[0] + 40, mom_pos[1] - 30]

            mom_state = "返回"
            self.return_to_original(mom_pos, mom_fruit_pos, self.original_pos)
            mom_state = "空闲"
        else:
            mom_state = "带水果返回"
            self.return_to_original(mom_pos, mom_fruit_pos, self.original_pos)
            mom_state = "空闲"

    def son_behavior(self):
        global son_state, son_fruit_pos, plate_fruits, son_pos

        son_state = "前往盘子"
        self.move_to_plate(son_pos, son_fruit_pos)

        if orange_available.acquire(blocking=False):
            son_state = "取橘子"
            time.sleep(0.1)

            with plate_lock:
                if "orange" in plate_fruits:
                    plate_fruits.remove("orange")
                    plate_empty.release()

            son_fruit_pos = [son_pos[0] + 40, son_pos[1] - 30]

            son_state = "返回"
            self.return_to_original(son_pos, son_fruit_pos,self.original_pos)
            son_state = "空闲"

            time.sleep(1)
            son_fruit_pos = [son_pos[0] + 40, son_pos[1] - 30]
        else:
            son_state = "空手返回"
            self.return_to_original2(son_pos, self.original_pos)
            son_state = "空闲"

    def daughter_behavior(self):
        global daughter_state, daughter_fruit_pos, plate_fruits, daughter_pos

        daughter_state = "前往盘子"

        self.move_to_plate(daughter_pos, daughter_fruit_pos)

        if apple_available.acquire(blocking=False):

            daughter_state = "取苹果"
            time.sleep(0.1)

            with plate_lock:
                if "apple" in plate_fruits:
                    plate_fruits.remove("apple")
                    plate_empty.release()

            daughter_fruit_pos = [daughter_pos[0] + 40, daughter_pos[1] - 30]

            daughter_state = "返回"
            self.return_to_original(daughter_pos, daughter_fruit_pos,self.original_pos)
            daughter_state = "空闲"

            time.sleep(1)
            daughter_fruit_pos = [daughter_pos[0] + 40, daughter_pos[1] - 30]  # 重置水果位置
        else:
            daughter_state = "空手返回"
            self.return_to_original2(daughter_pos, self.original_pos)
            daughter_state = "空闲"

    def move_to_plate(self, person_pos, fruit_pos):
        steps = 20
        for i in range(steps):
            person_pos[0] = person_pos[0] + (plate_pos[0] - person_pos[0]) / (steps - i)
            person_pos[1] = person_pos[1] + (plate_pos[1] - person_pos[1]) / (steps - i)
            fruit_pos[0] = fruit_pos[0] + (plate_pos[0] - fruit_pos[0]) / (steps - i)
            fruit_pos[1] = fruit_pos[1] + (plate_pos[1] - fruit_pos[1]) / (steps - i)
            time.sleep(0.01)

    def return_to_original(self, person_pos, fruit_pos, original_pos):
        steps = 20
        for i in range(steps):
            person_pos[0] = person_pos[0] + (original_pos[0] - person_pos[0]) / (steps - i)
            person_pos[1] = person_pos[1] + (original_pos[1] - person_pos[1]) / (steps - i)
            fruit_pos[0] = fruit_pos[0] + (original_pos[0] + 40 - fruit_pos[0]) / (steps - i)
            fruit_pos[1] = fruit_pos[1] + (original_pos[1] - 30 - fruit_pos[1]) / (steps - i)
            time.sleep(0.01)

    def return_to_original2(self, person_pos, original_pos):
        steps = 20
        for i in range(steps):
            person_pos[0] = person_pos[0] + (original_pos[0] - person_pos[0]) / (steps - i)
            person_pos[1] = person_pos[1] + (original_pos[1] - person_pos[1]) / (steps - i)
            time.sleep(0.01)

dad = Person("Dad", "dad", 1, dad_original_pos)
mom = Person("Mom", "mom", 1, mom_original_pos)
son = Person("Son", "son", 2, son_original_pos)
daughter = Person("Daughter", "daughter", 2, daughter_original_pos)

dad.start()
mom.start()
son.start()
daughter.start()

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            dad.running = False
            mom.running = False
            son.running = False
            daughter.running = False

    screen.fill(WHITE)

    screen.blit(plate_img, (plate_pos[0] - 50, plate_pos[1] - 30))

    fruit_positions = [
        [plate_pos[0] - 20, plate_pos[1] - 10],
        [plate_pos[0] + 20, plate_pos[1] - 10]
    ]

    for i, fruit in enumerate(plate_fruits):
        if i < 2:
            if fruit == "apple":
                screen.blit(apple_img, (fruit_positions[i][0] - 25, fruit_positions[i][1] - 25))
            elif fruit == "orange":
                screen.blit(orange_img, (fruit_positions[i][0] - 25, fruit_positions[i][1] - 25))

    screen.blit(dad_img, (dad_pos[0] - 40, dad_pos[1] - 60))
    screen.blit(mom_img, (mom_pos[0] - 40, mom_pos[1] - 60))
    screen.blit(son_img, (son_pos[0] - 40, son_pos[1] - 60))
    screen.blit(daughter_img, (daughter_pos[0] - 40, daughter_pos[1] - 60))

    if dad_state in ["空闲", "前往盘子", "带水果返回"]:
        screen.blit(apple_img, (dad_fruit_pos[0] - 25, dad_fruit_pos[1] - 25))

    if mom_state in ["空闲", "前往盘子", "带水果返回"]:
        screen.blit(orange_img, (mom_fruit_pos[0] - 25, mom_fruit_pos[1] - 25))

    if son_state in ["返回", "空闲"] and son_fruit_pos[1] < son_pos[1]:
        screen.blit(orange_img, (son_fruit_pos[0] - 25, son_fruit_pos[1] - 25))

    if daughter_state in ["返回", "空闲"] and daughter_fruit_pos[1] < daughter_pos[1]:
        screen.blit(apple_img, (daughter_fruit_pos[0] - 25, daughter_fruit_pos[1] - 25))

    dad_text = font.render(f"爸爸: {dad_state}", True, BLACK)
    mom_text = font.render(f"妈妈: {mom_state}", True, BLACK)
    son_text = font.render(f"儿子: {son_state}", True, BLACK)
    daughter_text = font.render(f"女儿: {daughter_state}", True, BLACK)
    plate_text = font.render(f"盘子水果: {len(plate_fruits)}个", True, BLACK)

    screen.blit(dad_text, (10, 10))
    screen.blit(mom_text, (10, 40))
    screen.blit(son_text, (10, 70))
    screen.blit(daughter_text, (10, 100))
    screen.blit(plate_text, (10, 130))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()