import os
os.chdir(os.environ.get('PROJECT_PATH'))
from secnlp.ml_logic import parsing as p
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline,FunctionTransformer
from nltk.corpus import stopwords

class LemmaTokenizer:
    def __init__(self,rm_stopwords):
        self.wnl = WordNetLemmatizer()
        self.stopwords = set(stopwords.words('english'))
        self.rm_stopwords = rm_stopwords
    def __call__(self, doc, rm_stopwords=False):
        verb_lemmatized = [WordNetLemmatizer().lemmatize(word, pos = "v") for word in  word_tokenize(doc)]
        noun_verb_lemmatized = [WordNetLemmatizer().lemmatize(word, pos = "n") for word in verb_lemmatized]
        if rm_stopwords == True:
            noun_verb_lemmatized = [word for word in noun_verb_lemmatized if not word in self.stopwords]
        return " ".join(noun_verb_lemmatized)


pipeline_without_stop_words = Pipeline([
    ('cleaning', FunctionTransformer(p.clean_text, validate=False)),
    ('tokenizing, lemmatizing, vectorizing', CountVectorizer(tokenizer=LemmaTokenizer(rm_stopwords=False),stop_words=None, ngram_range=(2, 2)))
    ])
