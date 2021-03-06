import json
import pandas as pd
import missingno as msno
from tqdm import tqdm
from random import sample, uniform
from collections import Counter
from ipyleaflet import *
from ipywidgets import Button, Layout
from SPARQLWrapper import SPARQLWrapper, JSON
from corpus import Corpus

PERSONS = "../data/person_dict.json"



def load_persons(id_list, author_names, author_years, label, gender="all"):
    persons = AuthorList(label, author_names, author_years)

    person_dict = json.load(open(PERSONS))

    for elem in id_list:
        id_ = elem[0]
        count = elem[1]
        data = person_dict[id_]

        try:
            year_of_birth = int(data["viaf"]["birth_date"][:4])
        except:
            year_of_birth = None

        try:
            year_of_death = int(data["viaf"]["death_date"][:4])
        except:
            year_of_death = None

        try:
            place_of_birth = data["wiki"]["place_of_birth"]
        except:
            place_of_birth = None            

        if gender != "all":
            if gender != data["wiki"]["gender"]:
                continue

        persons.add_person(Person(
            id_,
            list(set(author_names[id_]))[0],
            year_of_birth,
            year_of_death,
            data["wiki"]["gender"],
            place_of_birth,
            data["wiki"]["education"],
            data["ids"]["wkp"],
            count
        ))
    persons.setup_df()

    return persons


SPARQL = SPARQLWrapper("https://query.wikidata.org/sparql")
QUERY = "SELECT ?coords WHERE {{  wd:{wkp} wdt:P625 ?coords. }}"

def get_wiki_coords(wkp):
    SPARQL.setQuery(QUERY.format(wkp=wkp))
    SPARQL.setReturnFormat(JSON)
    results = SPARQL.query().convert()
    if len(results["results"]["bindings"]) > 0:
        point = results["results"]["bindings"][0]["coords"]["value"]
        lon = float(point.split("(")[-1].split()[0])
        lat = float(point.split()[-1].replace(")",""))
        return (lat, lon)


class Person():
    
    def __init__(
        self, 
        id_,
        name, 
        year_of_birth, 
        year_of_death, 
        gender, 
        place_of_birth, 
        education,
        wkp,
        article_count
    ):
        self.id = id_
        self.name = name
        self.year_of_birth = year_of_birth
        self.year_of_death = year_of_death
        self.gender = gender
        self.place_of_birth = place_of_birth
        self.education = education
        self.wkp = wkp
        self.article_count = article_count

    def to_json(self):
        data = {
            "name": self.name,
            "year_of_birth": self.year_of_birth if self.year_of_birth != 0 else None,
            "year_of_death": self.year_of_death if self.year_of_death != 0 else None,
            "gender": self.gender,
            "place_of_birth": self.place_of_birth,
            "education": "; ".join(self.education) if len(self.education) > 0 else None,
            "wikidata": self.wkp,
            "article_count": self.article_count
        }
        return data
    
    def get_en_name(self):
        return self.name

class AuthorList():

    def __init__(self, author_names, author_years, label=""):
        self.author_names = author_names
        self.author_years = author_years
        self.persons = []
        self.df = None
        self.label = label

    def __iter__(self):
        for person in self.persons:
            yield person

    def setup_df(self):
        self.df = self.get_dataframe()
        print("Anzahl Personen im Datenset: {}".format(len(self.persons)))

    def add_person(self, person):
        self.persons.append(person)

    def get_dataframe(self):
        data = [ x.to_json() for x in self.persons ]
        return pd.DataFrame(data)

    def available_data(self):
        msno.bar(self.df)


    def intersection(self, *others):
        this_list = set([ x.id for x in self ])
        for other in others:
            other_list = set([ x.id for x in other ])
            this_list = this_list.intersection(other_list)

        return load_persons([ (x, None) for x in this_list], self.author_names, self.author_years, self.label+"_intersection")
    
    def exclude(self, other):
        this_list = set([ x.id for x in self ])
        other_list = set([ x.id for x in other ])
        this_list = this_list - other_list
        return load_persons([ (x, None) for x in this_list], self.author_names, self.author_years, self.label+"_exclude_"+other.label)

    #### corpus
    def get_corpus(self):
        viaf_ids = [ x.id for x in self ]
        return Corpus(viaf_ids)


    #### publication map




    #### MAP
    
    def birth_map(self, marker=False):
        m = Map(
            center=(37, 138),
            zoom=5,
            layout=Layout(height='800px')
        )


        places = Counter()
        coords_list = []

        for person in tqdm(self.persons):
            if person.place_of_birth:
                title = "{}, *{}".format(person.get_en_name(), person.year_of_birth)

                places.update([person.place_of_birth["label"]])

                wkp = person.place_of_birth["wkp"]
                coords = get_wiki_coords(wkp)
                coords_list.append(coords)
                if coords and marker:
                    marker = Marker(location=coords, draggable=False, title=title)
                    m.add_layer(marker)        
        if not marker:
            heatmap = Heatmap(
                locations=[[x[0], x[1], 500] for x in coords_list if x],
                radius=20
            )
            m.add_layer(heatmap)     
        print(places.most_common(20))
        return m


    #### STATISTICS

    def gender_stats(self):
        self.df["gender"].value_counts().plot(kind="pie")
        print(self.df["gender"].value_counts())

    def birth_year_stats(self):
        print(self.df.groupby("year_of_birth").size())
        self.df.groupby("year_of_birth").size().plot(figsize=(20,12), kind="bar") 

    def death_year_stats(self, cumsum=False):
        print(self.df.groupby("year_of_death").size())
        if cumsum:
            self.df.groupby("year_of_death").size()[1920:2000].cumsum().plot(figsize=(20,12), kind="line") 
        else:
            self.df.groupby("year_of_death").size()[1920:2000].plot(figsize=(20,12), kind="bar") 

    def education_stats(self, topn=20):
        education = []
        for person in self.persons:
            education += person.education
        df = pd.DataFrame({"education": education})
        df["education"].value_counts()[:topn].plot(figsize=(20,12), kind="bar")

    def get_gender(self, viaf):
        for person in self.persons:
            if person.id == viaf:
                return person.gender
    
    def get_education(self, viaf):
        for person in self.persons:
            if person.id == viaf:
                return person.education

    def get_age(self, viaf, year):
        for person in self.persons:

            if person.id == viaf: 
                if not person.year_of_birth:
                    return None
                age = year-person.year_of_birth
                if age < 15:
                    return None
                else:
                    return age