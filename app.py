from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import time
import random
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

credentials = [
    {"email": "iakashreddy2k@gmail.com", "password": "Rz@Fas0923"},
    {"email": "irohitroy89@gmail.com", "password": "Rz@Fas0923"}
]

def login(driver, email, password):
    logging.debug(f"Logging in with email: {email}")
    driver.get("https://www.linkedin.com/login")
    email_elem = driver.find_element(By.ID, "username")
    email_elem.send_keys(email)
    password_elem = driver.find_element(By.ID, "password")
    password_elem.send_keys(password)
    password_elem.submit()

def extract_user_id(profile_url):
    user_id = profile_url.split('/')[-2]
    return user_id

def clean_text(text):
    return re.sub(r'<!---->', '', text)

def extract_profile_picture(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    profile_pictures = []
    for img_tag in soup.find_all('img', class_='pv-top-card-profile-picture__image--show'):
        profile_pictures.append(img_tag['src'])
    return profile_pictures[0] if profile_pictures else "Profile picture not found"

def extract_background_image(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    background_image_tag = soup.find('img', {'class': 'profile-background-image__image'})
    background_image_url = background_image_tag['src'] if background_image_tag else None
    return background_image_url if background_image_url else "Background image not found"

def extract_skills(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    skill_elements = soup.find_all('a', {'data-field': 'skill_card_skill_topic'})
    skills = []
    for skill in skill_elements:
        skill_text = skill.find('span', {'aria-hidden': 'true'}).text.strip()
        skills.append(clean_text(skill_text))
    return skills

def scrape_profile(driver, profile_url):
    logging.debug(f"Scraping profile: {profile_url}")
    driver.get(profile_url)
    time.sleep(5)
    
    html_content = driver.page_source
    user_id = extract_user_id(profile_url)

    # Extract full name using regex
    full_name_match = re.search(r'(?<=<title>).+? \| LinkedIn', html_content)
    full_name = full_name_match.group().replace(" | LinkedIn", "") if full_name_match else "Full name not found"
    full_name = clean_text(full_name)

    # Extract headline using regex
    headline_match = re.search(r'<div class="text-body-medium break-words"[^>]*>([^<]+)</div>', html_content)
    headline = headline_match.group(1).strip() if headline_match else "Headline not found"
    headline = clean_text(headline)

    # Extract location using regex
    location_match = re.search(r'<span class="text-body-small inline t-black--light break-words"[^>]*>([^<]+)</span>', html_content)
    location = location_match.group(1).strip() if location_match else "Location not found"
    location = clean_text(location)

    # Extract profile picture URL
    profile_picture_url = extract_profile_picture(html_content)

    # Extract background image URL
    background_image_url = extract_background_image(html_content)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the "About" section more specifically
    about_header = soup.find('div', {'id': 'about'})

    # Initialize the "About" section text
    about_text = "About section not found"

    # Ensure we find the specific parent container that contains the "About" text
    if about_header:
        about_section = about_header.find_next('div', class_='display-flex ph5 pv3')
        if about_section:
            # Extract the text content from each child element separately
            about_text = ""
            for child in about_section.children:
                if child.name is not None:
                    text = child.get_text(strip=True)
                    if text and text not in about_text:
                        about_text += text + "\n"
            about_text = about_text.strip()
            about_text = clean_text(about_text)

    # Extract experience section using regex
    experience_pattern = re.compile(r'<div id="experience".*?</section>', re.DOTALL)
    experience_section = experience_pattern.search(html_content)

    experiences = []
    if experience_section:
        experience_html = experience_section.group()
        
        item_pattern = re.compile(r'<li class="artdeco-list__item.*?</li>', re.DOTALL)
        items = item_pattern.findall(experience_html)

        for item in items:
            experience = {'position': '', 'company': '', 'duration': '', 'location': ''}
            
            company_match = re.search(r'data-field="experience_company_logo".*?<span aria-hidden="true">(.*?)</span>', item, re.DOTALL)
            if company_match:
                experience['position'] = re.sub(r'<.*?>', '', company_match.group(1)).strip()
            
            position_matches = re.findall(r'<span aria-hidden="true">(.*?)</span>', item)
            if position_matches:
                experience['company'] = position_matches[1].strip()
            
            duration_match = re.search(r'<span class="pvs-entity__caption-wrapper" aria-hidden="true">(.*?)</span>', item)
            if duration_match:
                experience['duration'] = re.sub(r'<.*?>', '', duration_match.group(1)).strip()
            
            location_matches = re.findall(r'<span aria-hidden="true">(.*?)</span>', item)
            if len(location_matches) > 2:
                experience['location'] = location_matches[-1].strip()

            experience = {key: clean_text(value) for key, value in experience.items()}
            experiences.append(experience)

    # Extract education section using regex
    education_pattern = re.compile(r'<div id="education".*?</section>', re.DOTALL)
    education_section = education_pattern.search(html_content)

    educations = []
    if education_section:
        education_html = education_section.group()
        
        entry_pattern = re.compile(r'<li class="artdeco-list__item.*?</li>', re.DOTALL)
        entries = entry_pattern.findall(education_html)
        
        for entry in entries:
            education = {'university': '', 'degree': '', 'field_of_study': '', 'years': ''}
            
            university_match = re.search(r'<span aria-hidden="true">(.*?)</span>', entry)
            if university_match:
                education['university'] = clean_text(university_match.group(1)).strip()
            
            degree_field_match = re.search(r'<span aria-hidden="true">(.*?), (.*?)</span>', entry)
            if degree_field_match:
                education['degree'] = clean_text(degree_field_match.group(1)).strip()
                education['field_of_study'] = clean_text(degree_field_match.group(2)).strip()
            
            years_match = re.search(r'<span class="pvs-entity__caption-wrapper" aria-hidden="true">(.*?)</span>', entry)
            if years_match:
                education['years'] = clean_text(years_match.group(1)).strip()
            
            educations.append(education)

    # Extract skills
    skills = extract_skills(html_content)

    profile_data = {
        "Full name": full_name,
        "Headline": headline,
        "Location": location,
        "Profile Picture URL": profile_picture_url,
        "Background Image URL": background_image_url,
        "About Section": about_text,
        "Experience": experiences,
        "Education": educations,
        "Skills": skills
    }

    return profile_data

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    logging.debug(f"Received data: {data}")
    profile_url = data.get('profile_url')
    logging.debug(f"Profile URL: {profile_url}")

    if not profile_url:
        logging.error("Profile URL is required")
        return jsonify({"error": "Profile URL is required"}), 400

    driver_path = r'C:\\KJX\\Linkedinscrapper\\chromedriver.exe'
    service = Service(driver_path)

    # Suppress Selenium logging
    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3")  # INFO = 0, WARNING = 1, LOG_ERROR = 2, LOG_FATAL = 3
    options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(service=service, options=options)

    # Randomly select a credential set
    cred = random.choice(credentials)
    logging.debug(f"Using credentials: {cred}")
    login(driver, cred["email"], cred["password"])

    try:
        profile_data = scrape_profile(driver, profile_url)
        response = jsonify(profile_data)
    except Exception as e:
        logging.error(f"Error scraping profile: {e}")
        response = jsonify({"error": str(e)})
    finally:
        driver.quit()

    return response

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 4000))
    app.run(host='0.0.0.0', port=port)
