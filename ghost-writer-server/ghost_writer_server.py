from flask import Flask, request, render_template, make_response
from markov_model import predict, n_grams
from ghost import ghost_list
import json


app = Flask(__name__)


@app.route('/')
def index():
    """
    Main view of the application.
    """

    ghosts_available = ghost_list()
    n_grams_available = n_grams()

    return render_template(
        'index.html', 
        ghosts_available=ghosts_available,
        n_grams_available=n_grams_available
    )


@app.route('/markov_predict', methods=["GET"])
def markov_predict():
    """
    Computes the markov model prediction for the current
    word, chain legth and ghost.

    Input
    - word. The word to be used as the start of the 
    sequence (DEFAULT most frequent word of the model).
    - is_complete. Whether or not it's a completed 
    word or needs to be autocompleted (DEFAULT 1).
    - n_gram. The length of the markov chain
    to be used in the prediction (DEFAULT 1).
    NOTE: DO NOT GO OVER 3 N_GRAMS. I'M NOT SURE
    IF I IMPLEMENTED THIS CORRECTLY. THIS GROWS
    EXPONENTIALLY!!!
    - ghost. The collection of corpus to be used
    (DEFAULT first ghost available).

    Output
    - List of words sorted by relevancy.
    """

    word = request.args.get("word", None)
    is_complete = request.args.get("is_complete", 1, type=int)
    n_gram = request.args.get("n_gram", 1, type=int)
    ghost = request.args.get("ghost", None)

    words = predict(word, is_complete, n_gram, ghost)

    response = make_response(json.dumps(words[:10]))
    response.mimetype = 'application/json'

    return response