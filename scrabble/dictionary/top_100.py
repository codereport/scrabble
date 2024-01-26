
import re
from collections import Counter

def get_words(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read().lower()  # Convert to lowercase for case-insensitive counting
        words = re.findall(r'\b\w+\b', text)
    return words

def print_top_words(file_path, top_count=100):
    words = get_words(file_path)
    word_count = Counter(words)
    top_words = word_count.most_common(top_count)

    print(f"Top {top_count} words by frequency:")
    for word, count in top_words:
        print(f"{word}: {count}")

if __name__ == "__main__":
    file_path = input("Enter the path to the file: ")
    print_top_words(file_path)
