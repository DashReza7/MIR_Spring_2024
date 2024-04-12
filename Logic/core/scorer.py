import numpy as np

class Scorer:
    def __init__(self, index, number_of_documents):
        """
        Initializes the Scorer.

        Parameters
        ----------
        index : dict
            The index to score the documents with.
        number_of_documents : int
            The number of documents in the index.
        """

        self.index = index
        self.idf = {}
        self.N = number_of_documents

    def get_list_of_documents(self,query):
        """
        Returns a list of documents that contain at least one of the terms in the query.

        Parameters
        ----------
        query: List[str]
            The query to be scored

        Returns
        -------
        list
            A list of documents that contain at least one of the terms in the query.
        
        Note
        ---------
            The current approach is not optimal but we use it due to the indexing structure of the dict we're using.
            If we had pairs of (document_id, tf) sorted by document_id, we could improve this.
                We could initialize a list of pointers, each pointing to the first element of each list.
                Then, we could iterate through the lists in parallel.
            
        """
        list_of_documents = []
        for term in query:
            if term in self.index.keys():
                list_of_documents.extend(self.index[term].keys())
        return list(set(list_of_documents))
    
    def get_idf(self, term):
        """
        Returns the inverse document frequency of a term.

        Parameters
        ----------
        term : str
            The term to get the inverse document frequency for.

        Returns
        -------
        float
            The inverse document frequency of the term.
        
        Note
        -------
            It was better to store dfs in a separate dict in preprocessing.
        """
        idf = self.idf.get(term, None)
        if idf is None:
            if term not in self.index:
                idf = 0
            else:
                df = len(self.index[term])
                if df == 0:
                    idf = 0
                else:
                    idf = np.log(self.N / df)
                self.idf[term] = idf
        return idf
    
    def get_query_tfs(self, query):
        """
        Returns the term frequencies of the terms in the query.

        Parameters
        ----------
        query : List[str]
            The query to get the term frequencies for.

        Returns
        -------
        dict
            A dictionary of the term frequencies of the terms in the query.
        """
        dic = {}
        for term in query:
            if term in dic:
                continue
            cnt = 0
            for word in query:
                if term == word:
                    cnt += 1
            dic[term] = cnt
        return dic

    def compute_scores_with_vector_space_model(self, query, method):
        """
        compute scores with vector space model

        Parameters
        ----------
        query: List[str]
            The query to be scored
        method : str ((n|l)(n|t)(n|c).(n|l)(n|t)(n|c))
            The method to use for searching.

        Returns
        -------
        dict
            A dictionary of the document IDs and their scores.
        """
        query_tfs = self.get_query_tfs(query)
        all_docs = self.get_list_of_documents(query)
        scores = dict()
        for doc in all_docs:
            scores[doc] = self.get_vector_space_model_score(query, query_tfs, doc, method[:3], method[4:])
        return scores

    def get_vector_space_model_score(self, query, query_tfs, document_id, document_method, query_method):
        """
        Returns the Vector Space Model score of a document for a query.

        Parameters
        ----------
        query: List[str]
            The query to be scored
        query_tfs : dict
            The term frequencies of the terms in the query.
        document_id : str
            The document to calculate the score for.
        document_method : str (n|l)(n|t)(n|c)
            The method to use for the document.
        query_method : str (n|l)(n|t)(n|c)
            The method to use for the query.

        Returns
        -------
        float
            The Vector Space Model score of the document for the query.
        """
        query_vec = []
        doc_vec = []
        unique_query_terms = list(set(query))
        for term in unique_query_terms:
            if term in self.index.keys():
                if query_method[0] == "n":
                    query_vec.append(query_tfs[term])
                else:
                    query_vec.append(1 + np.log(query_tfs[term]))
                if document_method[0] == "n":
                    doc_vec.append(self.index[term].get(document_id, 0))
                else:
                    if document_id in self.index[term]:
                        doc_vec.append(1 + np.log(self.index[term][document_id]))
                    else:
                        doc_vec.append(0)
                if query_method[1] == "t":
                    query_vec[-1] *= self.get_idf(term)
                if document_method[1] == "t":
                    doc_vec[-1] *= self.get_idf(term)
        query_vec = np.array(query_vec)
        doc_vec = np.array(doc_vec)
        if query_method[2] == "c":
            query_vec = query_vec / np.linalg.norm(query_vec)
        if document_method[2] == "c":
            doc_vec = doc_vec / np.linalg.norm(doc_vec)
        return np.dot(np.array(query_vec), np.array(doc_vec))

    def compute_socres_with_okapi_bm25(self, query, average_document_field_length, document_lengths):
        """
        compute scores with okapi bm25

        Parameters
        ----------
        query: List[str]
            The query to be scored
        average_document_field_length : float
            The average length of the documents in the index.
        document_lengths : dict
            A dictionary of the document lengths. The keys are the document IDs, and the values are
            the document's length in that field.
        
        Returns
        -------
        dict
            A dictionary of the document IDs and their scores.
        """
        documents = self.get_list_of_documents(query)
        scores = dict()
        for doc in documents:
            scores[doc] = self.get_okapi_bm25_score(query, doc, average_document_field_length, document_lengths)
        return scores

    def get_okapi_bm25_score(self, query, document_id, average_document_field_length, document_lengths):
        """
        Returns the Okapi BM25 score of a document for a query.

        Parameters
        ----------
        query: List[str]
            The query to be scored
        document_id : str
            The document to calculate the score for.
        average_document_field_length : float
            The average length of the documents in the index.
        document_lengths : dict
            A dictionary of the document lengths. The keys are the document IDs, and the values are
            the document's length in that field.

        Returns
        -------
        float
            The Okapi BM25 score of the document for the query.
        """
        query = list(set(query))
        b = 0.75
        k1 = 1.5
        score = 0
        for word in query:
            if word in self.index.keys():
                tf = self.index[word].get(document_id, 0)
                idf = self.get_idf(word)
                score += idf * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * document_lengths[document_id] / average_document_field_length)))
        return score
