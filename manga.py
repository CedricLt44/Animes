import streamlit as st
import base64
from pathlib import Path
import pandas as pd
import joblib

chemin = Path(__file__).parent
fichier_data = chemin / "archive/dfmanga.csv"
dfmanga = pd.read_csv(fichier_data)

DistanceKNN = joblib.load("KNN.pkl")
tfidf_matrix = joblib.load("tfidf_matrix.pkl")

users = [
    {"name":"Cédric LE TUTOUR", "linkedin":"https://www.linkedin.com/in/cedric-le-tutour-3189417b"},
    {"name": "Foade SEHLA", "linkedin":"https://www.linkedin.com/in/foade-sehla-727762140"},
    {"name": "Thomas MABED", "linkedin":"https://www.linkedin.com/in/thomas-mabed-a8207028a"},
    {"name": "Mohammed EL AHMADI", "linkedin":"https://www.linkedin.com/in/mohammed-el-ahmadi-8a801555"}
]
linkedin_logo_url = "https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png"


# Sélection du film de référence par l'utilisateur
if "genres" not in st.session_state:
    st.session_state["genres"] = "-"

list_genres =['-','Historical', 'Martial Arts', 'Sports', 'Seinen', 'Vampire',
       'School', 'Adventure', 'Cars', 'Game', 'Horror', 'Shoujo',
       'Slice of Life', 'Dementia', 'Mystery', 'Parody', 'Super Power',
       'Mecha', 'Kids', 'Fantasy', 'Shoujo Ai', 'Shounen Ai', 'Police',
       'Military', 'Space', 'Psychological', 'Comedy', 'Thriller',
       'Supernatural', 'Music', 'Josei', 'Drama', 'Romance', 'Sci-Fi',
       'Action', 'Demons', 'Ecchi', 'Samurai', 'Shounen', 'Harem',
       'Magic']

def recommend_moviesKNN(
    movie_title,
    KNN=DistanceKNN,
    movies_data=dfmanga,
    tfidf_matrix=tfidf_matrix,
    num_recommendations=50,
    genre=None
):
    # Check if the movie exists in the dataset
    movie_indices = movies_data.index[
        movies_data["title"].str.lower() == movie_title.lower()
    ].tolist()
    if not movie_indices:
        return f"Movie '{movie_title}' not found in the dataset."

    idx = movie_indices[0]
        # Find the K-nearest neighbors for the given movie index using the TF-IDF matrix
    distances, indices = KNN.kneighbors(tfidf_matrix[idx], n_neighbors=num_recommendations)
    # Get the indices of the top similar movies, excluding the first one (itself)
    similar_movie_indices = indices.flatten()[1:num_recommendations]
     # Define recommended_movies
    recommended_movies = movies_data[["title", "genre", "img_url"]].iloc[similar_movie_indices]

    # Filter movies by genre if specified
    if genre and genre != '-':
        recommended_movies = recommended_movies[recommended_movies["genre"].str.contains(genre, case=False, na=False)]

    return recommended_movies


# mettre une image en fond d'écran
def get_base64(bin_file):
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = (
        """
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    """
        % bin_str
    )
    st.markdown(page_bg_img, unsafe_allow_html=True)


def show():
    st.title("ANIMES")
    col_selectbox = st.columns([0.35, 0.30, 0.35])
    with col_selectbox[1]:
        title = st.selectbox(
            "choisissez un manga qui péte sa mère", sorted(dfmanga["title"])
        )
    # Sélection du genre
    with st.sidebar:
        genre = st.sidebar.selectbox("Genre recherché : ",sorted(list_genres))
        st.session_state["genres"] = genre

         # Afficher l'image du film sélectionné
        if title:
            movie_info = dfmanga[dfmanga["title"] == title].iloc[0]
            st.header(movie_info["title"])
            st.sidebar.image(movie_info["img_url"], width=200)
            st.text("Synopsis : ")
            synopsis = movie_info["synopsis"]
            st.sidebar.markdown(f"<div style='text-align: justify; color: #78ddd1;'>{synopsis}</div>", unsafe_allow_html=True)
        st.write("Dévelopé par :")
        
        for user in users:
            st.markdown(
               f"""
                <style>
                .custom-link {{ 
                    color: #78ddd1; 
                }}
                </style>
                <div style="display: flex; align-items: center;">
                    <img src="{linkedin_logo_url}" width="20" style="margin-right: 10px;">
                    <a href="{user['linkedin']}" target="_blank" class="custom-link">{user['name']}</a>
                </div>
                """,
                unsafe_allow_html=True
            )


    col_films = st.columns([0.20, 0.60, 0.20])
    with col_films[1]:
        recommended_movies = None
        if title:
            recommended_movies = recommend_moviesKNN(title, DistanceKNN, dfmanga, tfidf_matrix, genre=genre)
        url_diapo= """
        <style>
        .scroll-container {
            overflow: auto;
            white-space: nowrap;
            padding: 10px;
            width: 100%;
        }
        .image-container {
            display: inline-block;
            text-align: center;
            margin-right: 100px;
        }
        .caption {
            margin-top: 5px;
            font-style: italic;
        }
        </style>
        <div class="scroll-container">"""

        url_images = ""
    col_reco = st.columns([0.05,0.90, 0.05])
    with col_reco[1]:
        if recommended_movies is not None:
            for idx in range(20):
                try : 
                    url = recommended_movies.iloc[idx]["img_url"]
                    url_images += (
                            '<div class="image-container">'
                            + '<img src="'
                            + url
                            + '" height="310"></a><p class="caption">'
                            +"<br/>"
                            + recommended_movies.iloc[idx]["title"]
                            + " <br>"
                            + recommended_movies.iloc[idx]["genre"]
                            + " <br>"
                            + "</p></div>"
                        )
                except:
                    pass
        else :
            st.write("No recommended movies found.")
        url_diapo += url_images + "</div>"
        st.markdown(url_diapo, unsafe_allow_html=True)
    