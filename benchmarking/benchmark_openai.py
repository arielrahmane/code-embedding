import json
import openai
from sklearn.metrics.pairwise import cosine_similarity
import os

openai.api_key = os.getenv("OPENAI_API_KEY") 
openai_model = "text-embedding-ada-002"

def get_openai_embedding(text, model_name):
    """Function to get embeddings from OpenAI's API."""
    response = openai.embeddings.create(model=model_name, input=text)
    return response.data[0].embedding

def compute_similarity(embedding1, embedding2):
    """Function to compute cosine similarity between two embeddings and convert to float."""
    similarity = cosine_similarity([embedding1], [embedding2])[0][0]
    return float(similarity)  # Convert to native Python float for JSON serialization

# Load code blocks and descriptions from JSON file
with open("benchmark_inputs.json", "r") as f:
    data = json.load(f)

# Initialize results container
results = {"model": openai_model, "codeBlocks": []}

# Iterate over each code block in the JSON data
for block in data["codeBlocks"]:
    code = block["code"]
    descriptions = block["descriptions"]

    # Compute embedding for the code block using OpenAI model
    code_embedding = get_openai_embedding(code, openai_model)

    # Store similarity results and embeddings for this code block
    block_results = {
        "code": code,
        "codeEmbedding": code_embedding,
        "similarityScores": {
            "similar": None,
            "moderatelySimilar": None,
            "notSimilar": None
        },
        "descriptionEmbeddings": {
            "similar": None,
            "moderatelySimilar": None,
            "notSimilar": None
        }
    }

    # Iterate over each description type and compute similarity
    for description_type, description_text in descriptions.items():
        # Compute embedding for the description
        description_embedding = get_openai_embedding(description_text, openai_model)

        # Compute similarity score and store embedding
        similarity_score = compute_similarity(code_embedding, description_embedding)
        block_results["similarityScores"][description_type] = similarity_score
        block_results["descriptionEmbeddings"][description_type] = description_embedding

    # Append results for this block to the results container
    results["codeBlocks"].append(block_results)

# Save results to a new JSON file
output_filename = f"results/results_{openai_model}.json"
with open(output_filename, "w") as f:
    json.dump(results, f, indent=4)

print(f"Benchmarking completed for OpenAI model: {openai_model}. Results saved to {output_filename}")