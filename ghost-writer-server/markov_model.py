import os
import pickle
import numpy as np


from ghost import GHOST_DIRECTORY, ghost_list
from streams import term_stream, document_stream


MODEL_DIRECTORY = "models"
MAX_N_GRAM = 3


session = {}


def n_grams():
    return list(range(1, MAX_N_GRAM + 1))


def binary_search(values, key):
    lower = 0
    upper = len(values)
    while lower + 1 < upper:
        half = int((lower + upper) / 2)
        if key == values[half]:
            return half
        elif key > values[half]:
            lower = half
        elif key < values[half]:
            upper = half
    return -lower


def model_predict(model, word, is_complete):
    terms = model.get("terms", [])
    document_frequency = model.get(
        "document_frequency", 
        np.zeros((0, 0), dtype=np.float32)
    )

    if word is None:
        i = 0
        max_frequency = -1
        for j in range(len(terms)):
            frequency = document_frequency[j].sum()
            if max_frequency < frequency:
                max_frequency = frequency
                i = j
        word = terms[i]

    if not is_complete:
        lower = binary_search(terms, word)
        upper = len(terms) - 1

        if lower < 0:
            lower = 1-lower

            for j in range(lower, len(terms)):
                if not terms[j].startswith(word):
                    upper = j
                    break
            
            # term not found
            if lower == upper:
                if lower == 0:
                    upper = 1
                else:
                    lower = upper - 1

            # returns suggestions?
            return terms[lower:upper]

            # UNSURE IF I'LL USE THIS CODE.
            """
            i = 0
            max_frequency = -1
            for j in range(1 + upper - lower):
                frequency = document_frequency[j].sum()
                if max_frequency < frequency:
                    max_frequency = frequency
                    i = j
            
            word = terms[i]
            """

    i = binary_search(terms, word)
    suggestions = [
        (j, document_frequency[i, j]) for j in range(len(terms))
    ]
    
    suggestions.sort(key=lambda x: x[1], reverse=True)
    
    return list(map(lambda x: terms[x[0]], suggestions))

def create_model(ghost, n_gram):
    N = 0
    terms_set = set()
    for document in document_stream(ghost):
        for previous_term, term in term_stream(document, n_gram):
            terms_set.add(previous_term)
            terms_set.add(term)
            N += 1
    
    terms = list(terms_set)
    terms.sort()

    document_frequency = np.zeros(
        (len(terms), len(terms)), 
        dtype=np.float32
    )

    for document in document_stream(ghost):
        for previous_term, term in term_stream(document, n_gram):
            i = binary_search(terms, previous_term)
            j = binary_search(terms, term)
            if i > -1 and j > -1:
                document_frequency[i, j] += 1

    document_inverse_frequency = np.log(N / (document_frequency + 1))

    model = {
        'terms': terms,
        'document_frequency': document_frequency,
        'document_inverse_frequency': document_inverse_frequency
    }

    directory = os.path.join(MODEL_DIRECTORY, ghost)
    if not os.path.exists(directory):
        os.mkdir(directory)

    filename = os.path.join(directory, f"{n_gram}.pickle")
    if not os.path.exists(filename):
        with open(filename, 'wb') as file:
            pickle.dump(model, file)


def predict(word, is_complete, n_gram, ghost):
    if n_gram not in n_grams():
        n_gram = 1

    if ghost is None:
        ghosts = ghost_list()
        ghost = ghosts[0]

    model = session.get('model', None)
    session_ghost = session.get('ghost', None)
    session_n_gram = session.get('n_gram', None)
    if (model is None 
        or not ghost == session_ghost
        or not n_gram == session_n_gram):

        directory = os.path.join(MODEL_DIRECTORY, ghost)
        if not os.path.exists(directory):
            os.mkdir(directory)

        filename = os.path.join(directory, f"{n_gram}.pickle")
        if not os.path.exists(filename):
            create_model(ghost, n_gram)

        prediction = []
        with open(filename, 'rb') as file:
            model = pickle.load(file)

            session['model'] = model
            session['ghost'] = ghost
            session['n_gram'] = n_gram

    prediction = model_predict(model, word, is_complete)

    return prediction