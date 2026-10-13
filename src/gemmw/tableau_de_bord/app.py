"""Tableau de bord Gem'MW : `uv run streamlit run src/gemmw/tableau_de_bord/app.py`."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from gemmw.config import settings
from gemmw.tableau_de_bord.donnees import (
    PRIX_GEMMW,
    dernier_releve,
    lire_releves,
    lire_ventes,
    resume_ventes,
)

RACINE = Path(__file__).resolve().parents[3]
COULEURS = {"mespetitslivrets": "#2a78d6", "clesskidscreations": "#eb6834", "gemmw": "#1baf7a"}

st.set_page_config(page_title="Gem'MW, tableau de bord", page_icon="📘", layout="wide")
st.title("Gem'MW, tableau de bord")

releves = lire_releves([RACINE / "data" / "brut", RACINE / "data" / "exemples"])
ventes = lire_ventes(RACINE / settings.db_path)
dernier = dernier_releve(releves)

# ---- Ventes ---------------------------------------------------------------------------------
st.header("Les ventes")
r = resume_ventes(ventes)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Commandes", r["commandes"])
c2.metric("Chiffre d'affaires TTC", f"{r['ca_ttc']:.2f} €")
c3.metric("Net après frais et TVA", f"{r['net']:.2f} €")
c4.metric("Clientes", r["clientes"])
c5.metric("Clientes revenues", r["retour"])

if ventes.empty:
    st.info(
        "Aucune vente dans l'entrepôt pour l'instant. Importer un export avec "
        "`uv run python -m gemmw.cli importer <fichier.csv> --plateforme payhip|etsy`."
    )
else:
    par_semaine = (
        ventes.assign(semaine=pd.to_datetime(ventes["vendue_le"]).dt.to_period("W").dt.start_time)
        .groupby(["semaine", "plateforme"], as_index=False)
        .agg(commandes=("commande_ref", "count"), net=("net_eur", "sum"))
    )
    fig = px.bar(
        par_semaine,
        x="semaine",
        y="net",
        color="plateforme",
        barmode="group",
        labels={"semaine": "Semaine", "net": "Net (€)", "plateforme": "Plateforme"},
        color_discrete_map={"payhip": "#2a78d6", "etsy": "#eb6834", "amazon": "#eda100"},
    )
    fig.update_layout(margin={"t": 10, "l": 0, "r": 0, "b": 0}, legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)
    marge = ventes.groupby("plateforme", as_index=False).agg(
        commandes=("commande_ref", "count"),
        ttc=("prix_ttc_eur", "sum"),
        frais=("frais_eur", "sum"),
        tva=("tva_eur", "sum"),
        net=("net_eur", "sum"),
    )
    marge["net par commande (€)"] = (marge["net"] / marge["commandes"]).round(2)
    st.dataframe(marge, hide_index=True, use_container_width=True)

# ---- Prix concurrents ----------------------------------------------------------------------
st.header("Les prix concurrents")
if releves.empty:
    st.info("Aucun relevé. Lancer `uv run python -m gemmw.cli collecte`.")
else:
    date = dernier["releve_le"].iloc[0]
    livrets = dernier[~dernier["pack"]]
    st.caption(
        f"Dernier relevé : {date:%d/%m/%Y}, {len(dernier)} produits dont {len(livrets)} livrets "
        f"(hors packs) et {int(dernier['en_promo'].sum())} en promotion."
    )

    col_a, col_b = st.columns([3, 2])
    with col_a:
        st.subheader("Où se place Gem'MW")
        fig = go.Figure()
        for site, grp in livrets.groupby("site"):
            fig.add_trace(
                go.Box(
                    y=grp["prix_eur"],
                    name=site,
                    marker_color=COULEURS.get(site, "#6250d6"),
                    boxpoints="all",
                    jitter=0.4,
                    pointpos=0,
                    hovertext=grp["titre"],
                    line={"width": 1.5},
                )
            )
        fig.add_hline(
            y=PRIX_GEMMW,
            line={"color": COULEURS["gemmw"], "width": 2, "dash": "dash"},
            annotation_text=f"Gem'MW {PRIX_GEMMW:.2f} €",
            annotation_position="top left",
        )
        plafond = 30
        au_dessus = int((livrets["prix_eur"] > plafond).sum())
        fig.update_layout(
            yaxis={"title": "Prix d'un livret (€)", "range": [0, plafond]},
            showlegend=False,
            margin={"t": 10, "l": 0, "r": 0, "b": 0},
            height=420,
        )
        st.plotly_chart(fig, use_container_width=True)
        if au_dessus:
            st.caption(f"{au_dessus} livret(s) au-dessus de {plafond} € hors de l'échelle.")

    with col_b:
        st.subheader("Repères par site")
        synthese = (
            livrets.groupby("site")["prix_eur"]
            .agg(livrets="count", minimum="min", médiane="median", maximum="max")
            .round(2)
            .reset_index()
        )
        st.dataframe(synthese, hide_index=True, use_container_width=True)
        moins_cher = (livrets["prix_eur"] < PRIX_GEMMW).sum()
        st.markdown(
            f"**{moins_cher}** livret(s) concurrent(s) sont moins chers que Gem'MW, "
            f"**{(livrets['prix_eur'] >= PRIX_GEMMW).sum()}** sont au même prix ou plus chers."
        )

    st.subheader("Promotions en cours")
    promos = dernier[dernier["en_promo"]].copy()
    if promos.empty:
        st.write("Aucune promotion dans le dernier relevé.")
    else:
        remise = 1 - promos["prix_eur"] / promos["prix_initial_eur"]
        promos["remise"] = remise.map("{:.0%}".format)
        st.dataframe(
            promos[["site", "titre", "prix_initial_eur", "prix_eur", "remise"]]
            .rename(
                columns={
                    "prix_initial_eur": "avant (€)",
                    "prix_eur": "maintenant (€)",
                    "titre": "produit",
                }
            )
            .sort_values("remise", ascending=False),
            hide_index=True,
            use_container_width=True,
        )

    if releves["releve_le"].nunique() > 1:
        st.subheader("Évolution du prix médian")
        med = (
            releves[~releves["pack"]]
            .groupby(["releve_le", "site"], as_index=False)["prix_eur"]
            .median()
        )
        fig = px.line(
            med,
            x="releve_le",
            y="prix_eur",
            color="site",
            markers=True,
            color_discrete_map=COULEURS,
            labels={"releve_le": "Relevé", "prix_eur": "Prix médian (€)", "site": ""},
        )
        fig.add_hline(y=PRIX_GEMMW, line={"color": COULEURS["gemmw"], "dash": "dash"})
        fig.update_layout(margin={"t": 10, "l": 0, "r": 0, "b": 0})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("L'évolution dans le temps apparaîtra à partir du deuxième relevé hebdomadaire.")

    with st.expander("Tout le dernier relevé"):
        st.dataframe(
            dernier[["site", "titre", "prix_eur", "prix_initial_eur", "url"]],
            hide_index=True,
            use_container_width=True,
        )
