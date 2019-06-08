from ebooklib import utils


class PageBreaker:
    page_number = 0

    def __call__(self):
        self.page_number += 1
        pn = str(self.page_number)
        return utils.create_pagebreak(pn, pn)
