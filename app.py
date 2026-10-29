"""
Portfolio Streamlit — Arij Sghiri
Lancer en local :  python -m streamlit run app.py

Idée directrice : le parcours est dessiné comme un plan de lignes de transport.
Une ligne « Formation », une ligne « Entreprise », et une correspondance
au moment de l'alternance, quand les deux lignes avancent ensemble.
"""
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ASSETS = Path(__file__).parent / "assets"

# Palette ---------------------------------------------------------------------
INK = "#1C2733"
COBALT = "#2747A8"    # ligne Formation
SAFFRON = "#E8A317"   # ligne Entreprise
MUTED = "#6B7785"
TRACK = "#D3DBD6"
PAPER = "#F1F4F2"
FONT = "Overpass, 'Segoe UI', Arial, sans-serif"

st.set_page_config(page_title="Arij Sghiri", page_icon="🚉", layout="wide",
                   initial_sidebar_state="collapsed")

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Overpass:wght@400;600;800&display=swap');

html, body, [class*="css"], .stMarkdown, button, input {{ font-family: {FONT}; }}
[data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="collapsedControl"],
footer {{ display: none; }}
.block-container {{ max-width: 1080px; padding-top: 3.5rem; padding-bottom: 4rem; }}

.hero-name {{ font-size: clamp(3rem, 8vw, 6rem) !important; font-weight: 800; line-height: .92;
              letter-spacing: -0.03em; color: {INK}; margin: 0; }}
.hero-line {{ font-size: 1.3rem !important; line-height: 1.4; color: {INK}; max-width: 34ch; margin: 1.1rem 0 .4rem; }}
.hero-meta {{ color: {MUTED}; font-size: 1rem; }}
.hero-meta a {{ color: {COBALT}; }}

[data-testid="stImage"] img {{ border-radius: 50%; border: 4px solid {SAFFRON}; }}

.section {{ display: flex; align-items: center; gap: .7rem; margin: 3.2rem 0 .3rem; }}
.section .dot {{ width: 16px; height: 16px; border-radius: 50%; background: {PAPER};
                 border: 4px solid {INK}; flex: none; }}
.section h2 {{ font-size: 1.9rem; font-weight: 800; margin: 0; padding: 0; color: {INK}; }}
.hint {{ color: {MUTED}; font-size: .95rem; margin-bottom: .4rem; }}

.station {{ border-left: 8px solid var(--c); padding: .2rem 0 .2rem 1.1rem; margin-top: .2rem; }}
.station h3 {{ font-size: 1.35rem; font-weight: 800; margin: 0; padding: 0; }}
.station .when {{ color: {MUTED}; margin: .1rem 0 .5rem; }}
.station p {{ max-width: 68ch; margin: 0; }}

.proj {{ display: grid; grid-template-columns: 11rem 1fr; gap: 1.5rem;
         padding: 1.1rem 0; border-top: 1px solid {TRACK}; }}
.proj .ctx {{ color: {MUTED}; font-size: .95rem; }}
.proj .ctx b {{ color: {INK}; display: block; }}
.proj h4 {{ font-size: 1.15rem; font-weight: 800; margin: 0 0 .3rem; padding: 0; }}
.proj p {{ margin: 0 0 .35rem; max-width: 68ch; }}
.proj .stack {{ color: {MUTED}; font-size: .92rem; }}
.proj .stack mark {{ background: {SAFFRON}; color: {INK}; padding: 0 .2rem; border-radius: 2px; }}
@media (max-width: 640px) {{ .proj {{ grid-template-columns: 1fr; gap: .3rem; }} }}

.contact-mail {{ font-size: clamp(1.4rem, 4vw, 2.4rem) !important; font-weight: 800;
                 color: {COBALT} !important; text-decoration: none !important; }}
