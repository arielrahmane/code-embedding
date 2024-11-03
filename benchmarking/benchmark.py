from transformers import AutoModel, AutoTokenizer
from sklearn.metrics.pairwise import cosine_similarity
import torch

# Load embedding model (CodeBERT as an example)
model_name = "microsoft/codebert-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def get_embedding(text):
  inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
  outputs = model(**inputs)
  # Pooling: mean of the last hidden layer
  embedding = outputs.last_hidden_state.mean(dim=1)
  return embedding.detach().numpy()

# Sample data
code_block = """
def add(a, b):
  return a + b
"""

related_description = "This function takes two numbers and returns their sum."
unrelated_description = "The weather is sunny today with a high of 75 degrees."

# Generate embeddings
code_embedding = get_embedding(code_block)
related_embedding = get_embedding(related_description)
unrelated_embedding = get_embedding(unrelated_description)

# Calculate cosine similarities
similarity_related = cosine_similarity(code_embedding, related_embedding)[0][0]
similarity_unrelated = cosine_similarity(code_embedding, unrelated_embedding)[0][0]

print("Similarity with related description:", similarity_related)
print("Similarity with unrelated description:", similarity_unrelated)