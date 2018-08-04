import json
from collections import Counter
from person import load_persons

MAGAZINE = "../data/ck.json"

class Magazine():

    def __init__(self):
        self.data = json.load(open(MAGAZINE))


    def get_authors(self, year_from=1919, year_to=2001, threshold=1):
        authors = []
        a = Counter()
        for issue in self.data["issues"]:
            if issue["year"] >= year_from and issue["year"] <= year_to:
                for article in issue["toc"]:
                    a.update([ x["viaf"]["viaf_id"] for x in article["authors_viaf"] if x["viaf"] ])
                    authors += [ x["viaf"]["viaf_id"] for x in article["authors_viaf"] if x["viaf"] ]
        authors = list(set(authors))
        authors = [ x for x in a.items() if x[1] >= threshold ]
        return load_persons(list(set(authors)))