class Feed:
    def __init__(self, link, description=None, updated=None, feedurl=None, feedtitle=None, feedid=None):
        self.link = link
        self.description = description
        self.updated = updated
        self.feedurl = feedurl
        self.feedtitle = feedtitle
        self.feedid = feedid