import streamlit as st
import plotly.express as px
from sklearn.feature_extraction.text import CountVectorizer
from pathlib import Path
import pandas as pd
import ast

chemin = Path(__file__).parent
fichier_data = chemin / "archive/anim_freq.csv"
df_freq = pd.read_csv(fichier_data)

users = [
    {"name":"Cédric LE TUTOUR", "linkedin":"https://www.linkedin.com/in/cedric-le-tutour-3189417b"},
    {"name": "Foade SEHLA", "linkedin":"https://www.linkedin.com/in/foade-sehla-727762140"},
    {"name": "Thomas MABED", "linkedin":"https://www.linkedin.com/in/thomas-mabed-a8207028a"},
    {"name": "Mohammed EL AHMADI", "linkedin":"https://www.linkedin.com/in/mohammed-el-ahmadi-8a801555"}
]
linkedin_logo_url = "https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png"

fichier_viz = chemin /"archive/dataviz_manga.csv"
dataviz = pd.read_csv(fichier_viz,sep=',')
dataviz.drop(columns= ['aired'])
dataviz["start"]= dataviz["start"].apply(lambda x : x[-4:])
dataviz["end"] = dataviz["end"].apply(lambda x: "2024" if pd.isna(x) else x[-4:])

dataviz["start"] = dataviz["start"].apply(lambda x: x[-4:])
dataviz["end"] = dataviz["end"].apply(lambda x: "2024" if pd.isna(x) else x[-4:])

dataviz["genre"] = dataviz["genre"].apply(lambda x: ast.literal_eval(x))

            
        
def list_to_lowercase(lst):
    return [x.lower() for x in lst]

# Appliquer la fonction à chaque élément de la colonne 'genre'
dataviz["genre"] = dataviz["genre"].apply(list_to_lowercase)
unique_genres = list()
for genres in dataviz["genre"]:
    unique_genres += genres
unique_genres = set(unique_genres)
unique_genres = list(unique_genres)

    # Function to replace spaces with hyphens in each string of a list
def replace_spaces_in_list(lst):
        return [item.replace(" ", "-") for item in lst]

    # Apply the function to each list in the 'genre' column
dataviz["genre"] = dataviz["genre"].apply(replace_spaces_in_list)
dataviz["genre_str"] = dataviz["genre"].apply(lambda x: " ".join(x))
vec = CountVectorizer(token_pattern="(?u)\\b[\\w-]+\\b")
vec.fit(dataviz["genre_str"])
X = vec.transform(dataviz["genre_str"])
X_dense = X.todense()
df = pd.DataFrame(
    X_dense, columns=vec.get_feature_names_out(), index=dataviz.index
)

sorted_genres_perc = (
    100 * pd.Series(df.sum()).sort_values(ascending=True) / df.shape[0]
)  # à comprendre plus tard



def show():
    with st.sidebar:
         st.image("images/Logocnc.png")
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
    
    col_histo = st.columns([0.10, 0.80, 0.10])
    with col_histo[1]:
        st.title("DATAVISUALISATION")
        st.subheader("Comparaison des entrées entre les animés, fiction et documentaire")
    with col_histo[1]:
        df_freq[
            [
                "entree_fiction",
                "entree_doc",
                "entre_anim",
                "recette_fiction",
                "recette_doc",
                "recette_anim",
                "nb_seance_fiction",
                "nb_seance_doc",
                "nb_seance_anim",
            ]
        ] = (
            df_freq[
                [
                    "entree_fiction",
                    "entree_doc",
                    "entre_anim",
                    "recette_fiction",
                    "recette_doc",
                    "recette_anim",
                    "nb_seance_fiction",
                    "nb_seance_doc",
                    "nb_seance_anim",
                ]
            ]
            .replace("[\\s\u202f,]", "", regex=True)
            .replace("\\.", "", regex=True)
            .astype(int)
        )
        df_freq["total_entree"] = df_freq[
            ["entree_fiction", "entree_doc", "entre_anim"]
        ].sum(axis=1)
        fig = px.bar(
            df_freq,
            x="date",
            y=["entree_fiction", "entree_doc", "entre_anim"],
            labels={
                "value": "Nombre d'entrées",
                "variable": "Type d'entrée",
                "année": "Année",
            },
            height=500,
            width=1100,
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig.update_layout(
            legend=dict(
                title=dict(font=dict(size=14, color="#78ddd1")),
                font=dict(color="#78ddd1"),
                bgcolor="rgba(0, 0, 0, 0)",
            ),
            plot_bgcolor="rgba(0, 0, 0, 0)",
            paper_bgcolor="rgba(0, 0, 0, 0)",
            xaxis=dict(  # x-axis settings
                title=dict(
                    text="Année", font=dict(size=20, color="#78ddd1")
                ),  # x-axis title color
                tickfont=dict(color="#78ddd1"),  # x-axis tick color
            ),
            yaxis=dict(  # y-axis settings
                title=dict(
                    text="Nombre d'entrées", font=dict(color="#78ddd1")
                ),  # y-axis title color
                tickfont=dict(color="#78ddd1"),  # y-axis tick color
            ),
        )

        st.plotly_chart(fig)
  
            # Fonction pour convertir une liste de chaînes en minuscules
        
    col_bar = st.columns([0.10, 0.80, 0.10])
    with col_bar[1]:
        
        st.subheader("Diversité des genres dans les animés")

 

        fig = px.bar(sorted_genres_perc, x=sorted_genres_perc.values,
                    y=sorted_genres_perc.index, 
                    color_discrete_sequence=["#78ddd1"],
                    height=800,
                    width=1100,
                     )
        fig.update_layout(
             plot_bgcolor="rgba(0, 0, 0, 0)",
             paper_bgcolor="rgba(0, 0, 0, 0)",)
        
        fig.update_layout( xaxis=dict(  # x-axis settings
                title=dict(
                    text="Percentage of Films (%)", font=dict(size=20, color="#78ddd1")
                ),  # x-axis title color
                tickfont=dict(color="#78ddd1"),  # x-axis tick color
            ),
            yaxis=dict(  # y-axis settings
                title=dict(
                    text="", font=dict(color="#78ddd1")
                ),  # y-axis title color
                tickfont=dict(color="#78ddd1"),  # y-axis tick color
            ),
        )
             
        st.plotly_chart(fig)