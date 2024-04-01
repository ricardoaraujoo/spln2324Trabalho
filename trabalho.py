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
    lemmas_deps = [(token.lemma_.lower(), token.dep_) for token in doc if not token.is_punct]
    print(lemmas_deps)
    # Convert the lemmatized tokens back into a string
    lemmatized_text = ' '.join([lemma for lemma, dep in lemmas_deps])

    # Check for each key in the sentilex dictionary in the lemmatized text
    for key in sentilex:
        if ' ' in key and key in lemmatized_text:
            print("Key found:", key)
            # Replace the lemma with the key
            key_lemmas = key.split()
            print("Key lemmas:", key_lemmas)
            index = lemmatized_text.split().index(key_lemmas[0])
            lemmas_deps[index] = (key, lemmas_deps[index][1])
            print("Index:", index)
            print("key LENGTH:", len(key_lemmas))

            # Remove the next n-1 lemmas, where n is the number of words in the key
            print("Lemmas_deps:", lemmas_deps)
            print("Lemmas_deps length:", len(lemmas_deps))
            for i in range(len(key_lemmas) - 1, 0, -1):
                if index + i < len(lemmas_deps):
                    del lemmas_deps[index + i]

    print(lemmas_deps)

    return lemmas_deps

def calculate_sentiment(lemmas):
    texto = ""
    sentiment = 0
    multiplier = 1
    for lemma in lemmas:
        
        if lemma[0] in sentilex:
            
            #print(sentilex[lemma[0]])
            #Se tem 1 ou 2 polaridades(N0 e N1)
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

            if(polarity > 0):
                texto += f"<pos>{lemma[0]}</pos> "
            elif(polarity < 0):
                texto += f"<neg>{lemma[0]}</neg> "
            else:
                texto += f"<neutral>{lemma[0]}</neutral> "
            
        elif lemma[0] in boosters:
            if multiplier == -1:
                multiplier = 1
                texto += f"<boosters>{lemma[0]}</boosters> "
            else: 
                if boosters[lemma[0]] == 'INCR':
                    multiplier = 2
                    texto += f"<boostersINCR>{lemma[0]}</boostersINCR> "
                else:
                    multiplier = 0.5
                    texto += f"<boostersDECR>{lemma[0]}</boostersDECR> "


        elif lemma[0] in negatives:
            if multiplier == 2:
                multiplier = 1
            else: 
                multiplier = -1
            
            texto += f"<negatives>{lemma[0]}</negatives> "


        else:
            texto += lemma[0] + " "

    return (sentiment,texto)


def divideTexto(text):
    sentences = nltk.sent_tokenize(text)
    return sentences


def main():
    textoFinal = ""
    text = """Que dia maravilhoso! O sol está brilhando, o céu está azul e estou rodeado de pessoas queridas. 
        Sinto-me extremamente feliz e grato por tudo o que tenho e correr a toque de caixa LOL. 
        Este é o tipo de dia que me faz acreditar no poder da felicidade e na beleza da vida e doido varrido e."""

    sentimentoGlobal = 0
    textoDividido = divideTexto(text)
    for sentences in textoDividido:
        lemmas = preprocess_text(sentences)

        (sentimentoFrase,textoFrase) = calculate_sentiment(lemmas)
        sentimentoGlobal += sentimentoFrase
        textoFinal += textoFrase

    print(sentimentoGlobal)
    print(textoFinal)

if __name__ == "__main__":
    main()