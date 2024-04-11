import time
import os
import json
from enum import Enum
import copy
from indexes_enum import Indexes as Indexes

class Index:
    def __init__(self, preprocessed_documents: list):
        """
        Create a class for indexing.
        """

        self.preprocessed_documents = preprocessed_documents

        self.index = {
            Indexes.DOCUMENTS.value: self.index_documents(),
            Indexes.STARS.value: self.index_stars(),
            Indexes.GENRES.value: self.index_genres(),
            Indexes.SUMMARIES.value: self.index_summaries(),
        }

    def index_documents(self):
        """
        Index the documents based on the document ID. In other words, create a dictionary
        where the key is the document ID and the value is the document.

        Returns
        ----------
        dict
            The index of the documents based on the document ID.
        """

        documents_index = dict()
        for doc in self.preprocessed_documents:
            documents_index[doc["id"]] = doc
        return documents_index

    def index_stars(self):
        """
        Index the documents based on the stars.

        Returns
        ----------
        dict
            The index of the documents based on the stars. You should also store each terms' tf in each document.
            So the index type is: {term: {document_id: tf}}
        """
        stars_index = dict()
        for doc in self.preprocessed_documents:
            term_freq = dict()
            for star in doc["stars"]:
                star_splitted = star.split()
                for term in star_splitted:
                    if term not in term_freq:
                        term_freq[term] = 0
                    term_freq[term] += 1
            for term, freq in term_freq.items():
                if term not in stars_index:
                    stars_index[term] = dict()
                stars_index[term][doc["id"]] = freq
        return stars_index

    def index_genres(self):
        """
        Index the documents based on the genres.

        Returns
        ----------
        dict
            The index of the documents based on the genres. You should also store each terms' tf in each document.
            So the index type is: {term: {document_id: tf}}
        """
        genres_index = dict()
        for doc in self.preprocessed_documents:
            term_freq = dict()
            for genre in doc["genres"]:
                genres_splitted = genre.split()
                for term in genres_splitted:
                    if term not in term_freq:
                        term_freq[term] = 0
                    term_freq[term] += 1
            for term, freq in term_freq.items():
                if term not in genres_index:
                    genres_index[term] = dict()
                genres_index[term][doc["id"]] = freq
        return genres_index

    def index_summaries(self):
        """
        Index the documents based on the summaries (not first_page_summary).

        Returns
        ----------
        dict
            The index of the documents based on the summaries. You should also store each terms' tf in each document.
            So the index type is: {term: {document_id: tf}}
        """
        summaries_index = dict()
        for doc in self.preprocessed_documents:
            term_freq = dict()
            for summary in doc["summaries"]:
                summary_splitted = summary.split()
                for term in summary_splitted:
                    if term not in term_freq:
                        term_freq[term] = 0
                    term_freq[term] += 1
            for term, freq in term_freq.items():
                if term not in summaries_index:
                    summaries_index[term] = dict()
                summaries_index[term][doc["id"]] = freq
        return summaries_index

    def get_posting_list(self, word: str, index_type: str):
        """
        get posting_list of a word

        Parameters
        ----------
        word: str
            word we want to check
        index_type: str
            type of index we want to check (documents, stars, genres, summaries)

        Return
        ----------
        list
            posting list of the word (you should return the list of document IDs that contain the word and ignore the tf)
        """

        if index_type not in self.index:
            print(f"invalid index_type: {index_type}")
            exit(1)
        if index_type == "documents":
            print("index_type: documents. Not implemented yet!")
            exit(1)
        if word not in self.index[index_type]:
            print(f"index_type: {index_type}. No word found")
            return []
        return sorted(list(self.index[index_type][word].items()))

    def add_document_to_index(self, document: dict):
        """
        Add a document to all the indexes

        Parameters
        ----------
        document : dict
            Document to add to all the indexes
        """
        # documents
        # TODO: Haaa???
        if document["id"] not in self.index["documents"]:
            self.index["documents"][document["id"]] = document
        
        # stars
        term_freq = dict()
        for genre in document["stars"]:
            genre_splitted = genre.split()
            for term in genre_splitted:
                if document["id"] in self.index["stars"][term]:
                    continue
                if term not in term_freq:
                    term_freq[term] = 0
                term_freq[term] += 1
        for term, freq in term_freq.items():
            if term not in self.index["stars"]:
                self.index["stars"][term] = {document["id"]: freq}
            else:
                self.index["stars"][term][document["id"]] = freq
        
        # genres
        term_freq = dict()
        for genre in document["genres"]:
            genre_splitted = genre.split()
            for term in genre_splitted:
                if document["id"] in self.index["genres"][term]:
                    continue
                if term not in term_freq:
                    term_freq[term] = 0
                term_freq[term] += 1
        for term, freq in term_freq.items():
            if term not in self.index["genres"]:
                self.index["genres"][term] = {document["id"]: freq}
            else:
                self.index["genres"][term][document["id"]] = freq

        # summaries
        term_freq = dict()
        for summary in document["summaries"]:
            summary_splitted = summary.split()
            for term in summary_splitted:
                if document["id"] in self.index["summaries"][term]:
                    continue
                if term not in term_freq:
                    term_freq[term] = 0
                term_freq[term] += 1
        for term, freq in term_freq.items():
            if term not in self.index["summaries"]:
                self.index["summaries"][term] = {document["id"]: freq}
            else:
                self.index["summaries"][term][document["id"]] = freq

    def remove_document_from_index(self, document_id: str):
        """
        Remove a document from all the indexes

        Parameters
        ----------
        document_id : str
            ID of the document to remove from all the indexes
        """
        # document
        if document_id not in self.index["documents"]:
            return
        document = self.index["documents"][document_id]
        del self.index["documents"][document_id]
        # stars
        for star in document["stars"]:
            star_splitted = star.split()
            for term in star_splitted:
                if document_id in self.index["stars"][term]:
                    del self.index["stars"][term][document_id]
        # genres
        for genre in document["genres"]:
            genre_splitted = genre.split()
            for term in genre_splitted:
                if document_id in self.index["genres"][term]:
                    del self.index["genres"][term][document_id]        
        # summaries
        for summary in document["summaries"]:
            summary_splitted = summary.split()
            for term in summary_splitted:
                if document_id in self.index["summaries"][term]:
                    del self.index["summaries"][term][document_id]

    def check_add_remove_is_correct(self):
        """
        Check if the add and remove is correct
        """

        dummy_document = {
            'id': '100',
            'stars': ['tim', 'henry'],
            'genres': ['drama', 'crime'],
            'summaries': ['good']
        }

        index_before_add = copy.deepcopy(self.index)
        self.add_document_to_index(dummy_document)
        index_after_add = copy.deepcopy(self.index)

        if index_after_add[Indexes.DOCUMENTS.value]['100'] != dummy_document:
            print('Add is incorrect, document')
            return

        if (set(index_after_add[Indexes.STARS.value]['tim']).difference(set(index_before_add[Indexes.STARS.value]['tim']))
                != {dummy_document['id']}):
            print('Add is incorrect, tim')
            return

        if (set(index_after_add[Indexes.STARS.value]['henry']).difference(set(index_before_add[Indexes.STARS.value]['henry']))
                != {dummy_document['id']}):
            print('Add is incorrect, henry')
            return
        if (set(index_after_add[Indexes.GENRES.value]['drama']).difference(set(index_before_add[Indexes.GENRES.value]['drama']))
                != {dummy_document['id']}):
            print('Add is incorrect, drama')
            return

        if (set(index_after_add[Indexes.GENRES.value]['crime']).difference(set(index_before_add[Indexes.GENRES.value]['crime']))
                != {dummy_document['id']}):
            print('Add is incorrect, crime')
            return

        if (set(index_after_add[Indexes.SUMMARIES.value]['good']).difference(set(index_before_add[Indexes.SUMMARIES.value]['good']))
                != {dummy_document['id']}):
            print('Add is incorrect, good')
            return

        print('Add is correct')

        self.remove_document_from_index('100')
        index_after_remove = copy.deepcopy(self.index)

        if index_after_remove == index_before_add:
            print('Remove is correct')
        else:
            print('Remove is incorrect')

    def store_index(self, index_type: str, path: str = os.getcwd() + "/Logic/Data/"):
        """
        Stores the index in a file (such as a JSON file)

        Parameters
        ----------
        path : str
            Path to store the file
        index_type: str
            type of index we want to store (documents, stars, genres, summaries)
        """

        if not os.path.exists(path):
            os.makedirs(path)

        if index_type not in self.index:
            raise ValueError('Invalid index type')

        path = path + index_type + "_index.json"
        data = self.index[index_type]
        with open(path, "w") as file:
            json.dump(data, file)

    def load_index(self, index_type: str, path: str = os.getcwd() + "/Logic/Data/"):
        """
        Loads the index from a file (such as a JSON file)

        Parameters
        ----------
        path : str
            Path to load the file
        """
        if not os.path.exists(path):
            print("No such path exists: ", path)
            exit(1)
        if index_type not in self.index:
            print("No such index_type exits: ", index_type)
            exit(1)
        path = path + index_type + "_index.json"
        with open(path, "r") as file:
            self.index[index_type] = json.load(file)

    def check_if_index_loaded_correctly(self, index_type: str, loaded_index: dict):
        """
        Check if the index is loaded correctly

        Parameters
        ----------
        index_type : str
            Type of index to check (documents, stars, genres, summaries)
        loaded_index : dict
            The loaded index

        Returns
        ----------
        bool
            True if index is loaded correctly, False otherwise
        """

        return self.index[index_type] == loaded_index

    def check_if_indexing_is_good(self, index_type: str, check_word: str = 'good'):
        """
        Checks if the indexing is good. Do not change this function. You can use this
        function to check if your indexing is correct.

        Parameters
        ----------
        index_type : str
            Type of index to check (documents, stars, genres, summaries)
        check_word : str
            The word to check in the index

        Returns
        ----------
        bool
            True if indexing is good, False otherwise
        """

        # brute force to check check_word in the summaries
        start = time.time()
        docs = []
        for document in self.preprocessed_documents:
            if index_type not in document or document[index_type] is None:
                continue

            for field in document[index_type]:
                if check_word in field:
                    docs.append(document['id'])
                    break

            # if we have found 3 documents with the word, we can break
            if len(docs) == 3:
                break

        end = time.time()
        brute_force_time = end - start

        # check by getting the posting list of the word
        start = time.time()
        # TODO: based on your implementation, you may need to change the following line
        posting_list = self.get_posting_list(check_word, index_type)

        end = time.time()
        implemented_time = end - start

        print('Brute force time: ', brute_force_time)
        print('Implemented time: ', implemented_time)

        implemented_docs = [data[0] for data in posting_list]
        if set(docs).issubset(set(implemented_docs)):
            print('Indexing is correct')

            # less than or equal, because in small queries, cannot compare brute force and indexing. They both perform almost the same
            if implemented_time <= brute_force_time:
                print('Indexing is good')
                return True
            else:
                print('Indexing is bad')
                return False
        else:
            print('Indexing is wrong')
            return False

# TODO: Run the class with needed parameters, then run check methods and finally report the results of check methods

if __name__ == "__main__":
    preprocessed_documents = None
    with open(os.getcwd() + "/Logic/Data/PreprocessedDocuments.json", "r") as file:
        preprocessed_documents = json.load(file)
    my_index = Index(preprocessed_documents)
    # my_index.store_index("documents")
    # my_index.store_index("stars")
    # my_index.store_index("genres")
    # my_index.store_index("summaries")
    my_index.check_add_remove_is_correct()
    print(my_index.check_if_index_loaded_correctly("documents", my_index.index["documents"]))
    print(my_index.check_if_index_loaded_correctly("stars", my_index.index["stars"]))
    print(my_index.check_if_index_loaded_correctly("genres", my_index.index["genres"]))
    print(my_index.check_if_index_loaded_correctly("summaries", my_index.index["summaries"]))
    my_index.check_if_indexing_is_good("stars", "kenneth")
