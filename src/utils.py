class Corpus:

    def __init__(self, corpus_file):
        self.corpus_file = corpus_file

    def __iter__(self):
        with open(self.corpus_file, "r") as f:
            for line in f:
                yield line.strip().split()