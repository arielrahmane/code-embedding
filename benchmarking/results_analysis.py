import json
import pandas as pd
import glob
import numpy as np

# List of JSON files with benchmark results
benchmark_files = glob.glob("results/results_*.json")

# Initialize a list to store results for each model
analysis_results = []

# Iterate over each benchmark file
for file_path in benchmark_files:
    with open(file_path, "r") as f:
        data = json.load(f)
        
    model_name = data["model"]
    total_similarity = {"similar": 0, "moderatelySimilar": 0, "notSimilar": 0}
    correct_order_count = 0
    total_functions = len(data["codeBlocks"])
    
    # Store individual scores for each function
    function_scores = []

    for block in data["codeBlocks"]:
        code = block["code"]
        scores = block["similarityScores"]
        
        # Collect similarity scores for each description type
        similar_score = scores["similar"]
        moderately_similar_score = scores["moderatelySimilar"]
        not_similar_score = scores["notSimilar"]

        # Add scores to total
        total_similarity["similar"] += similar_score
        total_similarity["moderatelySimilar"] += moderately_similar_score
        total_similarity["notSimilar"] += not_similar_score

        # Check if the model ranks scores in the correct order: similar > moderatelySimilar > notSimilar
        if similar_score > moderately_similar_score > not_similar_score:
            correct_order_count += 1

        # Store the function score for CSV output
        function_scores.append({
            "model": model_name,
            "code": code,
            "similar_score": similar_score,
            "moderately_similar_score": moderately_similar_score,
            "not_similar_score": not_similar_score
        })

    # Calculate average similarity scores
    avg_similar = total_similarity["similar"] / total_functions
    avg_moderately_similar = total_similarity["moderatelySimilar"] / total_functions
    avg_not_similar = total_similarity["notSimilar"] / total_functions
    overall_avg_score = (avg_similar + avg_moderately_similar + avg_not_similar) / 3

    # Add the analysis results for this model
    analysis_results.append({
        "model": model_name,
        "correct_order_percentage": correct_order_count / total_functions * 100,
        "avg_similar": avg_similar,
        "avg_moderately_similar": avg_moderately_similar,
        "avg_not_similar": avg_not_similar,
        "overall_avg_score": overall_avg_score,
    })

    # Save function-level similarity scores for this model to CSV
    function_scores_df = pd.DataFrame(function_scores)
    sanitized_model_name = model_name.replace("/", "_")
    function_scores_df.to_csv(f"analysis/function_scores_{sanitized_model_name}.csv", index=False)

# Create a DataFrame to summarize the results for each model
summary_df = pd.DataFrame(analysis_results)

# Sort the models by correct order percentage
summary_df = summary_df.sort_values(by=["correct_order_percentage"], ascending=[False])

# Save the summary to a CSV file
summary_df.to_csv("analysis/model_comparison_summary.csv", index=False)

print("Analysis complete. Results saved to 'model_comparison_summary.csv' and individual function scores saved as 'function_scores_<model_name>.csv'.")