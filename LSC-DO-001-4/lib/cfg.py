import os
import json

class Cfg():
    def __init__(self, name = 'core'):
        self._file = name + '.json'
        self.data = {}
        self.refresh()    
    
    def exists(self):
        """
        判断配置文件是否存在
        """
        if self._file in os.listdir():
            return True
        else:
            return False
    
    def default(self):
        """
        获取默认配置
        """
        data = {}
        data['wifi'] = {}
        data['wifi']['ssid'] = ''
        data['wifi']['password'] = ''
        data['wifi']['ap_ssid'] = ''
        data['wifi']['ap_password'] = '12345678'
        return data
    
    def refresh(self):
        """
        刷新数据
        """
        try:
            if self.exists():
                with open(self._file, 'r') as f:
                    self.data = json.loads(f.read())
            else:
                self.data = self.default()
                with open(self._file, 'w+') as f:
                    f.write(json.dumps(self.data))
        except Exception as ex:
            self.data = self.default()
            print('config refresh error: ' + str(ex))
            
    def get(self, section, key):
        """
        读取数据
        """
        try:
            return self.data[section][key]
        except Exception as ex:
            return None
        
    def set(self, section, key, value):
        """
        写入数据
        """
        try:
            if section not in self.data:
                self.data[section] = {}
            self.data[section][key] = value
            return True
        except Exception as ex:
            return False
            
    def save(self):
        """
        保存数据
        """
        try:
            with open(self._file, 'w+') as f:
                f.write(json.dumps(self.data))
        except Exception as ex:
            print('save config error: ' + str(ex))
    
    def _tojson(self):
        """
        转json字符串
        """
        return json.dumps(self.data)