# Python mail receiver
import email
import os
import imaplib
import easygui
import urllib

class mailException(Exception):
    pass


class MailReceiver():
    mail_server = "mails.tsinghua.edu.cn"
    ssl_port = 993
    mail = None

    def __init__(self):
        login_title = "Login"
        login_msg = "Please input your email profile."
        login_info = [self.mail_server, self.ssl_port, "chengxl14@mails.tsinghua.edu.cn", "cxl19960610"]
        login_field = ["Mail Server", "SSL Port", "User Name", "Password"]
        while True:
            #login_info = easygui.multpasswordbox(login_msg, login_title, login_field)
            #try:
            #    login_info[1] = int(login_info[1])
            #    if login_info[1] == '':
            #        os._exit(0)
            #    if login_info[1]<1 or login_info[1]>65535:
            #        raise Exception("Out of bound")
            #except Exception:
            #    easygui.buttonbox("SSL port must be a integer between 1 and 65535")
            #    continue
            self.mail_server = login_info[0]
            self.ssl_port = login_info[1]
            try:
                self.mail = imaplib.IMAP4_SSL(self.mail_server, self.ssl_port)
                self.mail.login(login_info[2], login_info[3])
            except Exception as reason:
                easygui.buttonbox("Login failure: " + str(reason), choices = ["Try Again"])
                continue
            break


    def get_newest_mail(self):
        self.mail.select('INBOX')
        typ, id_byte_raw = self.mail.search(None, 'ALL')
        if typ != "OK":
            raise mailException("Cannot get email from inbox. Please check your connection.")
        # No email
        if id_byte_raw == [b'']:
            return []
        mail_list = []
        id_byte = id_byte_raw[0]
        id_list = id_byte.split()
        for i in range(int(id_list[-1]) - 1, int(id_list[-1]) - 2, -1):
            typ, mail_data = self.mail.fetch(str(i), '(RFC822)')
            try:
                mail_data = mail_data[0][1]
            except Exception:
                pass
            msg = email.message_from_bytes(mail_data)
            allTime = str(msg['received'])
            varTime = allTime.split()[-6] + " " + allTime.split()[-5] + " " + allTime.split()[-4] + " " + allTime.split()[-3]
            bSubject = email.header.decode_header(msg['subject'])
            try:
                varSubject = bSubject[0][0].decode(bSubject[0][1])
            except Exception:
                varSubject = bSubject[0][0]
            varFrom = str(msg['from']).split()[-1]
            # Get text and number of attachment(s) from email
            allUseful = msg.get_payload(decode = False)
            varText = allUseful[0].get_payload(decode = allUseful[0]["Content-Transfer-Encoding"]).decode(allUseful[0]['Content-Type'].split('charset=')[1])
            varAtt = len(allUseful) - 1
            mail_list.append([varTime, varFrom, varSubject, varText, varAtt])
        return mail_list


mr = MailReceiver()
mail_list = mr.get_newest_mail()
for each in mail_list:
    print(each)
            
        
        
    
