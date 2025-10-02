import time
from machine import Pin

class Switch:
    def __init__(self, pin):
        self._pin = Pin(int(pin), Pin.OUT)
        self._pin.value(0)
        self._mode = 0
        self._duration = 5
        self._interval = 0.5
        self._stop_status = True
        self._blink_flag = False #闪烁标记
        self._start_time = None
        self._last_time = None
        pass
    
    def set(self, mode = 0, duration = 5, interval = 0.5, stop_status = False):
        """
        开始闪烁
        :param mode: 0 单关 1单开 2延时关(不管当前状态如何,都打开, 到时关闭) 3延时开(不管当前状态如何,都关闭, 到时打开) 4长闪烁 5定时闪烁
        """
        if mode < 0:
            return
        self._mode = mode
        
        if self._mode == 0:         # 单关
            self._blink_flag = False
            self._pin.value(0)
        elif self._mode == 1:       # 单开
            self._blink_flag = False
            self._pin.value(1)
        elif self._mode == 2:       # 延时关(不管当前状态如何,都打开, 到时关闭)
            self._duration = duration * 1000
            self._start_time = time.ticks_ms()
            self._blink_flag = True
            self._pin.value(1)
        elif self._mode == 3:       # 延时开(不管当前状态如何,都关闭, 到时打开)
            self._duration = duration * 1000
            self._start_time = time.ticks_ms()
            self._blink_flag = True
            self._pin.value(0)
        else:
            self._duration = duration * 1000
            self._interval = interval * 1000
            self._stop_status = stop_status
            self._start_time = time.ticks_ms()
            self._blink_flag = True
            self._pin.value(not self._pin.value()) # 4,5
            self._last_time = time.ticks_ms()
        
    def do(self):
        """
        工作
        """
        if self._mode == 0 or self._mode == 1:
            return
        if self._blink_flag:
            ts = time.ticks_ms()
            if self._mode == 2:                     # 延时关结束(不管当前状态如何,都打开, 到时关闭)
                if time.ticks_diff(ts, self._start_time) >= self._duration:
                     self._blink_flag = False
                     self._pin.value(0)
            elif self._mode == 3:                   # 延时开结束(不管当前状态如何,都关闭, 到时打开)
                if time.ticks_diff(ts, self._start_time) >= self._duration:
                     self._blink_flag = False
                     self._pin.value(1)
            elif self._mode == 4:                     # 长闪烁动作
                if time.ticks_diff(ts, self._last_time) >= self._interval:
                    self._pin.value(not self._pin.value())
                    self._last_time = time.ticks_ms()
            elif self._mode == 5:                     
                if time.ticks_diff(ts, self._start_time) >= self._duration:  # 定时闪烁结束
                    # 结束
                    self._blink_flag = False
                    if self._stop_status:
                        self._pin.value(1)
                    else:
                        self._pin.value(0)
                else:                               # 定时闪烁动作
                    if time.ticks_diff(ts, self._last_time) >= self._interval:
                        self._pin.value(not self._pin.value())
                        self._last_time = time.ticks_ms()
            
            
class Switchs:
    def __init__(self):
        self._switchs = {}
        
    def add(self, pin, key = None):
        if key is None or key == '':
            key = str(pin)
        if key not in self._switchs:
            self._switchs[key] = Switch(int(pin))
            
    def add_range(self, pins = []):
        for pin in pins:
            key = str(pin)
            if key not in self._switchs:
                self._switchs[key] = Switch(int(pin))
    
    def get_switch(self, key):
        if key not in self._switchs:
            return None
        else:
            return self._switchs[key]
    
    def remove(self, pin):
        key = str(pin)
        if key in self._switchs:
            del self._switchs[key]
            
    def clear(self):
        """
        清除所有设置
        """
        for item in self._switchs.values():
            item.set(0)
    
    def set(self, indexs = None, mode = 0, duration = 5, interval = 0.5, stop_status = False):
        """
        设置
        """
        if mode > -1 and mode < 6:
            if indexs is None:
                # 全部设置
                self.clear()
                for item in self._switchs.values():
                    item.set(mode, duration, interval, stop_status)
            elif type(indexs) is list:
                # 批量设置
                pins = list(self._switchs.values())
                for index in indexs:
                    if index >= len(pins) and index < 0:
                        continue
                    pins[index].set(mode, duration, interval, stop_status)
            elif type(indexs) is int:
                pins = list(self._switchs.values())
                if indexs >= len(pins) and indexs < 0:
                    return
                else:
                    pins[indexs].set(mode, duration, interval, stop_status)
            elif type(indexs) is str:
                if indexs in self._switchs:
                    self._switchs[indexs].set(mode, duration, interval, stop_status)
                elif len(indexs) > 1 and '*' in indexs:
                    indexs = indexs.replace('*', '')
                    for key, value in self._switchs.items():
                        if indexs in key:
                            value.set(mode, duration, interval, stop_status)
    
    def do(self):
        for key, value in self._switchs.items():
            value.do()


