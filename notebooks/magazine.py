import json
from collections import Counter
from person import load_persons
from tqdm import tqdm
import pandas as pd
from collections import defaultdict
import numpy as np


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


    def gender_overview(self):
        authors = self.get_authors(1920,2000)
        year_stats = {}
        for issue in tqdm(self.data["issues"]):
            for article in issue["toc"]:
                for viaf in [ x["viaf"]["viaf_id"] for x in article["authors_viaf"] if x["viaf"] ]:
                    gender = authors.get_gender(viaf)
                    if gender:
                        if issue["year"] in year_stats:
                            year_stats[issue["year"]][gender] += 1
                        else:
                            year_stats[issue["year"]] = {
                                "male": 0,
                                "female": 0
                            }
                            year_stats[issue["year"]][gender] += 1
        df = pd.DataFrame([ {"year":year, "male":x["male"], "female":x["female"]} for year, x in year_stats.items () ])
        df.index = df["year"]
        df.pop("year")
        df["all"] = df["male"]+df["female"]
        df["female_ratio"] = df["female"]/df["all"]
        df["male_ratio"] = df["male"]/df["all"]
        df.plot(y=["female_ratio", "male_ratio"], kind="bar", figsize=(20,12), stacked=True)

    def education_overview(self):
        authors = self.get_authors(1920,2000)
        edu_stats = {}
        for issue in tqdm(self.data["issues"]):
            for article in issue["toc"]:
                use = False
                todai = 0
                for viaf in [ x["viaf"]["viaf_id"] for x in article["authors_viaf"] if x["viaf"] ]:
                    education = authors.get_education(viaf)
                    if education:
                        use = True
                        if "University of Tokyo" in education:
                            todai = 1
                            break

                if use:
                    if not issue["year"] in edu_stats:
                        edu_stats[issue["year"]] = {
                            "todai": 0,
                            "all":0
                        }
                    edu_stats[issue["year"]]["todai"] += todai
                    edu_stats[issue["year"]]["all"] += 1
        df = pd.DataFrame( [ {"year":year, "todai":x["todai"], "all":x["all"]} for year, x in edu_stats.items () ] )
        df.index = df["year"]
        df.pop("year")
        df["ratio"] = df["todai"]/df["all"]
        df["ratio"].plot(figsize=(20,12))

    def age_overview(self):
        authors = self.get_authors(1920,2000)
        age_stats = defaultdict(list)
        for issue in tqdm(self.data["issues"]):
            for article in issue["toc"]:
                for viaf in [ x["viaf"]["viaf_id"] for x in article["authors_viaf"] if x["viaf"] ]:
                    age = authors.get_age(viaf, issue["year"])
                    if age:
                        age_stats[issue["year"]].append(age)
        df = pd.DataFrame( [{ 
            "year":year, 
            "avg_age": np.array(x).mean(),
            "median_age": np.median(x) } for year, x in age_stats.items() ])
        df.index = df["year"]
        #print(age_stats[1931])
        df.plot(y=["median_age"],figsize=(20,12))