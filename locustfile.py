from locust import HttpUser, task, between
import random
import urllib.parse

# Load queries
with open("query_set.txt", "r", encoding="utf-8") as f:
    queries = [line.strip() for line in f if line.strip()]

class IMDbUser(HttpUser):
    wait_time = between(1, 2)  # simulates user delay

    @task
    def search_movie(self):
        query = random.choice(queries)
        encoded_query = urllib.parse.quote(query)  # <-- URL-encode
        self.client.get(f"/search?title={encoded_query}")
