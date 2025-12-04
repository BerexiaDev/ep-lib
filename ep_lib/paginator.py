class Paginator:
    content = None
    page = None
    size = None
    total = None

    def __init__(self, content, page, size, total, headers=None):
        self.content = content
        self.page = page
        self.size = size
        self.total = total
        self.headers = headers

    def to_dict(self):
        return self.__dict__
