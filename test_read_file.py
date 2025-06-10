# test_read_file.py
file_path = "Dataset/title.basics.tsv"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        print("First line:", f.readline())
except Exception as e:
    print("ERROR:", e)
