import json
import numpy as np
import os
import sys
sys.path.append(os.getcwd() + "/Logic/core/")
from preprocess import Preprocessor
from scorer import Scorer
sys.path.append(os.getcwd() + "/Logic/core/indexer/")
from indexer.indexes_enum import Indexes, Index_types
from indexer.index_reader import Index_reader
from copy import deepcopy

class SearchEngine:
    def __init__(self):
        """
        Initializes the search engine.

        """
        path = os.getcwd() + "/Logic/Data/"
        self.document_indexes = {
            Indexes.STARS.value: Index_reader(path, Indexes.STARS),
            Indexes.GENRES.value: Index_reader(path, Indexes.GENRES),
            Indexes.SUMMARIES.value: Index_reader(path, Indexes.SUMMARIES)
        }
        self.tiered_index = {
            Indexes.STARS.value: Index_reader(path, Indexes.STARS, Index_types.TIERED),
            Indexes.GENRES.value: Index_reader(path, Indexes.GENRES, Index_types.TIERED),
            Indexes.SUMMARIES.value: Index_reader(path, Indexes.SUMMARIES, Index_types.TIERED)
        }
        self.document_lengths_index = {
            Indexes.STARS.value: Index_reader(path, Indexes.STARS, Index_types.DOCUMENT_LENGTH),
            Indexes.GENRES.value: Index_reader(path, Indexes.GENRES, Index_types.DOCUMENT_LENGTH),
            Indexes.SUMMARIES.value: Index_reader(path, Indexes.SUMMARIES, Index_types.DOCUMENT_LENGTH)
        }
        self.metadata_index = Index_reader(
            path, Indexes.DOCUMENTS, Index_types.METADATA
        )

    def search(
        self,
        query,
        method,
        weights,
        safe_ranking=True,
        max_results=10,
        smoothing_method=None,
        alpha=0.5,
        lamda=0.5,
    ):
        """
        searches for the query in the indexes.

        Parameters
        ----------
        query : str
            The query to search for.
        method : str ((n|l)(n|t)(n|c).(n|l)(n|t)(n|c)) | OkapiBM25 | Unigram
            The method to use for searching.
        weights: dict
            The weights of the fields.
        safe_ranking : bool
            If True, the search engine will search in whole index and then rank the results.
            If False, the search engine will search in tiered index.
        max_results : int
            The maximum number of results to return. If None, all results are returned.
        smoothing_method : str (bayes | naive | mixture)
            The method used for smoothing the probabilities in the unigram model.
        alpha : float, optional
            The parameter used in bayesian smoothing method. Defaults to 0.5.
        lamda : float, optional
            The parameter used in some smoothing methods to balance between the document
            probability and the collection probability. Defaults to 0.5.

        Returns
        -------
        list
            A list of tuples containing the document IDs and their scores sorted by their scores.
        """
        preprocessor = Preprocessor([query])
        query = preprocessor.preprocess()[0].split()

        if max_results == -1:
            max_results = self.metadata_index["document_count"]
        
        scores = {}
        if method == "unigram":
            self.find_scores_with_unigram_model(
                query, smoothing_method, weights, scores, alpha, lamda
            )
        elif safe_ranking:
            self.find_scores_with_safe_ranking(query, method, weights, scores)
        else:
            self.find_scores_with_unsafe_ranking(
                query, method, weights, max_results, scores
            )

        final_scores = {}

        self.aggregate_scores(weights, scores, final_scores)

        result = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        print(len(result))
        if max_results is not None:
            result = result[:max_results]

        return result

    def aggregate_scores(self, weights, scores, final_scores):
        """
        Aggregates the scores of the fields.

        Parameters
        ----------
        weights : dict
            The weights of the fields.
        scores : dict
            The scores of the fields.
        final_scores : dict
            The final scores of the documents.
        """
        # TODO: probable bug
        sum = 0.0
        for field in weights:
            for doc, score in scores[field].items():
                if doc not in final_scores:
                    final_scores[doc] = 0
                final_scores[doc] += score * weights[field]

    def find_scores_with_unsafe_ranking(self, query, method, weights, max_results, scores):
        """
        Finds the scores of the documents using the unsafe ranking method using the tiered index.

        Parameters
        ----------
        query: List[str]
            The query to be scored
        method : str ((n|l)(n|t)(n|c).(n|l)(n|t)(n|c)) | OkapiBM25
            The method to use for searching.
        weights: dict
            The weights of the fields.
        max_results : int
            The maximum number of results to return.
        scores : dict
            The scores of the documents.
        """
        for field in weights:
            for tier in ["first_tier", "second_tier", "third_tier"]:
                scorer = Scorer(self.tiered_index[field.value].index[tier], self.metadata_index.index["document_count"])
                if method == "OkapiBM25":
                    score = scorer.compute_socres_with_okapi_bm25(query, self.metadata_index.index["averge_document_length"][field.value], self.document_lengths_index[field].index)
                else:
                    score = scorer.compute_scores_with_vector_space_model(query, method)
                scores[field] = self.merge_scores(scores[field], score)
                if len(scores[field]) >= max_results:
                    break

    def find_scores_with_safe_ranking(self, query, method, weights, scores):
        """
        Finds the scores of the documents using the safe ranking method.

        Parameters
        ----------
        query: List[str]
            The query to be scored
        method : str ((n|l)(n|t)(n|c).(n|l)(n|t)(n|c)) | OkapiBM25
            The method to use for searching.
        weights: dict
            The weights of the fields.
        scores : dict
            The scores of the documents.
        """

        for field in weights:
            scorer = Scorer(self.document_indexes[field.value].index, self.metadata_index.index["document_count"])
            if method == "OkapiBM25":
                score = scorer.compute_socres_with_okapi_bm25(query, self.metadata_index.index['averge_document_length'][field.value], self.document_lengths_index[field].index)
            else:
                score = scorer.compute_scores_with_vector_space_model(query, method)
            scores[field] = score

    def merge_scores(self, scores1, scores2):
        """
        Merges two dictionaries of scores.

        Parameters
        ----------
        scores1 : dict
            The first dictionary of scores.
        scores2 : dict
            The second dictionary of scores.

        Returns
        -------
        dict
            The merged dictionary of scores.
        """
        #TODO: probable bug
        scores = deepcopy(scores1)
        for k, v in scores2.items():
            if k not in scores:
                scores[k] = 0.0
            scores[k] += v
        return scores


if __name__ == "__main__":
    search_engine = SearchEngine()
    query = "spider man in wonderland"
    query = "tom holland spider man"
    method = "lnc.ltc"
    weights = {Indexes.STARS: 1, Indexes.GENRES: 1, Indexes.SUMMARIES: 1}
    result = search_engine.search(query, method, weights)
    print(result)
