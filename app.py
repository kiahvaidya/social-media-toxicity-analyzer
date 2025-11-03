import streamlit as st
import joblib
import re
from fastapi import FastAPI, HTTPException
import requests
import praw
from googleapiclient.discovery import build

# -------------------- CONSTANT API KEYS -------------------- #
YOUTUBE_API_KEY = "AIzaSyCDhBg95V-UDoRuChcJwcMyYWnuEUn8-FU"
TWITTER_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAOPv4wEAAAAArNVHceIkQlrWkyNdtvhH08nZgRA%3DZ4iqV40sT8N0HD1jxFXdVNoBLmoAh5b7laHtlQuCl5YvP0hoKT"
REDDIT_CLIENT_ID = "QQmegdOn_n5z_d3OBGqR5Q"
REDDIT_CLIENT_SECRET = "qeh851_bN1MOE6TPs1uKYuq-16cg8w"
REDDIT_USER_AGENT = "HateSpeechAnalyzerBot/0.1 by kv-05"

# -------------------- LOAD MODEL -------------------- #
model = joblib.load("models/model.pkl")
vectorizer = joblib.load("models/vectorizer.pkl")

# -------------------- RULE-BASED WORD CHECKS -------------------- #
positive_words = [
    "thank you", "great", "amazing", "love", "wonderful", "kind", "good job", "helpful", "respect", "brilliant",
    "excellent", "nice", "awesome", "fantastic", "outstanding", "impressive", "well done", "appreciate", "positive",
    "smart", "creative", "beautiful", "cheerful", "friendly", "supportive", "strong", "honest", "motivated", "bright",
    "happy", "enjoy", "like", "talented", "generous", "good", "cool", "fantabulous", "encouraging", "hopeful",
    "respectful", "determined", "trustworthy", "responsible", "hardworking", "helping", "successful", "nice work",
    "skillful", "peaceful", "sweet", "charming", "amused", "grateful", "satisfied", "calm", "relaxed", "smile",
    "confident", "inspiring", "motivational", "awesome job", "incredible", "adorable", "humble", "loyal", "brave",
    "caring", "courageous", "cheery", "optimistic", "faithful", "lovely", "amazing effort", "wonderful work",
    "incredible talent", "genius", "positive energy", "respectful attitude", "cooperative", "helping hand", "smiling",
    "graceful", "polite", "forgiving", "patient", "understanding", "thoughtful", "kind-hearted", "pure", "noble",
    "genuine", "fair", "great spirit", "excellent attitude", "motivated person", "friendly gesture", "appreciated",
    "commendable", "encouraged", "peaceful mind", "good-hearted", "hard-working", "bright idea", "lovable"
]

negative_words = [
    "idiot", "don't like", "chatak", "awful", "stupid", "hate", "nonsense", "kill", "trash", "dumb", "worst", "fool",
    "ugly", "lazy", "boring", "annoying", "disgusting", "horrible", "terrible", "bad", "negative", "useless",
    "dislike", "slow", "fake", "poor", "unhelpful", "rude", "unfair", "selfish", "sad", "frustrating", "angry",
    "careless", "irresponsible", "horrid", "ignorant", "arrogant", "mean", "cold", "unfriendly", "problematic",
    "ungrateful", "disrespectful", "worried", "fearful", "unhappy", "dissatisfied", "miserable", "hurt", "offensive",
    "wrong", "criticize", "fail", "failure", "weak", "hard", "stressful", "tired", "negative vibes", "no sense",
    "unpleasant", "argument", "jealous", "angry tone", "unwanted", "disappointing", "painful", "unbearable",
    "difficult", "unnecessary", "negative attitude", "embarrassing", "ashamed", "broke", "hopeless", "disheartened",
    "depressed", "unworthy", "crying", "unmotivated", "disconnected", "ignored", "forgotten", "pointless", "lost",
    "fear", "problem", "unwanted opinion", "nervous", "useless idea", "stressed", "doubt", "unsure", "uncomfortable",
    "angry comment", "critical", "toxic", "unpleasant tone", "hateful", "offended", "bitter", "argumentative",
    "defensive", "rude remark", "negative thought", "confused","dissapointed","nigga","rubbish"
]


def hybrid_predict(text):
    text_lower = text.lower()
    X = vectorizer.transform([text])
    prob = model.predict_proba(X)[0][1]
    label = int(prob > 0.5)

    if any(word in text_lower for word in negative_words):
        label, prob = 1, max(prob, 0.85)
    elif any(word in text_lower for word in positive_words):
        label, prob = 0, min(prob, 0.15)

    intensity = "Low" if prob < 0.4 else "Moderate" if prob < 0.7 else "High"
    return {"toxic": label, "intensity": intensity, "confidence": round(prob, 3)}

