from textblob import TextBlob

msg = "dont make angry which is the best premium"
blob = TextBlob(msg)
print(f"Message: {msg}")
print(f"Polarity: {blob.sentiment.polarity}")
print(f"Subjectivity: {blob.sentiment.subjectivity}")
