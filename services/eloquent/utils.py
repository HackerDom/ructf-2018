import re
from hashlib import sha512
from html.parser import HTMLParser
from html import escape


class ContentsRecord:
    def __init__(self, r_id):
        self.r_id = r_id
        self.header = None
        self.index = None

    def to_tuple(self):
        return self.r_id, self.header


def get_tag_deep(tag):
    return int(tag[1])


class ContentsTableCreator(HTMLParser):
    HEADER_TAGS = {'h3', 'h4', 'h5', 'h6'}

    def __init__(self):
        super().__init__()
        self.table_of_contents = []
        self.collect_inner_html = False
        self.current_levels = {
            3: 0,
            4: 0,
            5: 0,
            6: 0,
        }

    def error(self, message):
        pass

    def handle_starttag(self, tag, attrs):
        if tag in ContentsTableCreator.HEADER_TAGS:
            tag_deep = get_tag_deep(tag)

            self.table_of_contents.append(ContentsRecord(attrs[0][1]))
            self.collect_inner_html = True

    def handle_data(self, data):
        if not self.collect_inner_html:
            return
        self.table_of_contents[-1].header = escape(data)

    def handle_endtag(self, tag):
        if tag in ContentsTableCreator.HEADER_TAGS:
            self.collect_inner_html = False


USERNAME_TEMPLATE = re.compile('^[a-z0-9_-]{4,20}$')
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
    return [record.to_tuple() for record in table]
