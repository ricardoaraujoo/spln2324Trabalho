from leia import SentimentIntensityAnalyzer 

s = SentimentIntensityAnalyzer()

# Read the text file
with open('HP.txt', 'r', encoding='utf-8') as file:
    text = file.read()

# Apply sentiment analysis
result = s.polarity_scores(text)

# Print the result
print(result)