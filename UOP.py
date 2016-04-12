from bs4 import BeautifulSoup


class UOP():
    table_list = []
    online_no = 0
    online_info = []
    bs = object()

    
    def __init__(self, html):
        self.bs = BeautifulSoup(html, 'html.parser')


    def find_table(self):
        for each in self.bs.find_all("td", "maintd"):
            self.table_list.append(each.get_text())
        temp = [self.table_list[i + 1: i + 14] for i in range(0, len(self.table_list), 14)]
        self.table_list = temp


    def parse_data_usage(self):
        for each in self.online_info:
            key_list = ["入流量", "出流量"]
            for each_key in key_list:
                if each[each_key].endswith("B"):
                    each[each_key] = float(each[each_key].split("B")[0])
                elif each[each_key].endswith("K"):
                    each[each_key] = float(each[each_key].split("K")[0]) * 1000
                elif each[each_key].endswith("M"):
                    each[each_key] = float(each[each_key].split("M")[0]) * 1000 * 1000
                elif each[each_key].endswith("G"):
                    each[each_key] = float(each[each_key].split("G")[0]) * 1000 * 1000 * 1000


    def get_online_info(self):
        for i in range(1, len(self.table_list)):
            temp = dict(zip(self.table_list[0], self.table_list[i]))
            self.online_info.append(temp)
        self.online_no = len(self.online_info)
        self.parse_data_usage()
