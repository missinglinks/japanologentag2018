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
            tokens = [ x.base_form for x in T.tokenize(title) if "名詞" in x.part_of_speech and  "数" not in x.part_of_speech  ]
            tags = [ x for x in BIGRAM[tokens] if len(x) > 1]

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
        

            #doc = {
            #    "magazine": magazine,
            #    "issue": issue["title"],
            #    "year": year,
            #    "timestamp": timestamp,
            #    "title": article["title"],
            #    "tags": tags,
            #    "authors": authors_viaf,
            #    "page_count": p_count
            #}
            #res = es.index(index=ARTICLE_INDEX, doc_type=ARTICLE_DOC_TYPE, id=id_, body=doc)
        #time.sleep(0.4)
        helpers.bulk(es, article_docs)
        #time.sleep(2)

if __name__ == "__main__":
    articles_ingest()

    # channel_dir = os.path.join(CF["PROJECT_DIR"], "channels")
    # for file_name in os.listdir(channel_dir):
    #     if ".prov" not in file_name:
    #         channel = file_name.replace(".zip", "").strip()
    #         print("import channel <{}> into elasticsearch".format(channel))

    #         yy = ChannelReader(channel)

    #         for i, video in tqdm(enumerate(yy.videos)):

    #             video_playlists = [x["title"] for x in video.playlists]

    #             #caption = video.caption()

    #             doc = {
    #                 "id": video.id,
    #                 "title": video.title,
    #                 "channel": channel,
    #                 "description": video.description,
    #                 "publication_date": video.pub_date[:10],
    #                 "tags": video.tags,
    #                 "categories": video.categories,
    #                 "views": video.views,
    #                 "likes": video.likes,
    #                 "dislikes": video.dislikes,
    #                 "favorites": video.favorites,
    #                 "comment_count": video.comment_count,
    #                 "caption": video.caption(),
    #                 "users": video.users(),
    #                 "duration": video.duration,
    #                 "playlists": video_playlists
    #             }
    #             res = es.index(index=video_index, doc_type=VIDEO_DOC_TYPE, id=video.id, body=doc)

    #             comments_doc = []
    #             for comment in video.comments:
    #                 top_level_comment = True if "." in comment["id"] else False
    #                 comments_doc.append({
    #                     "_index": comment_index,
    #                     "_type": COMMENT_DOC_TYPE,
    #                     "_id": comment["id"],
    #                     "_source": {
    #                         "video_id": video.id,
    #                         "channel": channel, 
    #                         "video_title": video.title,
    #                         "video_playlists": video_playlists,
    #                         "user": comment["author"],
    #                         "text": comment["text"],
    #                         "reply_count": comment["reply_count"],
    #                         "timestamp": comment["timestamp"],
    #                         "likes": comment["likes"],
    #                         "top_level_comment": top_level_comment
    #                     }
    #                 })
    #             helpers.bulk(es, comments_doc)
    

