from flask import Flask, request, jsonify
import nltk
import networkx as nx
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import numpy as np

nltk.download('stopwords')
nltk.download('punkt')

app = Flask(__name__)

def read_article(text):
    sentences = nltk.sent_tokenize(text)
    return [nltk.word_tokenize(sentence) for sentence in sentences]

def sentence_similarity(sent1, sent2, stop_words=None):
    if stop_words is None:
        stop_words = []

    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]

    all_words = list(set(sent1 + sent2))

    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)

    for w in sent1:
        if w in stop_words:
            continue
        vector1[all_words.index(w)] += 1

    for w in sent2:
        if w in stop_words:
            continue
        vector2[all_words.index(w)] += 1

    return 1 - cosine_distance(vector1, vector2)

def build_similarity_matrix(sentences, stop_words):
    similarity_matrix = np.zeros((len(sentences), len(sentences)))

    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1 != idx2:
                similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2], stop_words)

    return similarity_matrix

def generate_summary(text, top_n=5):
    stop_words = stopwords.words('english')
    summarize_text = []

    sentences = read_article(text)

    sentence_similarity_martix = build_similarity_matrix(sentences, stop_words)

    sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_martix)
    scores = nx.pagerank(sentence_similarity_graph)

    ranked_sentence = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)

    for i in range(top_n):
        summarize_text.append(" ".join(ranked_sentence[i][1]))

    return " ".join(summarize_text)

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    text = data.get('text', '')
    number = data.get('number', '')
    number = int(number)
    summary = generate_summary(text,number)
    return jsonify({'summary': summary})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
