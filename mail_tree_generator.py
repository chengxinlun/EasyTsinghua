import email

class MailTree():
    raw_mail = ''
    mail_tree = []

    def __init__(self, raw):
        self.raw_mail = raw

    def list_all(self, tree):
        if not tree.get_content_maintype() == 'multipart':
            yield tree.get_payload(decode = tree["Content-Transfer-Encoding"]).decode(tree['Content-Type'].split('charset=')[1])
        else:
            yield from self.list_all(tree.get_payload())