.contact-mail:hover, .contact-mail:focus {{ text-decoration: underline !important; }}
.small {{ color: {MUTED}; font-size: .95rem; line-height: 1.6; }}
</style>
""", unsafe_allow_html=True)


def section(title):
    st.markdown(f"<div class='section'><span class='dot'></span><h2>{title}</h2></div>",
                unsafe_allow_html=True)


def selected_points(key):
    state = st.session_state.get(key)
    try:
        return [p["customdata"][0] for p in state["selection"]["points"] if p.get("customdata")]
    except (TypeError, KeyError):
        return []


# Données ---------------------------------------------------------------------
ETAPES = pd.DataFrame([
    dict(court="<b>Licence</b><br>informatique", nom="Licence en Sciences de l'Informatique",
         lieu="Faculté des Sciences de Tunis", ligne="Formation",
         debut="2021-09-01", fin="2024-06-30",
         texte="Trois ans de bases solides : algorithmique, programmation, bases de données, réseaux."),
    dict(court="<b>Master GIL</b><br>Rouen", nom="Master Génie de l'Informatique Logicielle",
         lieu="Université de Rouen", ligne="Formation",
         debut="2024-09-01", fin="2026-10-15",
         texte="Génie logiciel et architectures web, avec une première incursion dans le big data "
               "et le data mining sur des données biomédicales."),
    dict(court="<b>Ingénieure BDML</b><br>Efrei", nom="Cycle ingénieur Big Data & Machine Learning",
         lieu="Efrei Paris", ligne="Formation",
         debut="2026-10-01", fin="2028-08-31",
         texte="Cycle ingénieur en alternance : machine learning, data visualisation, big data."),
    dict(court="<b>Tanit Web</b><br>stage", nom="Stage développeuse full stack",
         lieu="Tanit Web", ligne="Entreprise",
         debut="2024-02-01", fin="2024-05-31",
         texte="Plateforme de feedback employés en Next.js, NestJS et MongoDB, avec notifications "
               "et messagerie en temps réel. Travail en SCRUM, code partagé sur GitLab."),
    dict(court="<b>Viridien</b><br>stage", nom="Stage développeuse full stack",
         lieu="Viridien, Massy", ligne="Entreprise",
         debut="2026-04-01", fin="2026-09-30",
         texte="Nouvelle version de la plateforme interne de e-learning : fonctionnalités front "
               "et back en .NET et React, tests, validation et mise en production via Azure DevOps."),
    dict(court="<b>Viridien</b><br>alternance", nom="Apprentie ingénieure",
         lieu="Viridien, Massy", ligne="Entreprise",
         debut="2026-10-01", fin="2028-08-31",
         texte="Deux ans d'alternance dans l'équipe HPC – Enterprise Digital Solutions, "
               "dans la continuité du stage, en parallèle du cycle ingénieur."),
])
ETAPES["debut"] = pd.to_datetime(ETAPES["debut"])
ETAPES["fin"] = pd.to_datetime(ETAPES["fin"])
EN_COURS = 5  # étape affichée par défaut

LIEUX = pd.DataFrame([
    dict(ville="Tunis", lat=36.81, lon=10.18, debut="2021-09-01", fin="2024-08-31"),
    dict(ville="Rouen", lat=49.44, lon=1.10, debut="2024-09-01", fin="2026-03-31"),
    dict(ville="Île-de-France", lat=48.76, lon=2.31, debut="2026-04-01", fin=None),
])

PROJETS = [
    dict(court="Messagerie", nom="Messagerie instantanée", cadre="Efrei", quand="2026, en cours",
         techs=["APIs REST", "WebSocket", "JWT"],
         desc="Projet de synthèse du module API et Web Services, en binôme : une messagerie "
              "instantanée entre deux appareils."),
    dict(court="Qualité du vin", nom="Classification de la qualité du vin", cadre="Efrei",
         quand="2026, en cours", techs=["Python", "XGBoost", "Tests unitaires"],
         desc="Projet de machine learning en équipe de trois. Je m'occupe des tests unitaires "
              "et de l'application web qui expose le modèle."),
    dict(court="E-learning", nom="Plateforme de e-learning interne", cadre="Viridien",
         quand="2026", techs=[".NET", "React", "MySQL", "Azure DevOps"],
         desc="Fonctionnalités front-end et back-end de la nouvelle version, de l'implémentation "
              "à la mise en production, puis correction de bugs et optimisation."),
    dict(court="Biomédical", nom="Big data et data mining sur données biomédicales",
         cadre="Master GIL", quand="Projet académique",
         techs=["Python", "Neo4j", "SQL", "NoSQL", "FP-Growth"],
         desc="Pipelines ETL pour ingérer et nettoyer des corpus scientifiques, règles "
              "d'association, et réseaux de connaissances visualisés sous Neo4j."),
    dict(court="Contenus IA", nom="Génération de contenus marketing assistée par IA",
         cadre="Master GIL", quand="Projet académique", techs=["APIs REST", "Penpot"],
         desc="De l'analyse des besoins aux interfaces : user stories, maquettes, puis front-end "
              "du studio d'édition Penpot avec des assistants de génération de contenu."),
    dict(court="Feedback", nom="Plateforme de feedback employés", cadre="Tanit Web",
         quand="2024", techs=["Next.js", "Tailwind CSS", "NestJS", "MongoDB", "GitLab"],
         desc="Application full stack avec notifications et messagerie en temps réel pour "
              "la communication interne."),
]
AUSSI = ("Java, Spring Boot, Angular, PHP, TypeScript, PostgreSQL, Oracle, BaseX, Scikit-learn, "
         "TensorFlow, Weka, Power BI, Matplotlib, ggplot2")


# Hero ------------------------------------------------------------------------
col_txt, col_img = st.columns([4, 1], vertical_alignment="center")
with col_txt:
    st.markdown(f"""
    <div class='hero-name'>Arij<br>Sghiri</div>
    <div class='hero-line'>Développeuse full stack qui bifurque vers la data,
    en alternance chez Viridien.</div>
    <div class='hero-meta'>Île-de-France |
    <a href='https://www.linkedin.com/in/arij-sghiri-54b002235/' target='_blank'>LinkedIn</a> |
    <a href='mailto:arij.sghiri2@gmail.com'>arij.sghiri2@gmail.com</a></div>
    """, unsafe_allow_html=True)
with col_img:
    st.image(str(ASSETS / "photo.png"), width=170)


# Trajet ----------------------------------------------------------------------
section("Le trajet")
st.markdown("<p class='hint'>Deux lignes, une correspondance. Clique sur une station "
            "pour l'ouvrir.</p>", unsafe_allow_html=True)

choix = selected_points("trajet")
actif = choix[0] if choix else EN_COURS
Y = {"Formation": 1, "Entreprise": 0}
COULEUR = {"Formation": COBALT, "Entreprise": SAFFRON}
debut_axe, fin_axe = pd.Timestamp("2021-03-01"), pd.Timestamp("2028-12-31")

fig = go.Figure()
for ligne, y in Y.items():  # voie de fond
    fig.add_trace(go.Scatter(x=[debut_axe, fin_axe], y=[y, y], mode="lines",
                             line=dict(color=TRACK, width=3), hoverinfo="skip"))
for _, e in ETAPES.iterrows():  # tronçons
    fig.add_trace(go.Scatter(x=[e.debut, e.fin], y=[Y[e.ligne]] * 2, mode="lines",
                             line=dict(color=COULEUR[e.ligne], width=10), hoverinfo="skip"))

alternance = ETAPES.loc[EN_COURS, "debut"]  # correspondance
fig.add_trace(go.Scatter(x=[alternance, alternance], y=[0, 1], mode="lines",
                         line=dict(color=INK, width=4), hoverinfo="skip"))
fig.add_annotation(x=alternance, y=0.5, text="correspondance<br>alternance", showarrow=False,
                   xanchor="left", xshift=10, font=dict(color=INK, size=12), align="left")

aujourdhui = pd.Timestamp(date.today())

# position des étiquettes : au-dessus pour la formation, en dessous pour l'entreprise
position = {0: ("top center", 1.0), 1: ("top center", 1.0), 2: ("top center", 1.0),
            3: ("bottom center", 0.0), 4: ("bottom left", 0.0), 5: ("bottom right", 0.0)}
for i, e in ETAPES.iterrows():
    on = i == actif
    fig.add_trace(go.Scatter(
        x=[e.debut], y=[Y[e.ligne]], mode="markers+text", customdata=[[i]],
        text=[e.court], textposition=position[i][0],
        textfont=dict(color=INK, size=13),
        marker=dict(size=24 if on else 18, color=COULEUR[e.ligne] if on else "white",
                    line=dict(color=INK, width=3.5)),
        hovertemplate=f"{e.nom}<br>{e.lieu}<extra></extra>",
    ))

fig.update_layout(
    showlegend=False, height=330, margin=dict(l=10, r=10, t=10, b=10),
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family=FONT, color=INK), dragmode=False, clickmode="event+select",
    xaxis=dict(range=[debut_axe, fin_axe], dtick="M12", tickformat="%Y", showgrid=False,
               zeroline=False, fixedrange=True, tickfont=dict(color=MUTED)),
    yaxis=dict(range=[-0.9, 1.8], tickvals=[0, 1], ticktext=["Entreprise", "Formation"],
               showgrid=False, zeroline=False, fixedrange=True, tickfont=dict(size=13)),
)
st.plotly_chart(fig, key="trajet", on_select="rerun", selection_mode="points",
                config={"displayModeBar": False}, width="stretch")

e = ETAPES.loc[actif]
en_cours = e.debut <= aujourdhui < e.fin
fin_txt = f"aujourd'hui (jusqu'en {e.fin:%m/%Y})" if en_cours else f"{e.fin:%m/%Y}"
st.markdown(f"""
<div class='station' style='--c:{COULEUR[e.ligne]}'>
  <h3>{e.nom}</h3>
  <div class='when'>{e.lieu} | {e.debut:%m/%Y} – {fin_txt}</div>
  <p>{e.texte}</p>
