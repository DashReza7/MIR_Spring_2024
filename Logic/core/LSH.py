import numpy as np
import itertools
import random
import os
import json

class MinHashLSH:
    def __init__(self, documents, num_hashes = 200, len_shingles = 2):
        """
        Initialize the MinHashLSH

        Parameters
        ----------
        documents : list of str
            The input documents for similarity analysis.
        num_hashes : int
            Number of hashes for mini-hashing.
        """
        self.documents = documents
        self.num_hashes = num_hashes
        self.shingled_docs = list()     # list of set of str
        self.len_shingles = len_shingles
        self.shingles = None    # list of shingles
        self.ch_matrix = None   # numpy.ndarray of 0 or 1. (len shingles, len documents)
        self.signature_matrix = None

    def shingle_document(self, document, k=2):
        """
        Convert a document into a set of shingles.

        Parameters
        ----------
        document : str
            The input document.
        k : int
            The size of each shingle.

        Returns
        ----------
        set
            A set of shingles.
        """
        shingles = set()
        splitted_doc = document.strip().split()
        for i in range(len(splitted_doc) - k + 1):
            shingles.add(" ".join(splitted_doc[i:i + k]))
        return shingles

    def build_characteristic_matrix(self):
        """
        Build the characteristic matrix representing the presence of shingles in documents.

        Returns
        ----------
        numpy.ndarray
            The binary characteristic matrix.
        """
        for doc in self.documents:
            self.shingled_docs.append(self.shingle_document(doc, self.len_shingles))
        self.shingles = set()
        for shingled_doc in self.shingled_docs:
            self.shingles.update(shingled_doc)
        self.shingles = list(self.shingles)
        ch_matrix = np.zeros((len(self.shingles), len(self.documents)), dtype=int)
        for i in range(len(self.documents)):
            shingled_doc = self.shingled_docs[i]
            for j in range(len(self.shingles)):
                shingle = self.shingles[j]
                if shingle in shingled_doc:
                    ch_matrix[j, i] = 1
        self.ch_matrix = ch_matrix        
        return ch_matrix

    def min_hash_signature(self):
        """
        Perform Min-Hashing to generate hash signatures for documents.

        Returns
        ----------
        numpy.ndarray
            The Min-Hash signatures matrix.
        """
        signature_matrix = np.zeros((self.num_hashes, len(self.documents)), dtype=int)
        for i in range(self.num_hashes):
            rnd_perm = np.random.permutation(len(self.shingles))
            for j in range(len(self.documents)):
                sign = 0
                while self.ch_matrix[rnd_perm[sign], j] == 0:
                    sign += 1
                signature_matrix[i, j] = sign
        self.signature_matrix = signature_matrix
        return signature_matrix

    def lsh_buckets(self, signature, bands=10, rows_per_band=10):
        """
        Group documents into Locality-Sensitive Hashing (LSH) buckets based on Min-Hash signatures.

        Parameters
        ----------
        signature : numpy.ndarray
            Min-Hash signatures for documents.
        bands : int
            Number of bands for LSH.
        rows_per_band : int
            Number of rows per band.

        Returns
        ----------
        dict
            A dictionary mapping bucket IDs to lists of document indices.
        """
        buckets = dict()
        for band in range(bands):
            for doc in range(signature.shape[1]):
                signs = signature[band * rows_per_band:(band + 1) * rows_per_band, doc]
                signs = sorted(signs)
                hashed = hash(tuple(signs))
                if hashed not in buckets:
                    buckets[hashed] = list()
                buckets[hashed].append(doc)
        return buckets

    def perform_lsh(self):
        """
        Perform the entire Locality-Sensitive Hashing (LSH) process.

        Returns
        ----------
        dict
            A dictionary mapping bucket IDs to lists of document indices.
        """

        print("building characteristic matrix...")
        self.build_characteristic_matrix()
        print("characteristic matrix is built.")
        print("building min hash signature matrix...")
        self.min_hash_signature()
        print("min hash signature matrix is built.")
        return self.lsh_buckets(self.signature_matrix, 50, 4)

    def jaccard_score(self, first_set, second_set):
        """
        Calculate jaccard score for two sets.

        Parameters
        ----------
        first_set : set
            Set of first shingled document.
        second_set : set
            Set of second shingled document.

        Returns
        ----------
        float
            Jaccard score.
        """
        union_set = set()
        union_set.update(first_set)
        union_set.update(second_set)
        return (len(first_set) + len(second_set) - len(union_set)) / len(union_set)

    def jaccard_similarity_test(self, buckets, all_documents):
        """
        Test your near duplicate detection code based on jaccard similarity.

        Parameters
        ----------
        buckets : dict
            A dictionary mapping bucket IDs to lists of document indices.
        all_documents : list
            The input documents for similarity analysis.
        """
        correct_near_duplicates = 0
        all_near_duplicates = 0

        checked_docs = set()
    
        for bucket_id in buckets.keys():
            docs_in_this_bucket = buckets[bucket_id]
            unique_doc_ids = set(docs_in_this_bucket)
            if len(unique_doc_ids) > 1:
                combinations = list(itertools.combinations(unique_doc_ids, 2))
                for comb in combinations:
                    first_doc_id = comb[0]
                    second_doc_id = comb[1]

                    doc_pair = (min(first_doc_id, second_doc_id), max(first_doc_id, second_doc_id))
                    if doc_pair in checked_docs:
                        continue
                    checked_docs.add(doc_pair)
                    
                    all_near_duplicates += 1

                    print(f"checking similarity of docs: {doc_pair[0]}, {doc_pair[1]}")
                    
                    first_shingled_doc = self.shingled_docs[first_doc_id]
                    second_shingled_doc = self.shingled_docs[second_doc_id]

                    near_duplicated_jaccard_score = self.jaccard_score(first_shingled_doc, second_shingled_doc)
                    current_score = 0

                    for _ in range(5):
                        random_doc_id = first_doc_id
                        while random_doc_id == first_doc_id or random_doc_id == second_doc_id:
                            random_doc_id = random.randint(0, len(all_documents) - 1)
                        random_shingled_doc = self.shingled_docs[random_doc_id]

                        random_jaccard_score = self.jaccard_score(first_shingled_doc, random_shingled_doc)

                        if near_duplicated_jaccard_score > random_jaccard_score:
                            current_score += 1

                    if current_score == 5:
                        correct_near_duplicates += 1

        # a good score is around 0.8
        print("your final score in near duplicate detection:", correct_near_duplicates / all_near_duplicates)

if __name__ == "__main__":
    crawled_data = None
    with open(os.getcwd() + "/Logic/tests/CrawlerResults/IMDB_Crawled.json", "r") as json_file:
        crawled_data = json.load(json_file)
    documents = list()
    for movie in crawled_data:
        documents.append(" ".join(movie["summaries"]))
    
    fake_data = None
    with open(os.getcwd() + "/Logic/core/LSHFakeData.json", "r") as json_file:
        fake_data = json.load(json_file)
    for fake_movie in fake_data:
        documents.append(" ".join(fake_movie["summaries"]))
    
    lsh_instance = MinHashLSH(documents=documents)
    buckets = lsh_instance.perform_lsh()
    lsh_instance.jaccard_similarity_test(buckets=buckets, all_documents=documents)
    print("The end")

# Total score: 1.0, Detects all the fake data
