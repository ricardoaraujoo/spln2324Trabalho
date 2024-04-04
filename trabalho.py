from telnetlib import PRAGMA_HEARTBEAT
from joblib import PrintTime
from numpy import double
import spacy
import re
import matplotlib.pyplot as plt

nlp = spacy.load("pt_core_news_lg")
max_key_length = 8
repeticoes = {}
repeticoes['pos'] = 0
repeticoes['neg'] = 0
repeticoes['neutral'] = 0
repeticoes['boostersINCR'] = 0
repeticoes['boostersDECR'] = 0
repeticoes['negatives'] = 0


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
                sentilex[word] = float(polarities[0])
            elif len(polarities) == 2:
                sentilex[word] = tuple(map(float, polarities))

def preprocess_text(text):
    global max_key_length

    if isinstance(text, list):
        print("true")
        text = ' '.join(text)

    text = text.lower()

    doc = nlp(text)

    with doc.retokenize() as retokenizer:
        for entity in doc.ents:
            retokenizer.merge(entity)

    lemmas_deps = []

    for token in doc:
        if not (token.is_punct or token.is_space):
            lemma = token.lemma_.lower()
            dep = token.dep_
            lemmas_deps.append((lemma, dep))

    # print("\n\nLemmatized_textSplit:\n", lemmatized_textSplit)
    len_lemmas = len(lemmas_deps)
    substitutes = {}
    found = False
    for i in range(len_lemmas):
        for j in range(min(len_lemmas - i, max_key_length), 1, -1):
            lemmas_slice = ' '.join(lemma for lemma, _ in lemmas_deps[i:i+j])
            #print("Lemmas_slice:", lemmas_slice)
            #print("i:", i, "j:", j)
            if lemmas_slice in sentilex: 
                #print("Lemmas_slice Aceitada:", lemmas_slice)
                found = True
                index = i
                break

        if found:
            substitutes[lemmas_slice] = (index)
            lemmas_deps[index] = (lemmas_slice, lemmas_deps[index][1])
            found = False
    
    for lemmas_slice, index in substitutes.items():
        # print("Index:", index,"Lemmas_slice ACEITADA DELETE:", lemmas_slice)

        lemmas_length = len(lemmas_slice.split())
        #print("Lemmas_deps:", lemmas_deps)
        #print("Lemmas_deps length:", len(lemmas_deps))
        for i in range(lemmas_length - 1, 0, -1):
            if index + i < len(lemmas_deps):
                del lemmas_deps[index + i]

    #print(lemmas_deps)

    return lemmas_deps

def calculate_sentiment(lemmas):
    global repeticoes
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
                    polarity = float(sentilex[lemma[0]][1])
                else:
                    #print("v3",sentilex[lemma[0]][0].split('=')[1])
                    polarity = float(sentilex[lemma[0]][0])
            else:
                polarity = float(sentilex[lemma[0]])
                #print("v4",sentilex[lemma[0]].split('=')[1])
            

            sentiment += polarity * multiplier
            #print(lemma[0], "polarity", polarity, "multiplier", multiplier, "sentiment", sentiment)
            multiplier = 1

            if(polarity > 0):
                texto += f"<pos>{lemma[0]}</pos> "
                repeticoes['pos'] += 1
            elif(polarity < 0):
                texto += f"<neg>{lemma[0]}</neg> "
                repeticoes['neg'] += 1
            else:
                texto += f"<neutral>{lemma[0]}</neutral> "
                repeticoes['neutral'] += 1
            
        elif lemma[0] in boosters:
            if multiplier == -1:
                if boosters[lemma[0]] == 'INCR':
                    multiplier = -1.3
                    texto += f"<boostersINCR>{lemma[0]}</boostersINCR> "
                    repeticoes['boostersINCR'] += 1
                else:
                    multiplier = -0.7
                    texto += f"<boostersDECR>{lemma[0]}</boostersDECR> "
                    repeticoes['boostersDECR'] += 1
            else: 
                if boosters[lemma[0]] == 'INCR':
                    multiplier = 1.3
                    texto += f"<boostersINCR>{lemma[0]}</boostersINCR> "
                    repeticoes['boostersINCR'] += 1
                else:
                    multiplier = 0.7
                    texto += f"<boostersDECR>{lemma[0]}</boostersDECR> "
                    repeticoes['boostersDECR'] += 1


        elif lemma[0] in negatives:
            if multiplier == 1.3 or multiplier == 0.7:
                multiplier = 1
            else: 
                multiplier = -1 
            
            texto += f"<negatives>{lemma[0]}</negatives> "
            repeticoes['negatives'] += 1

        else:
            texto += lemma[0] + " "

    return (sentiment,texto)


