import network
import time
from simple2 import MQTTClient, MQTTException
import json
import gc

class MQTTCLIENT:
    def __init__(self, config, wifi):
        self._config = config
        self._wifi = wifi
        self.client = None
        self.ping_time = (self._config.get('mqtt', 'keepalive') // 2) * 1000
        self.last_ping_time = time.ticks_ms()
        self.isconnected = False
        self.msg_callback = None
        self.retry_delay = 2  # 初始重连延迟（秒）
        self.topics = []
        
        
    def mqtt_callback(self, topic, msg, retained=False, duplicate=False):
        try:
            topic = topic.decode('utf-8')
            msg = msg.decode('utf-8')
            
            print("MQTT Received:", topic, msg)
            
            if self.msg_callback is not None:
                self.msg_callback(topic, msg)
            gc.collect()
        except Exception as ex:
            print('mqtt callback error: ' + str(ex))
        finally:
            gc.collect()
        
    def connect(self):
        """
        连接
        """
        try:
            if self._wifi and self._wifi.isconnected():
                self.disconnect()
                
                self.client = MQTTClient(
                    client_id=self._config.get('mqtt', 'client_id').encode(),
                    server=self._config.get('mqtt', 'host'),
                    port=self._config.get('mqtt', 'port'),
                    user=self._config.get('mqtt', 'username'),
                    password=self._config.get('mqtt', 'password'),
                    keepalive=self._config.get('mqtt', 'keepalive')
                )
                
                print('开始连接MQTT...')
                self.client.set_callback(self.mqtt_callback)
                self.client.connect()
                topic = self._config.get('mqtt', 'topic')
                if topic not in self.topics:
                    self.subscribe(topic, 0)
                for t in self.topics:
                    try:
                        self.client.subscribe(t, 0)
                    except Exception as e:
                        print("订阅主题失败:", t, e)
                print('MQTT连接成功并订阅主题:', topic)
                print('')
                time.sleep_ms(300)
                self.isconnected = True
        except (OSError, MQTTException) as e:
            print("MQTT 断开:", e)
        
    
    def subscribe(self, topic, qos=0):
        """
        订阅主题
        """
        if isinstance(topic, str):
            topic = topic.encode()
        self.client.subscribe(topic, qos)
        if topic not in self.topics:
            self.topics.append(topic)
            
    def disconnect(self):
        """
        断开连接
        """
        if self.client:
            try:
                self.client.disconnect()
            except Exception as e:
                print("MQTT断开连接错误:", e)
            finally:
                self.client = None
        self.isconnected = False
        
    def ping(self):
        """
        发送Ping操作
        """
        if self.client:
            self.client.ping()
    
    def check_msg(self):
        """
        检测消息并执行自动重连
        """
        try:
            if self._wifi and self._wifi.isconnected() and self.isconnected:
                self.client.check_msg()
                if time.ticks_diff(time.ticks_ms(), self.last_ping_time) >= self.ping_time:
                    self.ping()
                    self.last_ping_time = time.ticks_ms()
        except (OSError, MQTTException) as e:
            self.isconnected = False
            print("MQTT意外断开:", e)
            print("===MQTT执行自动重连===")
            time.sleep(self.retry_delay)
            try:
                self.connect()
                self.retry_delay = 2  # 成功重连后重置
            except Exception as e:
                print("MQTT重连失败:", e)
                self.retry_delay = min(self.retry_delay * 2, 60)  # 指数退避，最大 60 秒
