from utils import Corpus
from gensim.models import Word2Vec

CORPUS_FILE = "../corpus/corpus_phrases.txt"

MODEL_FILE = "../models/word2vec.model"


def build_word2vec():

    print("Tokens: ", Corpus(CORPUS_FILE).count_tokens())

    w2v = Word2Vec(Corpus(CORPUS_FILE), size=100, window=5, min_count=1, workers=4)
    w2v.save(MODEL_FILE)

if __name__ == "__main__":
    build_word2vec()