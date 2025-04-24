from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import csv
import time

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def normalize_content(content):
    # Remove whitespace and comments for normalization
    lines = content.splitlines()
    normalized_lines = []
    for line in lines:
        # Remove comments and strip whitespace
        line = line.split('//')[0].strip()
        if line:
            normalized_lines.append(line)
    return '\n'.join(normalized_lines)

def detect_similarities(file_paths, threshold=0.7):
    contents = [normalize_content(read_file(file_path)) for file_path in file_paths]
    vectorizer = TfidfVectorizer().fit_transform(contents)
    vectors = vectorizer.toarray()
    cosine_matrix = cosine_similarity(vectors)

    similar_pairs = []
    total_pairs = 0  # Initialize total pairs count
    for i in range(len(file_paths)):
        for j in range(i + 1, len(file_paths)):
            total_pairs += 1  # Increment total pairs count
            if cosine_matrix[i][j] > threshold:
                similar_pairs.append((file_paths[i], file_paths[j], cosine_matrix[i][j]))

    return similar_pairs, total_pairs  # Return both similar pairs and total pairs

# List of files to check for similarities in the source_code directory
source_code_dir = "contract_data/solidity"
file_paths = [os.path.join(source_code_dir, filename) for filename in os.listdir(source_code_dir) if filename.endswith('.sol')]
start_time = time.time()  # 记录开始时间
similar_pairs, total_pairs = detect_similarities(file_paths)
end_time = time.time()  # 记录结束时间
# Write similar pairs to a CSV file
csv_filename = "similar_bytecode.csv"
with open(csv_filename, "w", newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["Source Code 1", "Source Code 2", "Similarity"])
    for pair in similar_pairs:
        csvwriter.writerow([os.path.basename(pair[0]), os.path.basename(pair[1]), f"{pair[2]:.2f}"])

# Print results
execution_time = end_time - start_time
print(f"Execution time: {execution_time:.2f} seconds") 
print(f"Total pairs detected: {total_pairs}")
if similar_pairs:
    print(f"Number of similar contract pairs: {len(similar_pairs)}")
    print(f"Similar contract pairs have been saved to {csv_filename}.")
else:
    print("No similar contracts found.")
