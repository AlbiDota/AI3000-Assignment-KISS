import os
import json
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

# Directory containing the JSON files
json_dir = "documents/"

# Iterate through all JSON files in the directory
for filename in os.listdir(json_dir):
    if filename.endswith(".json"):
        filepath = os.path.join(json_dir, filename)
        
        # Load the JSON array
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Iterate through all objects in JSON arr
        for item in data:
            # Combining title+content for complete string
            text = item.get("title", "") + " " + item.get("content", "")
            # Generate vectors
            vector = model.encode(text)
            # Add semantic_vectors as additional property to rule object
            item["semantic_vectors"] = vector.tolist()
        
        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        print(f"Processed {filename}")