</div>""", unsafe_allow_html=True)


# Géographie --------------------------------------------------------------------
section("Trois villes")
col_t, col_m = st.columns([1, 1.6], vertical_alignment="center")
lieux = LIEUX.copy()
lieux["fin"] = pd.to_datetime(lieux["fin"]).fillna(aujourdhui)
lieux["mois"] = ((lieux["fin"] - pd.to_datetime(lieux["debut"])).dt.days / 30.44).round().astype(int)
with col_t:
    st.markdown(
        "<p>Licence à Tunis, master à Rouen, puis l'Île-de-France pour Viridien et l'Efrei.</p>"
        "<p class='small'>La taille de chaque point correspond au nombre de mois passés "
        "dans la ville.</p>", unsafe_allow_html=True)
with col_m:
    carte = go.Figure()
    carte.add_trace(go.Scattergeo(lat=lieux["lat"], lon=lieux["lon"], mode="lines",
                                  line=dict(color=INK, width=2, dash="dot"), hoverinfo="skip"))
    carte.add_trace(go.Scattergeo(
        lat=lieux["lat"], lon=lieux["lon"], mode="markers+text",
        text=lieux["ville"], textposition=["bottom center", "top left", "top right"],
        textfont=dict(family=FONT, size=14, color=INK),
        marker=dict(size=10 + lieux["mois"] * 0.9, color=[COBALT, COBALT, SAFFRON],
                    line=dict(color=INK, width=2), opacity=0.9),
        customdata=lieux["mois"], hovertemplate="%{text} : %{customdata} mois<extra></extra>",
    ))
    carte.update_geos(projection_type="mercator", lonaxis_range=[-4, 14], lataxis_range=[33, 52],
                      showland=True, landcolor="#E1E7E3", showocean=True, oceancolor=PAPER,
                      showcountries=True, countrycolor="#FFFFFF", coastlinecolor="#B9C3BD",
                      showframe=False, bgcolor="rgba(0,0,0,0)")
    carte.update_layout(height=380, margin=dict(l=0, r=0, t=0, b=0), showlegend=False,
                        paper_bgcolor="rgba(0,0,0,0)", dragmode=False)
    st.plotly_chart(carte, config={"displayModeBar": False}, width="stretch")


# Stack -------------------------------------------------------------------------
section("Ce que j'ai vraiment utilisé")
st.markdown("<p class='hint'>Chaque point est une technologie utilisée dans un projet réel ; "
            "une ligne relie les projets qui la réutilisent. Clique sur un point pour filtrer les projets en dessous, double-clique pour "
            "tout réafficher.</p>", unsafe_allow_html=True)

colonnes = [p["court"] for p in reversed(PROJETS)]  # du plus ancien au plus récent
utilise_dans = {}  # techno -> colonnes où elle apparaît
for p in reversed(PROJETS):
    for t in p["techs"]:
        utilise_dans.setdefault(t, []).append(colonnes.index(p["court"]))
# tri en escalier : chaque techno apparaît à la ligne du premier projet qui l'utilise
techs = sorted(utilise_dans, key=lambda t: (utilise_dans[t][0], t.lower()))
filtre = selected_points("stack")
tech_active = filtre[0] if filtre else None

xs, ys, cols = [], [], []
for p in PROJETS:
    for t in p["techs"]:
        xs.append(p["court"]); ys.append(t)
        cols.append(SAFFRON if t == tech_active else COBALT)

matrice = go.Figure()
for t in techs:  # une ligne relie les projets qui réutilisent la même techno
    pos = utilise_dans[t]
    if len(pos) > 1:
        matrice.add_trace(go.Scatter(
            x=[colonnes[pos[0]], colonnes[pos[-1]]], y=[t, t], mode="lines", hoverinfo="skip",
            line=dict(color=SAFFRON if t == tech_active else COBALT, width=5)))
matrice.add_trace(go.Scatter(
    x=xs, y=ys, mode="markers", customdata=[[y] for y in ys],
    marker=dict(size=15, color=cols, line=dict(color=INK, width=1.5)),
    hovertemplate="%{y} dans %{x}<extra></extra>",
))
matrice.update_layout(
    showlegend=False, height=110 + 26 * len(techs), margin=dict(l=10, r=10, t=10, b=10),
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family=FONT, color=INK), dragmode=False, clickmode="event+select",
    xaxis=dict(categoryorder="array", categoryarray=colonnes, side="top", showgrid=False,
               fixedrange=True, tickfont=dict(size=13)),
    yaxis=dict(categoryorder="array", categoryarray=list(reversed(techs)), showgrid=False,
               fixedrange=True, tickfont=dict(size=13)),
)
st.plotly_chart(matrice, key="stack", on_select="rerun", selection_mode="points",
                config={"displayModeBar": False}, width="stretch")
st.markdown(f"<p class='small'>Pratiqué aussi en cours : {AUSSI}.</p>", unsafe_allow_html=True)


# Projets -----------------------------------------------------------------------
section("Projets")
projets = [p for p in PROJETS if tech_active is None or tech_active in p["techs"]]
if tech_active:
    st.markdown(f"<p class='hint'>{len(projets)} projet(s) avec {tech_active}.</p>",
                unsafe_allow_html=True)

html = ""
for p in projets:
    stack = ", ".join(f"<mark>{t}</mark>" if t == tech_active else t for t in p["techs"])
    html += f"""
    <div class='proj'>
      <div class='ctx'><b>{p['cadre']}</b>{p['quand']}</div>
      <div><h4>{p['nom']}</h4><p>{p['desc']}</p><div class='stack'>{stack}</div></div>
    </div>"""
st.markdown(html, unsafe_allow_html=True)


# Contact -----------------------------------------------------------------------
section("Me contacter")
st.markdown("<a class='contact-mail' href='mailto:arij.sghiri2@gmail.com'>"
            "arij.sghiri2@gmail.com</a>", unsafe_allow_html=True)
c1, c2 = st.columns([1, 2], vertical_alignment="center")
with c1:
    with open(ASSETS / "Arij_Sghiri_CV.pdf", "rb") as f:
        st.download_button("Télécharger mon CV", f, file_name="Arij_Sghiri_CV.pdf",
                           mime="application/pdf", type="primary")
with c2:
    st.markdown(
        "<p class='small'>Arabe (langue maternelle), français C1, anglais avancé, "
        "espagnol intermédiaire.<br>En dehors du code : musculation, course à pied, "
        "photographie, voyages, bénévolat associatif.</p>", unsafe_allow_html=True)
