from gensim.models.phrases import Phraser, Phrases
from tqdm import tqdm
from utils import Corpus

CORPUS_FILE = "../corpus/corpus_preproc.txt"
PHRASES_FILE = "../data/phrases.txt"

MODEL_FILE = "../models/bigram.model"
OUT_FILE = "../corpus/corpus_phrases.txt"


def load_phrases():
    with open(PHRASES_FILE) as f:
        return [ x.strip() for x in f.readlines() ]


def check_phrase_list(phrase_list, tokens):

    for phrase in phrase_list:
        for i in range(len(tokens)):
            if i < len(tokens)-1:
                if phrase.startswith(tokens[i]) and tokens[i+1] in phrase:
                    print(phrase)
                    tokens[i:i+2] = [ "".join(tokens[i:i+2]) ] 
                    i = i-1
    return tokens


def remove_under(tokens):
    return [ tok.replace("_", "") for tok in tokens]


def build_phrase_model():

    phrase_list = load_phrases()

    phrases = Phrases(Corpus(CORPUS_FILE))
    bigrams = Phraser(phrases)

    bigrams.save(MODEL_FILE)

    years = Corpus(CORPUS_FILE).get_years()

    with open(OUT_FILE, "w") as f:
        for i, line in tqdm(enumerate(bigrams[Corpus(CORPUS_FILE)])):

            line = remove_under(line)
            line = check_phrase_list(phrase_list, line)

            line = [ years[i] ] + line

            f.write("{}\n".format(" ".join(remove_under(line))))


if __name__ == "__main__":
    build_phrase_model()
    
    #phrase_list = load_phrases()
    #print(check_phrase_list(phrase_list, ["a", "b", "想ひ", "出づる", "c"]))
    
