import spacy
import nltk
import os
import re

# Load Portuguese language model
nlp = spacy.load("pt_core_news_lg")

boosters = {}
for boost in open('booster.txt','r', encoding='utf-8'):
    parts = boost.strip().split(' ')
    boosters[' '.join(parts[:-1])] = parts[-1]


negatives = []
for negative in open('negative.txt','r', encoding='utf-8'):
    negatives.append(negative.strip())

sentilex = {}
with open('SentiLex-lem-PT02_copy.txt', 'r', encoding='utf-8') as file:
    for line in file:
        fields = line.strip().split(';')
        if len(fields) >= 4:
            word = fields[0].split('.')[0]
            polarities = [field.split('=')[1] for field in fields if field.startswith('POL')]
            if len(polarities) == 1:
                sentilex[word] = int(polarities[0])
            elif len(polarities) == 2:
                sentilex[word] = tuple(map(int, polarities))


def preprocess_text(text):
    if isinstance(text, list):  # Verifica se text é uma lista
        # Se for uma lista, junte os elementos em uma única string
        text = ' '.join(text)

    # Lowercase the text
    text = text.lower()

    # Tokenize the text
    doc = nlp(text)

    with doc.retokenize() as retokenizer:
        for entity in doc.ents:
            retokenizer.merge(entity)

    # Lemmatize the words, get their dependency relations, and exclude punctuation
    lemmas_deps = [(token.lemma_.lower(), token.dep_) for token in doc if not (token.is_punct or token.is_space)]
    print("OG: ",lemmas_deps)
    # Convert the lemmatized tokens back into a string
    lemmatized_text = ' '.join([lemma for lemma, dep in lemmas_deps])
    lemmatized_textSplit = lemmatized_text.split()
    # Check for each key in the sentilex dictionary in the lemmatized text
    for key in sentilex:
        if ' ' in key: 
            key_lemmas = key.split()
            for i in range(len(lemmatized_textSplit) - len(key_lemmas) + 1):
                if key_lemmas == lemmatized_textSplit[i:i+len(key_lemmas)]:
            
                    # Replace the lemma with the key
                    print("Key lemmas:", key_lemmas)
                    print("Lemmatized text:", lemmatized_textSplit.index(key_lemmas[0]))
                    index = lemmatized_textSplit.index(key_lemmas[0])
                    print("Index:", index)
                    lemmas_deps[index] = (key, lemmas_deps[index][1])
                    
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
            #print(lemma[0], "XXXXXXX")
            #print(sentilex[lemma[0]])
            #Se tem 1 ou 2 polaridades(N0 e N1)
            if type(sentilex[lemma[0]]) == tuple:
                if lemma[1] == 'obj' or lemma[1] == "dobj":
                    #print("v1",sentilex[lemma[0]][1].split('=')[1])
                    polarity = int(sentilex[lemma[0]][1])
                else:
                    #print("v3",sentilex[lemma[0]][0].split('=')[1])
                    polarity = int(sentilex[lemma[0]][0])
            else:
                polarity = int(sentilex[lemma[0]])
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
    sentences = re.split(r'[.!?]\s', text)
    print("Sentences:", sentences)
    return sentences


def dividir_por_capitulos(texto):
    capitulos = []
    capitulo_atual = None
    
    for linha in texto.split('\n'):
        if linha.startswith('#'):
            if capitulo_atual:
                capitulos.append(capitulo_atual)
            capitulo_atual = linha + '\n'
        elif capitulo_atual is not None:
            if not capitulo_atual.endswith('\n'):
                capitulo_atual += '\n'
            capitulo_atual += linha + '\n'
    
    if capitulo_atual:
        capitulos.append(capitulo_atual)
    
    return [capitulo.split('\n', 1)[1] for capitulo in capitulos]

def HarryPotter():

    
    # Leitura do arquivo e divisão por capítulos
    with open('HP.txt', 'r', encoding='utf-8') as arquivo:
        texto = arquivo.read()
    
    textoCapitulos = dividir_por_capitulos(texto)
    
    # Cálculo do sentimento para cada capítulo
    sentimentoGlobal = 0
    textoFinal= ""
    for i, capitulo in enumerate(textoCapitulos, start=1):
        textoDividido = divideTexto(capitulo)
        lemmas = preprocess_text(textoDividido)

        sentimento_capitulo = calculate_sentiment(lemmas)
        print(f"Sentimento do Capítulo {i}: {sentimento_capitulo}")
        (sentimentoTEXTO,texto) = sentimento_capitulo
        sentimentoGlobal += sentimentoTEXTO
        textoFinal += texto
    # Exibição do sentimento global
    print(f"Sentimento Global: {sentimentoGlobal}")
    print("Texto global:", texto)

def textoExemplo():
    text = """Este é o tipo de dia que me faz acreditar no poder da felicidade e na beleza da vida e doido varrido e."""
    
    textoFinal = ""
    sentimentoGlobal = 0
    textoDividido = divideTexto(text)
    for sentences in textoDividido:
        lemmas = preprocess_text(sentences)

        (sentimentoFrase,textoFrase) = calculate_sentiment(lemmas)
        sentimentoGlobal += sentimentoFrase
        textoFinal += textoFrase
    print(textoFinal)
    print(sentimentoGlobal)

def main():
    textoExemplo()
    #HarryPotter()

if __name__ == "__main__":
    main()