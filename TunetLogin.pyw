import requests
import os
import sys
import hashlib
import easygui
import multiprocessing
import easygui
import datetime
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from PyQt5.QtCore import QTimer, Qt
from login_dialog import Ui_login_dialog
from online_dialog import Ui_Dialog


class LoginException(Exception):
    pass

class LoginDialog(QDialog):
    def __init__(self, parent = None):
        QDialog.__init__(self, parent)
        self.ui = Ui_login_dialog()
        self.ui.setupUi(self)
        self.ui.login_button.clicked.connect(self.output)
        self.ui.quit_button.clicked.connect(self.totalexit)


    def totalexit(self):
        self.close()
        sys.exit(0)

        
    def output(self):
        usrname = self.ui.usrname_field.text()
        passwd = self.ui.passwd_field.text()
        if usrname !='' and passwd != '':
            s = requests.Session()
            login_data = {"action": "login", "username": str(usrname), "password": "{MD5_HEX}" + hashlib.md5(passwd.encode()).hexdigest(), "ac_id": "1"}
            login_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'}
            try:
                login_res = s.post("https://net.tsinghua.edu.cn/do_login.php", login_data, headers = login_headers)
            except Exception as reason:
                easygui.buttonbox("Login failure: " + str(reason), choices = ["Try Again"])
            else:
                if login_res.text == "Login is successful." or login_res.text == "IP has been online, please logout.":
                    self.close()
                else:
                    easygui.buttonbox("Login failure: " + str(login_res.text), choices = ["Try Again"])
        else:
            easygui.buttonbox("Username and password must not be empty.", choices = ["Try Again"])


class OnlineDialog(QDialog):
    check_headers = {"Referer": "https://net.tsinghua.edu.cn/wired/succeed.html", 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'}
    
    def __init__(self, parent = None):
        QDialog.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.logout_button.clicked.connect(self.logout)
        self.acceptClose = False


    def closeEvent(self, evnt):
        if self.acceptClose:
            super(OnlineDialog, self).closeEvent(evnt)
        else:
            evnt.ignore()
            self.setWindowState(Qt.WindowMinimized)

    
    def update_data(self):
        try:
            s = requests.Session()
            try:
                data = s.get("https://net.tsinghua.edu.cn/rad_user_info.php", headers = self.check_headers)
                if data.text == '':
                    raise Exception('off')
            except Exception as reason:
                easygui.buttonbox("You are offline.", choices = ["OK"])
                self.acceptClose = True
                self.close()
                sys.exit(0)
            data_list = data.text.split(',')
            login_time = int(data_list[2]) - int(data_list[1])
            data_usage = float(data_list[6]) * 0.001 * 0.001 *0.001
            self.ui.hour.display(int(login_time / 3600))
            self.ui.minute.display(int((login_time - self.ui.hour.value() * 3600) / 60))
            self.ui.second.display(int((login_time % 60)))
            self.ui.data.display(float(data_usage))
            self.ui.hour.repaint()
            self.ui.minute.repaint()
            self.ui.second.repaint()
            self.ui.data.repaint()
        finally:
            QTimer.singleShot(1000, self.update_data)

            
    def logout(self):
        s = requests.Session()
        try:
            logout_res = s.post("https://net.tsinghua.edu.cn/do_login.php", {"action": "logout"}, headers = self.check_headers)
        except Exception as reason:
            easygui.buttonbox("Logout failure: " + str(reason), choices = ["OK"])
        self.acceptClose = True
        self.close()
            

class TunetClient():
    login_status = False


    def check_online(self):
        s = requests.Session()
        login_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'}
        try:
            res = s.post("https://net.tsinghua.edu.cn/do_login.php", {"action": "check_online"}, headers = login_headers)
        except Exception:
            self.login_status = False
            return
        if res.text == "online":
            self.login_status = True
        else:
            self.login_status = False
        return
    
        
    def login(self):
        self.check_online()
        if not self.login_status:
            app = QApplication([])
            ld = LoginDialog()
            ld.show()
            app.exec_()


    def check_time_datausage(self):
        app = QApplication([])
        od = OnlineDialog()
        od.show()
        od.update_data()
        app.exec_()
        
            
        
t=TunetClient()
t.login()
t.check_time_datausage()
easygui.buttonbox("Logout successful. Have a nice day.", choices = ["Quit"])            
