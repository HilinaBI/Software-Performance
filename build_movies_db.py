import sqlite3
import pandas as pd
import os

# Base path
base_path = r"C:\Users\hp\Desktop\MA\2nd semester\performance\project\Dataset"

# Load IMDb data
basics = pd.read_csv(os.path.join(base_path, "title.basics.tsv"), sep='\t', dtype=str, na_values='\\N')
ratings = pd.read_csv(os.path.join(base_path, "title.ratings.tsv"), sep='\t', dtype=str, na_values='\\N')

# Filter for movies
movies = basics[(basics['titleType'] == 'movie') & basics['primaryTitle'].notna()]
movies = movies[['tconst', 'primaryTitle', 'startYear', 'runtimeMinutes', 'genres']]

# Merge with ratings
movies = movies.merge(ratings, on='tconst', how='left')
movies['averageRating'] = movies['averageRating'].astype(float)
movies['numVotes'] = pd.to_numeric(movies['numVotes'], errors='coerce').fillna(0).astype(int)

# Filter top 1000 by votes
movies = movies.sort_values(by='numVotes', ascending=False).head(1000)
top_tconsts = set(movies['tconst'])

# --- Read principals in chunks ---
chunks = []
principal_path = os.path.join(base_path, "title.principals.tsv")
cols = ['tconst', 'nconst', 'category']
for chunk in pd.read_csv(principal_path, sep='\t', dtype=str, na_values='\\N', usecols=cols, chunksize=100_000):
    filtered = chunk[chunk['tconst'].isin(top_tconsts) & chunk['category'].isin(['actor', 'actress', 'director', 'writer'])]
    chunks.append(filtered)

principals = pd.concat(chunks, ignore_index=True)

# Load names
names = pd.read_csv(os.path.join(base_path, "name.basics.tsv"), sep='\t', dtype=str, na_values='\\N')

# Merge with names
merged = principals.merge(names[['nconst', 'primaryName']], on='nconst', how='left')

# Group by tconst and category
grouped = merged.groupby(['tconst', 'category'])['primaryName'] \
    .apply(lambda x: ', '.join(x.dropna().unique()[:3])).unstack(fill_value='')

# Merge back to movies
movies = movies.merge(grouped, on='tconst', how='left')

# Combine actors + actress
movies['actors'] = movies[['actor', 'actress']].fillna('').agg(', '.join, axis=1).str.strip(', ')
movies['directors'] = movies['director'].fillna('')
movies['writers'] = movies['writer'].fillna('')

# Drop temp columns
movies.drop(columns=['actor', 'actress', 'director', 'writer'], errors='ignore', inplace=True)

# Final columns
movies = movies[['primaryTitle', 'startYear', 'averageRating', 'numVotes', 'runtimeMinutes', 'genres', 'actors', 'directors', 'writers']]

# Create DB
conn = sqlite3.connect("movies.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS movies")
cursor.execute("""
    CREATE TABLE movies (
        primaryTitle TEXT,
        startYear INTEGER,
        averageRating REAL,
        numVotes INTEGER,
        runtimeMinutes INTEGER,
        genres TEXT,
        actors TEXT,
        directors TEXT,
        writers TEXT
    )
""")

# Insert rows
movie_rows = [
    (
        row['primaryTitle'],
        int(row['startYear']) if pd.notna(row['startYear']) else None,
        row['averageRating'],
        row['numVotes'],
        int(row['runtimeMinutes']) if pd.notna(row['runtimeMinutes']) else None,
        row['genres'],
        row['actors'],
        row['directors'],
        row['writers']
    )
    for _, row in movies.iterrows()
]

cursor.executemany("""
    INSERT INTO movies VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", movie_rows)

conn.commit()
conn.close()

print("✅ DB created successfully with writers included (memory-safe)!")
