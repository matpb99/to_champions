import streamlit as st
import pandas as pd
import asyncio
from collections import defaultdict
import data
from vlr_api import load_played_matches
import time

def get_map_diff(score_str):
    try:
        score1, score2 = map(int, score_str.split('-'))
        return score1 - score2
    except (ValueError, IndexError):
        return 0

def get_current_standings(played_matches, groups):
    standings = defaultdict(lambda: {'victorias': 0, 'diferencia_mapas': 0})

    for match in played_matches:
        winner = match['winner']
        loser = next((team for team in [match['team1'], match['team2']] if team != winner), None)
        if loser is None: continue

        map_diff = get_map_diff(match['score'])
        
        standings[winner]['victorias'] += 1
        standings[winner]['diferencia_mapas'] += abs(map_diff)
        standings[loser]['diferencia_mapas'] -= abs(map_diff)

    alpha = dict(sorted(
        ((k, v) for k, v in standings.items() if k in groups['alpha']),
        key=lambda item: (item[1]['victorias'], item[1]['diferencia_mapas']), 
        reverse=True
    ))
    omega = dict(sorted(
        ((k, v) for k, v in standings.items() if k in groups['omega']),
        key=lambda item: (item[1]['victorias'], item[1]['diferencia_mapas']), 
        reverse=True
    ))
    return alpha, omega

def display_sidebar():

    with st.sidebar:
        st.header("⚙️ Datos de Configuración")

        if st.button("Cargar Partidos Jugados desde la API"):
            cooldown_seconds = 3600  # 1 hour
            current_time = time.time()

            if 'last_api_call_time' not in st.session_state:
                st.session_state.last_api_call_time = 0

            time_elapsed = current_time - st.session_state.last_api_call_time

            if time_elapsed < cooldown_seconds:
                remaining_time = int(cooldown_seconds - time_elapsed)
                st.warning(f"Por favor, espera {remaining_time // 60} minutos y {remaining_time % 60} segundos antes de cargar partidos de nuevo.")
            else:
                with st.spinner("Cargando partidos desde la API...", show_time=True):
                    new_matches = load_played_matches()
                    # Deduplicate new_matches before storing in session_state
                    unique_matches = {}
                    for match in new_matches:
                        key = tuple(sorted((match["team1"], match["team2"]))) + (match["winner"],)
                        unique_matches[key] = match
                    st.session_state.played_matches = list(unique_matches.values())
                    st.session_state.last_api_call_time = current_time
                    st.success("Partidos cargados con éxito!")

        st.subheader("👥 Grupos de Equipos")
        st.dataframe(pd.DataFrame({
            "Grupo Alpha": data.groups['alpha'],
            "Grupo Omega": data.groups['omega']
        }), hide_index=True)
        
        st.subheader("📊 Puntos de Champions")
        st.dataframe(pd.DataFrame(list(data.clasification_points.items()), columns=['Equipo', 'Puntos']), hide_index=True)
        
        st.subheader("⚔️ Partidos Jugados")
        st.dataframe(pd.DataFrame(st.session_state.get('played_matches', [])), hide_index=True)

        st.subheader("📈 Resumen actual de los Grupos")
        alpha_standings, omega_standings = get_current_standings(st.session_state.get('played_matches', []), data.groups)

        st.write("**Grupo Alpha:**")
        alpha_data_for_df = [{'Equipo': team, **stats} for team, stats in alpha_standings.items()]
        alpha_df = pd.DataFrame(alpha_data_for_df).rename(columns={'victorias': 'Victorias', 'diferencia_mapas': 'Dif. Mapas'})
        st.dataframe(alpha_df, hide_index=True)

        st.write("**Grupo Omega:**")
        omega_data_for_df = [{'Equipo': team, **stats} for team, stats in omega_standings.items()]
        omega_df = pd.DataFrame(omega_data_for_df).rename(columns={'victorias': 'Victorias', 'diferencia_mapas': 'Dif. Mapas'})
        st.dataframe(omega_df, hide_index=True)