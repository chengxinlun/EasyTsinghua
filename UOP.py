from bs4 import BeautifulSoup


class UOP():
    table_list = []
    online_no = 0
    online_info = []
    bs = object()
    down = 0.0

    def __init__(self, html):
        self.bs = BeautifulSoup(html, 'html.parser')

    def find_table(self):
        temp = []
        for each in self.bs.find_all("td", "maintd"):
            temp.append(each.get_text())
        self.table_list = [temp[i + 1: i + 14] for i in range(0, len(temp), 14)]

    def parse_data_usage(self):
        d = 0
        for each in self.table_list:
            if each[2].endswith("B"):
                d = d + float(each[2].split("B")[0])
            elif each[2].endswith("K"):
                d = d + float(each[2].split("K")[0]) * 1000.0
            elif each[2].endswith("M"):
                d = d + float(each[2].split("M")[0]) * 1000.0 * 1000.0
            elif each[2].endswith("G"):
                d = d + float(each[2].split("G")[0]) * 1000.0 * 1000.0 * 1000.0
        return d

    def get_online_info(self):
        d = self.parse_data_usage()
        self.down = d
