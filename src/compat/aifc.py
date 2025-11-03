"""
Compatibility shim for aifc module (removed in Python 3.13)
This is a minimal implementation to prevent import errors
"""

class Error(Exception):
    pass

class Aifc_read:
    def __init__(self, f):
        self.f = f
    
    def close(self):
        pass
    
    def getnchannels(self):
        return 1
    
    def getsampwidth(self):
        return 2
    
    def getframerate(self):
        return 16000
    
    def getnframes(self):
        return 0
    
    def readframes(self, n):
        return b''

class Aifc_write:
    def __init__(self, f):
        self.f = f
    
    def close(self):
        pass
    
    def setnchannels(self, n):
        pass
    
    def setsampwidth(self, w):
        pass
    
    def setframerate(self, r):
        pass
    
    def writeframes(self, data):
        pass

def open(f, mode=None):
    if mode == 'r' or mode == 'rb':
        return Aifc_read(f)
    elif mode == 'w' or mode == 'wb':
        return Aifc_write(f)
    else:
        raise Error("mode must be 'r', 'rb', 'w', or 'wb'")
