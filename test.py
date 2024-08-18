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
