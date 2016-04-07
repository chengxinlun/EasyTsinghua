import requests
import pickle
import os
import sys
import hashlib
import easygui
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from PyQt5.QtCore import QTimer, Qt
from login_dialog import Ui_login_dialog
from online_dialog import Ui_Dialog
import traceback


class LoginException(Exception):
    pass

class LoginDialog(QDialog):
    cert_dir = ""
    # Class constructor
    def __init__(self, cert, parent = None):
        # Standard gui initialization
        QDialog.__init__(self, parent)
        self.ui = Ui_login_dialog()
        self.ui.setupUi(self)
        # Connect events and triggers
        self.ui.login_button.clicked.connect(self.login)
        self.ui.quit_button.clicked.connect(self.reject)
        self.cert_dir = cert
  

    # Override reject() to exit the dialog when quit button is clicked
    def reject(self):
        self.close()
        sys.exit(0)

        
    def login(self):
        usrname = self.ui.usrname_field.text()
        passwd = self.ui.passwd_field.text()
        if usrname !='' and passwd != '':
            s = requests.Session()
            login_data = {"action": "login", "username": str(usrname), "password": "{MD5_HEX}" + hashlib.md5(passwd.encode()).hexdigest(), "ac_id": "1"}
            login_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'}
            try:
                login_res = s.post("https://net.tsinghua.edu.cn/do_login.php", login_data, headers = login_headers, verify = self.cert_dir)
            except Exception as reason:
                traceback.print_stack()
                traceback.print_exc()
                # Possible network errors
                easygui.buttonbox("Login failure: " + str(reason), choices = ["Try Again"])
            else:
                # Login successful
                if login_res.text == "Login is successful." or login_res.text == "IP has been online, please logout.":  
                    self.accept()
                # Login unsuccessful due to non-network errors
                else:
                    easygui.buttonbox("Login failure: " + str(login_res.text), choices = ["Try Again"])
        # Empty username or password
        else:
            easygui.buttonbox("Username and password must not be empty.", choices = ["Try Again"])

        
class OnlineDialog(QDialog):
    check_headers = {"Referer": "https://net.tsinghua.edu.cn/wired/succeed.html", 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'}
    cert_dir = ""
    
    def __init__(self, cert, parent = None):
        QDialog.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.logout_button.clicked.connect(self.logout)
        self.acceptClose = False
        self.cert_dir = cert


    # Prevent fake offline by closing the window
    def closeEvent(self, evnt):
        if self.acceptClose:
            super(OnlineDialog, self).closeEvent(evnt)
        else:
            evnt.ignore()
            self.setWindowState(Qt.WindowMinimized)  # Not working on linux


    # Update the online duration from server
    # Data usage not working due to web API
    def update_data(self):
        try:
            s = requests.Session()
            try:
                data = s.get("https://net.tsinghua.edu.cn/rad_user_info.php", headers = self.check_headers, verify = self.cert_dir)
                if data.text == '':
                    raise Exception('off')
            except Exception as reason:
                easygui.buttonbox("Something wrong with your network. Please logout manually", choices = ["OK"])
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


    # Logout        
    def logout(self):
        s = requests.Session()
        self.hide()  # Prevent "Something wrong with your network." dialog from showing up
        try:
            logout_res = s.post("https://net.tsinghua.edu.cn/do_login.php", {"action": "logout"}, headers = self.check_headers, verify = self.cert_dir)
        except Exception as reason:
            easygui.buttonbox("Logout failure: " + str(reason), choices = ["OK"])
            self.show()  # Restore the dialog if any problems
        self.acceptClose = True
        self.close()
            

class TunetClient():
    login_status = False
    cert_dir = ""


    # Handling the ssl certification
    def find_data_file(self, filename):
        if getattr(sys, 'frozen', False):
            # The application is frozen
            datadir = os.path.dirname(sys.executable)
        else:
            # The application is not frozen
            datadir = os.path.dirname("./")
        return os.path.join(datadir, filename)


    def check_online(self):
        self.cert_dir = self.find_data_file("cacert.pem")
        s = requests.Session()
        login_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'}
        try:
            res = s.post("https://net.tsinghua.edu.cn/do_login.php", {"action": "check_online"}, headers = login_headers, verify = self.cert_dir)
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
            ld = LoginDialog(cert = self.cert_dir)
            ld.show()
            app.exec_()


    def check_time_datausage(self):
        app = QApplication([])
        od = OnlineDialog(cert = self.cert_dir)
        od.show()
        od.update_data()
        app.exec_()
        
            
        
t=TunetClient()
t.login()
t.check_time_datausage()
easygui.buttonbox("Logout successful. Have a nice day.", choices = ["Quit"])            
