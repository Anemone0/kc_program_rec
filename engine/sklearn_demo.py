#!/usr/bin/env python
# -*-coding=utf-8-*-
import nltk, string
from sklearn.feature_extraction.text import TfidfVectorizer

stemmer = nltk.stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)


def stem_tokens(tokens):
    return [stemmer.stem(item) for item in tokens]


'''remove punctuation, lowercase, stem'''


def normalize(text):
    vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))

def cosine_sim(text1, text2):
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([text1, text2])
    print ((tfidf * tfidf.T).A)
    return ((tfidf * tfidf.T).A)[0, 1]


print cosine_sim('a little bird', 'a little bird')
print cosine_sim('a little bird', 'a little bird chirps')
print cosine_sim('a little bird', 'a big dog barks')

# if __name__ == '__main__':
#     pass
