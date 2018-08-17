from elasticsearch import Elasticsearch
import os
import json
import time
from config import ES_SERVER
from tqdm import tqdm
from elasticsearch import helpers
from datetime import datetime
from gensim.models import Phrases
from janome.tokenizer import Tokenizer
from utils import Corpus

#MODELS
CORPUS_DIR = "../data/corpus"
BIGRAM_MODEL = os.path.join(CORPUS_DIR, "rondan_bigram.model")
BIGRAM = Phrases.load(BIGRAM_MODEL)

#TOKENIZER
T = Tokenizer()

#ELASTICSEARCH CONFIGURATION
ARTICLE_INDEX = "ck_articles"
ARTICLE_DOC_TYPE = "article"
ARTICLE_MAPPING = {
    "article": {
        "properties": {
            "magazine": {"type": "keyword"},
            "issue": {"type": "keyword"},
            "year": {"type": "integer"},
            "timestamp": {"type": "date"},
            "title": { 
                "type": "text"
            },
            "tags": { "type": "keyword" },
            "authors": { "type": "keyword" },
            "page_count": {"type": "integer"}
        }
    }
}

#INGEST DATA
DATA_FILEPATH = os.path.join("data","ck.json")
DATA_FILEPATH = "../data/ck.json"

#CORPUS
CORPUS_FILE = "../corpus/corpus_phrases.txt"


def _init_es(es):
    """
    sets up blank es index and adds doc type mapping information
    """
    if es.indices.exists(index=ARTICLE_INDEX):
        es.indices.delete(index=ARTICLE_INDEX)

    es.indices.create(ARTICLE_INDEX)
    es.indices.put_mapping(index=ARTICLE_INDEX, doc_type=ARTICLE_DOC_TYPE, body=ARTICLE_MAPPING)



def articles_ingest():
    """
    Imports channel :channel_name: into elasticsearch
    """

    #set up elasticsearch connection
    es = Elasticsearch(ES_SERVER)

    _init_es(es)

    #load data
    article_count = 0
    corpus = Corpus(CORPUS_FILE)
    print("load data ...")
    data = json.load(open(DATA_FILEPATH, "r", encoding="utf-8"))
    magazine = data["magazine"]
    print("ingest data ...")
    for issue in tqdm(data["issues"]):
        year = issue["year"]
        month = issue["month"]
        #print(issue)
        timestamp = datetime(year, month, 1).isoformat()
                
        article_docs = []

        for i, article in enumerate(issue["toc"]):

            id_ = issue["title"]+"_"+str(i)

            title = article["title"]
            #tokens = [ x.base_form for x in T.tokenize(title) if "名詞" in x.part_of_speech and  "数" not in x.part_of_speech  ]
            #tags = [ x for x in BIGRAM[tokens] if len(x) > 1]

            authors_viaf = [ x["name"] for x in article["authors_viaf"] ]

            try:
                p_from = int(article["pageFrom"])
                p_until = int(article["pageUntil"])
                if p_from < p_until:
                    p_count = p_until - p_from
                else:
                    p_count = None
            except:
                p_count = None

            #print(article["title"])
            tags = corpus.get_article(article_count)[2:]
            article_count += 1
            #print(" ")
            
            article_docs.append({
                "_index": ARTICLE_INDEX,
                "_type": ARTICLE_DOC_TYPE,
                "_id": id_,
                "_source":  {
                    "magazine": magazine,
                    "issue": issue["title"],
                    "year": year,
                    "timestamp": timestamp,
                    "title": article["title"],
                    "tags": tags,
                    "authors": authors_viaf,
                    "page_count": p_count
                }
            })
        
        helpers.bulk(es, article_docs)

if __name__ == "__main__":
    articles_ingest()

 