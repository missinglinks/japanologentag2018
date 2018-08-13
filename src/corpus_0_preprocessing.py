import json
import re
from janome.tokenizer import Tokenizer
from tqdm import tqdm
from kyujipy import KyujitaiConverter


DATA_FILE = "../data/ck.json"

OUT_FILE = "../corpus/corpus_preproc.txt"


NUMBERING_RE = re.compile(r'ー[0-9]+ー')
NUMBERING2_RE = re.compile(r'第.{1,3}回')
NUMBERING3_RE = re.compile(r'\([0-9]{1,2}\)')
NUMBERING4_RE = re.compile(r'ー.{1,3}ー')
PAGING_RE = re.compile(r'《.*枚》')
PAGING2_RE = re.compile(r' .{1,3}枚')



def get_titles(filepath):
    data = json.load(open(filepath))
    for issue in data["issues"]:
        for article in issue["toc"]:
            yield article["title"], issue["year"]


converter = KyujitaiConverter()
def to_shinjitai(s):
    return converter.kyujitai_to_shinjitai(s)


t = Tokenizer()
def tokenize(s):
    tokens = [ token.base_form for token in t.tokenize(s) if  "記号" not in token.part_of_speech]
    return tokens


def preprocess():

    titles = []

    for title, year in tqdm(get_titles(DATA_FILE)):
        #print(title)

        title = title.replace("ーー", " ")
        title = title.replace("ー上ー"," ")
        title = title.replace("ー下ー"," ")
        title = title.replace("ー中ー"," ")
        title = title.replace(" 上 ", " ")
        title = title.replace(" 下 ", " ")
        title = title.replace("(", " ")
        title = title.replace(")", " ")
        title = title.replace("｠", " ")
        title = title.replace("｟", " ")
        title = title.replace("･", " ")
        title = title.replace("､", " ")
        title = title.replace("。", " ")
        title = title.replace('"', " ")
        title = title.replace("<", " ")
        title = title.replace(">", " ")
        title = title.replace(" : ", " ")
        title = NUMBERING_RE.sub(" ", title)
        title = NUMBERING2_RE.sub(" ", title)
        title = NUMBERING3_RE.sub(" ", title)
        title = NUMBERING4_RE.sub(" ", title)
        title = PAGING_RE.sub(" ", title)
        title = PAGING2_RE.sub(" ", title)

        title = to_shinjitai(title)

        tokens = tokenize(title)
        titles.append(" ".join(tokens))
        #print(" ")


    with open(OUT_FILE, "w") as f:
        f.writelines("\n".join(titles))


if __name__ == "__main__":
    preprocess()