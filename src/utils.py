class Corpus:

    def __init__(self, corpus_file):
        self.corpus_file = corpus_file
        with open(self.corpus_file, "r") as f:
            self._corpus = f.readlines()       

    def __iter__(self):
        with open(self.corpus_file, "r") as f:
            for line in f:
                yield line.strip().split()[2:]

    def get_article(self, i):
        return self._corpus[i].split()

    def count_tokens(self):
        count = 0
        with open(self.corpus_file, "r") as f:
            for line in f:
                count += len(line.strip().split())
        return count

    def get_years(self):
        year_list = []
        with open(self.corpus_file, "r") as f:
            for line in f:
                year_list.append(line.strip().split()[0])
        return year_list

    def get_authors(self):
        authors = []
        with open(self.corpus_file, "r") as f:
            for line in f:
                authors.append(line.strip().split()[1])
        return authors        