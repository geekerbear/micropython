from cfg import Cfg
from switch import Switchs
from wifi import WIFI
import binascii
import machine
import gc
import time
from mqtt import MQTTCLIENT

class EspCore:
    def __init__(self):
        self.UniqueId = binascii.hexlify(machine.unique_id()).decode()
        self.cfg = Cfg()
        self.wifi = None
        self.mqtt = None
        self.switchs = Switchs()
        self._hb_timer = machine.Timer(1)
        self.hb_callback = None
        self._hb_timer.init(period=10, mode=machine.Timer.PERIODIC, callback=self.hb_timer_callback)
        self._last_gc_time = time.ticks_ms()
        
    def hb_timer_callback(self, t):
        try:
            if self.hb_callback is not None:
                self.hb_callback(t)
            self.switchs.do()
            if self.wifi and self.wifi.isconnected() and self.mqtt:
                self.mqtt.check_msg()
            # 自动垃圾回收，每5秒一次
            if time.ticks_diff(time.ticks_ms(), self._last_gc_time) > 5000:
                gc.collect()
                self._last_gc_time = time.ticks_ms()   
        except Exception as ex:
            print('hb callback error: ' + str(ex))
        
    def init_wifi(self):
        self.wifi = WIFI(self.cfg)
    
    def init_mqtt(self, mqtt_callback=None):
        if self.wifi and self.wifi.isconnected():
            self.mqtt = MQTTCLIENT(self.cfg, self.wifi)
            if mqtt_callback:
                self.mqtt.msg_callback = mqtt_callback
            self.mqtt.connect()
        
    def GetMem(self):
        '''
        获取当前内存
        '''
        return gc.mem_free()
        
    def GC(self):
        '''
        回收垃圾
        '''
        gc.collect()
        
    def Reset(self):
        """
        重启
        """
        machine.reset()