def divideTexto(text):
    if text == "":
        del(text[-1])
    sentences = re.split(r'[.!?]\s', text)
    if sentences and sentences[-1] == "":
        sentences.pop()

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

    with open('HP.txt', 'r', encoding='utf-8') as arquivo:
        texto = arquivo.read()
    
    textoCapitulos = dividir_por_capitulos(texto)
    
    sentimentoGlobal = 0
    textoFinal= ""
    sentimento_por_capitulo = []
    for i, capitulo in enumerate(textoCapitulos, start=1):
        # print(f"\nCapítulo {i}\n")
        textoFinal += f"\nCapítulo {i}\n"
        sentimentoInterno = 0
        for sentence in divideTexto(capitulo):
            
            lemmas = preprocess_text(sentence)
            sentimento_capitulo = calculate_sentiment(lemmas)
            (sentimentoTEXTO,texto) = sentimento_capitulo
            sentimentoInterno += sentimentoTEXTO
            textoFinal += f"{texto}\n"
        print(f"\nCapítulo {i}  {sentimentoInterno}\n")
        sentimento_por_capitulo.append(sentimentoInterno)
        sentimentoGlobal += sentimentoInterno

        
    # Abrir o arquivo para escrita
    with open('histograma.png', 'wb') as ficheiro:

        plt.figure(figsize=(10, 6))
        plt.bar(range(1, len(sentimento_por_capitulo) + 1), sentimento_por_capitulo, color='skyblue')
        plt.xlabel('Capítulo')
        plt.ylabel('Sentimento')
        plt.title('Sentimento por Capítulo em Harry Potter')
        plt.xticks(range(1, len(sentimento_por_capitulo) + 1))  
        plt.yticks(range(-60, int(max(sentimento_por_capitulo)) + 1, 10)) 
        plt.grid(True)
        plt.savefig(ficheiro)  
        plt.show()


    
    print("Texto global:", textoFinal)
    print(f"Sentimento Global: {sentimentoGlobal}")

def textoExemplo():
    text = """ Eu adoro jogar à bola com os meus amigos.

    O meu cão é muito brincalhão e adora correr no parque.

    O tempo está muito mau e não consigo sair de casa.

    O meu irmão é muito chato e não me deixa brincar com os meus brinquedos.

    A minha mãe fez um bolo delicioso e eu comi uma fatia inteira.

    O meu pai está sempre a trabalhar e não tem tempo para brincar comigo.

    A minha avó é muito simpática e faz-me sempre festinhas na cabeça.

    O meu gato é muito preguiçoso e passa o dia a dormir no sofá.

    O presidente nunca volta com o palavra atrás na TV.

    O João é um rapaz muito simpático e ajuda sempre os outros e não para de tocar na minha campainha.
"""
    
    textoFinal = "" 
    sentimentoGlobal = 0
    textoDividido = divideTexto(text)
    i=1
    for sentences in textoDividido:
        textoFinal += f"\nFrase {i}\n"
        i+=1
        lemmas = preprocess_text(sentences)

        (sentimentoFrase,textoFrase) = calculate_sentiment(lemmas)
        sentimentoGlobal += sentimentoFrase
        textoFinal += f"\n {textoFrase} \n"
    print(textoFinal)
    print(sentimentoGlobal)

def main():
    #textoExemplo()
    HarryPotter()
    print(repeticoes)


if __name__ == "__main__":
    main()