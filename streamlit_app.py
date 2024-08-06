import streamlit as st
import requests
import json

st.set_page_config(layout="centered", initial_sidebar_state="collapsed")

st.title("LinkedIn Profile Advisor")

# Ask for user's name
full_name = st.text_input("Enter your full name")

if full_name:
    # Fetch profile data from MongoDB through Flask API
    response = requests.post("http://localhost:5000/get_profile", json={"full_name": full_name})
    
    if response.status_code == 200:
        profile_data = response.json()["profile"]
        st.success(f"Profile found for {full_name}")

        st.header("Options")
        option = st.selectbox("Choose an option", ["Rate Profile", "Get Section Suggestion"])

        if option == "Rate Profile":
            if st.button("Rate Profile"):
                response = requests.post("http://localhost:5000/rate_profile", json=profile_data)
                if response.status_code == 200:
                    result = response.json()
                    st.subheader("Profile Ratings")
                    st.write(result["ratings"])
                else:
                    st.error("Error: Unable to rate profile")
            
        elif option == "Get Section Suggestion":
            section = st.selectbox("Choose Section", ["About Section", "Experience", "Education", "Skills"])
            word_limit = st.number_input("Word Limit", min_value=50, max_value=500, value=150)
            user_input = st.text_area("Specific Details (Optional)")
            
            if st.button("Get Suggestion"):
                data = {
                    "section": section,
                    "word_limit": word_limit,
                    "user_input": user_input
                }
                data.update(profile_data)
                response = requests.post("http://localhost:5000/suggest_section", json=data)
                if response.status_code == 200:
                    result = response.json()
                    st.subheader(f"Suggestion for {section}")
                    st.write(result["suggestions"])
                else:
                    st.error("Error: Unable to get suggestions")

        st.header("Profile Data")
        st.json(profile_data)
    else:
        st.error("Profile not found. Please check the name and try again.")