import os

import joblib
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class SemanticRecommender:
    """
    Loads dataset, builds embeddings for career items, and exposes a recommend() method.
    Can be saved and loaded using joblib for persistence.
    """

    def __init__(self, df: pd.DataFrame, model_name="all-MiniLM-L6-v2"):
        self.df = df
        self.model_name = model_name
        self.cache_dir = "cache"
        os.makedirs(self.cache_dir, exist_ok=True)

        self.df["combined_text"] = self.df.apply(
            lambda row: " ".join(
                [
                    str(row.get("description", "")),
                    str(row.get("skills", "")),
                    str(row.get("personality_match", "")),
                ]
            ),
            axis=1,
        )

        print("Loading sentence-transformers model:", self.model_name)
        self.model = SentenceTransformer(self.model_name)

        self.embeddings_path = os.path.join(self.cache_dir, "career_embeddings.npy")
        self.titles_path = os.path.join(self.cache_dir, "career_titles.pkl")

        if os.path.exists(self.embeddings_path) and os.path.exists(self.titles_path):
            try:
                self.career_embeddings = np.load(self.embeddings_path)
                self.career_titles = joblib.load(self.titles_path)
                if len(self.career_embeddings) != len(self.df):
                    raise ValueError("Cached embeddings length mismatch; recomputing.")
                print("Loaded cached career embeddings.")
            except Exception as e:
                print("Failed to load cache - recomputing embeddings:", e)
                self._compute_and_cache_embeddings()
        else:
            self._compute_and_cache_embeddings()

    def _compute_and_cache_embeddings(self):
        texts = self.df["combined_text"].tolist()
        print(f"Computing embeddings for {len(texts)} careers...")
        self.career_embeddings = self.model.encode(
            texts, show_progress_bar=True, convert_to_numpy=True
        )
        np.save(self.embeddings_path, self.career_embeddings)
        joblib.dump(self.df["career_title"].tolist(), self.titles_path)
        print("Saved career embeddings to cache.")

    def recommend(self, quiz_answers_text: str, top_n: int = 5):
        user_emb = self.model.encode([quiz_answers_text], convert_to_numpy=True)
        sims = cosine_similarity(user_emb, self.career_embeddings)[0]
        top_idx = sims.argsort()[-top_n:][::-1]

        recommendations = []
        for idx in top_idx:
            row = self.df.iloc[idx]
            item = {
                "career_title": row["career_title"],
                "description": row.get("description", ""),
                "skills": row.get("skills", ""),
                "personality_match": row.get("personality_match", ""),
                "education_required": row.get("education_required", ""),
                "average_salary_usd": float(row.get("average_salary_usd", 0) or 0),
                "job_outlook": row.get("job_outlook", ""),
                "learning_resources": row.get("learning_resources", ""),
                "similarity_score": float(sims[idx]),
            }
            recommendations.append(item)
        return recommendations


data = pd.read_csv(r"C:\Users\ayemi\Documents\CareerHub\data\careers.csv")
recommender = SemanticRecommender(data)


def get_recommendations(quiz_answers_text: str, top_n: int = 5):
    return recommender.recommend(quiz_answers_text, top_n)
