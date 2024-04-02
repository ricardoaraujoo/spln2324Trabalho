from LeIA.leia import SentimentIntensityAnalyzer 
from vaderSentiment.vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer as Vader

s_english = Vader()
s = SentimentIntensityAnalyzer()

def analyze_chapters():
    for i in range(1, 18):
            file_path = f'HP/capitulo_{i}.txt'
            # Ler o arquivo de texto do capítulo
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            # Aplicar a análise de sentimento
            result = s.polarity_scores(text)
            # Imprimir os resultados
            print(f"Resultados do Capítulo {i}:")
            print(result)
            print()  # Adiciona uma linha em branco para separar os resultados dos capítulos


def analyze_full_book():
    # Ler o arquivo de texto
    with open('HP.txt', 'r', encoding='utf-8') as file:
        text = file.read()
    # Aplicar a análise de sentimento
    result = s.polarity_scores(text)
    # Imprimir o resultado
    print(f"Resultado do Livro completo:")
    print(result)
    print()  # Adiciona uma linha em branco para separar os resultados dos capítulos

def analyze_full_book_english():
    # Ler o arquivo de texto
    with open('HP_Eng.txt', 'r', encoding='utf-8') as file:
        text = file.read()
    # Aplicar a análise de sentimento
    result = s_english.polarity_scores(text)
    # Imprimir o resultado
    print(f"Resultado do Livro completo em Ingles:")
    print(result)
    print()  # Adiciona uma linha em branco para separar os resultados dos capítulos


def main():
    #analyze_chapters()
    analyze_full_book()
    analyze_full_book_english()

if __name__ == "__main__":
    main()