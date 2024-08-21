import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils import *

# Gerar características iniciais das árvores
np.random.seed(42)

# Default Parameters
N = 1000  # Number of trees
T = 36  # Number of months in the simulation
critical_distance = 1.0  # Critical distance in meters
n_simulation = 500  # Number of Events
growth_rate = 0.387  # Monthly growth in meters
total_trees = 20  # Number of trees pruned per day
total_day = 20  # Number of days in a month
total_teams = 1 # Number of pruning teams

METRICS = {
    'PRECISION': 0.6820,
    'RECALL': 0.4496,
    'MAE_DISTANCE': 1.20
}

# Streamlit interface
st.title('Tree Growth and Pruning Simulation')

st.sidebar.header('Simulation Parameters')
N = st.sidebar.number_input('Number of trees', min_value=100, max_value=50000, value=N)
T = st.sidebar.number_input('Number of months', min_value=12, max_value=120, value=T)
critical_distance = st.sidebar.number_input('Critical distance (m)', 
                                             min_value=0.01, 
                                             max_value=10.00, 
                                             step=0.001, 
                                             format="%.3f",
                                             value=critical_distance)
growth_rate = st.sidebar.number_input('Monthly growth (m)', 
                                       min_value=0.001, 
                                       max_value=1.000, 
                                       step=0.001, 
                                       format="%.3f",
                                       value=growth_rate)
total_trees = st.sidebar.number_input('Number of trees pruned per day', min_value=1, max_value=100, value=total_trees)
total_day = st.sidebar.number_input('Number of days in a month', min_value=1, max_value=31, value=total_day)
total_teams = st.sidebar.number_input('Number of pruning teams', min_value=1, max_value=30, value=total_teams)
total_tree = total_trees * total_day * total_teams

# Create the efficiency selector
efficiency = st.sidebar.selectbox(
    'Select the field team efficiency:',
    ('Low efficiency', 'Medium efficiency', 'High efficiency'),
    index=2
)

if efficiency == 'High efficiency':
    prob_min = 0.9
elif efficiency == 'Medium efficiency':
    prob_min = 0.7
else:
    prob_min = 0.3

st.sidebar.header('Metrics Model')
METRICS['PRECISION'] = st.sidebar.number_input('Precision', 
                                                min_value=0.0001, 
                                                max_value=1.000, 
                                                step=0.0001, 
                                                format="%.4f",
                                                value=METRICS['PRECISION'])
METRICS['RECALL'] = st.sidebar.number_input('Recall', 
                                             min_value=0.0001, 
                                             max_value=1.000, 
                                             step=0.0001, 
                                             format="%.4f",
                                             value=METRICS['RECALL'])
METRICS['MAE_DISTANCE'] = st.sidebar.number_input('Mean Absolute Error (MAE) - Distance', 
                                                   min_value=0.01, 
                                                   max_value=100.00, 
                                                   step=0.01, 
                                                   format="%.2f",
                                                   value=METRICS['MAE_DISTANCE'])

if st.button('Run Simulation'):
    
    data = simulation(
        METRICS = METRICS,
        N = N,
        n_simulation = n_simulation,
        T = T,
        critical_distance = critical_distance,
        growth_rate = growth_rate,
        total_tree = total_tree,
        prob_min = prob_min
    )

    df_melted = create_dataframe_simulation(data, T)

    # Crie o gráfico usando Plotly
    fig = px.box(df_melted, x='variable', y='value', color='Estimativa',
                title='Impacto da Utilização do Modelo M e Crescimento das Árvores (TX)')   

    # Ajustes adicionais
    fig.update_layout(
        xaxis_title='Mês',
        yaxis_title='Quantidade',
        xaxis_tickangle=-30,
        width=1500,  # Largura ajustável
        height=500   # Altura ajustável
    )

    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig, use_container_width=True)

    df_table = create_table(df=df_melted)
    st.subheader('Average Pruning Estimates for Selected Months')
    st.table(df_table)
