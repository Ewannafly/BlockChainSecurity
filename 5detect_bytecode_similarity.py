import os
import json
from typing import Dict, List, Tuple, Set
from fuzzywuzzy import fuzz
from tqdm import tqdm
from datetime import datetime
from collections import defaultdict

def read_bytecode(file_path: str) -> str:
    """
    Read the bytecode from a pre-compiled file
    """
    try:
        with open(file_path, 'r') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading bytecode from {file_path}: {str(e)}")
        return ""

def calculate_similarity(bytecode1: str, bytecode2: str) -> float:
    """
    Calculate similarity between two bytecode strings using fuzzywuzzy
    Returns similarity percentage (0-100)
    """
    try:
        # Use ratio() for exact matching
        similarity = fuzz.ratio(bytecode1, bytecode2)
        return similarity
    except Exception as e:
        print(f"Error calculating similarity: {str(e)}")
        return 0.0

def find_similar_groups(similar_pairs: List[Tuple[str, str, float]]) -> List[Set[str]]:
    """
    Find groups of similar contracts using connected components
    """
    # Create graph of similar contracts
    graph = defaultdict(set)
    for file1, file2, _ in similar_pairs:
        graph[file1].add(file2)
        graph[file2].add(file1)
    
    # Find connected components
    visited = set()
    groups = []
    
    def dfs(node: str, group: Set[str]):
        visited.add(node)
        group.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                dfs(neighbor, group)
    
    for node in graph:
        if node not in visited:
            group = set()
            dfs(node, group)
            if len(group) > 1:  # Only add groups with more than one contract
                groups.append(group)
    
    return groups

def analyze_bytecode_similarity(directory: str, threshold: float = 70.0) -> List[Tuple[str, str, float]]:
    """
    Analyze bytecode similarity between all bytecode files in the directory
    Returns list of (file1, file2, similarity) tuples where similarity >= threshold
    """
    # Get all bytecode files
    bytecode_files = [f for f in os.listdir(directory) if f.endswith('.bin')]
    similar_pairs = []
    
    print("Reading bytecode files...")
    # Read all bytecodes with progress bar
    file_bytecodes = {}
    for file_name in tqdm(bytecode_files, desc="Reading files"):
        file_path = os.path.join(directory, file_name)
        bytecode = read_bytecode(file_path)
        if bytecode:
            file_bytecodes[file_name] = bytecode
    
    print("\nAnalyzing bytecode similarity...")
    # Calculate total number of comparisons
    total_comparisons = sum(range(len(bytecode_files)))
    
    # Compare all pairs with progress bar
    with tqdm(total=total_comparisons, desc="Comparing files") as pbar:
        for i, file1 in enumerate(bytecode_files):
            if file1 not in file_bytecodes:
                pbar.update(len(bytecode_files) - i - 1)
                continue
                
            for file2 in bytecode_files[i+1:]:
                if file2 not in file_bytecodes:
                    continue
                    
                similarity = calculate_similarity(file_bytecodes[file1], file_bytecodes[file2])
                if similarity >= threshold:
                    similar_pairs.append((file1, file2, similarity))
                pbar.update(1)
    
    return similar_pairs

def save_results(similar_pairs: List[Tuple[str, str, float]], output_dir: str):
    """
    Save analysis results to a JSON file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate timestamp for unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"bytecode_similarity_{timestamp}.json")
    
    # Find similar groups
    similar_groups = find_similar_groups(similar_pairs)
    
    # Get unique similar contracts
    unique_similar_contracts = set()
    for file1, file2, _ in similar_pairs:
        unique_similar_contracts.add(file1)
        unique_similar_contracts.add(file2)
    
    # Convert results to list of dictionaries
    results = [
        {
            "file1": file1,
            "file2": file2,
            "similarity": similarity
        }
        for file1, file2, similarity in similar_pairs
    ]
    
    # Add metadata and statistics
    output_data = {
        "timestamp": timestamp,
        "total_pairs": len(similar_pairs),
        "total_similar_contracts": len(unique_similar_contracts),
        "number_of_groups": len(similar_groups),
        "threshold": 70.0,
        "similar_groups": [list(group) for group in similar_groups],
        "results": results
    }
    
    # Save to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)
    
    print(f"\nResults saved to: {output_file}")

def main():
    # Use the absolute path for bytecode files
    directory = os.path.abspath(r"D:\COMP\4SECURITY\PROJECT3.29\contract_data\bytecode")
    output_dir = os.path.abspath(r"D:\COMP\4SECURITY\PROJECT3.29\contract_data\results")
    
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist")
        return
        
    print(f"Analyzing bytecode similarity in directory: {directory}")
    print("This may take a few minutes...")
    
    similar_pairs = analyze_bytecode_similarity(directory)
    
    if similar_pairs:
        # Find similar groups
        similar_groups = find_similar_groups(similar_pairs)
        
        # Get unique similar contracts
        unique_similar_contracts = set()
        for file1, file2, _ in similar_pairs:
            unique_similar_contracts.add(file1)
            unique_similar_contracts.add(file2)
        
        print("\nSimilarity Analysis Results:")
        print("-" * 50)
        print(f"Total number of similar pairs: {len(similar_pairs)}")
        print(f"Total number of similar contracts: {len(unique_similar_contracts)}")
        print(f"Number of similar groups: {len(similar_groups)}")
        print("\nSimilar Groups:")
        for i, group in enumerate(similar_groups, 1):
            print(f"\nGroup {i} ({len(group)} contracts):")
            for contract in group:
                print(f"  - {contract}")
        
        print("\nDetailed Similarity Results:")
        print("-" * 50)
        for file1, file2, similarity in similar_pairs:
            print(f"\nSimilarity: {similarity:.2f}%")
            print(f"File 1: {file1}")
            print(f"File 2: {file2}")
        
        # Save results to file
        save_results(similar_pairs, output_dir)
    else:
        print("\nNo similar contracts found with similarity >= 70%")

if __name__ == "__main__":
    main() 