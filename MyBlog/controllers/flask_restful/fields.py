#因为 posts 表中的 text 字段内容是一系列的 HTML 字符串(由 CKEditor 产生), 这些 HTML 字符串是不允许被 RESTful API 返回的,
# 因为要满足 REST 的约束之一, 服务端不参与用户界面表现层的业务逻辑(即 HTML 代码),
# 所以我们需要将该字段值中的 HTML 标签过滤掉.
from HTMLParser import HTMLParser
from flask_restful import fields

class HTMLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed=[]
    def handle_data(self, data):
        self.fed.append(data)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    stripper=HTMLStripper()
    stripper.feed(html)
    return stripper.get_data()

class HTMLField(fields.Raw):
    def format(self,value):
        return strip_tags(str(value))

