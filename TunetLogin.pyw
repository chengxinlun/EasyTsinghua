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
from UpSaver import UsrPasswd


class LoginException(Exception):
    pass


class LoginDialog(QDialog):
    cert_dir = ""
    up = UsrPasswd()
    username = ""
    password = ""
    
    
    def __init__(self, cert, parent = None):
        # Standard gui initialization
        QDialog.__init__(self, parent)
        self.ui = Ui_login_dialog()
        self.ui.setupUi(self)
        # Connect events and triggers
        self.ui.login_button.clicked.connect(self.login)
        self.ui.quit_button.clicked.connect(self.reject)
        # For the freezing
        self.cert_dir = cert
        # If login.tmp find, use data in it
        # Currently under overhaul (-_-)
  

    # Override reject() to exit the dialog when quit button is clicked
    def reject(self):
        self.close()
        sys.exit(0)


    # Login function
    def login(self):
        usrname = self.ui.usrname_field.text()
        passwd = self.ui.passwd_field.text()
        # Check if username or password is empty
        if usrname !='' and passwd != '':
            s = requests.Session()
            login_data = {"action": "login", "username": str(usrname), "password": "{MD5_HEX}" + hashlib.md5(passwd.encode()).hexdigest(), "ac_id": "1"}
            login_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'}
            try:
                login_res = s.post("https://net.tsinghua.edu.cn/do_login.php", login_data, headers = login_headers, verify = self.cert_dir)
            except Exception as reason:
                # Possible network errors
                easygui.buttonbox("Login failure: " + str(reason), choices = ["Try Again"])
            else:
                # Login successful
                if login_res.text == "Login is successful." or login_res.text == "IP has been online, please logout.":
                    self.username = usrname
                    self.password = passwd
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
    do_logout = False  # Prevent user logout to be judged as network problem
    username = ""
    password = ""
    
    def __init__(self, cert, usrname, passwd, parent = None):
        QDialog.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.logout_button.clicked.connect(self.logout)
        self.acceptClose = False
        self.cert_dir = cert
        self.username = usrname
        self.password = passwd


    # Prevent fake offline by closing the window
    def closeEvent(self, evnt):
        if self.acceptClose:
            super(OnlineDialog, self).closeEvent(evnt)
        else:
            evnt.ignore()
            self.setWindowState(Qt.WindowMinimized)  # Not working on linux, still bugged on Ubuntu 14.04


    # If username and password is given, check data plan from usereg
    def update_data_usereg(self):
        s = requests.Session()
        header = {"referer": "https://usereg.tsinghua.edu.cn/login.php", 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'}
        login_data = {"action": "login", "user_login_name": str(self.username), "user_password": hashlib.md5(self.password.encode()).hexdigest()}
        data = s.post("https://usereg.tsinghua.edu.cn/do.php", login_data, headers = header, verify = False)  # Have to turn off SSL verification to prevent crashing
        if data.text != 'ok':
            raise Exception('off')
        data_usage_html = s.get("https://usereg.tsinghua.edu.cn/online_user_ipv4.php", headers = header, verify = False).text.split("可用时长")[1].split("</td>")[4]
        download = data_usage_html.split('<td class="maintd">')[1]
        if download.endswith("B"):
            download = float(download.split("B")[0])
        elif download.endswith("K"):
            download = float(download.split("K")[0]) * 1000
        elif download.endswith("M"):
            download = float(download.split("M")[0]) * 1000 * 1000
        elif download.endswith("G"):
            download = float(download.split("G")[0]) * 1000 * 1000 * 1000
        last = s.post("https://usereg.tsinghua.edu.cn/do.php", {"action": "logout"}, headers = header, verify = False)
        s.close()
        return download

    
    # Update the online duration from server
    # Update is performed every 10 seconds
    # Don't worry. It's campus network, and it won't count into the data plan.
    def update_data(self):
        try:
            s = requests.Session()
            try:
                data = s.get("https://net.tsinghua.edu.cn/rad_user_info.php", headers = self.check_headers, verify = self.cert_dir)
                if data.text == '':
                    raise Exception('off')
            except Exception as reason:
                if not do_logout:
                    easygui.buttonbox("Something wrong with your network. Please logout manually", choices = ["OK"])
                    self.acceptClose = True
                    self.close()
                    sys.exit(0)
            data_list = data.text.split(',')
            login_time = int(data_list[2]) - int(data_list[1])
            data_usage = float(data_list[6]) * 0.001 * 0.001 *0.001
            data_usage = float(self.update_data_usereg()) * 0.001 * 0.001 *0.001 + data_usage
            self.ui.hour.display(int(login_time / 3600))
            self.ui.minute.display(int((login_time - self.ui.hour.value() * 3600) / 60))
            self.ui.second.display(int((login_time % 60)))
            self.ui.data.display(float(data_usage))
            self.ui.hour.repaint()
            self.ui.minute.repaint()
            self.ui.second.repaint()
            self.ui.data.repaint()
        finally:
            QTimer.singleShot(10000, self.update_data)
        

    # Logout        
    def logout(self):
        s = requests.Session()
        try:
            logout_res = s.post("https://net.tsinghua.edu.cn/do_login.php", {"action": "logout"}, headers = self.check_headers, verify = self.cert_dir)
        except Exception as reason:
            easygui.buttonbox("Logout failure: " + str(reason), choices = ["OK"])
        self.do_logout = True
        self.acceptClose = True
        self.close()
            

class TunetClient():
    login_status = False
    cert_dir = ""
    usrname = ""
    passwd = ""


    # Handling the ssl certification
    def find_data_file(self, filename):
        if getattr(sys, 'frozen', False):
            # The application is frozen
            datadir = os.path.dirname(sys.executable)
        else:
            # The application is not frozen
            datadir = os.path.dirname("./")
        return os.path.join(datadir, filename)


    # Check whether you are online or not
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
        app = QApplication([])
        ld = LoginDialog(cert = self.cert_dir)
        ld.show()
        app.exec_()
        self.usrname = ld.username
        self.passwd = ld.password


    def check_time_datausage(self):
        app = QApplication([])
        od = OnlineDialog(self.cert_dir, self.usrname, self.passwd)
        od.show()
        od.update_data()
        app.exec_()
        
            
        
t=TunetClient()
t.login()
t.check_time_datausage()
easygui.buttonbox("Logout successful. Have a nice day.", choices = ["Quit"])            
