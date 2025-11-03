# social-media-toxicity-analyzer
This project detects toxic and non-toxic comments from YouTube, Twitter, Reddit, and custom text input using machine learning.
It supports English and Hinglish (code-mixed) comments and uses TF-IDF vectorization with a Logistic Regression classifier.

🧩 Features

Fetches comments using APIs (YouTube, Twitter, Reddit)

Accepts custom user text input

Preprocesses multilingual text for better accuracy

Classifies comments as toxic or non-toxic

Displays labeled results on a simple web interface

⚙️ Tech Stack

Backend: Python

Frontend: Streamlit

Machine Learning: scikit-learn, TF-IDF, Logistic Regression

APIs: YouTube Data API v3, Twitter API v2, Reddit API (PRAW)

📁 Dataset

Download the dataset used for model training and testing here:
➡️ [Dataset Link (https://www.kaggle.com/datasets/sharduldhekane/code-mixed-hinglish-hate-speech-detection-dataset)]

🧠 How It Works

User enters a YouTube/Twitter/Reddit link or custom text.

The system fetches data using the respective API.

Text is preprocessed — cleaned, tokenized, and converted into TF-IDF vectors.

The Logistic Regression model classifies each entry as toxic or non-toxic.

Results are displayed on the frontend with labels and confidence scores.

🖥️ Run Locally
1. Clone the repository
git clone https://github.com/kiahvaidya/social-media-toxicity-analyzer.git
cd social-media-toxicity-analyzer

2. Install dependencies
pip install -r requirements.txt

3. Add your API keys in a .env file
YOUTUBE_API_KEY=your_api_key
TWITTER_BEARER_TOKEN=your_token
REDDIT_CLIENT_ID=your_client_id
REDDIT_SECRET=your_secret
REDDIT_USER_AGENT=your_user_agent

4. Run the project
streamlit run app.py


