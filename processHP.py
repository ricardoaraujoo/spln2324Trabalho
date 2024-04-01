import os

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

def salvar_capitulos(capitulos):
    if not os.path.exists('HP'):
        os.makedirs('HP')
        
    for i, capitulo in enumerate(capitulos, start=1):
        nome_arquivo = f"HP/capitulo_{i}.txt"
        with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
            arquivo.write(capitulo)

with open('HP.txt', 'r', encoding='utf-8') as arquivo:
    texto = arquivo.read()

capitulos = dividir_por_capitulos(texto)
salvar_capitulos(capitulos)
