import os
import sys

print("Checking imports...")
try:
    import PyPDF2
    print("PyPDF2 imported successfully")
except ImportError as e:
    print(f"Failed to import PyPDF2: {e}")

try:
    from docx import Document
    print("python-docx imported successfully")
except ImportError as e:
    print(f"Failed to import python-docx: {e}")

try:
    import textblob
    print("textblob imported successfully")
except ImportError as e:
    print(f"Failed to import textblob: {e}")

print("Checking textblob corpora...")
try:
    from textblob import TextBlob
    blob = TextBlob("This is a test.")
    print(f"TextBlob sentiment: {blob.sentiment}")
except Exception as e:
    print(f"TextBlob error: {e}")

print("Done.")
