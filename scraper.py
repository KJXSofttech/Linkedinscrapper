import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re

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
    print(f"Scraping profile: {profile_url}")
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

    print("Extracted Profile Details:")
    print(f"Full name: {full_name}")
    print(f"Headline: {headline}")
    print(f"Location: {location}")
    print("\nAbout Section:")
    print(about_text)
    print("\nExperience:")
    for exp in experiences:
        print(f"{exp['position']} at {exp['company']}")
        if exp['duration']:
            print(f"   Duration: {exp['duration']}")
        if exp['location']:
            print(f"   Location: {exp['location']}")
        print()
    print("\nEducation:")
    for edu in educations:
        print(f"University: {edu['university']}")
        print(f"Degree: {edu['degree']}")
        print(f"Field of Study: {edu['field_of_study']}")
        print(f"Duration: {edu['years']}")
        print()

def scrape_profiles(email, password, profile_links):
    driver_path = './chromedriver.exe'
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service)
    login(driver, email, password)
    for link in profile_links:
        scrape_profile(driver, link)
    driver.quit()
