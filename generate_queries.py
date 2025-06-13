import sqlite3
import random
import numpy as np

# Connect to the movies.db
conn = sqlite3.connect("movies.db")
cursor = conn.cursor()

# Fetch all movie titles and their vote counts
cursor.execute("SELECT primaryTitle, numVotes FROM movies")
rows = cursor.fetchall()
conn.close()

# Separate titles and vote counts
titles = [row[0] for row in rows]
votes = [row[1] for row in rows]

# Normalize vote counts into probabilities
total_votes = sum(votes)
probabilities = [v / total_votes for v in votes]

# Sample 10,000 titles with replacement, weighted by vote count
sampled_titles = np.random.choice(titles, size=10000, replace=True, p=probabilities)

# Save to file
with open("query_set.txt", "w", encoding="utf-8") as f:
    for title in sampled_titles:
        f.write(f"{title}\n")

print("✅ 10,000 movie queries saved to 'query_set.txt'")
