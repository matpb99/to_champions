import random
import data
import streamlit as st
import pandas as pd

from collections import defaultdict
from itertools import combinations
from joblib import Parallel, delayed
from ui_sidebar import display_sidebar


def simulate_match_bo3(team1, team2):
    match_simulated = [
        (team1, team2, "2-0"),
        (team1, team2, "2-1"),
        (team2, team1, "2-0"),
        (team2, team1, "2-1"),
    ]

    return random.choice(match_simulated)


def simulate_match_bo5(team1, team2):
    match_simulated = [
        (team1, team2, "3-0"),
        (team1, team2, "3-1"),
        (team1, team2, "3-2"),
        (team2, team1, "3-0"),
        (team2, team1, "3-1"),
        (team2, team1, "3-2"),
    ]

    return random.choice(match_simulated)


def generate_remaining_matches(groups, played_matches):
    played_pairs = {
        tuple(sorted((match["team1"], match["team2"]))) for match in played_matches
    }
    remaining = []
    for group_teams in groups.values():
        for pair in combinations(group_teams, 2):
            if tuple(sorted(pair)) not in played_pairs:
                remaining.append(pair)
    return remaining


def simulate_regular_season(groups, played_matches):

    standings = defaultdict(lambda: {"victorias": 0})

    for match in played_matches:
        winner = match["winner"]
        standings[winner]["victorias"] += 1

    remaining_matches = generate_remaining_matches(groups, played_matches)

    for team1, team2 in remaining_matches:
        winner, loser, score = simulate_match_bo3(team1, team2)

        standings[winner]["victorias"] += 1

    alpha = dict(
        sorted(
            ((k, v) for k, v in standings.items() if k in groups["alpha"]),
            key=lambda item: item[1]["victorias"],
            reverse=True,
        )
    )
    omega = dict(
        sorted(
            ((k, v) for k, v in standings.items() if k in groups["omega"]),
            key=lambda item: item[1]["victorias"],
            reverse=True,
        )
    )
    return alpha, omega


def simulate_playoffs(alpha_standings, omega_standings):

    playoff_results_dict = {}

    A1, A2, A3, A4 = list(alpha_standings.keys())[:4]
    O1, O2, O3, O4 = list(omega_standings.keys())[:4]

    # Upper Bracket QF
    uqf1_winner, uqf1_loser, uqf1_score = simulate_match_bo3(A1, O4)
    playoff_results_dict["uqf1"] = {
        "teams": (A1, O4),
        "winner": uqf1_winner,
        "loser": uqf1_loser,
        "score": uqf1_score,
    }

    uqf2_winner, uqf2_loser, uqf2_score = simulate_match_bo3(A2, O3)
    playoff_results_dict["uqf2"] = {
        "teams": (A2, O3),
        "winner": uqf2_winner,
        "loser": uqf2_loser,
        "score": uqf2_score,
    }

    uqf3_winner, uqf3_loser, uqf3_score = simulate_match_bo3(O1, A4)
    playoff_results_dict["uqf3"] = {
        "teams": (O1, A4),
        "winner": uqf3_winner,
        "loser": uqf3_loser,
        "score": uqf3_score,
    }

    uqf4_winner, uqf4_loser, uqf4_score = simulate_match_bo3(O2, A3)
    playoff_results_dict["uqf4"] = {
        "teams": (O2, A3),
        "winner": uqf4_winner,
        "loser": uqf4_loser,
        "score": uqf4_score,
    }

    # Lower Bracket R1 (losers UQF)
    lr1_1_winner, lr1_1_loser, lr1_1_score = simulate_match_bo3(
        uqf1_loser, uqf2_loser)
    playoff_results_dict["lr1_1"] = {
        "teams": (uqf1_loser, uqf2_loser),
        "winner": lr1_1_winner,
        "loser": lr1_1_loser,
        "score": lr1_1_score,
    }

    lr1_2_winner, lr1_2_loser, lr1_2_score = simulate_match_bo3(
        uqf3_loser, uqf4_loser)
    playoff_results_dict["lr1_2"] = {
        "teams": (uqf3_loser, uqf4_loser),
        "winner": lr1_2_winner,
        "loser": lr1_2_loser,
        "score": lr1_2_score,
    }

    # Upper Bracket SF
    usf1_winner, usf1_loser, usf1_score = simulate_match_bo3(
        uqf1_winner, uqf2_winner)
    playoff_results_dict["usf1"] = {
        "teams": (uqf1_winner, uqf2_winner),
        "winner": usf1_winner,
        "loser": usf1_loser,
        "score": usf1_score,
    }

    usf2_winner, usf2_loser, usf2_score = simulate_match_bo3(
        uqf3_winner, uqf4_winner)
    playoff_results_dict["usf2"] = {
        "teams": (uqf3_winner, uqf4_winner),
        "winner": usf2_winner,
        "loser": usf2_loser,
        "score": usf2_score,
    }

    # Lower Bracket R2
    lr2_1_winner, lr2_1_loser, lr2_1_score = simulate_match_bo3(
        lr1_1_winner, usf1_loser
    )
    playoff_results_dict["lr2_1"] = {
        "teams": (lr1_1_winner, usf1_loser),
        "winner": lr2_1_winner,
        "loser": lr2_1_loser,
        "score": lr2_1_score,
    }

    lr2_2_winner, lr2_2_loser, lr2_2_score = simulate_match_bo3(
        lr1_2_winner, usf2_loser
    )
    playoff_results_dict["lr2_2"] = {
        "teams": (lr1_2_winner, usf2_loser),
        "winner": lr2_2_winner,
        "loser": lr2_2_loser,
        "score": lr2_2_score,
    }

    # Lower Bracket R3
    lr3_winner, lr3_loser, lr3_score = simulate_match_bo3(
        lr2_1_winner, lr2_2_winner)
    playoff_results_dict["lr3"] = {
        "teams": (lr2_1_winner, lr2_2_winner),
        "winner": lr3_winner,
        "loser": lr3_loser,
        "score": lr3_score,
    }

    # Upper Final
    uf_winner, uf_loser, uf_score = simulate_match_bo3(
        usf1_winner, usf2_winner)
    playoff_results_dict["uf"] = {
        "teams": (usf1_winner, usf2_winner),
        "winner": uf_winner,
        "loser": uf_loser,
        "score": uf_score,
    }

    # Lower Final
    lf_winner, lf_loser, lf_score = simulate_match_bo5(uf_loser, lr3_winner)
    playoff_results_dict["lf"] = {
        "teams": (uf_loser, lr3_winner),
        "winner": lf_winner,
        "loser": lf_loser,
        "score": lf_score,
    }

    # Grand Final
    grandf_winner, grandf_loser, grandf_score = simulate_match_bo5(
        uf_winner, lf_winner)
    playoff_results_dict["grandf"] = {
        "teams": (uf_winner, lf_winner),
        "winner": grandf_winner,
        "loser": grandf_loser,
        "score": grandf_score,
    }

    playoff_best_4_teams = [grandf_winner, grandf_loser, lf_loser, lr3_loser]

    return playoff_results_dict, playoff_best_4_teams


