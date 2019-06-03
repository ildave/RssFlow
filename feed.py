class Feed:
    def __init__(self, link, description=None, updated=None, feedurl=None, feedtitle=None, feedid=None, title=None):
        self.link = link
        self.description = description
        self.updated = updated
        self.feedurl = feedurl
        self.feedtitle = feedtitle
        self.feedid = feedid
        self.title = title

    def to_dict(self):
        out = {}
        out['link'] = self.link
        out['description'] = self.description
        out['updated'] = self.updated
        out['feedurl'] = self.feedurl
        out['feedtitle'] = self.feedtitle
        out['feedid'] = self.feedid
        out['title'] = self.title
        return out