import pickle
from flask import Flask, request, jsonify
import os
import time

app = Flask(__name__)

# Configuration
#MODEL_PATH = "association_rules.pkl"
MODEL_PATH = "/app/data/association_rules.pkl"
MODEL_VERSION = "1.1.0"

# Load the model initially
def load_model():
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        model_date = time.ctime(os.path.getmtime(MODEL_PATH))
        return model, model_date
    else:
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

app.model, app.model_date = load_model()

def get_recommendations(user_songs, model, n=5):
    """
    Generate recommendations based on user_songs using association rules.

    Parameters:
    - user_songs: List of songs the user likes.
    - model: DataFrame of association rules with antecedents, consequents, and confidence.
    - n: Number of recommendations to return.

    Returns:
    - List of recommended songs.
    """
    recommendations = []
    
    # Iterate over association rules
    for _, row in model.iterrows():
        antecedents = row['antecedents']
        consequents = row['consequents']
        confidence = row['confidence']

        # Check if the user's songs match the antecedents
        if antecedents.issubset(user_songs):
            recommendations.extend(list(consequents))
    
    # Remove duplicates and songs already in the user's list
    recommendations = [song for song in recommendations if song not in user_songs]

    # Rank recommendations by their occurrence (or confidence)
    ranked_recommendations = sorted(
        list(set(recommendations)),
        key=lambda x: max(
            model.loc[model['consequents'].apply(lambda c: x in c), 'confidence'].max(),
            0
        ),
        reverse=True
    )
    
    return ranked_recommendations[:n]

@app.route('/api/rules', methods=['GET'])
def get_rules():
    return jsonify(app.model.to_json())

@app.route('/api/version', methods=['GET'])
def get_version():
    return jsonify({"Version": MODEL_VERSION})


@app.route("/api/recommend", methods=["POST"])
def recommend():
    try:
        # Validate request
        if not request.is_json:
            return jsonify({"error": "Request must be in JSON format"}), 400
        
        data = request.get_json()
        if "songs" not in data or not isinstance(data["songs"], list):
            return jsonify({"error": "Request JSON must contain a 'songs' field with a list of songs"}), 400
        
        user_songs = set(data["songs"])
        
        # Generate recommendations
        recommended_songs = get_recommendations(user_songs, app.model)

        # Build the response
        response = {
            "songs": recommended_songs,
            "version": MODEL_VERSION,
            "model_date": app.model_date,
        }
        return jsonify(response)

    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": str(e)}), 500

# Watch for changes in the model file and reload if necessary
@app.before_request
def reload_model_if_updated():
    if os.path.exists(MODEL_PATH):
        model_date = time.ctime(os.path.getmtime(MODEL_PATH))
        if model_date != app.model_date:
            app.model, app.model_date = load_model()

if __name__ == "__main__":
    # Run the server
    app.run(host="0.0.0.0", port=5000)

