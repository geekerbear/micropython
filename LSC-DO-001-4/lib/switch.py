import time
from machine import Pin

class Switch:
    def __init__(self, pin):
        self._pin = Pin(int(pin), Pin.OUT)
        self._pin.value(0)
        self._mode = 0
        self._duration = 0
        self._interval = 0
        self._stop_status = True
        self._blink_flag = False
        self._start_time = 0
        self._last_time = 0

    def set(self, mode=0, duration=5, interval=0.5, stop_status=False):
        """
        设置开关模式：
        0: 单关
        1: 单开
        2: 延时关（打开->延时->关闭）
        3: 延时开（关闭->延时->打开）
        4: 长闪烁（持续闪烁）
        5: 定时闪烁（闪烁一段时间后恢复状态）
        """
        if mode < 0 or mode > 5:
            return
        self._mode = mode
        self._duration = duration * 1000
        self._interval = interval * 1000
        self._stop_status = stop_status
        self._start_time = time.ticks_ms()
        self._last_time = self._start_time
        self._blink_flag = mode not in (0, 1)

        if mode == 0:
            self._pin.value(0)
        elif mode == 1:
            self._pin.value(1)
        elif mode == 2:
            self._pin.value(1)
        elif mode == 3:
            self._pin.value(0)
        elif mode in (4, 5):
            self._pin.value(not self._pin.value())

    def do(self):
        if not self._blink_flag:
            return

        now = time.ticks_ms()
        if self._mode == 2:  # 延时关
            if time.ticks_diff(now, self._start_time) >= self._duration:
                self._pin.value(0)
                self._blink_flag = False
        elif self._mode == 3:  # 延时开
            if time.ticks_diff(now, self._start_time) >= self._duration:
                self._pin.value(1)
                self._blink_flag = False
        elif self._mode == 4:  # 长闪烁
            if time.ticks_diff(now, self._last_time) >= self._interval:
                self._pin.value(not self._pin.value())
                self._last_time = now
        elif self._mode == 5:  # 定时闪烁
            if time.ticks_diff(now, self._start_time) >= self._duration:
                self._pin.value(1 if self._stop_status else 0)
                self._blink_flag = False
            elif time.ticks_diff(now, self._last_time) >= self._interval:
                self._pin.value(not self._pin.value())
                self._last_time = now

    def status(self):
        """返回当前开关状态"""
        return self._pin.value()


class Switchs:
    def __init__(self):
        self._switches = {}

    def add(self, pin, key=None):
        if key is None:
            key = str(pin)
        if key not in self._switches:
            self._switches[key] = Switch(pin)

    def add_range(self, pins):
        for pin in pins:
            self.add(pin)

    def remove(self, key):
        if key in self._switches:
            del self._switches[key]

    def clear(self):
        """关闭所有开关"""
        for sw in self._switches.values():
            sw.set(0)

    def set(self, indexs=None, mode=0, duration=5, interval=0.5, stop_status=False):
        """
        设置开关模式
        indexs: None 全部, int 单个, list 批量, str key 或通配符 '*' 
        """
        targets = []

        if indexs is None:
            targets = list(self._switches.values())
        elif isinstance(indexs, int):
            pins = list(self._switches.values())
            if 0 <= indexs < len(pins):
                targets = [pins[indexs]]
        elif isinstance(indexs, list):
            pins = list(self._switches.values())
            for idx in indexs:
                if 0 <= idx < len(pins):
                    targets.append(pins[idx])
        elif isinstance(indexs, str):
            if '*' in indexs:
                pattern = indexs.replace('*', '')
                targets = [sw for k, sw in self._switches.items() if pattern in k]
            elif indexs in self._switches:
                targets = [self._switches[indexs]]

        for sw in targets:
            sw.set(mode, duration, interval, stop_status)

    def do(self):
        for sw in self._switches.values():
            sw.do()

    def status(self, key=None):
        """获取开关状态"""
        if key:
            sw = self._switches.get(key)
            return sw.status() if sw else None
        else:
            return {k: sw.status() for k, sw in self._switches.items()}
