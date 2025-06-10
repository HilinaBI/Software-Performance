import pandas as pd
import os

# Define your dataset path
dataset_path = r"C:\Users\hp\Desktop\MA\2nd semester\performance\project\Dataset"

# Load title.basics
print("Loading title.basics.tsv...")
title_df = pd.read_csv(os.path.join(dataset_path, "title.basics.tsv"), sep='\t', na_values='\\N', low_memory=False)
print("✅ Loaded title.basics.tsv")
print(title_df.head())

# Load title.ratings
print("\nLoading title.ratings.tsv...")
ratings_df = pd.read_csv(os.path.join(dataset_path, "title.ratings.tsv"), sep='\t', na_values='\\N')
print("✅ Loaded title.ratings.tsv")
print(ratings_df.head())

# Merge the two
print("\nMerging movies with ratings...")
merged_df = title_df[title_df['titleType'] == 'movie'].merge(ratings_df, on='tconst')
print("✅ Merged. Sample:")
print(merged_df[['primaryTitle', 'startYear', 'averageRating', 'numVotes']].head())
