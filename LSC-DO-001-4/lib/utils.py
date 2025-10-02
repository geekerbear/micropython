import machine
import binascii
import gc

class Utils:
    @staticmethod
    def GetUniqueId():
        """
        获取唯一ID
        """
        return binascii.hexlify(machine.unique_id()).decode()

    @staticmethod
    def GC():
        '''
        回收垃圾
        '''
        gc.collect()

    @staticmethod
    def GetMem():
        '''
        获取当前内存
        '''
        return gc.mem_free()

    @staticmethod
    def GetFreq():
        '''
        获取当前频率
        '''
        return machine.freq()

    @staticmethod
    def Reboot():
        """
        设备重启
        """
        machine.reset()

    @staticmethod
    def GetPinId(pin):
        """
        获取指定Pin的ID
        """
        if type(pin) is machine.Pin:
            return str(pin).replace('Pin(','').replace(')', '')
        else:
            return None
    
    @staticmethod
    def On(pin):
        """
        开
        """
        if type(pin) is machine.Pin:
            pin.value(1)
    
    @staticmethod
    def Off(pin):
        """
        关
        """
        if type(pin) is machine.Pin:
            pin.value(0)
    
    @staticmethod
    def Toggle(pin):
        """
        切换
        """
        if type(pin) is machine.Pin:
            pin.value(not pin.value())
