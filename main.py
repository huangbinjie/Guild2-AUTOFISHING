import threading
import time
from pymem import Pymem
from pynput import keyboard
from pynput.mouse import Controller
from PIL import ImageGrab
import cv2
import pyautogui

target_image_path = "bait.png"
source_image_path = "screenshot.png"


def find_target_location():
    # 读取目标图像和源图像
    target_image = cv2.imread(target_image_path)
    source_image = cv2.imread(source_image_path)

    # 使用模板匹配找到目标在源图像中的位置
    result = cv2.matchTemplate(source_image, target_image, cv2.TM_CCOEFF_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(result)

    # 获取目标图像的宽度和高度
    target_width, target_height = target_image.shape[1], target_image.shape[0]

    # 计算目标中心位置
    target_center_x = max_loc[0] + target_width // 2
    target_center_y = max_loc[1] + target_height // 2

    target_location = (target_center_x, target_center_y)

    return target_location


# 使用方法：人物技能栏只需要切换到钓鱼的技能，按F10启动和停止脚本，脚本会自动抛竿，监控鱼咬钩，溜鱼（玩钓鱼游戏）

# exe名称
pm = Pymem("Gw2-64")

# 鱼杆
ygaddr = pm.read_longlong(pm.base_address + 0x02A14D10)
ygaddr = pm.read_longlong(ygaddr + 0x18)
ygaddr = pm.read_longlong(ygaddr + 0x20)
ygaddr = pm.read_longlong(ygaddr + 0x1C8)
ygaddr = ygaddr + 0xB0

# 浮漂
fpaddr = pm.read_longlong(pm.base_address + 0x02A35240)
fpaddr = fpaddr + 0x40

# 系统滚动条
addr1 = pm.read_longlong(pm.base_address + 0x02A159D0)
addr1 = pm.read_longlong(addr1 + 0x1B0)
addr1 = addr1 + 0x84

# 用户滚动条
addr2 = pm.read_longlong(pm.base_address + 0x02A159D0)
addr2 = pm.read_longlong(addr2 + 0x1B0)
addr2 = addr2 + 0x88

mykeyboard = keyboard.Controller()
mouse = Controller()


class Worker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()  # 创建一个事件对象来控制线程的终止

    def stop(self):
        self._stop_event.set()  # 设置事件对象，终止线程

    def run(self):
        while not self._stop_event.is_set():  # 循环直到事件被设置
            yg = pm.read_int(ygaddr)
            mykeyboard.release("2")
            mykeyboard.release("3")
            if yg == 1:
                # 抛竿
                mykeyboard.press("1")
                mykeyboard.release("1")
                time.sleep(1)
                print("开始抛竿")
                continue

            if yg == 0:
                time.sleep(8)
                fp = 0
                # 等待浮漂状态为1 - 鱼咬钩
                while fp == 0 and yg == 0 and not self._stop_event.is_set():
                    fp = pm.read_int(fpaddr)
                    yg = pm.read_int(ygaddr)
                    time.sleep(0.2)

                if fp == 1:
                    print("开始拉杆")
                    mykeyboard.press("1")
                    mykeyboard.release("1")

                    while pm.read_int(ygaddr) == 0 and not self._stop_event.is_set():
                        value1 = pm.read_float(addr1)
                        value2 = pm.read_float(addr2)
                        if value2 > value1:
                            mykeyboard.release("3")
                            mykeyboard.press("2")

                        elif value2 < value1:
                            mykeyboard.release("2")
                            mykeyboard.press("3")
                    continue

            if self._stop_event.is_set():
                return
            print("正在装备鱼饵")
            # 打开背包
            mykeyboard.press("i")
            mykeyboard.release("i")
            time.sleep(1)

            # 截取全屏
            screenshot = ImageGrab.grab()
            # 保存截图
            screenshot.save(source_image_path)
            # 获取诱饵位置
            baitLocation = find_target_location()
            # 移动到诱饵位置
            pyautogui.moveTo(baitLocation[0], baitLocation[1], 0.25)
            # 装备诱饵
            pyautogui.doubleClick()

            # 关闭背包
            mykeyboard.press("i")
            mykeyboard.release("i")
            time.sleep(1)

    # def my_thread():
    #     while flag:
    #         yg = pm.read_int(ygaddr)

    #         if yg == 1:
    #             # 抛竿
    #             mykeyboard.press("1")
    #             mykeyboard.release("1")
    #             time.sleep(1)
    #             print("开始抛竿")
    #             continue

    #         if yg == 0:
    #             time.sleep(8)
    #             fp = 0
    #             # 等待浮漂状态为1 - 鱼咬钩
    #             while fp == 0 and yg == 0:
    #                 fp = pm.read_int(fpaddr)
    #                 yg = pm.read_int(ygaddr)
    #                 time.sleep(0.2)

    #             if fp == 1:
    #                 print("开始拉杆")
    #                 mykeyboard.press("1")
    #                 mykeyboard.release("1")

    #                 while pm.read_int(ygaddr) == 0:
    #                     value1 = pm.read_float(addr1)
    #                     value2 = pm.read_float(addr2)
    #                     if value2 > value1:
    #                         mykeyboard.release("3")
    #                         mykeyboard.press("2")

    #                     elif value2 < value1:
    #                         mykeyboard.release("2")
    #                         mykeyboard.press("3")
    #                 continue

    #         print("正在装备鱼饵")
    #         # 打开背包
    #         mykeyboard.press("i")
    #         mykeyboard.release("i")
    #         time.sleep(1)

    #         # 截取全屏
    #         screenshot = ImageGrab.grab()
    #         # 保存截图
    #         screenshot.save(source_image_path)
    #         # 获取诱饵位置
    #         baitLocation = find_target_location()
    #         # 移动到诱饵位置
    #         pyautogui.moveTo(baitLocation[0], baitLocation[1], 0.25)
    #         # 装备诱饵
    #         pyautogui.doubleClick()

    #         # 关闭背包
    #         mykeyboard.press("i")
    #         mykeyboard.release("i")
    #         time.sleep(1)


flag = False


def on_release(key):
    global flag
    global thread
    if key == keyboard.Key.f10:
        flag = not flag

        if flag:
            thread = Worker()
            thread.start()
        else:
            thread.stop()
            thread.join()


with keyboard.Listener(on_release=on_release) as listener:
    listener.join()