# -------------------- FETCH FUNCTIONS -------------------- #
def fetch_youtube_comments(video_url):
    video_id = video_url.split("v=")[-1].split("&")[0]
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=10,
        textFormat="plainText"
    )
    response = request.execute()
    return [item["snippet"]["topLevelComment"]["snippet"]["textDisplay"] for item in response.get("items", [])]

def fetch_reddit_comments(post_url):
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )
    submission = reddit.submission(url=post_url)
    submission.comments.replace_more(limit=0)
    return [comment.body for comment in submission.comments[:10]]

def fetch_twitter_comments(tweet_url):
    match = re.search(r"status/(\d+)", tweet_url)
    if not match:
        return []
    tweet_id = match.group(1)
    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
    search_url = "https://api.twitter.com/2/tweets/search/recent"
    params = {"query": f"conversation_id:{tweet_id}", "max_results": 10, "tweet.fields": "text"}
    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code != 200:
        return []
    data = response.json()
    return [tweet["text"] for tweet in data.get("data", [])]


# -------------------- STREAMLIT STYLING -------------------- #
st.set_page_config(page_title="Toxicity Detector", page_icon="🧠", layout="wide")

st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: #fff;
    }
    .main {
        background-color: rgba(255,255,255,0.05);
        padding: 2rem;
        border-radius: 1rem;
    }
    .result-card {
        border-radius: 12px;
        padding: 1rem;
        margin-top: 0.5rem;
        color: white;
    }
    .positive {background-color: rgba(46, 204, 113, 0.8);}
    .moderate {background-color: rgba(243, 156, 18, 0.8);}
    .toxic {background-color: rgba(231, 76, 60, 0.8);}
    .stButton>button {
        background-color: #16a085;
        color: white;
        border-radius: 10px;
        height: 45px;
        font-weight: 600;
        border: none;
    }
    .stTextInput>div>div>input, textarea {
        background-color: rgba(255,255,255,0.1);
        color: black;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------- APP UI -------------------- #
st.title("💬 Advanced Hate Speech & Toxicity Detector")
st.markdown("Analyze text or fetch comments from **YouTube**, **Reddit**, or **Twitter (X)** ")

choice = st.sidebar.radio("Choose Input Type", ["📝 Custom Text", "📺 YouTube", "👽 Reddit", "🐦 Twitter (X)"])

if choice == "📝 Custom Text":
    st.subheader("Enter your text below 👇")
    text = st.text_area("Type or paste text:", height=150,)
    if st.button("🔍 Analyze"):
        if text.strip():
            res = hybrid_predict(text)
            color_class = "positive" if res['toxic'] == 0 else "moderate" if res['intensity'] == "Moderate" else "toxic"
            st.markdown(f"""
                <div class="result-card {color_class}">
                    <h4>Prediction: {'✅ Safe / Positive' if res['toxic']==0 else '⚠️ Toxic Content Detected'}</h4>
                    <p><b>Intensity:</b> {res['intensity']}</p>

            """, unsafe_allow_html=True)
            st.progress(res['confidence'])
        else:
            st.warning("Please enter text first.")

else:
    url = st.text_input(f"Enter {choice.split()[1]} URL:")
    if st.button("Fetch & Analyze"):
        with st.spinner("Fetching comments..."):
            if "YouTube" in choice:
                comments = fetch_youtube_comments(url)
            elif "Reddit" in choice:
                comments = fetch_reddit_comments(url)
            else:
                comments = fetch_twitter_comments(url)

        if not comments:
            st.error("No comments found or invalid link.")
        else:
            st.success(f"Fetched {len(comments)} comments.")
            for c in comments:
                res = hybrid_predict(c)
                color_class = "positive" if res['toxic'] == 0 else "moderate" if res['intensity'] == "Moderate" else "toxic"
                with st.expander(c[:80] + "..."):
                    st.markdown(f"""
                        <div class="result-card {color_class}">
                            <b>Prediction:</b> {'✅ Safe' if res['toxic']==0 else '⚠️ Toxic'} <br>
                            <b>Intensity:</b> {res['intensity']} <br>
                            
                        </div>
                    """, unsafe_allow_html=True)
                    st.progress(res['confidence'])

st.markdown("---")

