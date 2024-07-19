from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return "LinkedIn Scraper is running!"

@app.route('/save', methods=['POST'])
def save_profile():
    data = request.json
    # Process and save the data as needed
    print(data)
    return jsonify({"status": "success", "data": data})

if __name__ == '__main__':
    app.run(debug=True)
