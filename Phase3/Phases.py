import json
import math
import pickle
from collections import defaultdict


#### tf-idf
def compute_tf(term, document):
    return document.count(term) / len(document)


def compute_idf(term, documents):
    num_docs_containing_term = sum(1 for doc in documents if term in doc)
    if num_docs_containing_term > 0:
        return math.log(len(documents) / num_docs_containing_term)
    else:
        return 0


def compute_tf_idf(term, document, documents):
    return compute_tf(term, document) * compute_idf(term, documents)


class RankedRetrieval:
    matching_terms = []

    def __init__(self, phase3_instance):
        self.phase3 = phase3_instance

    def rank_documents(self, query):
        RankedRetrieval.matching_terms = []
        query_terms = query.split()
        doc_scores = defaultdict(float)

        for term in query_terms:
            if '*' in term:  # Handle wildcard term
                matching_terms = self.expand_wildcard(term)
                RankedRetrieval.matching_terms.extend(matching_terms)
                for m_term in matching_terms:
                    self.update_doc_scores(True, m_term, doc_scores)
            else:
                self.update_doc_scores(False, term, doc_scores)

        ranked_docs = sorted(doc_scores.items(), key=lambda item: item[1], reverse=True)
        return ranked_docs

    def expand_wildcard(self, term):
        wildcards = self.phase3.wildcard_index.keys()

        pre, post = term.split("*")
        terms = []
        if pre and post:
            for text in wildcards:
                if text.startswith(pre) and text.endswith(post):
                    terms.append(text)

        elif pre:
            for text in wildcards:
                if text.startswith(pre):
                    terms.append(text)

        else:
            for text in wildcards:
                if text.endswith(post):
                    terms.append(text)

        return terms
        # return self.phase3.wildcard_index[term.replace("*", "")]

    def update_doc_scores(self, is_wildcard, term, doc_scores):
        search_from = self.phase3.wildcard_index if is_wildcard else self.phase3.non_positional_index

        for doc_id in search_from[term]:
            # print(doc_id, self.phase3.positional_index[term][str(doc_id)])
            # doc_scores[str(doc_id)] += compute_tf_idf(term, self.phase3.positional_index[term][str(doc_id)],

            try:
                doc_scores[str(doc_id)] += compute_tf_idf(term, self.get_doc_content(str(doc_id)),
                                                          self.phase3.positional_index)
            except ZeroDivisionError:
                pass

    def get_doc_content(self, doc_id):
        doc_content = []
        for term, postings in self.phase3.positional_index.items():
            if str(doc_id) in postings.keys() or int(doc_id) in postings.keys():
                doc_content.extend([term] * len(postings[str(doc_id)]))
        return doc_content


class PhraseSearch:
    def __init__(self, phase3_instance):
        self.phase3 = phase3_instance

    def match_phrases(self, query):
        phrases = self.extract_phrases(query)
        matching_docs = self.find_matching_docs(phrases)
        ranked_docs = self.rank_phrase_documents(query, matching_docs)
        return ranked_docs

    def extract_phrases(self, query):
        import re
        phrases = re.findall(r'"([^"]*)"', query)
        return phrases

    def find_matching_docs(self, phrases):
        doc_sets = [set(self.phase3.non_positional_index[term]) for phrase in phrases for term in phrase.split()]
        if not doc_sets:
            return set()
        matching_docs = set.intersection(*doc_sets)
        return matching_docs

    def rank_phrase_documents(self, query, matching_docs):
        query_terms = query.replace('"', '').split()
        doc_scores = defaultdict(float)

        for doc_id in matching_docs:
            doc_content = self.get_doc_content(str(doc_id))
            for term in query_terms:
                doc_scores[str(doc_id)] += compute_tf_idf(term, str(doc_content), self.phase3.positional_index)

        ranked_docs = sorted(doc_scores.items(), key=lambda item: item[1], reverse=True)
        return ranked_docs

    def get_doc_content(self, doc_id):
        doc_content = []
        for term, postings in self.phase3.positional_index.items():
            if str(doc_id) in postings.keys() or int(doc_id) in postings.keys():
                doc_content.extend([term] * len(postings[str(doc_id)]))
        return doc_content


