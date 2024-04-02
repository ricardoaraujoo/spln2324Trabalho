import re

# Dicionário para armazenar as ocorrências de POL:...
occurrences = {}

# Abrir o arquivo e percorrer linha por linha
with open('SentiLex-lem-PT02_copy.txt', 'r') as file:
    for line in file:
        # Encontrar todas as ocorrências de POL:... na linha
        matches = re.findall(r'POL:N\d=(-?\d)', line)
        # Contar as ocorrências e atualizar o dicionário
        for match in matches:
            if match in occurrences:
                occurrences[match] += 1
            else:
                occurrences[match] = 1

# Imprimir o dicionário de ocorrências
print("Ocorrências de POL:...")
for key, value in occurrences.items():
    print(f"POL:{key} - {value} ocorrência(s)")
