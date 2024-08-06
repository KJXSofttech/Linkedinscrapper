from flask import Flask, request, jsonify
import json
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from pymongo import MongoClient

# Suppress unwanted logging
logging.getLogger('absl').setLevel(logging.WARNING)

# Initialize Flask app
app = Flask(__name__)

# Initialize Google Gemini model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", verbose=False, temperature=0.5, google_api_key="AIzaSyB3h-gapoolBHxMqf5s5QVDEmSnwjC4-tY")

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['AskToMentor']
collection = db['Mentor']

# Function to get profile data from MongoDB
def get_profile_data(full_name):
    return collection.find_one({"Full Name": full_name})

# Function to update profile data in MongoDB
def update_profile_data(full_name, section, new_content):
    result = collection.update_one(
        {"Full Name": full_name},
        {"$set": {section: new_content}}
    )
    return result.modified_count > 0

# Function to create the prompt for rating sections
def create_rating_prompt(data):
    full_name = data.get('Full Name', 'Not provided')
    prompt = f"Assume you are an expert LinkedIn profile reviewer. Here is the LinkedIn profile data for {full_name}:\n\n"
    prompt += f"Full Name: {full_name}\n"
    prompt += f"Headline: {data.get('Headline', 'Not provided')}\n"
    prompt += f"Location: {data.get('Location', 'Not provided')}\n"
    prompt += f"Profile Picture URL: {data.get('Profile Picture URL', 'Not provided')}\n"
    prompt += f"Background Image URL: {data.get('Background Image URL', 'Not provided')}\n"
    prompt += f"About Section: {data.get('About Section', 'Not provided')}\n\n"
    prompt += "Experience:\n"
    for exp in data.get('Experience', []):
        prompt += f" - Position: {exp.get('position', 'Not provided')}, Company: {exp.get('company', 'Not provided')}, Duration: {exp.get('duration', 'Not provided')}, Location: {exp.get('location', 'Not provided')}\n"
    prompt += "\nEducation:\n"
    for edu in data.get('Education', []):
        prompt += f" - University: {edu.get('university', 'Not provided')}, Degree: {edu.get('degree', 'Not provided')}, Field of Study: {edu.get('field_of_study', 'Not provided')}, Years: {edu.get('years', 'Not provided')}\n"
    prompt += "\nSkills:\n"
    for skill in data.get('Skills', []):
        prompt += f" - {skill}\n"
    
    prompt += "\nAnalyze each section carefully and rate them individually out of 100, providing brief one-line feedback on each. After the ratings, give an option to rewrite or get suggestions for any section.\n"
    return prompt

# Function to create the prompt for suggestions
def create_suggestion_prompt(data, section, word_limit, user_input=None):
    full_name = data.get('Full Name', 'Not provided')
    prompt = f"Assume you are {full_name}. Here is your LinkedIn profile data:\n\n"
    prompt += f"Full Name: {full_name}\n"
    prompt += f"Headline: {data.get('Headline', 'Not provided')}\n"
    prompt += f"Location: {data.get('Location', 'Not provided')}\n"
    prompt += f"Profile Picture URL: {data.get('Profile Picture URL', 'Not provided')}\n"
    prompt += f"Background Image URL: {data.get('Background Image URL', 'Not provided')}\n"
    prompt += f"About Section: {data.get('About Section', 'Not provided')}\n\n"
    prompt += "Experience:\n"
    for exp in data.get('Experience', []):
        prompt += f" - Position: {exp.get('position', 'Not provided')}, Company: {exp.get('company', 'Not provided')}, Duration: {exp.get('duration', 'Not provided')}, Location: {exp.get('location', 'Not provided')}\n"
    prompt += "\nEducation:\n"
    for edu in data.get('Education', []):
        prompt += f" - University: {edu.get('university', 'Not provided')}, Degree: {edu.get('degree', 'Not provided')}, Field of Study: {edu.get('field_of_study', 'Not provided')}, Years: {edu.get('years', 'Not provided')}\n"
    prompt += "\nSkills:\n"
    for skill in data.get('Skills', []):
        prompt += f" - {skill}\n"

    if user_input:
        prompt += f"\nConsidering the above information, assume you are {full_name}. Write the {section} section of your LinkedIn profile within a {word_limit} word limit, including the following details: {user_input}. The text should sound like it is written by {full_name}, highlighting their experience, achievements, and passion.\n"
    else:
        prompt += f"\nConsidering the above information, assume you are {full_name}. Write the {section} section of your LinkedIn profile within a {word_limit} word limit. The text should sound like it is written by {full_name}, highlighting their experience, achievements, and passion.\n"

    return prompt

@app.route('/get_profile', methods=['POST'])
def get_profile():
    data = request.json
    full_name = data.get('full_name')
    profile_data = get_profile_data(full_name)
    if profile_data:
        # Convert ObjectId to string for JSON serialization
        profile_data['_id'] = str(profile_data['_id'])
        return jsonify({"profile": profile_data})
    else:
        return jsonify({"error": "Profile not found"}), 404

@app.route('/rate_profile', methods=['POST'])
def rate_profile():
    data = request.json
    prompt = create_rating_prompt(data)
    response = llm.invoke(prompt)
    try:
        ratings = response.content
        return jsonify({"ratings": ratings})
    except AttributeError as e:
        return jsonify({"error": str(e), "message": "Response object structure might be different. Check the attributes and adjust accordingly."})

@app.route('/suggest_section', methods=['POST'])
def suggest_section():
    data = request.json
    section = data['section']
    word_limit = data['word_limit']
    user_input = data.get('user_input', None)
    prompt = create_suggestion_prompt(data, section, word_limit, user_input)
    response = llm.invoke(prompt)
    try:
        suggestions = response.content
        return jsonify({"suggestions": suggestions})
    except AttributeError as e:
        return jsonify({"error": str(e), "message": "Response object structure might be different. Check the attributes and adjust accordingly."})

@app.route('/edit_section', methods=['POST'])
def edit_section():
    data = request.json
    full_name = data.get('full_name')
    section = data.get('section')
    new_content = data.get('new_content')
    
    if update_profile_data(full_name, section, new_content):
        return jsonify({"message": "Section updated successfully"})
    else:
        return jsonify({"error": "Failed to update section"}), 400

if __name__ == '__main__':
    app.run(debug=True)