class Phase3:
    doc_id = 0

    def __init__(self):
        self.file_name = dict()
        self.non_positional_index = defaultdict(set)
        self.positional_index = defaultdict(lambda: defaultdict(list))
        self.wildcard_index = defaultdict(set)
        self.state = [0, "Not Started Yet!", '']

        self.ranked_retrieval = RankedRetrieval(self)
        self.phrase_search = PhraseSearch(self)

    def ranked_search(self, query):
        return self.ranked_retrieval.rank_documents(query)

    def exact_phrase_search(self, query):
        return self.phrase_search.match_phrases(query)

    @staticmethod
    def next_doc_id():
        Phase3.doc_id = str(int(Phase3.doc_id) + 1)
        return Phase3.doc_id

    def state_updater(self, done: int, process_length: int, section: str, directory: str = ''):
        """
            Updates the state of the preprocessing process.

            Args:
                done (int): Number of processed items.
                process_length (int): Total number of items to be processed.
                section (str): Current preprocessing section.
                directory (str, optional): Directory name being processed. Defaults to ''.
        """

        self.state = [round((done / process_length) * 100, 3), section, directory]

    def add_document(self, doc_id, text, **kwargs):
        words = text.split()
        for pos, word in enumerate(words):
            if kwargs['non-positional']:
                self.non_positional_index[word].add(str(doc_id))
            if kwargs['positional']:
                self.positional_index[word][str(doc_id)].append(pos)
            if kwargs['wildcard']:
                self._add_to_wildcard_index(word, str(doc_id))

    def _remove_from_index(self, word, doc_id, pos):
        if doc_id in self.non_positional_index[word]:
            self.non_positional_index[word].remove(str(doc_id))
            if not self.non_positional_index[word]:
                del self.non_positional_index[word]
        if doc_id in self.positional_index[word]:
            self.positional_index[word][str(doc_id)].remove(pos)
            if not self.positional_index[word][str(doc_id)]:
                del self.positional_index[word][str(doc_id)]
            if not self.positional_index[word]:
                del self.positional_index[word]
        self._remove_from_wildcard_index(word, str(doc_id))

    def _add_to_wildcard_index(self, word, doc_id):
        for i in range(len(word)):
            for j in range(i + 1, len(word) + 1):
                self.wildcard_index[word[i:j]].add(str(doc_id))

    def _remove_from_wildcard_index(self, word, doc_id):
        for i in range(len(word)):
            for j in range(i + 1, len(word) + 1):
                if doc_id in self.wildcard_index[word[i:j]]:
                    self.wildcard_index[word[i:j]].remove(str(doc_id))
                    if not self.wildcard_index[word[i:j]]:
                        del self.wildcard_index[word[i:j]]

    def save_index(self):
        with open("index.file", "wb") as file:
            pickle.dump({
                "file_names": {str(k): v for k, v in self.file_name.items()},
                "non_positional_index": {str(k): list(v) for k, v in self.non_positional_index.items()},
                "positional_index": {str(k): {str(dk): dv for dk, dv in v.items()} for k, v in
                                     self.positional_index.items()},
                "wildcard_index": {str(k): list(v) for k, v in self.wildcard_index.items()}
            }, file)
        try:
            with open('index.json', 'w', encoding='utf8') as file:
                json.dump(
                    #     {
                    #     "file_names": {str(k): v for k, v in self.file_name.items()},
                    #     "non_positional_index": {k: list(v) for k, v in self.non_positional_index.items()},
                    #     "positional_index": {k: {dk: dv for dk, dv in v.items()} for k, v in self.positional_index.items()},
                    #     "wildcard_index": {k: list(v) for k, v in self.wildcard_index.items()}
                    # }
                    {
                        "file_names": {str(k): v for k, v in self.file_name.items()},
                        "non_positional_index": {str(k): list(v) for k, v in self.non_positional_index.items()},
                        "positional_index": {str(k): {str(dk): dv for dk, dv in v.items()} for k, v in
                                             self.positional_index.items()},
                        "wildcard_index": {str(k): list(v) for k, v in self.wildcard_index.items()}
                    }, file, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving index to 'index.json': {e}")

    def load_index(self):
        # with open("index.file", "rb") as file:
        #     data = pickle.load(file)
        try:
            # with open('index.json', 'r', encoding="utf8") as file:
            #     data = json.load(file)
            with open("index.file", "rb") as file:
                data = pickle.load(file)
                self.file_name = {str(k): v for k, v in data["file_names"].items()}
                self.non_positional_index = defaultdict(set,
                                                        {str(k): set(v) for k, v in
                                                         data["non_positional_index"].items()})
                self.positional_index = defaultdict(lambda: defaultdict(list), {str(k): defaultdict(list, v) for k, v in
                                                                                data["positional_index"].items()})
                self.wildcard_index = defaultdict(set, {str(k): set(v) for k, v in data["wildcard_index"].items()})
        except IOError as e:
            print(f"Error loading index from 'index.json': {e}")


class Evaluation:
    def __init__(self):
        pass

    @staticmethod
    def precision(retrieved, relevant):
        true_positives = len(set(retrieved).intersection(set(relevant)))
        return true_positives / len(retrieved) if retrieved else 0

    @staticmethod
    def recall(retrieved, relevant):
        true_positives = len(set(retrieved).intersection(set(relevant)))
        return true_positives / len(relevant) if relevant else 0

    def f_measure(self, retrieved, relevant):
        precision = self.precision(retrieved, relevant)
        recall = self.recall(retrieved, relevant)
        if precision + recall == 0:
            return 0
        return (2 * (precision * recall)) / (precision + recall)

    def average_precision(self, retrieved, relevant):
        hits = 0
        sum_precisions = 0
        for i, doc_id in enumerate(retrieved):
            if str(doc_id) in relevant:
                hits += 1
                sum_precisions += hits / (i + 1)
        return sum_precisions / len(relevant) if relevant else 0

    def mean_average_precision(self, queries_results, relevant_docs):
        avg_precisions = []
        for query in queries_results:
            retrieved = [str(i) for i in queries_results[query]]
            relevant = [str(i) for i in relevant_docs.get(query, [])]
            avg_precisions.append(self.average_precision(retrieved, relevant))
        return sum(avg_precisions) / len(avg_precisions) if avg_precisions else 0


def part1(phase3, phrase_query):
    ranked_results_return = []
    phrase_results_return = []

    phase3.state_updater(1, 3, "Ranking...!")
    ranked_results = phase3.ranked_search(phrase_query.replace("\"", ""))

    x = 1
    for doc_id, score in ranked_results:
        ranked_results_return.append({
            'rank': x,
            'file_name': phase3.file_name[str(doc_id)].split('\\')[-1],
            'path': phase3.file_name[str(doc_id)],
            'score': score,
            'doc_id': str(doc_id)
        })
        x += 1

    # Perform an exact phrase search
    phase3.state_updater(2, 3, "Exact Ranking...!")
    phrase_results = phase3.exact_phrase_search(phrase_query if '"' in phrase_query else f'"{phrase_query}"')

    x = 1
    for doc_id, score in phrase_results:
        phrase_results_return.append({
            'rank': x,
            'file_name': phase3.file_name[str(doc_id)].split('\\')[-1],
            'path': phase3.file_name[str(doc_id)],
            'score': score,
            'doc_id': str(doc_id)
        })
        x += 1

    phase3.state_updater(3, 3, "Done!")

    return ranked_results_return, phrase_results_return, RankedRetrieval.matching_terms


def part2(phase3, queries):
    evaluation = Evaluation()

    phase3.load_index()
    res_return = {}

    queries_results_ranked = {}
    queries_results_phrase = {}

    phase3.state_updater(1, 4, "Getting ready...")
    for query in queries:
        ranked_results = phase3.ranked_search(query)  # [:5]  # max 5 retrieved docs
        phrase_results = phase3.exact_phrase_search(f'"{query}"')  # [:5]  # max 5 retrieved docs
        queries_results_ranked[query] = [str(doc_id) for doc_id, _ in ranked_results]
        queries_results_phrase[query] = [str(doc_id) for doc_id, _ in phrase_results]

    phase3.state_updater(2, 4, "Measure ranked...")
    f_measure_ranks = []
    for i in range(0, len(queries.keys())):
        f_measure_ranks.append(
            evaluation.f_measure(queries_results_ranked[list(queries.keys())[i]], queries[list(queries.keys())[i]]))

    f_measure_ranked = max(f_measure_ranks)  # sum(f_measure_ranks) / len(f_measure_ranks)
    map_ranked = evaluation.mean_average_precision(queries_results_ranked, queries)

    res_return['ranked'] = {
        'f_measure': f_measure_ranked,
        'map': map_ranked
    }

    phase3.state_updater(3, 4, "Measure phrase...")
    f_measure_ranks = []
    for i in range(0, len(queries.keys())):
        f_measure_ranks.append(
            evaluation.f_measure(queries_results_phrase[list(queries.keys())[i]], queries[list(queries.keys())[i]]))

    f_measure_phrase = max(f_measure_ranks)  # sum(f_measure_ranks) / len(f_measure_ranks)
    map_phrase = evaluation.mean_average_precision(queries_results_phrase, queries)

    res_return['phrase'] = {
        'f_measure': f_measure_phrase,
        'map': map_phrase
    }

    phase3.state_updater(4, 4, "Done!")

    return res_return


if __name__ == "__main__":
    pass
    # Add some sample documents
    # docs = [
    #     "the quick brown fox jumps over the lazy dog",
    #     "the fast brown fox leaps over the lazy hound",
    #     "the quick red fox jumps over the sleepy dog",
    # ]
    # phrase_query = '"q* brown fox" "lazy dog"'
    #
    # phase3 = Phase3()
    # part1(phase3, phrase_query)
    # part2()
