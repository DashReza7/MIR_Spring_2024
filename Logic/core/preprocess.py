import nltk
from nltk.stem import WordNetLemmatizer, PorterStemmer
import re
from copy import deepcopy
import os
import json

class Preprocessor:

    def __init__(self, documents: list):
        """
        Initialize the class.

        Parameters
        ----------
        documents : list
            The list of documents to be preprocessed, path to stop words, or other parameters.
        """
        # TODO
        self.documents = documents
        self.stopwords = ["\bthis\b", "\bthat\b", "\babout\b", "\bwhom\b", "\bbeing\b", "\bwhere\b", "\bwhy\b", "\bhad\b", "\bshould\b", "\beach\b"]
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()

    def preprocess(self):
        """
        Preprocess the text using the methods in the class.

        Returns
        ----------
        List[str]
            The preprocessed documents.
        """
        documents = deepcopy(self.documents)
        for doc in documents:
            fields = ["genres", "summaries"]
            for field in fields:
                if doc[field] is None:
                    continue
                for i in range(len(doc[field])):
                    doc[field][i] = self.remove_links(doc[field][i])
                    doc[field][i] = self.remove_punctuations(doc[field][i])
                    doc[field][i] = self.normalize(doc[field][i])
                    doc[field][i] = self.remove_stopwords(doc[field][i])
            fields = ["stars"]
            for field in fields:
                if doc[field] is None:
                    continue
                for i in range(len(doc[field])):
                    doc[field][i] = doc[field][i].lower()
                
        return documents

    def normalize(self, text: str):
        """
        Normalize the text by converting it to a lower case, stemming, lemmatization, etc.

        Parameters
        ----------
        text : str
            The text to be normalized.

        Returns
        ----------
        str
            The normalized text.
        """
        text = text.lower()
        # tokenization
        tokens = self.tokenize(text)
        # stemming
        stemmed = [self.stemmer.stem(token) for token in tokens]
        # lemmatization of the stemmed tokens
        lemmatized = [self.lemmatizer.lemmatize(stemmed_token) for stemmed_token in stemmed]
        return " ".join(lemmatized)

    def remove_links(self, text: str):
        """
        Remove links (and HTML tags) from the text.

        Parameters
        ----------
        text : str
            The text to be processed.

        Returns
        ----------
        str
            The text with links removed.
        """
        # patterns = [r'\S*http\S*', r'\S*www\S*', r'\S+\.ir\S*', r'\S+\.com\S*', r'\S+\.org\S*', r'\S*@\S*']
        patterns = [r'http\S*', r'www\S*', r'\S+\.com\S*', r'\S+\.org\S*', r'\S*@\S*']
        clean_text = re.sub("<[^<]+?>","", text)
        for pattern in patterns:
            clean_text = re.sub(pattern, "", clean_text)
        return clean_text

    def remove_punctuations(self, text: str):
        """
        Remove punctuations and HTML and Unicode characters from the text.

        Parameters
        ----------
        text : str
            The text to be processed.

        Returns
        ----------
        str
            The text with punctuations removed.
        """
        text = re.sub(r"\n", " ", text)
        text = re.sub(r"&#[0-9]+;", " ", text)
        text = re.sub(r"[\u0080-\uffff]", " ", text)
        text = re.sub(r"[^\w\s]", " ", text)
        return text

    def tokenize(self, text: str):
        """
        Tokenize the words in the text.

        Parameters
        ----------
        text : str
            The text to be tokenized.

        Returns
        ----------
        list
            The list of words.
        """
        return nltk.word_tokenize(text)

    def remove_stopwords(self, text: str):
        """
        Remove stopwords from the text.

        Parameters
        ----------
        text : str
            The text to remove stopwords from.

        Returns
        ----------
        list
            The list of words with stopwords removed.
        """
        for stopword in self.stopwords:
            pattern = re.compile(stopword, re.IGNORECASE)
            text = re.sub(pattern, "", text)
        return text

if __name__ == "__main__":
    documents = None
    with open(os.getcwd() + "/Logic/tests/CrawlerResults/IMDB_Crawled.json", "r") as file:
        documents = json.load(file)
    preprocessor = Preprocessor(documents)
    preprocessed_documents = preprocessor.preprocess()
    with open(os.getcwd() + "/Logic/Data/PreprocessedDocuments.json", "w") as file:
        json.dump(preprocessed_documents, file)
    print("the end!")
