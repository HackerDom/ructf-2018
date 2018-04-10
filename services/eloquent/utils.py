import re
from hashlib import sha512
from html.parser import HTMLParser
from html import escape


class ContentsRecord:
    def __init__(self, r_id, index):
        self.r_id = r_id
        self.header = None
        self.index = index

    def to_dict(self):
        return {
            'index': '.'.join(map(str, self.index)),
            'r_id': self.r_id,
            'header': self.header,
            'deep': len(self.index) - 1,
        }


def get_tag_deep(tag):
    return int(tag[1])


class ContentsTableCreator(HTMLParser):
    HEADER_TAGS = {'h3', 'h4', 'h5'}

    def __init__(self):
        super().__init__()
        self.table_of_contents = []
        self.collect_inner_html = False
        self.vc = VersionController()

    def error(self, message):
        pass

    def handle_starttag(self, tag, attrs):
        if tag in ContentsTableCreator.HEADER_TAGS:
            tag_deep = get_tag_deep(tag)
            index = self.vc.feed(tag_deep)
            self.table_of_contents.append(ContentsRecord(attrs[0][1], index))
            self.collect_inner_html = True

    def handle_data(self, data):
        if not self.collect_inner_html:
            return
        self.table_of_contents[-1].header = escape(data)

    def handle_endtag(self, tag):
        if tag in ContentsTableCreator.HEADER_TAGS:
            self.collect_inner_html = False


USERNAME_TEMPLATE = re.compile('^[a-zA-Z0-9_-]{4,20}$')
PASSWORD_TEMPLATE = re.compile('^.{1,20}$')


def is_username_valid(username):
    return USERNAME_TEMPLATE.match(username) is not None


def is_password_valid(password):
    return PASSWORD_TEMPLATE.match(password) is not None


def get_sha512(data):
    return sha512(data).digest()


def strip_html_tags(html_text):
    return ' '.join(re.sub(r'<[^>]*?>', '', html_text).split())


def get_table_contents(html_text):
    contents_table_creator = ContentsTableCreator()
    contents_table_creator.feed(html_text)
    table = contents_table_creator.table_of_contents
    return [record.to_dict() for record in table]


class VersionController:
    def __init__(self):
        self.current_level = ()
        self.current_deep = -1

    def feed(self, deep):
        if self.current_deep == -1:
            self.current_deep = deep
            self.current_level = (1,)
            return self.current_level
        elif self.current_deep < deep:
            delta = deep - self.current_deep
            self.current_level += (1,) * delta
            self.current_deep = deep
            return self.current_level
        elif self.current_deep == deep:
            self.current_level = self.current_level[:-1] + (self.current_level[-1] + 1,)
            self.current_deep = deep
            return self.current_level
        else:
            delta = self.current_deep - deep
            self.current_level = self.current_level[:-1 - delta] + (self.current_level[-1 - delta] + 1,)
            self.current_deep = deep
            return self.current_level
