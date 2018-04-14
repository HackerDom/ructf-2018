from html.parser import HTMLParser


class ContentsTableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.collect_data = False
        self.links = []
        self.collect_link_data = False

    def error(self, message):
        pass

    def handle_endtag(self, tag):
        if tag == 'nav':
            self.collect_data = True

    def handle_starttag(self, tag, attrs):
        if not self.collect_data:
            return
        if tag == 'a':
            attrs = dict(attrs)
            if attrs['href'][0] == '#':
                self.collect_link_data = True

    def handle_data(self, data):
        if self.collect_link_data:
            self.links.append(data)
            self.collect_link_data = False


def get_contents_table(html_text):
    parser = ContentsTableParser()
    parser.feed(html_text)
    return parser.links
