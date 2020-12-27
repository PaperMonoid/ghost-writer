import os


from ghost import GHOST_DIRECTORY, ghost_list


def document_stream(ghost):
    for filename in os.listdir(GHOST_DIRECTORY):
        path = os.path.join(GHOST_DIRECTORY, filename)
        if os.path.isdir(path) and filename == ghost:
            for subfilename in os.listdir(path):
                subpath = os.path.join(path, subfilename)
                if os.path.isfile(subpath):
                    yield subpath


def is_whitespace(character):
    return character == ' ' or character == '\t' or character == '\n'


def is_valid(character):
    return ord(character) < 0xFF and character.isprintable()


def is_punctuation(character):
    return character in '.,:;"\'-+=()[]{}¿?¡!'


def character_stream(document):
    with open(document, 'r', encoding='utf-8') as document_file:
        character = document_file.read(1)
        while character:
            yield character
            character = document_file.read(1)


def word_stream(document):
    word = ''

    for character in character_stream(document):
        character = character.lower()
        if is_whitespace(character) and word is not '':
            yield word
            word = ''
        elif is_punctuation(character):
            if word is not '':
                yield word
                word = ''
            yield character
        elif not is_whitespace(character) and is_valid(character):
            word += character

    if word is not '':
        yield word


def term_stream(document, n_gram):
    terms = []

    for word in word_stream(document):
        terms.append(word)

        if len(terms) >= 2 * n_gram:
            first = terms[:len(terms)//2]
            second = terms[len(terms)//2:]
            yield (' '.join(first), ' '.join(second))
            terms = second
