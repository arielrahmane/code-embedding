import json
from transformers import AutoModel, AutoTokenizer
from sklearn.metrics.pairwise import cosine_similarity
import torch

# Load embedding model
model_prefix_name = "microsoft/"
model_base_name = "graphcodebert-base"
model_name = model_prefix_name + model_base_name
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)
pooling_strategy = "cls"

def get_embedding(text, pooling_strategy="mean"):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    outputs = model(**inputs)
    if pooling_strategy == "mean":
        embedding = outputs.last_hidden_state.mean(dim=1)
    elif pooling_strategy == "cls":
        embedding = outputs.last_hidden_state[:, 0, :]
    return embedding.detach().numpy()

def compute_similarity(embedding1, embedding2):
  """Function to compute cosine similarity between two embeddings."""
  similarity = cosine_similarity(embedding1, embedding2)[0][0]
  return float(similarity) 

# Load code blocks and descriptions from JSON file
with open("benchmark_inputs.json", "r") as f:
  data = json.load(f)

# Initialize results container
results = {"model": model_name, "pooling_strategy": pooling_strategy, "codeBlocks": []}

# Iterate over each code block in the JSON data
for block in data["codeBlocks"]:
  code = block["code"]
  descriptions = block["descriptions"]

  # Compute embedding for the code block
  code_embedding = get_embedding(code)

  # Store similarity results for this code block
  block_results = {
    "code": code,
    "codeEmbedding": code_embedding.tolist(),  # Store the code embedding as a list for JSON serialization
    "similarityScores": {
      "similar": None,
      "moderatelySimilar": None,
      "notSimilar": None
    },
    "descriptionEmbeddings": {  # Store embeddings for each description
      "similar": None,
      "moderatelySimilar": None,
      "notSimilar": None
    }
  }

  # Iterate over each description type and compute similarity
  for description_type, description_text in descriptions.items():
    description_embedding = get_embedding(description_text, pooling_strategy)
    similarity_score = compute_similarity(code_embedding, description_embedding)
    block_results["similarityScores"][description_type] = similarity_score
    block_results["descriptionEmbeddings"][description_type] = description_embedding.tolist()  # Store as list for JSON serialization

  # Append results for this block to the results container
  results["codeBlocks"].append(block_results)

# Save results to a new JSON file
with open("results/results_" + model_base_name + "_" + pooling_strategy + ".json", "w") as f:
  json.dump(results, f, indent=4)

print("Benchmarking completed. Results saved to results.json.")