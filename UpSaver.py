import os
import re
import random
import pickle
import base64
from cryptography.fernet import Fernet


class UsrPasswd():
    key = b"XaY_iY1yJtPfq2wjBm8XJU-TygNoHe8u4ZxrzR2q3rg="
    usrname = ""
    passwd_salted = ""
    passwd = ""
    crymachine = Fernet(key)
    
    def __init__(self):
        try:
            f = open("login.tmp", "rb")
            data = pickle.load(f)
            self.usrname = data[0]
            self.passwd_salted = self.crymachine.decrypt(data[1]).decode("utf-8")
            f.close()
        except Exception:
            pass


    def input_info(self, usrname, passwd):
        self.passwd = passwd
        self.usrname = usrname
        

    def add_salt(self):
        self.passwd_salted = ""
        passwd_seg = re.findall(r'.{1,2}', self.passwd, re.DOTALL)
        for each in passwd_seg:
            self.passwd_salted = self.passwd_salted + each + str(random.randint(0,9))


    def desalt(self):
        self.passwd = ""
        passwd_seg = re.findall(r'.{2,3}', self.passwd_salted, re.DOTALL)
        for each in passwd_seg:
            self.passwd = self.passwd + each[:-1]


    def output_to_gui(self):
        if self.passwd == "":
            self.desalt()
        return [self.usrname, self.passwd]


    def output_to_file(self):
        if self.passwd_salted =="":
            self.add_salt()
        try:
            f = open("login.tmp", "wb")
        except Exception:
            return
        pickle.dump([self.usrname, self.crymachine.encrypt(self.passwd_salted.encode("utf-8"))], f)
        f.close()
            
            
        
