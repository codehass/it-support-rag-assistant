import joblib
import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings


class ClusterModel:
    def __init__(self, model_path: str):
        self.kmeans = joblib.load(f"{model_path}/it_support_clusters.joblib")
        self.pca = joblib.load(f"{model_path}/pca_transformer.joblib")
        self.embedding_function = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5"
        )

    def predict_cluster(self, question: str) -> int:
        """Predicts the cluster ID for a single input string."""
        if not question.strip():
            return -1

        new_vector = self.embedding_function.embed_query(question)

        input_data = np.array(new_vector).reshape(1, -1)
        reduced_vector = self.pca.transform(input_data)
        cluster_id = self.kmeans.predict(reduced_vector)

        return int(cluster_id[0])


#  Example
# cluster = ClusterModel(model_path="ml/model")

# question = "How do I fix a blue screen?"
# cluster_id = cluster.predict_cluster(question)
# print(f"Cluster ID for the question '{question}': {cluster_id}")
