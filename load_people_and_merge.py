import pandas as pd
import os
import sqlite3

dataset_path = r"C:\Users\hp\Desktop\MA\2nd semester\performance\project\Dataset"

# Load smaller datasets normally
titles = pd.read_csv(os.path.join(dataset_path, "title.basics.tsv"), sep='\t', na_values='\\N', low_memory=False)
ratings = pd.read_csv(os.path.join(dataset_path, "title.ratings.tsv"), sep='\t', na_values='\\N')
movies = titles[titles['titleType'] == 'movie'].merge(ratings, on='tconst')

names = pd.read_csv(os.path.join(dataset_path, "name.basics.tsv"), sep='\t', na_values='\\N', low_memory=False)
crew = pd.read_csv(os.path.join(dataset_path, "title.crew.tsv"), sep='\t', na_values='\\N')

# Load principals in chunks and filter for actors/actresses while reading
chunk_list = []
chunk_size = 100000

print("Loading title.principals.tsv in chunks...")

for chunk in pd.read_csv(os.path.join(dataset_path, "title.principals.tsv"),
                         sep='\t', na_values='\\N', low_memory=False, chunksize=chunk_size):
    filtered_chunk = chunk[chunk['category'].isin(['actor', 'actress'])]
    chunk_list.append(filtered_chunk)

main_cast = pd.concat(chunk_list)
print(f"Filtered main cast rows: {len(main_cast)}")

main_cast_sorted = main_cast.sort_values(by=['tconst', 'ordering'])
top_actors = main_cast_sorted.groupby('tconst').head(3)
top_actors = top_actors.merge(names[['nconst', 'primaryName']], on='nconst', how='left')
actors_per_movie = top_actors.groupby('tconst')['primaryName'].apply(list).reset_index()

crew['directorList'] = crew['directors'].fillna('').apply(lambda x: x.split(','))
directors_expanded = crew.explode('directorList')[['tconst', 'directorList']].rename(columns={'directorList': 'nconst'})
directors_expanded = directors_expanded.merge(names[['nconst', 'primaryName']], on='nconst', how='left')
directors_per_movie = directors_expanded.groupby('tconst')['primaryName'].apply(list).reset_index()

movies = movies.merge(actors_per_movie, on='tconst', how='left')
movies = movies.merge(directors_per_movie, on='tconst', how='left')

# ✅ Fix here: Correct variable name
movies_clean = movies[['tconst', 'primaryTitle', 'startYear', 'averageRating', 'numVotes',
                       'runtimeMinutes', 'genres']].copy()
movies_clean['actors'] = movies['primaryName_x'].apply(
    lambda x: ', '.join(str(name) for name in x if pd.notna(name)) if isinstance(x, list) else '')

movies_clean['directors'] = movies['primaryName_y'].apply(
    lambda x: ', '.join(str(name) for name in x if pd.notna(name)) if isinstance(x, list) else '')


# Save to SQLite
conn = sqlite3.connect("movies.db")
movies_clean.to_sql("movies", conn, if_exists="replace", index=False)
conn.close()

print("✅ Saved to movies.db")
