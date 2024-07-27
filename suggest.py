import os
import json
import logging
from langchain_google_genai import ChatGoogleGenerativeAI

# Suppress unwanted logging
logging.getLogger('absl').setLevel(logging.WARNING)

# Initialize Google Gemini model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", verbose=False, temperature=0.5, google_api_key="AIzaSyB3h-gapoolBHxMqf5s5QVDEmSnwjC4-tY")

# Function to read the profile data from the text file
def read_profile_data(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

# Function to create the prompt for rating sections
def create_rating_prompt(data):
    full_name = data.get('Full name', 'Not provided')
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

# Function to create the prompt for missing fields
def create_suggestion_prompt(data, section, word_limit, user_input=None):
    full_name = data.get('Full name', 'Not provided')
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

# Main function to generate missing information
def main():
    filename = "(6) Nicola Roberts.txt"  # Change to the correct filename if different
    profile_data = read_profile_data(filename)

    # Initial user choice: rate profile or get section suggestion
    initial_choice = input("Choose an option: (1) Rate Profile, (2) Get Section Suggestion: ").strip()

    if initial_choice == '1':
        prompt = create_rating_prompt(profile_data)
        response = llm.invoke(prompt)
        
        try:
            ratings = response.content
            print("Profile Ratings and Feedback:")
            print(ratings)
        except AttributeError as e:
            print(f"Error: {e}")
            print("Response object structure might be different. Check the attributes and adjust accordingly.")

        suggest_choice = input("Do you want suggestions for any section? (yes/no): ").strip().lower()
        if suggest_choice == "yes":
            section_to_suggest = input("Enter the section you want suggestions for: ").strip()
            word_limit = input("Enter the word limit for the suggestions: ")
            user_input = input(f"Enter any specific details you want to include for {section_to_suggest}: ").strip()
            prompt = create_suggestion_prompt(profile_data, section_to_suggest, word_limit, user_input if user_input else None)
            response = llm.invoke(prompt)
            try:
                suggestions = response.content
                print("Generated Suggestions:")
                print(suggestions)
            except AttributeError as e:
                print(f"Error: {e}")
                print("Response object structure might be different. Check the attributes and adjust accordingly.")
        
        rewrite_choice = input("Do you want to rewrite any section? (yes/no): ").strip().lower()
        if rewrite_choice == "yes":
            section_to_rewrite = input("Enter the section you want to rewrite: ").strip()
            word_limit = input("Enter the word limit for the rewrite: ")
            user_input = input(f"Enter any specific details you want to include for {section_to_rewrite}: ").strip()
            prompt = create_suggestion_prompt(profile_data, section_to_rewrite, word_limit, user_input if user_input else None)
            response = llm.invoke(prompt)
            try:
                suggestions = response.content
                print("Rewritten Section:")
                print(suggestions)
            except AttributeError as e:
                print(f"Error: {e}")
                print("Response object structure might be different. Check the attributes and adjust accordingly.")
    elif initial_choice == '2':
        # Ask user for the section they want suggestions for and the word limit
        section = input("Enter the section you want suggestions for (e.g., About Section, Experience, Education, Skills): ")
        word_limit = input("Enter the word limit for the suggestions: ")

        # Ask user if they want to specify the kind of section and information
        user_choice = input("Do you want to specify the kind of section and information to include? (yes/no): ").strip().lower()
        user_input = None
        if user_choice == "yes":
            user_input = input("Enter the specific details you want to include in the section: ")

        prompt = create_suggestion_prompt(profile_data, section, word_limit, user_input)
        
        response = llm.invoke(prompt)
        
        # Attempt to extract the text from the response object
        try:
            suggestions = response.content  # Modify this based on the printed attributes
            print("Generated Suggestions:")
            print(suggestions)
        except AttributeError as e:
            print(f"Error: {e}")
            print("Response object structure might be different. Check the attributes and adjust accordingly.")

        # Profile completeness check
        check_choice = input("Do you want to check the completeness of the profile? (yes/no): ").strip().lower()
        if check_choice == "yes":
            prompt = create_rating_prompt(profile_data)
            response = llm.invoke(prompt)
            try:
                ratings = response.content
                print("Profile Ratings and Feedback:")
                print(ratings)
            except AttributeError as e:
                print(f"Error: {e}")
                print("Response object structure might be different. Check the attributes and adjust accordingly.")

            suggest_choice = input("Do you want suggestions for any section? (yes/no): ").strip().lower()
            if suggest_choice == "yes":
                section_to_suggest = input("Enter the section you want suggestions for: ").strip()
                word_limit = input("Enter the word limit for the suggestions: ")
                user_input = input(f"Enter any specific details you want to include for {section_to_suggest}: ").strip()
                prompt = create_suggestion_prompt(profile_data, section_to_suggest, word_limit, user_input if user_input else None)
                response = llm.invoke(prompt)
                try:
                    suggestions = response.content
                    print("Generated Suggestions:")
                    print(suggestions)
                except AttributeError as e:
                    print(f"Error: {e}")
                    print("Response object structure might be different. Check the attributes and adjust accordingly.")
            
            rewrite_choice = input("Do you want to rewrite any section? (yes/no): ").strip().lower()
            if rewrite_choice == "yes":
                section_to_rewrite = input("Enter the section you want to rewrite: ").strip()
                word_limit = input("Enter the word limit for the rewrite: ")
                user_input = input(f"Enter any specific details you want to include for {section_to_rewrite}: ").strip()
                prompt = create_suggestion_prompt(profile_data, section_to_rewrite, word_limit, user_input if user_input else None)
                response = llm.invoke(prompt)
                try:
                    suggestions = response.content
                    print("Rewritten Section:")
                    print(suggestions)
                except AttributeError as e:
                    print(f"Error: {e}")
                    print("Response object structure might be different. Check the attributes and adjust accordingly.")

if __name__ == "__main__":
    main()