def simulate_season(played_matches, groups, playoff_points, classification_points):

    # Simular temporada regular
    alpha_standings, omega_standings = simulate_regular_season(
        groups, played_matches)

    # Simular playoffs
    playoff_results_dict, playoff_top_4_teams = simulate_playoffs(
        alpha_standings, omega_standings
    )

    # Diccionario para almacenar los puntos de champions totales
    total_stats = defaultdict(lambda: {"puntos": 0})

    # Añadir los puntos de champions actuales
    for team, points in classification_points.items():
        total_stats[team]["puntos"] = points

    # Añadir los puntos de la temporada regular (real + simulado)
    for team, stats in {**alpha_standings, **omega_standings}.items():
        total_stats[team]["puntos"] += stats["victorias"]

    # Añadir los puntos según la posición de los playoffs
    for pos, team in enumerate(playoff_top_4_teams, 1):
        total_stats[team]["puntos"] += playoff_points.get(pos, 0)

    aux_qualified, qualified_teams_with_reasons = set(), list()

    # GF Winner y Loser
    qualified_teams_with_reasons.append(
        ("Clasificado como **Ganador** de los playoffs",
         playoff_top_4_teams[0])
    )
    qualified_teams_with_reasons.append(
        (
            "Clasificado por llegar a la Grand Final de los playoffs",
            playoff_top_4_teams[1],
        )
    )

    aux_qualified.add(playoff_top_4_teams[0])
    aux_qualified.add(playoff_top_4_teams[1])

    all_teams_sorted = sorted(
        total_stats.keys(), key=lambda team: total_stats[team]["puntos"], reverse=True
    )

    for team in all_teams_sorted:
        if len(aux_qualified) >= 4:
            break

        if team not in aux_qualified:
            aux_qualified.add(team)
            qualified_teams_with_reasons.append(
                (
                    f"Clasificado por puntos de Champions: {total_stats.get(team, 0).get('puntos')}",
                    team,
                )
            )

    return (
        qualified_teams_with_reasons,
        playoff_results_dict,
        total_stats,
        alpha_standings,
        omega_standings,
    )


