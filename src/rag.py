from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class LocalRAG:
    def __init__(self, path="data/knowledge_base.txt"):
        self.text = Path(path).read_text(encoding="utf-8")
        self.chunks = [x.strip() for x in self.text.split("\n\n") if x.strip()]
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform(self.chunks)

    def retrieve(self, query, k=3):
        q = self.vectorizer.transform([query])
        scores = cosine_similarity(q, self.matrix).ravel()
        idx = scores.argsort()[::-1][:k]
        return [(self.chunks[i], float(scores[i])) for i in idx if scores[i] > 0]
