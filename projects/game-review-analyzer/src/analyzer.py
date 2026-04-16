import pandas as pd
import requests
import nltk

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from datetime import datetime
from urllib.parse import quote

nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt_tab')

def resolve_game_candidates(search_txt: str):
    if search_txt == '':
        raise ValueError("Ne peux pas rien chercher.")

    try:
        return int(search_txt)
    except ValueError:
        url = f"https://store.steampowered.com/api/storesearch/?term={search_txt}&l=english&cc=US"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        items = data["items"]

        if len(items) == 0:
            return None
        elif len(items) == 1:
            return items[0]
        else:
            return items

def create_score_precision(row, game_early_access:bool = False):
    score_precision = 0
    
    # Gestion de si récent ou non    
    interval_days = (datetime.today() - row['date']).days
    if interval_days < 90:
        score_precision += 1
    elif interval_days < 365:
        score_precision += 0.75
    elif interval_days <= (365 * 3):
        score_precision += 0.35

    # Gestion de la qualité via le score Steam
    if row['weighted_vote_score'] > 0.7:
        score_precision += 1.5
    elif row['weighted_vote_score'] > 0.5:
        score_precision += 1
    elif row['weighted_vote_score'] > 0.2:
        score_precision += 0.5

    # Gestion de la validation sociale brute
    if row['votes_up'] > 20:
        score_precision += 0.5
    elif row['votes_up'] > 5:
        score_precision += 0.25
    
    # Gestion de la crédibilité via temps de jeu
    if row['playtime_at_review'] >= 20*60 :
      score_precision += 1
    elif row['playtime_at_review'] >= 5*60 :
      score_precision += 0.6
    elif row['playtime_at_review'] >= 60 :
      score_precision += 0.25
        
    # Gestion de l'early access
    if row['written_during_early_access'] and not game_early_access:
        score_precision -= 0.75

    row['score_precision'] = score_precision
    
    return row

def get_game_informations(game):

    cursor = "*"
    data = []
    
    while True:
        cursor = quote(cursor)
        url= f"https://store.steampowered.com/appreviews/{game['id']}?json=1&num_per_page=100&language=english&filter=all&cursor={cursor}"
        response = requests.get(url)
        response.raise_for_status()
        response_json = response.json()
        
        if 'reviews' not in response_json:
            break
        print(len(response_json['reviews']))
        data.extend(response_json['reviews'])
        print(f"Total reviews: {len(data)}")
        if len(response_json['reviews']) < 100:
            break

        cursor = response_json['cursor']

    df = pd.DataFrame(data)

    df['weighted_vote_score'] = df['weighted_vote_score'].astype("float")
    df['playtime_at_review'] = df['author'].apply(lambda x: x['playtime_at_review'])
    df['recommendationid'] = df['recommendationid'].astype("int")
    df['date'] = df.apply(lambda x: pd.to_datetime(max(x['timestamp_created'], x['timestamp_updated']), unit='s'), axis=1)
    df = df.drop(['votes_funny', 'comment_count', 'received_for_free', 'refunded', 'primarily_steam_deck', 'app_release_date', 'reactions', 'hardware', 'steam_purchase', 'author', 'timestamp_created', 'timestamp_updated'], axis=1)
    df = df.rename(columns={'recommendationid': 'id', 'review': 'text'})

    df = df.apply(create_score_precision, axis=1, args=(False,))

    return df

analyzer = SentimentIntensityAnalyzer()

def preprocess_text(text):
    tokens = word_tokenize(text.lower())

    filtered_tokens = [token for token in tokens if token not in stopwords.words('english')]

    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]

    processed_text = ' '.join(lemmatized_tokens)

    return processed_text

def get_sentiment(text):
    scores = analyzer.polarity_scores(text)
    sentiment = 1 if scores['pos'] > 0 else 0
    return sentiment

def get_clusters(text):
    vectorizer = TfidfVectorizer(max_features=500)
    X = vectorizer.fit_transform(text)
    vectorizer.get_feature_names_out()
    kmeans = KMeans(n_clusters=8, random_state=0, n_init="auto").fit(X)
    return kmeans.labels_, vectorizer, kmeans

def get_top_words_per_cluster(vectorizer, kmeans, n_words=10):
    feature_names = vectorizer.get_feature_names_out()
    clusters = {}
    
    for i in range(kmeans.n_clusters):
        # récupère les indices des n_words plus grands scores du cluster i
        top_indices = kmeans.cluster_centers_[i].argsort()[-n_words:]
        # utilise ces indices pour récupérer les mots correspondants
        clusters[i] = feature_names[top_indices]
    
    return clusters