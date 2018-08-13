from corpus_1_phrase_model import check_phrase_list, load_phrases
from corpus_0_preprocessing import tokenize, to_shinjitai

def test_check_phrase_list():
    phrase_list = load_phrases()
    assert check_phrase_list(phrase_list, ["a", "b", "想ひ", "出づる", "c"]) == ["a", "b", "想ひ出づる", "c"]
    assert check_phrase_list(phrase_list, ["a", "いたづら", "b", " ", "c"]) == ["a", "いたづら", "b", " ", "c"]
    assert check_phrase_list(phrase_list, ["い", "たづら", "b", " ", "c"]) == ["いたづら", "b", " ", "c"]
    assert check_phrase_list(phrase_list, ["いた", "づら"]) == ["いたづら"]


def test_tokenize():
    assert tokenize("国家主義") == [ "国家", "主義"]

def test_to_shinjitai():
    assert to_shinjitai("國家") == "国家"