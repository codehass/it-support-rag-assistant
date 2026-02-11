import os
import time

import joblib
import numpy as np
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings

import mlflow

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")


class ClusterModel:
    def __init__(self, model_path: str):
        self.model_path = model_path

        self.kmeans = joblib.load(f"{model_path}/it_support_clusters.joblib")
        self.pca = joblib.load(f"{model_path}/pca_transformer.joblib")

        self.embedding_model_name = "BAAI/bge-small-en-v1.5"
        self.embedding_function = HuggingFaceEmbeddings(
            model_name=self.embedding_model_name,
            model_kwargs={"token": HF_TOKEN},
        )

    def predict_cluster(self, question: str) -> int:
        if not question.strip():
            return -1

        with mlflow.start_run(run_name="cluster_prediction", nested=True):
            mlflow.log_param("embedding_model", self.embedding_model_name)
            mlflow.log_param("model_path", self.model_path)
            mlflow.log_text(question, "input_question.txt")

            start = time.time()
            new_vector = self.embedding_function.embed_query(question)
            input_data = np.array(new_vector).reshape(1, -1)
            reduced_vector = self.pca.transform(input_data)
            cluster_id = self.kmeans.predict(reduced_vector)
            latency = time.time() - start

            mlflow.log_metric("latency_sec", latency)
            mlflow.log_metric("predicted_cluster", int(cluster_id[0]))

            return int(cluster_id[0])


#  Example
# cluster = ClusterModel(model_path="ml/model")

# question = "How do I fix a blue screen?"
# cluster_id = cluster.predict_cluster(question)
# print(f"Cluster ID for the question '{question}': {cluster_id}")