def monte_carlo_simulation(
    n_simulations, played_matches, groups, playoff_points, classification_points
):

    results = Parallel(n_jobs=-1, backend="loky")(
        delayed(simulate_season)(
            played_matches, groups, playoff_points, classification_points
        )
        for _ in range(n_simulations)
    )

    standings_counter = defaultdict(int)

    for (
        qualified_teams,
        playoff_results_dict,
        total_stats,
        alpha_standings,
        omega_standings,
    ) in results:
        for reason, team in qualified_teams:
            standings_counter[team] += 1
    return {
        team: round(100 * count / n_simulations, 2)
        for team, count in standings_counter.items()
    }


### INIT STREAMLIT ##
st.set_page_config(
    page_title="Simulador de Clasificación Valornat Champions", layout="wide"
)
st.title("🎮 Simulador de Clasificación Valorant Champions tour 🏆")

if "played_matches" not in st.session_state:
    st.session_state.played_matches = data.played_matches

display_sidebar()

#### INIT UI ####
remaining_matches = generate_remaining_matches(
    data.groups, st.session_state.played_matches
)
simulated_matches_to_add = []
playoff_points = data.playoff_points
classification_points = data.clasification_points
groups = data.groups

with st.expander("🗓️ Simular Partidos Faltantes y sus Resultados"):
    st.write(
        "Selecciona los ganadores para los partidos restantes (se simulará un BO3 con el ganador seleccionado):"
    )
    for i, (team1, team2) in enumerate(remaining_matches):
        col1, col2, col3 = st.columns([0.35, 0.25, 0.4])
        with col1:
            st.write(f"**{team1} vs {team2}**")
        with col2:
            include_match = st.checkbox("Incluir", key=f"include_{i}")
        with col3:
            winner = st.selectbox(
                "Selecciona Ganador",
                [team1, team2],
                key=f"winner_{i}",
                disabled=not include_match,
                label_visibility="hidden",
            )

        if include_match:
            loser = team2 if winner == team1 else team1
            simulated_score = random.choice(["2-0", "2-1"])
            simulated_matches_to_add.append(
                {
                    "team1": team1,
                    "team2": team2,
                    "winner": winner,
                    "loser": loser,
                    "score": simulated_score,
                }
            )

with st.expander("📈 Simular una Temporada Completa"):
    if st.button("Simular Temporada"):
        st.info("Simulando una temporada...")
        current_played_matches = (
            st.session_state.played_matches + simulated_matches_to_add
        )

        (
            qualified_teams,
            playoff_results_dict,
            total_stats,
            alpha_standings,
            omega_standings,
        ) = simulate_season(
            current_played_matches, groups, playoff_points, classification_points
        )

        st.subheader("📈 Resultados de la Temporada Regular:")
        st.write("**Grupo Alpha:**")
        alpha_df = pd.DataFrame.from_dict(alpha_standings, orient="index").rename(
            columns={"victorias": "Victorias"}
        )
        st.dataframe(alpha_df)

        st.write("**Grupo Omega:**")
        omega_df = pd.DataFrame.from_dict(omega_standings, orient="index").rename(
            columns={"victorias": "Victorias"}
        )
        st.dataframe(omega_df)

        st.subheader("📊 Resultados de los Playoffs:")

        st.write("#### Resumen de Partidos de Playoffs:")
        for match_key, match_info in playoff_results_dict.items():
            st.write(
                f"- **{match_key.upper()}**: {match_info['teams'][0]} vs {match_info['teams'][1]} -> Ganador: **{match_info['winner']}** ({match_info['score']})"
            )

        st.subheader("🏆 Clasificados Finales:")

        for reason, team in qualified_teams:
            st.write(f"- **{team}**: {reason} ")

        st.success("Temporada simulada con éxito!")

st.header("📊 Simulación de Monte Carlo")
n_simulations = st.number_input(
    "Número de simulaciones:", 1000, 100000, 10000, 1000)
if st.button("Ejecutar Simulación"):
    with st.spinner("Simulando temporadas...", show_time=True):
        current_played_matches = (
            st.session_state.played_matches + simulated_matches_to_add
        )
        probs = monte_carlo_simulation(
            n_simulations,
            current_played_matches,
            groups,
            playoff_points,
            classification_points,
        )
    st.subheader("📊 Probabilidad de Clasificar (%)")
    results_df = pd.DataFrame(
        sorted(probs.items(), key=lambda x: -x[1]),
        columns=["Equipo", "Probabilidad (%)"],
    )
    st.dataframe(results_df, hide_index=True)
