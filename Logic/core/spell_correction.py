import os
import json

class SpellCorrection:
    def __init__(self, all_documents):
        """
        Initialize the SpellCorrection

        Parameters
        ----------
        all_documents : list of str
            The input documents.
        """
        self.all_shingled_words, self.word_counter = self.shingling_and_counting(all_documents)

    def shingle_word(self, word, k=2):
        """
        Convert a word into a set of shingles.

        Parameters
        ----------
        word : str
            The input word.
        k : int
            The size of each shingle.

        Returns
        -------
        set
            A set of shingles.
        """
        shingles = set()
        if len(word) < k:
            shingles.add(word)
            return shingles
        for i in range(len(word) - k + 1):
            shingles.add(word[i:i+k])
        return shingles
    
    def jaccard_score(self, first_set, second_set):
        """
        Calculate jaccard score.

        Parameters
        ----------
        first_set : set
            First set of shingles.
        second_set : set
            Second set of shingles.

        Returns
        -------
        float
            Jaccard score.
        """
        # TODO: is this true?
        if len(first_set) == 0 or len(second_set) == 0:
            return 0
        union_set = set()
        union_set.update(first_set)
        union_set.update(second_set)
        return (len(first_set) + len(second_set) - len(union_set)) / len(union_set)

    def shingling_and_counting(self, all_documents):
        """
        Shingle all words of the corpus and count TF of each word.

        Parameters
        ----------
        all_documents : list of str
            The input documents.

        Returns
        -------
        all_shingled_words : dict
            A dictionary from words to their shingle sets.
        word_counter : dict
            A dictionary from words to their TFs.
        """
        documents = [doc.lower() for doc in all_documents]
        all_shingled_words = dict()
        word_counter = dict()

        for doc in documents:
            doc_splitted = doc.strip().split()
            for term in doc_splitted:
                if term not in word_counter:
                    word_counter[term] = 0
                    all_shingled_words[term] = self.shingle_word(term)
                word_counter[term] += 1
                
        return all_shingled_words, word_counter
    
    def find_nearest_words(self, word):
        """
        Find correct form of a misspelled word.

        Parameters
        ----------
        word : str
            The misspelled word.

        Returns
        -------
        list of str
            5 nearest words.
        """
        # (jaccard_score of term with word_shingle, term)
        top5_candidates = list()

        word_shingled = self.shingle_word(word)
        for term, term_shingled in self.all_shingled_words.items():
            top5_candidates.append((self.jaccard_score(word_shingled, term_shingled), term))
            if len(top5_candidates) > 5:
                top5_candidates = sorted(top5_candidates, reverse=True)
                del top5_candidates[-1]
        max_cf = self.word_counter[top5_candidates[0][1]]
        for i in range(1, len(top5_candidates)):
            max_cf = max(max_cf, self.word_counter[top5_candidates[i][1]])
        new_list = [(foo[0] * (self.word_counter[foo[1]] / max_cf), foo[0], foo[1]) for foo in top5_candidates]
        new_list = sorted(new_list, reverse=True)
        top5_candidates = [(new_list[i][1], new_list[i][2]) for i in range(5)]

        return [cand[1] for cand in top5_candidates]
    
    def spell_check(self, query):
        """
        Find correct form of a misspelled query.

        Parameters
        ----------
        query : stf
            The misspelled query.

        Returns
        -------
        str
            Correct form of the query.
        """
        query = query.lower()
        query_splitted = query.split()
        fixed_query = ""
        for term in query_splitted:
            if term in self.word_counter:
                fixed_query += term + " "
            else:
                candidates = self.find_nearest_words(term)
                fixed_query += candidates[0] + " "
        fixed_query = fixed_query.strip()
        return fixed_query


if __name__ == "__main__":
    corpus = []
    with open(os.getcwd() + "/Logic/Data/corpus_for_spell_correction.json", "r") as file:
        corpus = json.load(file)
    spell_corrector = SpellCorrection(corpus)
    nws = spell_corrector.find_nearest_words("how")
    print(nws)
    foo = spell_corrector.spell_check("Whaat the hel are yo doing")
    print(foo)
