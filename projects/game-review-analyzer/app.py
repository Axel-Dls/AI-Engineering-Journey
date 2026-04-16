import streamlit as st
import plotly.express as px

from src.analyzer import resolve_game_candidates, get_game_informations, preprocess_text, get_sentiment, get_clusters, get_top_words_per_cluster

st.title("Game Review Analyzer")

# Form for the search
if 'selected_game' not in st.session_state:
    st.session_state['selected_game'] = None
if 'game_confirmed' not in st.session_state:
    st.session_state['game_confirmed'] = False
if 'df' not in st.session_state:
    st.session_state['df'] = None

default_value = st.session_state['selected_game']['name'] if st.session_state['game_confirmed'] else ''

with st.form("my_form"):
    col1, col2 = st.columns([4, 1], vertical_alignment="bottom")
    with col1:
        input_val = st.text_input("Search the game: ", placeholder="Id/Name of the game", icon="🔍", value=default_value)

    with col2:
        submitted = st.form_submit_button("Search", use_container_width=True)

    if submitted:
        if input_val:
            st.session_state['selected_game'] = resolve_game_candidates(input_val)
            st.session_state['df'] = None
        else:
            st.toast(":yellow[Aucun texte n'a été mis dans la barre de recherche]", icon="⚠️")

if st.session_state['selected_game'] is not None and not st.session_state['game_confirmed']:
    if len(st.session_state['selected_game']) > 1:
        left, right = st.columns([4, 1], vertical_alignment="bottom")
        with left:
            option = st.selectbox(
                label="Quel jeu est le bon ?",
                options=st.session_state['selected_game'],
                format_func=lambda x: x["name"]
            )
        with right:
            if st.button("Valider", use_container_width=True):
                st.session_state['game_confirmed'] = True
                st.session_state['selected_game'] = option
                st.rerun()

if st.session_state['game_confirmed'] and st.session_state['df'] is None:
    with st.spinner("Chargement des reviews..."):
        df = get_game_informations(st.session_state['selected_game'])
        df['text'] = df['text'].apply(preprocess_text)
        df['sentiment'] = df['text'].apply(get_sentiment)
        labels, vectorizer, kmeans = get_clusters(df['text'])
        df['cluster'] = labels
        
        st.session_state['df'] = df
        st.session_state['clusters'] = get_top_words_per_cluster(vectorizer, kmeans)

    st.write(f"{len(df)} reviews ont été récupérées.")

    if len(df) < 500:
        st.write("⚠️ Il peut y avoir un problème de pertinence dû au manque de reviews.")

    st.write(st.session_state['clusters'])
    nb_pos = len(df[df['voted_up']])
    nb_neg = len(df[~df['voted_up']])
    fig = px.pie(values=[nb_pos, nb_neg], names=["Positives", "Négatives"])
    st.plotly_chart(fig)