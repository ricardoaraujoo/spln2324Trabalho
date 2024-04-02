# Open the file in read mode
with open('SentiLex-lem-PT02_teste.txt', 'r') as file:
    lines = file.readlines()

# Replace spaces with '|'
lines = [line.replace(' ', '|') for line in lines]

# Open the file in write mode and write the modified lines
with open('SentiLex-lem-PT02_teste.txt', 'w') as file:
    file.writelines(lines)