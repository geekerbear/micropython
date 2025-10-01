import network
import time

class WIFI:
    def __init__(self, config):
        self._config = config
        self.ap = network.WLAN(network.AP_IF)
        self.sta = network.WLAN(network.STA_IF)    
    
    def enable_ap(self):
        """
        打开AP
        """
        self.ap.active(True)
        self.sta.active(True)
        self.ap.config(essid=self._config.get('wifi', 'ap_ssid'), password=self._config.get('wifi', 'ap_password'), authmode=network.AUTH_WPA_WPA2_PSK)
        print('\nap config:', self.ap.ifconfig())
    
    def disabled_ap(self):
        """
        关闭AP
        """
        self.ap.active(False)    
    
    def isconnected(self):
        """
        获取连接状态
        """
        return self.sta.isconnected()
    
    def connect(self):
        """
        连接WIFI
        """
        n = 0
        self.sta.active(True)
        if not self.isconnected():
            print('\nConnecting to WLAN...', end='')
            self.sta.connect(self._config.get('wifi', 'ssid'), self._config.get('wifi', 'password'))
            while not self.isconnected() and n < 20000:
                print('.', end='')
                time.sleep_ms(100)
                n = n + 100
        if self.isconnected():
            print('\nnetwork config:', self.sta.ifconfig())
            print('')
        else:
            print('\nnetwork connection timeout.')
            self.disconnect()
    
    def disconnect(self):
        """
        断开WIFI连接
        """
        self.sta.active(False)
        
    def get_ssids(self):
        """
        获取周围的WIFI信号名称
        """
        ssids = []
        networks = self.sta.scan()
        for net in networks:
            item = {}
            item['ssid'] = net[0].decode('UTF-8') # WiFi 名称
            item['bssid'] = ':'.join('{:02x}'.format(b) for b in net[1])                # MAC 地址 (bytes)
            item['channel'] = net[2]              # 信道
            item['rssi'] = net[3]                 # 信号强度
            item['authmode'] = net[4]             # 加密类型
            item['hidden'] = net[5]               # 是否隐藏
            
            item['ssid'] = item['ssid'].replace(" ", "+")
            if item['ssid'] == ' ' or item['ssid'] == '':
                continue
            ssids.append(item)
        return ssids
        
    def start(self):
        if self.isconnected():
            print('\nnetwork config:', self.sta.ifconfig())
            print('')
            return
        
        if self._config.get('wifi', 'ssid') != '':
            n = 0
            while not self.isconnected() and n < 3:
                self.connect()
                n = n + 1
        
        if not self.isconnected():
            self.enable_ap()
            ssids = self.get_ssids()
            from microdot import Microdot, Response
            app = Microdot()
            Response.default_content_type = 'application/json'
            # Add routes
            @app.route('/')
            def index(request):
                return {"message": "Welcome to REST API!"}
            
            @app.route('/ssid')
            def status(request):
                return ssids
            
            @app.post('/set')
            def submit(request):
                try:
                    data = request.json
                    if type(data) is dict:
                        ssid = data['ssid']
                        password = data['password']
                        if ssid != '' and password != '':
                            print('wifi set ok')
                            self._config.set('wifi', 'ssid', ssid)
                            self._config.set('wifi', 'password', password)
                            self._config.save()
                            import machine
                            machine.reset()
                except Exception as ex:
                    pass
                
            print('start config network.')
            app.run(host="0.0.0.0", port=80)
            