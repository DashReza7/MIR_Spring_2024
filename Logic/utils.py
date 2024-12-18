from typing import Dict, List
from core.search import SearchEngine
from core.spell_correction import SpellCorrection
from core.snippet import Snippet
from core.indexer.indexes_enum import Indexes, Index_types
import json
import os

movies_dataset = None  # TODO
search_engine = SearchEngine()

def init_utils():
    with open(os.getcwd() + "/Logic/tests/CrawlerResults/IMDB_Crawled.json", "r") as file:
        global movies_dataset
        foo = json.load(file)
        movies_dataset = dict()
        for movie in foo:
            movies_dataset[movie["id"]] = movie
    global search_engine
    if search_engine is None:
        search_engine = SearchEngine()

def correct_text(text: str, all_documents: List[str] = None) -> str:
    """
    Correct the give query text, if it is misspelled using Jacard similarity

    Paramters
    ---------
    text: str
        The query text
    all_documents : list of str
        The input documents.

    Returns
    str
        The corrected form of the given text
    """
    # TODO: You can add any preprocessing steps here, if needed!
    if all_documents == None:
        with open(os.getcwd() + "/Logic/Data/corpus_for_spell_correction.json", "r") as file:
            all_documents = json.load(file)
    spell_correction_obj = SpellCorrection(all_documents)
    text = spell_correction_obj.spell_check(text)
    return text


def search(
    query: str,
    max_result_count: int = 10,
    method: str = "ltn-lnn",
    weights: list = [0.3, 0.3, 1],
    should_print=False,
    preferred_genre: str = None,
):
    """
    Finds relevant documents to query

    Parameters
    ---------------------------------------------------------------------------------------------------
    query:
        The query text

    max_result_count: Return top 'max_result_count' docs which have the highest scores.
                      notice that if max_result_count = -1, then you have to return all docs

    method: 'ltn.lnn' or 'ltc.lnc' or 'OkapiBM25'

    weights:
        The list, containing importance weights in the search result for each of these items:
            Indexes.STARS: weights[0],
            Indexes.GENRES: weights[1],
            Indexes.SUMMARIES: weights[2],

    preferred_genre:
        A list containing preference rates for each genre. If None, the preference rates are equal.
        (You can leave it None for now)

    Returns
    ----------------------------------------------------------------------------------------------------
    list
    Retrieved documents with snippet
    """
    # weights = ...  # TODO
    weights = {
        Indexes.STARS: weights[0],
        Indexes.GENRES: weights[1],
        Indexes.SUMMARIES: weights[2]
    }
    global search_engine
    return search_engine.search(
        query, method, weights, max_results=max_result_count, safe_ranking=True
    )


def get_movie_by_id(id: str, movies_dataset: List[Dict[str, str]]) -> Dict[str, str]:
    """
    Get movie by its id

    Parameters
    ---------------------------------------------------------------------------------------------------
    id: str
        The id of the movie

    movies_dataset: List[Dict[str, str]]
        The dataset of movies

    Returns
    ----------------------------------------------------------------------------------------------------
    dict
        The movie with the given id
    """
    # result = movies_dataset.get(
    #     id,
    #     {
    #         "Title": "This is movie's title",
    #         "Summary": "This is a summary",
    #         "URL": "https://www.imdb.com/title/tt0111161/",
    #         "Cast": ["Morgan Freeman", "Tim Robbins"],
    #         "Genres": ["Drama", "Crime"],
    #         "Image_URL": "https://m.media-amazon.com/images/M/MV5BNDE3ODcxYzMtY2YzZC00NmNlLWJiNDMtZDViZWM2MzIxZDYwXkEyXkFqcGdeQXVyNjAwNDUxODI@._V1_.jpg",
    #     },
    # )

    # result["Image_URL"] = (
    #     "https://m.media-amazon.com/images/M/MV5BNDE3ODcxYzMtY2YzZC00NmNlLWJiNDMtZDViZWM2MzIxZDYwXkEyXkFqcGdeQXVyNjAwNDUxODI@._V1_.jpg"  # a default picture for selected movies
    # )
    # result["URL"] = (
    #     f"https://www.imdb.com/title/{result['id']}"  # The url pattern of IMDb movies
    # )
    # return result
    return None
