import logging
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the HTML content from the file
with open('html4.txt', 'r', encoding='utf-8') as file:
    html_content = file.read()

logging.info("HTML content loaded from file.")

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')
logging.info("HTML content parsed with BeautifulSoup.")

# Print the first 2000 characters of the HTML to inspect the structure
print(html_content[:2000])

# Function to extract information based on HTML structure
def extract_information(soup):
    profile_info = {}

    # Extract the current position
    current_position_tag = soup.find('h2', {'class': 'mt1 t-18 t-black t-normal'}) or \
                           soup.find('h2', class_='t-24 t-black t-bold')
    if current_position_tag:
        profile_info['Current Position'] = current_position_tag.text.strip()
        logging.info(f"Current Position found: {profile_info['Current Position']}")
    else:
        logging.warning("Current Position not found.")

    # Extract education information
    education_tag = soup.find('span', string='Studied at') or \
                    soup.find('span', string='Education') or \
                    soup.find('h3', string='Education')
    if education_tag:
        education_info = education_tag.find_next('span')
        if education_info:
            profile_info['Education'] = education_info.text.strip()
            logging.info(f"Education found: {profile_info['Education']}")
        else:
            logging.warning("Education information not found.")
    else:
        logging.warning("Education tag not found.")

    # Extract skills
    skills_section = soup.find('section', {'id': 'skills'}) or \
                     soup.find('section', class_='pv-skill-categories-section')
    if skills_section:
        skills_tags = skills_section.find_all('span', {'class': 't-14 t-normal'})
        skills = [skill.text.strip() for skill in skills_tags]
        profile_info['Skills'] = ', '.join(skills)
        logging.info(f"Skills found: {profile_info['Skills']}")
    else:
        logging.warning("Skills section not found.")

    # Extract experience
    experience_tag = soup.find('section', {'id': 'experience'}) or \
                     soup.find('section', class_='experience-section')
    if experience_tag:
        experiences = experience_tag.find_all('span', {'class': 't-14 t-normal'})
        experience_details = [exp.text.strip() for exp in experiences]
        profile_info['Experience'] = ' '.join(experience_details)
        logging.info(f"Experience found: {profile_info['Experience']}")
    else:
        logging.warning("Experience section not found.")

    # Extract projects
    projects_section = soup.find('section', {'id': 'projects'}) or \
                       soup.find('section', class_='projects-section')
    if projects_section:
        projects_tags = projects_section.find_all('span', {'class': 't-14 t-normal'})
        projects = [project.text.strip() for project in projects_tags]
        profile_info['Projects'] = ', '.join(projects)
        logging.info(f"Projects found: {profile_info['Projects']}")
    else:
        logging.warning("Projects section not found.")

    return profile_info

# Extract the profile information
profile_info = extract_information(soup)

# Print the extracted information
for key, value in profile_info.items():
    print(f"{key}: {value}")

logging.info("Profile information extraction complete.")
