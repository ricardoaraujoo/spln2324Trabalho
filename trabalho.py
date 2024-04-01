import spacy
import nltk
import os
nltk.download('punkt')

# Load Portuguese language model
nlp = spacy.load("pt_core_news_lg")

boosters = {}
for boost in open('booster.txt'):
    parts = boost.strip().split(' ')
    boosters[' '.join(parts[:-1])] = parts[-1]


negatives = []
for negative in open('negative.txt'):
    negatives.append(negative.strip())

sentilex = {}
with open('SentiLex-lem-PT02.txt', 'r') as file:
    for line in file:
        fields = line.strip().split(';')
        if len(fields) == 5:
            sentilex[fields[0].split('.')[0]] = (fields[2], fields[3])
        elif len(fields) == 4:
            sentilex[fields[0].split('.')[0]] = fields[2]

def preprocess_text(text):
    # Lowercase the text
    text = text.lower()

    # Tokenize the text
    doc = nlp(text)

    with doc.retokenize() as retokenizer:
        for entity in doc.ents:
            retokenizer.merge(entity)

    # Lemmatize the words, get their dependency relations, and exclude punctuation
    lemmas_deps = [(token.lemma_, token.dep_) for token in doc if not token.is_punct]

    return lemmas_deps

def calculate_sentiment(lemmas):
    sentiment = 0
    multiplier = 1
    for lemma in lemmas:

        if lemma[0] in sentilex:
            
            #print(sentilex[lemma[0]])
            if type(sentilex[lemma[0]]) == tuple:
                if lemma[1] == 'obj' or lemma[1] == "dobj":
                    #print("v1",sentilex[lemma[0]][1].split('=')[1])
                    polarity = int(sentilex[lemma[0]][1].split('=')[1])
                else:
                    #print("v3",sentilex[lemma[0]][0].split('=')[1])
                    polarity = int(sentilex[lemma[0]][0].split('=')[1])
            else:
                polarity = int(sentilex[lemma[0]].split('=')[1])
                #print("v4",sentilex[lemma[0]].split('=')[1])

            # Aplica o multiplicador à polaridade
            sentiment += polarity * multiplier
            #print(lemma[0], "polarity", polarity, "multiplier", multiplier, "sentiment", sentiment)
            multiplier = 1

            
        if lemma[0] in boosters:
            if multiplier == -1:
                multiplier = 1
            else: 
                if boosters[lemma[0]] == 'INCR':
                    multiplier = 2
                else:
                    multiplier = 0.5

        if lemma[0] in negatives:
            if multiplier == 2:
                multiplier = 1
            else: 
                multiplier = -1

    return sentiment


def divideTexto(text):

    sentences = nltk.sent_tokenize(text)

    
    
    return sentences


def main():
    text = """Que dia maravilhoso! O sol está brilhando, o céu está azul e estou rodeado de pessoas queridas. 
        Sinto-me extremamente feliz e grato por tudo o que tenho. 
        Este é o tipo de dia que me faz acreditar no poder da felicidade e na beleza da vida."""

    sentimentoGlobal = 0
    textoDividido = divideTexto(text)
    for sentences in textoDividido:
        lemmas = preprocess_text(sentences)
        sentimentoGlobal += calculate_sentiment(lemmas)
    print(sentimentoGlobal)

if __name__ == "__main__":
    main()