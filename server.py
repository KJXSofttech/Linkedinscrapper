from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import time

app = Flask(__name__)

# Global driver variable
driver = None

def initialize_driver():
    global driver
    driver_path = r'C:\\path\\to\\chromedriver.exe'  # Adjust the path to your chromedriver
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service)

def login(driver, email, password):
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

def scrape_profile(driver, profile_url):
    driver.get(profile_url)
    time.sleep(5)
    
    html_content = driver.page_source
    user_id = extract_user_id(profile_url)
    
    full_name_match = re.search(r'(?<=<title>).+? \| LinkedIn', html_content)
    full_name = full_name_match.group().replace(" | LinkedIn", "") if full_name_match else "Full name not found"
    full_name = clean_text(full_name)

    headline_match = re.search(r'<div class="text-body-medium break-words"[^>]*>([^<]+)</div>', html_content)
    headline = headline_match.group(1).strip() if headline_match else "Headline not found"
    headline = clean_text(headline)

    location_match = re.search(r'<span class="text-body-small inline t-black--light break-words"[^>]*>([^<]+)</span>', html_content)
    location = location_match.group(1).strip() if location_match else "Location not found"
    location = clean_text(location)

    soup = BeautifulSoup(html_content, 'html.parser')

    about_header = soup.find('div', {'id': 'about'})

    about_text = "About section not found"
    if about_header:
        about_section = about_header.find_next('div', class_='display-flex ph5 pv3')
        if about_section:
            about_text = ""
            for child in about_section.children:
                if child.name is not None:
                    text = child.get_text(strip=True)
                    if text and text not in about_text:
                        about_text += text + "\n"
            about_text = about_text.strip()
            about_text = clean_text(about_text)

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

    profile_data = {
        "full_name": full_name,
        "headline": headline,
        "location": location,
        "about": about_text,
        "experience": experiences,
        "education": educations
    }
    return profile_data

@app.route('/scrape', methods=['POST'])
def scrape():
    global driver
    data = request.get_json()
    profile_url = data.get('url')
    if not driver:
        initialize_driver()
        email = "your-email@example.com"  # Replace with your LinkedIn email
        password = "your-password"  # Replace with your LinkedIn password
        login(driver, email, password)
    profile_data = scrape_profile(driver, profile_url)
    return jsonify(profile_data)

if __name__ == "__main__":
    app.run(port=5000)
