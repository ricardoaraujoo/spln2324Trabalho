import spacy

nlp = spacy.load('pt_core_news_lg')  # Load the Portuguese language model

# Read the file into a list of lines
with open('SentiLex-lem-PT02_copy.txt', 'r') as file:
    lines = file.readlines()

# Process each line
for i in range(len(lines)):
    fields = lines[i].strip().split(';')
    if len(fields) >= 4:
        words = fields[0].split('.')[0]
        lemmas = ' '.join([token.lemma_ for token in nlp(words)])  # Lemmatize the words
        fields[0] = lemmas + fields[0][len(words):]  # Replace the words with their lemmas
        lines[i] = ';'.join(fields) + '\n'  # Join the fields back into a line

# Write the processed lines back to the file
with open('SentiLex-lem-PT02_copy.txt', 'w') as file:
    file.writelines(lines)