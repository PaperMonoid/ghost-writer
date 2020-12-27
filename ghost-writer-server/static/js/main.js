let writer = document.getElementById('writer');
let suggestion = document.getElementById('suggestion');
let lastWord = document.getElementById('lastWord');
let backend = document.getElementById('backend');


let n_gram = 1;
let suggestionResponse = [''];
let suggestionResponseIndex = 0;



function isWhitespace(character) {
    return character == ' ' || character == '\t' || character == '\n';
}


function isASCII(character) {
    return /^[\x00-\xFF]*$/.test(character);
}


function isPunctuation(character) {
    return '.,:;"\'-+=()[]{}¿?¡!'.indexOf(character) > -1;
}


function* getWords(text) {
    let word = '';

    for (let character of text) {
        if (isWhitespace(character) && word != '') {
            yield word;
            word = '';
        } else if (isPunctuation(character)) {
            if (word != '') {
                yield word;
                word = '';
            }
            yield character;
        } else if (!isWhitespace(character) && isASCII(character)) {
            word += character;
        }
    }

    if (word != '') {
        yield word;
    }
}

function getLastWord(n_gram) {
    allWords = Array.from(getWords(writer.value));
    return allWords.slice(-n_gram).join(' ');
}


writer.addEventListener("input", function (e) {
    if (writer.value.length && writer.value[writer.value.length - 1] == ' ') {
        // complete
        lastWord.value = getLastWord(n_gram);
        fetch(`/markov_predict?word=${lastWord.value}&is_complete=1&n_gram=${n_gram}&ghost=${backend.value}`)
            .then(response => response.json())
            .then(data => {
                suggestionResponseIndex = 0;
                suggestionResponse = data;
                suggestion.value = writer.value + suggestionResponse[suggestionResponseIndex];
            });
    } else {
        // incomplete
        lastWord.value = getLastWord(n_gram);
        fetch(`/markov_predict?word=${lastWord.value}&is_complete=0&n_gram=${n_gram}&ghost=${backend.value}`)
            .then(response => response.json())
            .then(data => {
                suggestionResponseIndex = 0;
                suggestionResponse = data;

                let lastWordIndex = suggestionResponse[suggestionResponseIndex].indexOf(lastWord.value);
                console.log(lastWordIndex);
                if (lastWordIndex > -1) {
                    suggestion.value = writer.value + suggestionResponse[suggestionResponseIndex].slice(lastWord.value.length);
                } else {
                    suggestion.value = writer.value + ' ' + suggestionResponse[suggestionResponseIndex];
                }
            });
        //suggestion.value = writer.value + ' ' + suggestionResponse[0];
    }
});

writer.addEventListener("keydown", function (e) {
    /**
     * keyCode 9 = TAB
     * keyCode 13 = ENTER
     * keyCode 32 = SPACE
     */
    console.log(e.keyCode);
    if (e.keyCode == 9) {
        e.preventDefault();
        suggestion.value = writer.value + ' ' + suggestionResponse[suggestionResponseIndex++];
        //writer.value = suggestion.value;
    } else if (e.keyCode == 13) {
        e.preventDefault();
        writer.value = suggestion.value;
    }


    if (writer.value.length &&
        (writer.value[writer.value.length - 1] == ' ' ||
            writer.value[writer.value.length - 1] == '\n')
    ) {
        if (e.keyCode == 13) {
            e.preventDefault();
        }
    }
});