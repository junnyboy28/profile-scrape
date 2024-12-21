from flask import render_template, jsonify, request
from app import app
from app.scraper import scrape_linkedin_profile
from app.storage import save_data_to_json

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape_profile', methods=['POST'])
def scrape_profile():
    data = request.json
    profile_url = data.get('profile_url')
    cookies = data.get('cookies')

    if not profile_url or not cookies:
        return jsonify({"error": "Profile URL and cookies are required"}), 400

    try:
        profile_data = scrape_linkedin_profile(profile_url, cookies)
        save_data_to_json(profile_data, 'profile_data.json')  # Save data to JSON for debugging
        return jsonify(profile_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500