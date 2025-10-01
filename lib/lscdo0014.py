from esp32_core import Esp32Core
from cfg import Cfg
import ujson

class LSCDO0014(Esp32Core):
    def __init__(self):
        super().__init__()
        
        # 配置输出设备
        self.switchs.add(23, 'led')
        self.switchs.add(32, 'relay_1')
        self.switchs.add(33, 'relay_2')
        self.switchs.add(25, 'relay_3')
        self.switchs.add(26, 'relay_4')
        
        # 配置WIFI和MQTT
        self.cfg.set('wifi', 'ap_ssid', 'LSC-DO-001-4')
        self.cfg.set('wifi', 'ap_password', '12345678')
        self.cfg.set('mqtt', 'host', '172.16.200.2')
        self.cfg.set('mqtt', 'port', 1883)
        self.cfg.set('mqtt', 'client_id', 'LSCDO0014_' + self.UniqueId)
        self.cfg.set('mqtt', 'username', 'LSCDO0014')
        self.cfg.set('mqtt', 'password', 'LSCDO0014')
        self.cfg.set('mqtt', 'keepalive', 30)
        self.cfg.set('mqtt', 'topic', '/RTU/LSCDO0014/' + self.UniqueId)
        self.cfg.save()
        
        # 初始化WIFI
        self.init_wifi()
        self.wifi.start()

        

        # 初始化MQTT
        self.init_mqtt(self.mqtt_callback)
        #self.mqtt.subscribe(self.cfg.get('mqtt', 'topic').encode())
    
    def mqtt_callback(self, topic, msg):
        try:
            # {"switch":"relay_1","mode":5,"duration":5,"interval":0.5,"stop_status": false}
            print(msg)
            data = ujson.loads(msg)
            key = data.get("switch")
            mode = data.get("mode")
            duration = data.get("duration")
            interval = data.get("interval")
            stop_status = data.get("stop_status")
            self.switchs.set(key, mode=mode, duration=duration, interval=interval, stop_status=stop_status)
        except Exception as e:
            print("MQTT消息处理错误:", e)
        
