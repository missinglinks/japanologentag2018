from collections import Counter

CORPUS_FILE = "../corpus/corpus_phrases.txt"

def tf(corpus, top_n=50):
    counter = Counter([x for x in corpus.text.split(" ") if len(x) > 1 ])
    return counter.most_common(top_n)    

def tfidf(*corpusi, top_n):
    pass

class Corpus:

    def __init__(self, viaf_ids, corpus_file=CORPUS_FILE):
        self.corpus_file = corpus_file

        texts = []
        with open(self.corpus_file, "r") as f:
            for line in f:
                tokens = line.strip().split()
                year = int(tokens[0])
                authors = tokens[1]
                text = tokens[2:]

                add_text = False
                for id_ in viaf_ids:
                    if str(id_) in authors:
                        add_text = True
                        break

                if add_text:
                    texts += text
        self.text = " ".join(texts)



            