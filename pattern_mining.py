import pickle
import os
import requests
import pandas as pd
from mlxtend.frequent_patterns import fpgrowth
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import association_rules

# Step 1: Read the CSV file
DATASET_URL = os.getenv("DATASET_URL", "https://raw.githubusercontent.com/MatheusFarnese/cloudcomputingTP2/main/spotify_dataset.csv")
DATASET_PATH = os.getenv("DATASET_PATH", "dataset.csv")

if not os.path.exists(DATASET_PATH):
    print(f"Downloading dataset from {DATASET_URL}...")
    response = requests.get(DATASET_URL)
    if response.status_code == 200:
        with open(DATASET_PATH, "wb") as f:
            f.write(response.content)
        print(f"Dataset downloaded to {DATASET_PATH}")
    else:
        print(f"Failed to download dataset: {response.status_code}")
        exit(1)

data = pd.read_csv(DATASET_PATH)

#file_path = "spotify_dataset.csv"
#data = pd.read_csv(file_path)

# Ensure 'pid' and 'track_name' columns exist
if 'pid' not in data.columns or 'track_name' not in data.columns:
    raise ValueError("The CSV file must contain 'pid' and 'track_name' columns.")

print(data[["track_name", "pid"]])

# Step 2: Group track_names by `pid` to form baskets
baskets = data.groupby('pid')['track_name'].apply(list)
print(baskets)

# Step 3: Transform the baskets into a one-hot encoded DataFrame
te = TransactionEncoder()
te_ary = te.fit(baskets).transform(baskets)
basket_df = pd.DataFrame(te_ary, columns=te.columns_)
print(basket_df)

# Step 4: Run FP-growth
min_support = 0.03  # Adjust this value based on your requirements
frequent_itemsets = fpgrowth(basket_df, min_support=min_support, use_colnames=True)

# Display frequent itemsets
print(frequent_itemsets)

# Step 5: Generate association rules
min_threshold = 0.5  # Minimum confidence threshold
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_threshold)

# Display association rules
print(rules.iloc[:,:5])
print()
print(rules.iloc[:,5:])

# Select and sort the desired columns
rules_subset = rules[['antecedents', 'consequents', 'confidence']]
rules_subset = rules_subset.sort_values(by='confidence', ascending=False)

# Save to a pickle file
output_pickle_path = "association_rules.pkl"  # Specify the output path
with open(output_pickle_path, 'wb') as f:
    pickle.dump(rules_subset, f)

print(f"Rules saved to {output_pickle_path}")
