"""
from bs4 import BeautifulSoup

# Path to your saved HTML file
file_path = 'sakshi-gawande-0095351ab_profile.html.txt'

# Read the content of the file
with open(file_path, 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Find the specific full-size profile picture by looking for larger dimensions (e.g., 400x400)
profile_picture = soup.find('img', {
    'src': lambda x: x and '400_400' in x
})

# Check if the profile picture was found and extract the URL
if profile_picture:
    profile_picture_url = profile_picture['src']
    print(f"Full-Size Profile Picture URL: {profile_picture_url}")
else:
    print("Full-size profile picture not found.")
"""


from pymongo import MongoClient
import urllib.parse

# MongoDB connection setup
username = urllib.parse.quote_plus("kjxsofttechpvtltd")
password = urllib.parse.quote_plus("KJXSOFTTECH123")
connection_string = f"mongodb+srv://{username}:{password}@kjxwebsite.3mup0.mongodb.net/?retryWrites=true&w=majority&appName=kjxwebsite"

try:
    # Establish a connection to the MongoDB cluster
    client = MongoClient(connection_string, tls=True)
    
    # Access the database
    db = client['LinkedinScrapper']  # New database name is LinkedinScrapper
    
    # Access the collection
    collection = db['Mentors data']  # New collection name is Mentors data
    
    # Sample document to insert
    sample_document = {
        "About Section": "About section not found",
        "Background Image URL": "https://media.licdn.com/dms/image/v2/D5616AQE2_TIVzmhHMw/profile-displaybackgroundimage-shrink_350_1400/profile-displaybackgroundimage-shrink_350_1400/0/1706193872412?e=1729728000&v=beta&t=LjkRJTy-nsGFNqXeuy8PPB9PvTv9vTDPQBO0arbg6Vw",
        "Education": [
            {
                "degree": "Data Scientist Bootcamp",
                "field_of_study": "Data Science",
                "university": "upGrad.com",
                "years": "Jul 2023 - Jan 2024"
            },
            {
                "degree": "S.B. Jain Institute of Technology,Management &amp; Research",
                "field_of_study": "Nagpur",
                "university": "S.B. Jain Institute of Technology,Management &amp; Research, Nagpur",
                "years": "Mar 2019 - Jun 2023"
            }
        ],
        "Experience": [
            {
                "company": "KJXSOFTTECH · Full-time",
                "duration": "Jan 2024 - Present · 8 mos",
                "location": "I'm thrilled to announce that I've embarked on a new journey as a Junior Data Scientist at KJX SoftTech! 🚀 Excited to dive in and contribute to the team's success 💼💡 Can't wait to see where this opportunity takes me in my career! Here's to new beginnings and meaningful contributions! 🎉#NewJob #DataScience",
                "position": "Junior Data Scientist"
            }
        ],
        "Full Name": "Devam Kathane",
        "Headline": "Data scientist| Machine Learning | NLP | Deep Learning | Python | SQL | Tableau | Data visualization | Data analytics",
        "Location": "Nagpur, Maharashtra, India",
        "Profile Picture URL": "https://media.licdn.com/dms/image/v2/D5603AQHzIDhr7wL3kQ/profile-displayphoto-shrink_100_100/profile-displayphoto-shrink_100_100/0/1707400798206?e=1729728000&v=beta&t=SiJUpRJn9f15SfuG6uvbkbQoVCLV4wWOo9xwZ0eBSWo",
        "Skills": [
            "Large Language Models (LLM)",
            "Data Science"
        ],
        "User ID": "devam-kathane-1ba11721b"
    }
    
    # Insert the sample document into the collection
    result = collection.insert_one(sample_document)
    
    # Print success message
    print(f"Document inserted with _id: {result.inserted_id}")
    
except Exception as e:
    print(f"An error occurred: {e}")
