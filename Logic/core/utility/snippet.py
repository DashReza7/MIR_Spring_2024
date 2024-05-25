import re
import nltk
from nltk.stem import WordNetLemmatizer, PorterStemmer

class Snippet:
    def __init__(self, number_of_words_on_each_side=5):
        """
        Initialize the Snippet

        Parameters
        ----------
        number_of_words_on_each_side : int
            The number of words on each side of the query word in the doc to be presented in the snippet.
        """
        self.number_of_words_on_each_side = number_of_words_on_each_side
        self.stopwords = [r"\bthis\b", r"\bthat\b", r"\babout\b", r"\bwhom\b", r"\bbeing\b", r"\bwhere\b", r"\bwhy\b", r"\bhad\b", r"\bshould\b", r"\beach\b"]
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()

    def remove_stop_words_from_query(self, query):
        """
        Remove stop words from the input string.

        Parameters
        ----------
        query : str
            The query that you need to delete stop words from.

        Returns
        -------
        str
            The query without stop words.
        """
        query = query.lower()
        for stopword in self.stopwords:
            query = re.sub(stopword, "", query)
        return

    # doc must be clean(lower cased with removed redundant characters) and not stemmed or lemmatized.
    def find_snippet(self, doc, query):
        """
        Find snippet in a doc based on a query.

        Parameters
        ----------
        doc : str
            The retrieved doc which the snippet should be extracted from that.
        query : str
            The query which the snippet should be extracted based on that.

        Returns
        -------
        final_snippet : str
            The final extracted snippet. IMPORTANT: The keyword should be wrapped by *** on both sides.
            For example: Sahwshank ***redemption*** is one of ... (for query: redemption)
        not_exist_words : list
            Words in the query which don't exist in the doc.
        """
        k = self.number_of_words_on_each_side
        doc_tokens = nltk.word_tokenize(doc)
        query_tokens = nltk.word_tokenize(query)
        doc_tokens_stemmed = [self.stemmer.stem(token) for token in doc_tokens]
        query_tokens_stemmed = [self.stemmer.stem(token) for token in query_tokens]

        # occurances
        occs = []
        exist_words = set()
        for i, token in enumerate(doc_tokens_stemmed):
            if token in query_tokens_stemmed:
                occs.append((i, query_tokens_stemmed.index(token)))
                exist_words.add(query_tokens_stemmed.index(token))
        not_exist_words = [query_tokens[i] for i in range(len(query_tokens)) if i not in exist_words]

        foo = [{} for query_index in range(len(query_tokens_stemmed))]
        for (doc_pos, query_pos) in occs:
            cnt = 0
            for i in range(doc_pos - 1, doc_pos - k - 1, -1):
                if i < 0:
                    break
                if doc_tokens_stemmed[i] in query_tokens_stemmed:
                    cnt += 1
            for i in range(doc_pos + 1, doc_pos + k + 1, 1):
                if i >= len(doc_tokens_stemmed):
                    break
                if doc_tokens_stemmed[i] in query_tokens_stemmed:
                    cnt += 1
            foo[query_pos][doc_pos] = cnt
        
        for i in range(len(foo)):
            if len(foo[i]) == 0:
                continue
            (doc_pos_mx, cnt_mx) = (-1, 0)
            for doc_pos, cnt in foo[i].items():
                if cnt > cnt_mx:
                    (doc_pos_mx, cnt_mx) = (doc_pos, cnt)
            foo[i] = {doc_pos_mx: cnt_mx}
        
        # (cnt, list of consecutive indexes)
        windows = list()
        visited_query_indexes = set()
        for i in range(len(foo)):
            if len(foo[i]) == 0 or i in visited_query_indexes:
                continue
            visited_query_indexes.add(i)
            cnt = 1
            pos = list(foo[i].keys())[0]
            around_indexes = [pos]
            for j in range(pos - 1, pos - 1 - k, -1):
                if j < 0:
                    break
                around_indexes.append(j)
            
            j = pos + 1
            bound = pos + 1 + k
            while j < bound:
                if j >= len(doc_tokens_stemmed):
                    break
                around_indexes.append(j)
                if doc_tokens_stemmed[j] in query_tokens_stemmed:
                    visited_query_indexes.add(query_tokens_stemmed.index(doc_tokens_stemmed[j]))
                    bound = j + 1 + k
                    cnt += 1
                j += 1
            
            around_indexes = sorted(around_indexes)
            windows.append((cnt, around_indexes))
        
        windows = sorted(windows)
        window_strings = []
        for window in windows:
            around_indexes = window[1]
            window_str = ""
            for i in around_indexes:
                if doc_tokens_stemmed[i] in query_tokens_stemmed:
                    window_str += f"***{doc_tokens[i]}*** "
                else:
                    window_str += doc_tokens[i] + " "
            window_str = window_str.strip()
            window_strings.append(window_str)
        result = "...".join(window_strings)
        print(result)
        return (result, not_exist_words)

if __name__ == "__main__":
    query = "stumble stupid floats flying machines"
    doc = "a young boy and a girl with a magic crystal must race against pirates and foreign agents in a search for a legendary floating castle  a young boy stumbles into a mysterious girl who floats down from the sky  the girl  sheeta  was chased by pirates  army and government secret agents  in saving her life  they begin a high flying adventure that goes through all sorts of flying machines  eventually searching for sheeta s identity in a floating castle of a lost civilization  tzung i lin  a 13 year old teenage girl  sheeta  escapes from the clutches of some mysterious pirate like villains  she ends up in a small village and is befriended by a 13 year old teenage boy  pazu  however  the villains track them down  as do a variety of other people who seem keen to get their hands on the girl  and soon sheeta and pazu are fleeing for their lives    grantss on a cloudy night  brave pazu  an engineer s apprentice with a heart of gold  discovers sheeta  the mysterious girl who fell from the sky  not knowing what to expect  the boy approaches her  drawn by the iridescent  almost mystical light emanating from sheeta s necklace  but the same gem has already caught unwanted attention  now  with dangerous sky pirates and the unstoppable agents of a shadowy organisation hot on their trail  sheeta and pazu embark on a challenging quest to decipher the meaning of the intriguing crystal amulet  legend has it that laputa was a mythical flying island  after all  pazu s father was confident that he had seen it  will the young allies unravel the pendant s puzzling secret and the myth of the floating castle in the sky  nick riganas pazu  the apprentice of the engineer who maintains a mine s elevator machinery  finds an unconscious girl floating down from the sky  this girl  sheeta  and her magical levitation stone pendant hold the key to a mysterious  mythical sky castle known as laputa  sheeta and pazu must flee from both air pirates  who seek the sky kingdom for its legendary treasure  and the army  led by a government agent with his own mysterious agenda for laputa  christopher e  meadows"
    snippet = Snippet(7)
    print(snippet.find_snippet(doc, query))
