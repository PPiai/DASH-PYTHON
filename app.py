import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
import time
import os
from io import StringIO
import locale
import numpy as np
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA

# Configurar localização para formato brasileiro
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        pass

# Configuração da página
st.set_page_config(
    page_title="Meta Ads Dashboard Farol",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para estilização
st.markdown("""
<style>
    .metric-card {
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .metric-green {
        background-color: rgba(0, 200, 0, 0.1);
        border-left: 5px solid #00c800;
    }
    .metric-yellow {
        background-color: rgba(255, 200, 0, 0.1);
        border-left: 5px solid #ffc800;
    }
    .metric-red {
        background-color: rgba(255, 0, 0, 0.1);
        border-left: 5px solid #ff0000;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #000000;
        border-radius: 4px 4px 0 0;
        border-right: 1px solid rgba(255, 255, 255, 0.2);
        border-top: 1px solid rgba(255, 255, 255, 0.2);
        border-left: 1px solid rgba(255, 255, 255, 0.2);
        gap: 1px;
        padding: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        color: black;
    }
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .last-update {
        font-size: 0.8rem;
        color: #888;
    }
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 250px;
        background-color: #555;
        color: #fff;
        text-align: left;
        border-radius: 6px;
        padding: 10px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -125px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    .delta-positive {
        color: #00c800;
    }
    .delta-negative {
        color: #ff0000;
    }
    .warning-red {
        background-color: rgba(255, 0, 0, 0.1);
        color: #ff0000;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 15px;
        border-left: 5px solid #ff0000;
    }
    .warning-yellow {
        background-color: rgba(255, 200, 0, 0.1);
        color: #ffc800;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 15px;
        border-left: 5px solid #ffc800;
    }
</style>
""", unsafe_allow_html=True)

# Carregar dados das contas
@st.cache_data(ttl=3600)
def load_accounts():
    # Em um cenário real, isso seria carregado de um banco de dados ou arquivo
    contas = pd.DataFrame([
    {"nome_cliente": "Resimaq", "conta_id": "act_995978674482822", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Marluvas", "conta_id": "act_937586130079158", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Aguia de Ouro", "conta_id": "act_930138122661830", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "SRT Transportes ", "conta_id": "act_913549057234070", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "HS Gold", "conta_id": "act_905719624940336", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Remo Fenut", "conta_id": "act_898336111347971", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "CTC", "conta_id": "act_860506788095972", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Hidraucambio", "conta_id": "act_859616951882800", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Ornare Semijóias", "conta_id": "act_841878016587031", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Clero Brasil", "conta_id": "act_838288521687758", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Italian Gastronomia", "conta_id": "act_814045333572501", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Agromann", "conta_id": "act_764715671633746", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Absoluta Incorporação", "conta_id": "act_743422994203639", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Café com Leite", "conta_id": "act_733072060715959", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Suruka", "conta_id": "act_694252122331708", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "SmartX", "conta_id": "act_679012503781785", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Zatta", "conta_id": "act_656032961789593", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Recoplast", "conta_id": "act_623122470618153", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Lefer", "conta_id": "act_617886166202496", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Sartori Auto Peças", "conta_id": "act_616436801130224", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "GTL", "conta_id": "act_602220500784998", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Nila Photography", "conta_id": "act_5837453393018571", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Casa dos Motores", "conta_id": "act_556908113899805", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "AJL", "conta_id": "act_5557603504330426", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Calvin Klein", "conta_id": "act_535788031261479", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "MF Peças", "conta_id": "act_531544614131498", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Stone Mall", "conta_id": "act_531409504089794", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "UV Line", "conta_id": "act_513209639246301", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Trisul", "conta_id": "act_496159270236236", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Trisul (JL)", "conta_id": "act_496159270236236", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Monnaie", "conta_id": "act_1328655617999318", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "MaqCenter", "conta_id": "act_470618307419362", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Brasil Piscis", "conta_id": "act_458704915937220", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Nutriquality", "conta_id": "act_439991594112145", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Marlin Autos ", "conta_id": "act_432026079386037", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Supranet", "conta_id": "act_422110711745409", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Highaus", "conta_id": "act_420443957644515", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Adapter Sistemas", "conta_id": "act_413912314603205", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Comam", "conta_id": "act_394120044591493", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Biovit", "conta_id": "act_3896030874057266", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Proinfo - FIA", "conta_id": "act_3577843515771052", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Bawer Motores", "conta_id": "act_346860261810268", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Extinseto", "conta_id": "act_3461207023864", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Bahls Odontologia", "conta_id": "act_341929899811752", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Makebetter", "conta_id": "act_3236627973136982", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Alcance B2B", "conta_id": "act_2904536849786560", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Alcance", "conta_id": "act_2904536849786560", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Mega Coffee", "conta_id": "act_282434177103318", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Logline", "conta_id": "act_2786386548206132", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Pluralquimica", "conta_id": "act_2488064127938269", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "RTT", "conta_id": "act_231030318338724", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Dziabas", "conta_id": "act_2281392792260986", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Repsol", "conta_id": "act_2232590890444963", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "CSS Log", "conta_id": "act_220492102569024", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Evolution Signs", "conta_id": "act_218764335949405", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Vieira Rossi", "conta_id": "act_2149206938558605", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Condor", "conta_id": "act_203537889759095", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Ferragens Floresta", "conta_id": "act_199516851165071", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Panorama", "conta_id": "act_1915942465406802", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Intact Estojos", "conta_id": "act_1836117320469996", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Enmed", "conta_id": "act_1775072306366660", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Oftalmoclínica Américas", "conta_id": "act_1749225102281713", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Day Hospital", "conta_id": "act_1663531577433280", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Moretti Odontologia", "conta_id": "act_1641829612969953", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Metalsider", "conta_id": "act_1625896747769654", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Kalatec", "conta_id": "act_1604948507066510", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Mactoot", "conta_id": "act_155886204959659", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Amalog", "conta_id": "act_1557368498476976", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Gloria Rabello", "conta_id": "act_1503339850472458", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Auto Credcard", "conta_id": "act_131715405272596", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Polpa & Congelados", "conta_id": "act_1259525575587947", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "JTP Solution", "conta_id": "act_1209571203593781", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Tutto Casa", "conta_id": "act_1158215392516029", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Sérgio Calçados", "conta_id": "act_1145544443248370", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Wave Solutions", "conta_id": "act_1051202479011920", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Aquifero", "conta_id": "act_1038346274756810", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Poligarbo", "conta_id": "act_914691500545820", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Vivacril", "conta_id": "act_330431722463892", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "FOR-TY STORE", "conta_id": "act_7767604866623167", "token_acesso": "EAAII0Wm9NVMBOZBdFQXpiUvkwectRt6meoWO0caJJAyxzobVhJbgvrZBsIauWCNZCuwZCXR5ZAvRPiRyE6QyE6XBt5VUYkjKT4m0LtIiGE40BITjZCtiKQ4j8ndvbURD3iZCVTbvsAf6FAiJ22FDQVptOg7FA7Auz3Wa0M5Coe4ntCPCVjBQsypwFUpjOZCZBWuvWdQZDZD"},
    {"nome_cliente": "Exohair", "conta_id": "act_922812376352170", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
    {"nome_cliente": "Vogel", "conta_id": "act_921923696764459", "token_acesso": "EAGge1iO10QgBOwtjkzAVdKaZBoAXC8m8DcnDZA7op4oX7xZAGJ62ZAo40CJk744gcc1299ZBd4vENs176XhaIZC7ajgmAHoslH1RUT4A2QRb6SyZB28rfS0xcxCO3XZA5NJXxPAQcE6YU3QhdvzofXEGQ1WGOhX7ZCZCOvZBmlraXvZCirgczRsZBP52ZCRch9qBlBdMuaBwZDZD"},
])
    return contas

# Definir valores de referência para métricas
benchmarks = {
    "cpl": {"bom": 10, "atencao": 20},  # Custo por Lead
    "cpa": {"bom": 30, "atencao": 50},  # Custo por Aquisição
    "ctr": {"bom": 0.015, "atencao": 0.008},  # Taxa de Cliques
    "roas": {"bom": 3.0, "atencao": 2.0},  # Retorno sobre Investimento
    "frequencia": {"ideal_min": 1.5, "ideal_max": 3.0},  # Frequência
    "cpm": {"medio_min": 10, "medio_max": 25}  # Custo por Mil Impressões
}

# Tipos de conversão a serem considerados
CONVERSION_TYPES = [
    "offsite_conversion.custom",
    "lead",
    "purchase",
    "submit_application",
    "complete_registration",
    "onsite_conversion.messaging_conversation_started_7d"  # Conversas iniciadas
]

# Mapeamento de nomes de métricas para exibição amigável
METRIC_DISPLAY_NAMES = {
    "spend": "Valor Gasto",
    "impressions": "Impressões",
    "clicks": "Cliques",
    "ctr": "Taxa de Cliques",
    "cpm": "Custo por Mil Impressões",
    "conversions": "Conversões",
    "conversion_value": "Valor de Conversão",
    "cpa": "Custo por Aquisição",
    "cpc": "Custo por Clique",
    "roas": "Retorno sobre Investimento",
    "frequency": "Frequência",
    "reach": "Alcance",
    "account_name": "Nome da Conta",
    "campaign_name": "Nome da Campanha",
    "status": "Status",
    "updated_time": "Data de Atualização",
    "total_spend": "Gasto Total",
    "total_impressions": "Total de Impressões",
    "total_clicks": "Total de Cliques",
    "total_conversions": "Total de Conversões",
    "total_conversion_value": "Valor Total de Conversão",
    "avg_ctr": "CTR Médio",
    "avg_cpm": "CPM Médio",
    "avg_cpc": "CPC Médio",
    "avg_cpa": "CPA Médio",
    "avg_roas": "ROAS Médio",
    "avg_frequency": "Frequência Média",
    "total_reach": "Alcance Total",
    "variable": "Métrica",
    "value": "Valor"
}

# Função para formatar números no padrão brasileiro
def format_br(value, prefix="", suffix="", decimal_places=2):
    if isinstance(value, (int, float)):
        if decimal_places == 0:
            formatted = f"{int(value):,}".replace(",", ".")
        else:
            formatted = f"{value:,.{decimal_places}f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{prefix}{formatted}{suffix}"
    return f"{prefix}{value}{suffix}"

# Função para buscar dados da API do Meta
@st.cache_data(ttl=3600)
def fetch_meta_data(conta_id, token_acesso, start_date, end_date, prev_start_date, prev_end_date):
    try:
        # Buscar campanhas
        campaigns_url = f"https://graph.facebook.com/v22.0/{conta_id}/campaigns"
        campaigns_params = {
            "fields": "id,name,status,start_time,stop_time,updated_time",
            "access_token": token_acesso
        }
        
        campaigns_response = requests.get(campaigns_url, params=campaigns_params)
        
        if campaigns_response.status_code != 200:
            st.error(f"Erro ao buscar campanhas: {campaigns_response.text}")
            return None, None
        
        campaigns_data = campaigns_response.json().get('data', [])
        
        # Preparar dataframes de resultados
        current_results = []
        previous_results = []
        
        for campaign in campaigns_data:
            campaign_id = campaign['id']
            
            # Buscar insights para o período atual
            insights_url = f"https://graph.facebook.com/v22.0/{campaign_id}/insights"
            insights_params = {
                "fields": "spend,impressions,clicks,ctr,cpm,actions,action_values,frequency,reach",
                "time_range[since]": start_date,
                "time_range[until]": end_date,
                "level": "campaign",
                "access_token": token_acesso
            }
            
            insights_response = requests.get(insights_url, params=insights_params)
            
            if insights_response.status_code != 200:
                st.warning(f"Erro ao buscar insights para campanha {campaign['name']}: {insights_response.text}")
                continue
            
            insights_data = insights_response.json().get('data', [])
            
            if not insights_data:
                # Sem dados para esta campanha no período
                continue
            
            insights = insights_data[0]
            
            # Extrair ações (conversões) e valores
            conversions = {}
            conversion_value = 0
            total_conversions = 0
            
            if 'actions' in insights:
                for action in insights['actions']:
                    action_type = action.get('action_type')
                    if action_type in CONVERSION_TYPES:
                        value = int(action.get('value', 0))
                        conversions[action_type] = value
                        total_conversions += value
            
            if 'action_values' in insights:
                for action_value in insights['action_values']:
                    if action_value.get('action_type') in ['purchase']:
                        conversion_value += float(action_value.get('value', 0))
            
            # Calcular métricas
            spend = float(insights.get('spend', 0))
            impressions = int(insights.get('impressions', 0))
            clicks = int(insights.get('clicks', 0))
            ctr = float(insights.get('ctr', 0))
            cpm = float(insights.get('cpm', 0))
            frequency = float(insights.get('frequency', 0))
            reach = int(insights.get('reach', 0))
            
            # Calcular CPC, CPA e ROAS
            cpc = spend / clicks if clicks > 0 else 0
            cpa = spend / total_conversions if total_conversions > 0 else 0
            roas = conversion_value / spend if spend > 0 else 0
            
            # Adicionar aos resultados atuais
            current_results.append({
                'campaign_id': campaign_id,
                'campaign_name': campaign['name'],
                'status': campaign['status'],
                'updated_time': campaign.get('updated_time', ''),
                'spend': spend,
                'impressions': impressions,
                'clicks': clicks,
                'ctr': ctr,
                'cpm': cpm,
                'conversions': total_conversions,
                'conversion_details': conversions,
                'conversion_value': conversion_value,
                'cpa': cpa,
                'cpc': cpc,
                'roas': roas,
                'frequency': frequency,
                'reach': reach
            })
            
            # Buscar insights para o período anterior
            prev_insights_params = {
                "fields": "spend,impressions,clicks,ctr,cpm,actions,action_values,frequency,reach",
                "time_range[since]": prev_start_date,
                "time_range[until]": prev_end_date,
                "level": "campaign",
                "access_token": token_acesso
            }
            
            prev_insights_response = requests.get(insights_url, params=prev_insights_params)
            
            if prev_insights_response.status_code == 200:
                prev_insights_data = prev_insights_response.json().get('data', [])
                
                if prev_insights_data:
                    prev_insights = prev_insights_data[0]
                    
                    # Extrair ações (conversões) e valores para o período anterior
                    prev_conversions = {}
                    prev_conversion_value = 0
                    prev_total_conversions = 0
                    
                    if 'actions' in prev_insights:
                        for action in prev_insights['actions']:
                            action_type = action.get('action_type')
                            if action_type in CONVERSION_TYPES:
                                value = int(action.get('value', 0))
                                prev_conversions[action_type] = value
                                prev_total_conversions += value
                    
                    if 'action_values' in prev_insights:
                        for action_value in prev_insights['action_values']:
                            if action_value.get('action_type') in ['purchase']:
                                prev_conversion_value += float(action_value.get('value', 0))
                    
                    # Calcular métricas para o período anterior
                    prev_spend = float(prev_insights.get('spend', 0))
                    prev_impressions = int(prev_insights.get('impressions', 0))
                    prev_clicks = int(prev_insights.get('clicks', 0))
                    prev_ctr = float(prev_insights.get('ctr', 0))
                    prev_cpm = float(prev_insights.get('cpm', 0))
                    prev_frequency = float(prev_insights.get('frequency', 0))
                    prev_reach = int(prev_insights.get('reach', 0))
                    
                    # Calcular CPC, CPA e ROAS para o período anterior
                    prev_cpc = prev_spend / prev_clicks if prev_clicks > 0 else 0
                    prev_cpa = prev_spend / prev_total_conversions if prev_total_conversions > 0 else 0
                    prev_roas = prev_conversion_value / prev_spend if prev_spend > 0 else 0
                    
                    # Adicionar aos resultados anteriores
                    previous_results.append({
                        'campaign_id': campaign_id,
                        'campaign_name': campaign['name'],
                        'status': campaign['status'],
                        'updated_time': campaign.get('updated_time', ''),
                        'spend': prev_spend,
                        'impressions': prev_impressions,
                        'clicks': prev_clicks,
                        'ctr': prev_ctr,
                        'cpm': prev_cpm,
                        'conversions': prev_total_conversions,
                        'conversion_details': prev_conversions,
                        'conversion_value': prev_conversion_value,
                        'cpa': prev_cpa,
                        'cpc': prev_cpc,
                        'roas': prev_roas,
                        'frequency': prev_frequency,
                        'reach': prev_reach
                    })
        
        return pd.DataFrame(current_results), pd.DataFrame(previous_results)
    
    except Exception as e:
        st.error(f"Erro ao buscar dados: {str(e)}")
        return None, None

# Função para buscar dados diários
@st.cache_data(ttl=3600)
def fetch_daily_data(conta_id, token_acesso, campaign_id, start_date, end_date):
    try:
        # Buscar insights diários
        insights_url = f"https://graph.facebook.com/v22.0/{campaign_id}/insights"
        insights_params = {
            "fields": "spend,impressions,clicks,actions,action_values,reach",
            "time_range[since]": start_date,
            "time_range[until]": end_date,
            "time_increment": 1,
            "level": "campaign",
            "access_token": token_acesso
        }
        
        insights_response = requests.get(insights_url, params=insights_params)
        
        if insights_response.status_code != 200:
            st.warning(f"Erro ao buscar insights diários: {insights_response.text}")
            return None
        
        insights_data = insights_response.json().get('data', [])
        
        if not insights_data:
            return None
        
        # Processar dados diários
        daily_results = []
        
        for day_data in insights_data:
            date = day_data.get('date_start')
            
            # Extrair ações (conversões) e valores
            conversions = 0
            conversion_value = 0
            
            if 'actions' in day_data:
                for action in day_data['actions']:
                    if action.get('action_type') in CONVERSION_TYPES:
                        conversions += int(action.get('value', 0))
            
            if 'action_values' in day_data:
                for action_value in day_data['action_values']:
                    if action_value.get('action_type') in ['purchase']:
                        conversion_value += float(action_value.get('value', 0))
            
            # Calcular métricas
            spend = float(day_data.get('spend', 0))
            impressions = int(day_data.get('impressions', 0))
            clicks = int(day_data.get('clicks', 0))
            reach = int(day_data.get('reach', 0))
            
            daily_results.append({
                'date': date,
                'spend': spend,
                'impressions': impressions,
                'clicks': clicks,
                'conversions': conversions,
                'conversion_value': conversion_value,
                'reach': reach
            })
        
        return pd.DataFrame(daily_results)
    
    except Exception as e:
        st.error(f"Erro ao buscar dados diários: {str(e)}")
        return None

# Função para buscar dados dos últimos 3 meses para verificação de conversões
@st.cache_data(ttl=3600)
def fetch_last_3_months_data(conta_id, token_acesso):
    try:
        today = datetime.now()
        end_date = today.strftime('%Y-%m-%d')
        start_date = (today - timedelta(days=90)).strftime('%Y-%m-%d')
        
        # Buscar campanhas
        campaigns_url = f"https://graph.facebook.com/v22.0/{conta_id}/campaigns"
        campaigns_params = {
            "fields": "id,name",
            "access_token": token_acesso
        }
        
        campaigns_response = requests.get(campaigns_url, params=campaigns_params)
        
        if campaigns_response.status_code != 200:
            return 0, False
        
        campaigns_data = campaigns_response.json().get('data', [])
        
        total_purchases = 0
        has_purchases = False
        
        for campaign in campaigns_data:
            campaign_id = campaign['id']
            
            # Buscar insights
            insights_url = f"https://graph.facebook.com/v22.0/{campaign_id}/insights"
            insights_params = {
                "fields": "actions,action_values",
                "time_range[since]": start_date,
                "time_range[until]": end_date,
                "level": "campaign",
                "access_token": token_acesso
            }
            
            insights_response = requests.get(insights_url, params=insights_params)
            
            if insights_response.status_code != 200:
                continue
            
            insights_data = insights_response.json().get('data', [])
            
            if not insights_data:
                continue
            
            insights = insights_data[0]
            
            # Verificar compras
            if 'actions' in insights:
                for action in insights['actions']:
                    if action.get('action_type') == 'purchase':
                        total_purchases += int(action.get('value', 0))
                        has_purchases = True
        
        return total_purchases, has_purchases
    
    except Exception as e:
        st.error(f"Erro ao buscar dados dos últimos 3 meses: {str(e)}")
        return 0, False

# Função para prever tendências futuras
def predict_future_trends(daily_data, metric, days_to_predict=7):
    if daily_data is None or daily_data.empty or len(daily_data) < 3:
        return None
    
    # Preparar dados
    daily_data['date'] = pd.to_datetime(daily_data['date'])
    daily_data = daily_data.sort_values('date')
    
    # Criar feature numérica para dias
    daily_data['day_num'] = (daily_data['date'] - daily_data['date'].min()).dt.days
    
    # Treinar modelo de regressão linear
    X = daily_data[['day_num']]
    y = daily_data[metric]
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Gerar previsões
    last_day = daily_data['day_num'].max()
    future_days = pd.DataFrame({'day_num': range(last_day + 1, last_day + days_to_predict + 1)})
    predictions = model.predict(future_days)
    
    # Criar dataframe de previsões
    last_date = daily_data['date'].max()
    future_dates = [last_date + timedelta(days=i+1) for i in range(days_to_predict)]
    
    predictions_df = pd.DataFrame({
        'date': future_dates,
        metric: predictions
    })
    
    return predictions_df

# Função para determinar a cor do status com base no valor da métrica
def get_status_color(metric, value, delta=None, delta_conversions=None, delta_spend=None):
    # Caso especial: se as conversões aumentaram e o gasto diminuiu, o gasto está bom
    if metric == 'spend' and delta_conversions is not None and delta_spend is not None:
        if delta_conversions > 0 and delta_spend < 0:
            return "green"
    
    # Se delta for fornecido, usar para determinar a cor
    if delta is not None:
        # Métricas onde diminuição é positiva (verde se diminuir, vermelho se aumentar)
        if metric in ['cpl', 'cpa', 'cpc', 'cpm']:
            if delta < 0:
                return "green"  # Diminuiu (bom)
            else:
                return "red"    # Aumentou (ruim)
        
        # Frequência: caso especial (verde se diminuir, amarelo se aumentar)
        elif metric == 'frequencia':
            if delta < 0:
                return "green"  # Diminuiu (bom)
            else:
                return "yellow" # Aumentou (atenção)
        
        # Outras métricas (verde se aumentar mais de 10%, amarelo se variar menos de 10%, vermelho se cair mais de 10%)
        else:
            if delta > 0:
                return "green"  # Aumentou (bom)
            elif delta >= -10:
                return "yellow" # Caiu menos de 10% (médio)
            else:
                return "red"    # Caiu mais de 10% (ruim)
    
    # Caso contrário, usar benchmarks
    if metric == 'cpl' or metric == 'cpa':
        if value <= benchmarks[metric]['bom']:
            return "green"
        elif value <= benchmarks[metric]['atencao']:
            return "yellow"
        else:
            return "red"
    elif metric == 'ctr':
        if value >= benchmarks[metric]['bom']:
            return "green"
        elif value >= benchmarks[metric]['atencao']:
            return "yellow"
        else:
            return "red"
    elif metric == 'roas':
        if value >= benchmarks[metric]['bom']:
            return "green"
        elif value >= benchmarks[metric]['atencao']:
            return "yellow"
        else:
            return "red"
    elif metric == 'frequencia':
        if benchmarks[metric]['ideal_min'] <= value <= benchmarks[metric]['ideal_max']:
            return "green"
        elif value > benchmarks[metric]['ideal_max']:
            return "yellow"
        else:
            return "red"
    else:
        return "gray"

# Função para criar um cartão de métrica com status de cor
def metric_card(title, value, prefix="", suffix="", status_color="gray", delta=None, tooltip=None, conversion_details=None, delta_conversions=None, delta_spend=None):
    # Formatar valor no padrão brasileiro
    if isinstance(value, (int, float)):
        if title in ['impressions', 'clicks', 'conversions', 'reach']:
            formatted_value = format_br(value, prefix, suffix, 0)
        else:
            formatted_value = format_br(value, prefix, suffix, 2)
    else:
        formatted_value = f"{prefix}{value}{suffix}"
    
    # Formatar delta
    delta_html = ""
    if delta is not None:
        arrow = "↑" if delta >= 0 else "↓"
        delta_color = "delta-positive" if delta >= 0 else "delta-negative"
        
        # Inverter cores para métricas onde diminuição é positiva
        if title in ['cpl', 'cpa', 'cpc', 'cpm', 'frequencia']:
            delta_color = "delta-negative" if delta >= 0 else "delta-positive"
            
        delta_html = f'<span class="{delta_color}">{arrow} {format_br(abs(delta), "", "%", 1)}</span>'
    
    # Determinar cor de fundo com base na variação
    if delta is not None:
        # Caso especial: se as conversões aumentaram e o gasto diminuiu, o gasto está bom
        if title == 'spend' and delta_conversions is not None and delta_spend is not None:
            if delta_conversions > 0 and delta_spend < 0:
                status_color = "green"
        # Métricas onde diminuição é positiva
        elif title in ['cpl', 'cpa', 'cpc', 'cpm']:
            status_color = "green" if delta < 0 else "red"
        # Frequência: caso especial
        elif title == 'frequencia':
            status_color = "green" if delta < 0 else "yellow"
        # Outras métricas
        else:
            if delta > 0:
                status_color = "green"  # Aumentou (bom)
            elif delta >= -10:
                status_color = "yellow" # Caiu menos de 10% (médio)
            else:
                status_color = "red"    # Caiu mais de 10% (ruim)
    
    # Formatar tooltip
    tooltip_html = ""
    if tooltip:
        tooltip_content = tooltip
        
        # Adicionar detalhes de conversão se disponíveis
        if title == 'conversions' and conversion_details:
            tooltip_content += "<br><br><b>Detalhes:</b><br>"
            for conv_type, conv_value in conversion_details.items():
                # Traduzir tipos de conversão
                type_name = {
                    "offsite_conversion.custom": "Conversão personalizada",
                    "lead": "Leads gerados",
                    "purchase": "Compras",
                    "submit_application": "Envio de formulário",
                    "complete_registration": "Cadastro concluído",
                    "onsite_conversion.messaging_conversation_started_7d": "Conversas iniciadas"
                }.get(conv_type, conv_type)
                
                tooltip_content += f"{type_name}: {conv_value}<br>"
        
        tooltip_html = f"""
        <div class="tooltip">ℹ️
            <span class="tooltiptext">{tooltip_content}</span>
        </div>
        """
    
    return f"""
    <div class="metric-card metric-{status_color}">
        <h3>{title.upper()} {tooltip_html}</h3>
        <h2>{formatted_value}</h2>
        {delta_html}
    </div>
    """

# Função principal do dashboard
def main():
    # Cabeçalho
    st.title("📊 Meta Ads Dashboard Farol")
    st.markdown("Monitoramento de desempenho de campanhas do Meta Ads com sistema de farol")
    
    # Carregar contas
    contas = load_accounts()
    
    # Barra lateral para filtros
    st.sidebar.title("Filtros")
    
    # Seleção de contas
    selected_accounts = st.sidebar.multiselect(
        "Selecione as contas",
        options=contas['nome_cliente'].tolist(),
        default=contas['nome_cliente'].tolist()[:5]  # Padrão para as primeiras 5 contas
    )
    
    # Seleção de intervalo de datas
    today = datetime.now()
    max_date = today
    min_date = today - timedelta(days=365)  # Limite de 1 ano atrás
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(
            "Data inicial",
            value=today - timedelta(days=7),
            min_value=min_date,
            max_value=max_date
        )
    with col2:
        end_date = st.date_input(
            "Data final",
            value=today,
            min_value=min_date,
            max_value=max_date
        )
    
    # Validar intervalo de datas
    if start_date > end_date:
        st.sidebar.error("A data inicial deve ser anterior à data final.")
        return
    
    # Calcular período anterior para comparação
    date_diff = (end_date - start_date).days + 1
    prev_end_date = start_date - timedelta(days=1)
    prev_start_date = prev_end_date - timedelta(days=date_diff - 1)
    
    # Formatar datas para API
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    prev_start_date_str = prev_start_date.strftime('%Y-%m-%d')
    prev_end_date_str = prev_end_date.strftime('%Y-%m-%d')
    
    # Filtro de status da campanha
    status_options = ["ACTIVE", "PAUSED", "COMPLETED", "ALL"]
    selected_status = st.sidebar.selectbox(
        "Status da campanha",
        options=status_options,
        index=3  # Padrão para ALL
    )
    
    # Botão para atualizar dados
    if st.sidebar.button("Atualizar dados"):
        st.cache_data.clear()
        st.experimental_rerun()
    
    # Hora da última atualização
    last_update = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    st.sidebar.markdown(f"**Última atualização:** {last_update}")
    
    # Botão para exportar dados
    st.sidebar.markdown("### Exportar dados")
    export_format = st.sidebar.selectbox(
        "Formato",
        options=["CSV", "Excel"],
        index=0
    )
    
    # Filtrar contas com base na seleção
    filtered_contas = contas[contas['nome_cliente'].isin(selected_accounts)]
    
    # Inicializar contêineres para seções do dashboard
    kpi_container = st.container()
    charts_container = st.container()
    table_container = st.container()
    
    # Buscar e processar dados para as contas selecionadas
    all_current_data = []
    all_previous_data = []
    account_summaries = []
    
    with st.spinner("Carregando dados..."):
        for _, conta in filtered_contas.iterrows():
            current_data, previous_data = fetch_meta_data(
                conta['conta_id'], 
                conta['token_acesso'], 
                start_date_str, 
                end_date_str,
                prev_start_date_str,
                prev_end_date_str
            )
            
            if current_data is not None and not current_data.empty:
                current_data['account_name'] = conta['nome_cliente']
                current_data['account_id'] = conta['conta_id']
                current_data['token_acesso'] = conta['token_acesso']
                all_current_data.append(current_data)
                
                # Calcular resumo da conta
                account_summary = {
                    'account_name': conta['nome_cliente'],
                    'account_id': conta['conta_id'],
                    'token_acesso': conta['token_acesso'],
                    'campaigns': len(current_data),
                    'total_spend': current_data['spend'].sum(),
                    'total_impressions': current_data['impressions'].sum(),
                    'total_clicks': current_data['clicks'].sum(),
                    'total_conversions': current_data['conversions'].sum(),
                    'total_conversion_value': current_data['conversion_value'].sum(),
                    'conversion_details': {},
                    'avg_ctr': current_data['clicks'].sum() / current_data['impressions'].sum() if current_data['impressions'].sum() > 0 else 0,
                    'avg_cpm': current_data['spend'].sum() / (current_data['impressions'].sum() / 1000) if current_data['impressions'].sum() > 0 else 0,
                    'avg_cpc': current_data['spend'].sum() / current_data['clicks'].sum() if current_data['clicks'].sum() > 0 else 0,
                    'avg_cpa': current_data['spend'].sum() / current_data['conversions'].sum() if current_data['conversions'].sum() > 0 else 0,
                    'avg_roas': current_data['conversion_value'].sum() / current_data['spend'].sum() if current_data['spend'].sum() > 0 else 0,
                    'avg_frequency': current_data['frequency'].mean(),
                    'total_reach': current_data['reach'].sum()
                }
                
                # Agregar detalhes de conversão
                all_conversion_details = {}
                for _, row in current_data.iterrows():
                    if isinstance(row['conversion_details'], dict):
                        for conv_type, conv_value in row['conversion_details'].items():
                            if conv_type in all_conversion_details:
                                all_conversion_details[conv_type] += conv_value
                            else:
                                all_conversion_details[conv_type] = conv_value
                
                account_summary['conversion_details'] = all_conversion_details
                account_summaries.append(account_summary)
            
            if previous_data is not None and not previous_data.empty:
                previous_data['account_name'] = conta['nome_cliente']
                all_previous_data.append(previous_data)
    
    # Combinar todos os dados
    if all_current_data and all_previous_data:
        combined_current_data = pd.concat(all_current_data, ignore_index=True)
        combined_previous_data = pd.concat(all_previous_data, ignore_index=True)
        account_summary_df = pd.DataFrame(account_summaries)
        
        # Filtrar por status da campanha se não for ALL
        if selected_status != "ALL":
            combined_current_data = combined_current_data[combined_current_data['status'] == selected_status]
            combined_previous_data = combined_previous_data[combined_previous_data['status'] == selected_status]
        
        # Verificar se é uma única conta
        is_single_account = len(filtered_contas) == 1
        
        # Se for uma única conta, verificar compras nos últimos 3 meses
        if is_single_account:
            account_id = filtered_contas.iloc[0]['conta_id']
            token_acesso = filtered_contas.iloc[0]['token_acesso']
            
            total_purchases, has_purchases = fetch_last_3_months_data(account_id, token_acesso)
            
            if has_purchases:
                if total_purchases < 10:
                    st.markdown(f"""
                    <div class="warning-red">
                        <strong>⚠️ Alerta de Red Flag:</strong> Esta conta teve apenas {total_purchases} compras nos últimos 3 meses, o que está abaixo do mínimo recomendado de 10 compras.
                    </div>
                    """, unsafe_allow_html=True)
                elif total_purchases < 20:
                    st.markdown(f"""
                    <div class="warning-yellow">
                        <strong>⚠️ Alerta de Yellow Flag:</strong> Esta conta teve apenas {total_purchases} compras nos últimos 3 meses, o que está abaixo do ideal de 20 compras.
                    </div>
                    """, unsafe_allow_html=True)
        
        # Seção de Resumo KPI
        with kpi_container:
            st.markdown("## 📈 Resumo KPI")
            
            # Calcular métricas gerais
            total_spend = combined_current_data['spend'].sum()
            total_impressions = combined_current_data['impressions'].sum()
            total_clicks = combined_current_data['clicks'].sum()
            total_conversions = combined_current_data['conversions'].sum()
            total_conversion_value = combined_current_data['conversion_value'].sum()
            total_reach = combined_current_data['reach'].sum()
            
            avg_ctr = total_clicks / total_impressions if total_impressions > 0 else 0
            avg_cpm = total_spend / (total_impressions / 1000) if total_impressions > 0 else 0
            avg_cpc = total_spend / total_clicks if total_clicks > 0 else 0
            avg_cpa = total_spend / total_conversions if total_conversions > 0 else 0
            avg_roas = total_conversion_value / total_spend if total_spend > 0 else 0
            avg_frequency = combined_current_data['frequency'].mean()
            
            # Calcular métricas do período anterior
            prev_total_spend = combined_previous_data['spend'].sum()
            prev_total_impressions = combined_previous_data['impressions'].sum()
            prev_total_clicks = combined_previous_data['clicks'].sum()
            prev_total_conversions = combined_previous_data['conversions'].sum()
            prev_total_conversion_value = combined_previous_data['conversion_value'].sum()
            prev_total_reach = combined_previous_data['reach'].sum()
            
            prev_avg_ctr = prev_total_clicks / prev_total_impressions if prev_total_impressions > 0 else 0
            prev_avg_cpm = prev_total_spend / (prev_total_impressions / 1000) if prev_total_impressions > 0 else 0
            prev_avg_cpc = prev_total_spend / prev_total_clicks if prev_total_clicks > 0 else 0
            prev_avg_cpa = prev_total_spend / prev_total_conversions if prev_total_conversions > 0 else 0
            prev_avg_roas = prev_total_conversion_value / prev_total_spend if prev_total_spend > 0 else 0
            prev_avg_frequency = combined_previous_data['frequency'].mean()
            
            # Calcular variações percentuais
            delta_spend = ((total_spend - prev_total_spend) / prev_total_spend * 100) if prev_total_spend > 0 else 0
            delta_impressions = ((total_impressions - prev_total_impressions) / prev_total_impressions * 100) if prev_total_impressions > 0 else 0
            delta_clicks = ((total_clicks - prev_total_clicks) / prev_total_clicks * 100) if prev_total_clicks > 0 else 0
            delta_conversions = ((total_conversions - prev_total_conversions) / prev_total_conversions * 100) if prev_total_conversions > 0 else 0
            delta_conversion_value = ((total_conversion_value - prev_total_conversion_value) / prev_total_conversion_value * 100) if prev_total_conversion_value > 0 else 0
            delta_reach = ((total_reach - prev_total_reach) / prev_total_reach * 100) if prev_total_reach > 0 else 0
            
            delta_ctr = ((avg_ctr - prev_avg_ctr) / prev_avg_ctr * 100) if prev_avg_ctr > 0 else 0
            delta_cpm = ((avg_cpm - prev_avg_cpm) / prev_avg_cpm * 100) if prev_avg_cpm > 0 else 0
            delta_cpc = ((avg_cpc - prev_avg_cpc) / prev_avg_cpc * 100) if prev_avg_cpc > 0 else 0
            delta_cpa = ((avg_cpa - prev_avg_cpa) / prev_avg_cpa * 100) if prev_avg_cpa > 0 else 0
            delta_roas = ((avg_roas - prev_avg_roas) / prev_avg_roas * 100) if prev_avg_roas > 0 else 0
            delta_frequency = ((avg_frequency - prev_avg_frequency) / prev_avg_frequency * 100) if prev_avg_frequency > 0 else 0
            
            # Agregar todos os detalhes de conversão
            all_conversion_details = {}
            for _, row in combined_current_data.iterrows():
                if isinstance(row['conversion_details'], dict):
                    for conv_type, conv_value in row['conversion_details'].items():
                        if conv_type in all_conversion_details:
                            all_conversion_details[conv_type] += conv_value
                        else:
                            all_conversion_details[conv_type] = conv_value
            
            # Criar cartões KPI em colunas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(metric_card(
                    "Gasto Total", 
                    total_spend, 
                    prefix="R$ ", 
                    delta=delta_spend,
                    delta_conversions=delta_conversions,
                    delta_spend=delta_spend,
                    tooltip="Total investido nas campanhas selecionadas"
                ), unsafe_allow_html=True)
                
                st.markdown(metric_card(
                    "CTR", 
                    avg_ctr * 100, 
                    suffix="%", 
                    status_color=get_status_color("ctr", avg_ctr, delta_ctr),
                    delta=delta_ctr,
                    tooltip="Taxa de cliques (Clicks / Impressões)"
                ), unsafe_allow_html=True)
                
                st.markdown(metric_card(
                "Impressões", 
                f"{total_impressions:,}".replace(",", "."),  # aqui formatamos com pontos nos milhares
                delta=delta_impressions,
                status_color=get_status_color("impressions", 0, delta_impressions),
                tooltip="Número total de vezes que os anúncios foram exibidos"
                ), unsafe_allow_html=True)

            
            with col2:
                st.markdown(metric_card(
                    "CPM", 
                    avg_cpm, 
                    prefix="R$ ", 
                    delta=delta_cpm,
                    status_color=get_status_color("cpm", 0, delta_cpm),
                    tooltip="Custo por mil impressões"
                ), unsafe_allow_html=True)

                st.markdown(metric_card(
                "Conversões", 
                f"{total_conversions:,}".replace(",", "."),  # ← formatação aplicada aqui
                delta=delta_conversions,
                status_color=get_status_color("conversions", 0, delta_conversions),
                tooltip="Total de leads, compras ou registros completos",
                conversion_details=all_conversion_details
                ), unsafe_allow_html=True)

                st.markdown(metric_card(
                    "CPA", 
                    avg_cpa, 
                    prefix="R$ ", 
                    status_color=get_status_color("cpa", avg_cpa, delta_cpa),
                    delta=delta_cpa,
                    tooltip="Custo por aquisição (Gasto / Conversões)"
                ), unsafe_allow_html=True)
            
            with col3:
                st.markdown(metric_card(
                    "ROAS", 
                    avg_roas, 
                    status_color=get_status_color("roas", avg_roas, delta_roas),
                    delta=delta_roas,
                    tooltip="Retorno sobre investimento em anúncios (Valor / Gasto)"
                ), unsafe_allow_html=True)
                
                st.markdown(metric_card(
                    "Frequência", 
                    avg_frequency, 
                    status_color=get_status_color("frequencia", avg_frequency, delta_frequency),
                    delta=delta_frequency,
                    tooltip="Média de vezes que uma pessoa viu seus anúncios"
                ), unsafe_allow_html=True)

                st.markdown(metric_card(
                    "Receita", 
                    total_conversion_value, 
                    prefix="R$ ", 
                    delta=delta_conversion_value,
                    status_color=get_status_color("conversion_value", 0, delta_conversion_value),
                    tooltip="Valor total gerado pelas conversões"
                ), unsafe_allow_html=True)
            
            with col4:
                st.markdown(metric_card(
                    "CPC", 
                    avg_cpc, 
                    prefix="R$ ", 
                    delta=delta_cpc,
                    status_color=get_status_color("cpc", 0, delta_cpc),
                    tooltip="Custo por clique (Gasto / Cliques)"
                ), unsafe_allow_html=True)
            
                st.markdown(metric_card(
                "Cliques", 
                f"{total_clicks:,}".replace(",", "."),  # ← formato 1.234.567 aplicado
                delta=delta_clicks,
                status_color=get_status_color("clicks", 0, delta_clicks),
                tooltip="Número total de cliques nos anúncios"
                ), unsafe_allow_html=True)
                
                st.markdown(metric_card(
                "Alcance", 
                f"{total_reach:,}".replace(",", "."),  # ← formato 1.234.567 aplicado
                delta=delta_reach,
                status_color=get_status_color("reach", 0, delta_reach),
                tooltip="Número de pessoas únicas que viram seus anúncios"
                ), unsafe_allow_html=True)
             
        
        # Seção de Gráficos
        with charts_container:
            st.markdown("## 📊 Visualizações")
            
            # Verificar se apenas uma conta foi selecionada
            if is_single_account:
                # Visualizações específicas para uma única conta
                account_data = account_summary_df.iloc[0]
                account_name = account_data['account_name']
                account_id = account_data['account_id']
                token_acesso = account_data['token_acesso']
                
                st.markdown(f"### Análise da conta: {account_name}")
                
                # Seletor de métricas para gráficos
                metric_options = {
                    "Gasto": "spend",
                    "Impressões": "impressions",
                    "Cliques": "clicks",
                    "Conversões": "conversions",
                    "Valor de Conversão": "conversion_value",
                    "Alcance": "reach"
                }
                
                # Criar abas para diferentes visualizações
                chart_tabs = st.tabs([
                    "Tendência Diária", 
                    "Desempenho por Campanha", 
                    "Previsão de Tendências",
                    "Análise de Frequência",
                    "Comparação de Evolução"
                ])
                
                # Tab 1: Tendência Diária
                with chart_tabs[0]:
                    # Mover o seletor de métricas para cima do gráfico
                    selected_metrics = st.multiselect(
                        "Selecione as métricas para visualizar",
                        options=list(metric_options.keys()),
                        default=["Gasto", "Conversões"]
                    )
                    
                    if selected_metrics:
                        # Buscar dados diários para a conta
                        campaign_ids = combined_current_data[combined_current_data['account_id'] == account_id]['campaign_id'].unique()
                        
                        all_daily_data = []
                        for campaign_id in campaign_ids:
                            daily_data = fetch_daily_data(
                                account_id, 
                                token_acesso, 
                                campaign_id, 
                                start_date_str, 
                                end_date_str
                            )
                            
                            if daily_data is not None and not daily_data.empty:
                                daily_data['campaign_id'] = campaign_id
                                all_daily_data.append(daily_data)
                        
                        if all_daily_data:
                            combined_daily_data = pd.concat(all_daily_data, ignore_index=True)
                            
                            # Agregar dados por dia
                            daily_summary = combined_daily_data.groupby('date').agg({
                                'spend': 'sum',
                                'impressions': 'sum',
                                'clicks': 'sum',
                                'conversions': 'sum',
                                'conversion_value': 'sum',
                                'reach': 'sum'
                            }).reset_index()
                            
                            # Gráfico de linha para métricas selecionadas
                            fig_line = go.Figure()
                            
                            for metric_name in selected_metrics:
                                metric_key = metric_options[metric_name]
                                
                                fig_line.add_trace(go.Scatter(
                                    x=daily_summary['date'],
                                    y=daily_summary[metric_key],
                                    name=metric_name,
                                    mode='lines+markers'
                                ))
                            
                            fig_line.update_layout(
                                title=f'Tendência diária - {account_name}',
                                xaxis_title='Data',
                                yaxis_title='Valor',
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=1.02,
                                    xanchor="right",
                                    x=1
                                )
                            )
                            
                            st.plotly_chart(fig_line, use_container_width=True)
                        else:
                            st.warning("Não foi possível obter dados diários para esta conta.")
                    else:
                        st.warning("Selecione pelo menos uma métrica para visualizar.")
                
                # Tab 2: Desempenho por Campanha
                with chart_tabs[1]:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Gráfico de barras para campanhas por gasto
                        top_campaigns = combined_current_data[combined_current_data['account_id'] == account_id].sort_values('spend', ascending=False).head(10)
                        
                        fig_bar_campaign = px.bar(
                            top_campaigns,
                            x='campaign_name',
                            y='spend',
                            title=f'Top 10 Campanhas por Gasto - {account_name}',
                            color='conversions',
                            color_continuous_scale='Viridis',
                            hover_data=['clicks', 'conversions', 'cpa', 'roas'],
                            labels={
                                'campaign_name': 'Nome da Campanha',
                                'spend': 'Valor Gasto',
                                'clicks': 'Cliques',
                                'conversions': 'Conversões',
                                'cpa': 'CPA',
                                'roas': 'ROAS'
                            }
                        )
                        fig_bar_campaign.update_layout(
                            xaxis_title="Nome da Campanha", 
                            yaxis_title="Valor Gasto (R$)",
                            xaxis={'categoryorder':'total descending'}
                        )
                        st.plotly_chart(fig_bar_campaign, use_container_width=True)
                    
                    with col2:
                        # Gráfico de barras para campanhas por conversões
                        top_conv_campaigns = combined_current_data[combined_current_data['account_id'] == account_id].sort_values('conversions', ascending=False).head(10)
                        
                        fig_bar_conv = px.bar(
                            top_conv_campaigns,
                            x='campaign_name',
                            y='conversions',
                            title=f'Top 10 Campanhas por Conversões - {account_name}',
                            color='cpa',
                            color_continuous_scale='RdYlGn_r',
                            hover_data=['spend', 'clicks', 'cpa', 'roas'],
                            labels={
                                'campaign_name': 'Nome da Campanha',
                                'conversions': 'Conversões',
                                'spend': 'Valor Gasto',
                                'clicks': 'Cliques',
                                'cpa': 'CPA',
                                'roas': 'ROAS'
                            }
                        )
                        fig_bar_conv.update_layout(
                            xaxis_title="Nome da Campanha", 
                            yaxis_title="Conversões",
                            xaxis={'categoryorder':'total descending'}
                        )
                        st.plotly_chart(fig_bar_conv, use_container_width=True)
                    
                    # Gráfico de dispersão para CPA vs ROAS
                    fig_scatter = px.scatter(
                        combined_current_data[combined_current_data['account_id'] == account_id],
                        x='cpa',
                        y='roas',
                        size='spend',
                        color='conversions',
                        hover_name='campaign_name',
                        title=f'CPA vs ROAS por Campanha - {account_name}',
                        log_x=True,
                        labels={
                            'cpa': 'CPA (R$)',
                            'roas': 'ROAS',
                            'spend': 'Valor Gasto',
                            'conversions': 'Conversões',
                            'campaign_name': 'Nome da Campanha'
                        }
                    )
                    
                    # Adicionar linhas de referência
                    fig_scatter.add_hline(y=benchmarks['roas']['bom'], line_dash="dash", line_color="green", annotation_text="ROAS Bom")
                    fig_scatter.add_hline(y=benchmarks['roas']['atencao'], line_dash="dash", line_color="orange", annotation_text="ROAS Atenção")
                    fig_scatter.add_vline(x=benchmarks['cpa']['bom'], line_dash="dash", line_color="green", annotation_text="CPA Bom")
                    fig_scatter.add_vline(x=benchmarks['cpa']['atencao'], line_dash="dash", line_color="orange", annotation_text="CPA Atenção")
                    
                    fig_scatter.update_layout(
                        xaxis_title="CPA (R$)",
                        yaxis_title="ROAS"
                    )
                    
                    st.plotly_chart(fig_scatter, use_container_width=True)
                
                # Tab 3: Previsão de Tendências
                with chart_tabs[2]:
                    # Seletor de métricas para previsão
                    selected_metrics = st.multiselect(
                        "Selecione as métricas para prever",
                        options=list(metric_options.keys()),
                        default=["Gasto", "Conversões"],
                        key="forecast_metrics"
                    )
                    
                    # Adicionar seletor para tipo de visualização
                    visualization_type = st.selectbox(
                        "Tipo de visualização",
                        options=["Gráfico", "Tabela"],
                        index=0
                    )
                    
                    if selected_metrics:
                        # Buscar dados diários para a conta
                        campaign_ids = combined_current_data[combined_current_data['account_id'] == account_id]['campaign_id'].unique()
                        
                        all_daily_data = []
                        for campaign_id in campaign_ids:
                            daily_data = fetch_daily_data(
                                account_id, 
                                token_acesso, 
                                campaign_id, 
                                start_date_str, 
                                end_date_str
                            )
                            
                            if daily_data is not None and not daily_data.empty:
                                daily_data['campaign_id'] = campaign_id
                                all_daily_data.append(daily_data)
                        
                        if all_daily_data:
                            combined_daily_data = pd.concat(all_daily_data, ignore_index=True)
                            
                            # Agregar dados por dia
                            daily_summary = combined_daily_data.groupby('date').agg({
                                'spend': 'sum',
                                'impressions': 'sum',
                                'clicks': 'sum',
                                'conversions': 'sum',
                                'conversion_value': 'sum',
                                'reach': 'sum'
                            }).reset_index()
                            
                            # Gerar previsões para as métricas selecionadas
                            st.markdown("### Previsão de tendências para os próximos 7 dias")
                            st.markdown("*Baseado no crescimento/queda observado no período selecionado*")
                            
                            for metric_name in selected_metrics:
                                metric_key = metric_options[metric_name]
                                
                                # Prever tendência futura
                                predictions_df = predict_future_trends(daily_summary, metric_key)
                                
                                if predictions_df is not None:
                                    st.markdown(f"#### {metric_name}")
                                    
                                    if visualization_type == "Gráfico":
                                        # Combinar dados históricos e previsões
                                        historical_data = daily_summary[['date', metric_key]].copy()
                                        historical_data['tipo'] = 'Histórico'
                                        
                                        predictions_df['tipo'] = 'Previsão'
                                        combined_data = pd.concat([historical_data, predictions_df])
                                        
                                        # Criar gráfico
                                        fig_forecast = px.line(
                                            combined_data,
                                            x='date',
                                            y=metric_key,
                                            color='tipo',
                                            title=f'Previsão de {metric_name} - {account_name}',
                                            color_discrete_map={'Histórico': 'blue', 'Previsão': 'red'},
                                            labels={
                                                'date': 'Data',
                                                metric_key: metric_name,
                                                'tipo': 'Tipo de Dado'
                                            }
                                        )
                                        
                                        fig_forecast.update_layout(
                                            xaxis_title="Data",
                                            yaxis_title=f"{metric_name}",
                                            legend_title="Tipo de Dado"
                                        )
                                        
                                        st.plotly_chart(fig_forecast, use_container_width=True)
                                    else:  # Tabela
                                        # Mostrar tabela de previsões
                                        # Formatar dados para exibição
                                        display_predictions = predictions_df.copy()
                                        display_predictions['date'] = display_predictions['date'].dt.strftime('%d/%m/%Y')
                                        
                                        if metric_key == 'spend' or metric_key == 'conversion_value':
                                            display_predictions[metric_key] = display_predictions[metric_key].apply(lambda x: format_br(x, "R$ ", "", 2))
                                        elif metric_key in ['impressions', 'clicks', 'conversions', 'reach']:
                                            display_predictions[metric_key] = display_predictions[metric_key].apply(lambda x: format_br(x, "", "", 0))
                                        else:
                                            display_predictions[metric_key] = display_predictions[metric_key].apply(lambda x: format_br(x, "", "", 2))
                                        
                                        # Renomear colunas
                                        display_predictions.columns = ['Data', metric_name, 'Tipo']
                                        
                                        st.dataframe(display_predictions[['Data', metric_name]], use_container_width=True)
                                else:
                                    st.warning(f"Dados insuficientes para prever tendência de {metric_name}")
                        else:
                            st.warning("Não foi possível obter dados diários para esta conta.")
                    else:
                        st.warning("Selecione pelo menos uma métrica para prever.")
                
                # Tab 4: Análise de Frequência
                with chart_tabs[3]:
                    # Análise de frequência e alcance
                    st.markdown("### Análise de Frequência e Alcance")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Gráfico de frequência por campanha
                        fig_freq = px.bar(
                            combined_current_data[combined_current_data['account_id'] == account_id].sort_values('frequency', ascending=False),
                            x='campaign_name',
                            y='frequency',
                            title=f'Frequência por Campanha - {account_name}',
                            color='frequency',
                            color_continuous_scale='RdYlGn_r',
                            hover_data=['spend', 'impressions', 'reach'],
                            labels={
                                'campaign_name': 'Nome da Campanha',
                                'frequency': 'Frequência',
                                'spend': 'Valor Gasto',
                                'impressions': 'Impressões',
                                'reach': 'Alcance'
                            }
                        )
                        
                        # Adicionar linhas de referência
                        fig_freq.add_hline(y=benchmarks['frequencia']['ideal_max'], line_dash="dash", line_color="red", annotation_text="Máximo Ideal")
                        fig_freq.add_hline(y=benchmarks['frequencia']['ideal_min'], line_dash="dash", line_color="green", annotation_text="Mínimo Ideal")
                        
                        fig_freq.update_layout(
                            xaxis_title="Nome da Campanha",
                            yaxis_title="Frequência",
                            xaxis={'categoryorder':'total descending'}
                        )
                        
                        st.plotly_chart(fig_freq, use_container_width=True)
                    
                    with col2:
                        # Gráfico de alcance por campanha
                        fig_reach = px.bar(
                            combined_current_data[combined_current_data['account_id'] == account_id].sort_values('reach', ascending=False).head(10),
                            x='campaign_name',
                            y='reach',
                            title=f'Top 10 Campanhas por Alcance - {account_name}',
                            color='frequency',
                            color_continuous_scale='RdYlGn_r',
                            hover_data=['spend', 'impressions', 'frequency'],
                            labels={
                                'campaign_name': 'Nome da Campanha',
                                'reach': 'Alcance',
                                'frequency': 'Frequência',
                                'spend': 'Valor Gasto',
                                'impressions': 'Impressões'
                            }
                        )
                        
                        fig_reach.update_layout(
                            xaxis_title="Nome da Campanha",
                            yaxis_title="Alcance",
                            xaxis={'categoryorder':'total descending'}
                        )
                        
                        st.plotly_chart(fig_reach, use_container_width=True)
                    
                    # Gráfico de dispersão para Alcance vs Frequência
                    fig_scatter_reach = px.scatter(
                        combined_current_data[combined_current_data['account_id'] == account_id],
                        x='reach',
                        y='frequency',
                        size='spend',
                        color='conversions',
                        hover_name='campaign_name',
                        title=f'Alcance vs Frequência por Campanha - {account_name}',
                        log_x=True,
                        labels={
                            'reach': 'Alcance',
                            'frequency': 'Frequência',
                            'spend': 'Valor Gasto',
                            'conversions': 'Conversões',
                            'campaign_name': 'Nome da Campanha'
                        }
                    )
                    
                    # Adicionar linhas de referência
                    fig_scatter_reach.add_hline(y=benchmarks['frequencia']['ideal_max'], line_dash="dash", line_color="red", annotation_text="Frequência Máxima Ideal")
                    fig_scatter_reach.add_hline(y=benchmarks['frequencia']['ideal_min'], line_dash="dash", line_color="green", annotation_text="Frequência Mínima Ideal")
                    
                    fig_scatter_reach.update_layout(
                        xaxis_title="Alcance",
                        yaxis_title="Frequência"
                    )
                    
                    st.plotly_chart(fig_scatter_reach, use_container_width=True)
                
                # Tab 5: Comparação de Evolução
                with chart_tabs[4]:
                    st.markdown("### Comparação de Evolução das Métricas")
                    
                    # Calcular tendências com base nos dados atuais e anteriores
                    trend_data = pd.DataFrame({
                        'Período': ['Atual', 'Anterior'],
                        'Gasto': [total_spend, prev_total_spend],
                        'Conversões': [total_conversions, prev_total_conversions],
                        'Impressões': [total_impressions, prev_total_impressions],
                        'Cliques': [total_clicks, prev_total_clicks],
                        'Valor de Conversão': [total_conversion_value, prev_total_conversion_value],
                        'Alcance': [total_reach, prev_total_reach]
                    })
                    
                    # Gráfico de barras para comparação de períodos
                    fig_bar_trend = px.bar(
                        trend_data,
                        x='Período',
                        y=['Gasto', 'Conversões', 'Impressões', 'Cliques', 'Valor de Conversão', 'Alcance'],
                        title=f'Comparação: {start_date.strftime("%d/%m/%Y")} a {end_date.strftime("%d/%m/%Y")} vs. Período Anterior',
                        barmode='group',
                        labels={
                            'Período': 'Período',
                            'value': 'Valor',
                            'variable': 'Métrica'
                        }
                    )
                    
                    # Atualizar nomes dos eixos
                    fig_bar_trend.update_layout(
                        xaxis_title="Período",
                        yaxis_title="Valor",
                        legend_title="Métrica"
                    )
                    
                    st.plotly_chart(fig_bar_trend, use_container_width=True)
                    
                    # Calcular variações percentuais para exibição
                    trend_changes = pd.DataFrame({
                        'Métrica': ['Gasto', 'Conversões', 'Impressões', 'Cliques', 'Valor de Conversão', 'Alcance', 'CTR', 'CPA', 'ROAS'],
                        'Variação (%)': [delta_spend, delta_conversions, delta_impressions, delta_clicks, delta_conversion_value, delta_reach, delta_ctr, delta_cpa, delta_roas]
                    })
                    
                    # Gráfico de barras para variações percentuais
                    fig_bar_changes = px.bar(
                        trend_changes,
                        x='Métrica',
                        y='Variação (%)',
                        title='Variação Percentual em Relação ao Período Anterior',
                        color='Variação (%)',
                        color_continuous_scale=['red', 'yellow', 'green'],
                        range_color=[-50, 50]
                    )
                    
                    st.plotly_chart(fig_bar_changes, use_container_width=True)
            else:
                # Visualizações para múltiplas contas
                chart_tabs = st.tabs(["Desempenho por Conta", "Desempenho por Campanha", "Tendências"])
                
                # Tab 1: Desempenho por Conta
                with chart_tabs[0]:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Gráfico de pizza para distribuição de orçamento
                        fig_pie = px.pie(
                            account_summary_df,
                            values='total_spend',
                            names='account_name',
                            title='Distribuição de Orçamento por Conta',
                            hole=0.4,
                            color_discrete_sequence=px.colors.qualitative.Pastel,
                            labels={
                                'total_spend': 'Gasto Total',
                                'account_name': 'Nome da Conta'
                            }
                        )
                        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(fig_pie, use_container_width=True)
                    
                    with col2:
                        # Gráfico de barras para CPA por conta
                        fig_bar_cpa = px.bar(
                            account_summary_df,
                            x='account_name',
                            y='avg_cpa',
                            title='CPA Médio por Conta',
                            color='avg_cpa',
                            color_continuous_scale=['green', 'yellow', 'red'],
                            range_color=[0, benchmarks['cpa']['atencao'] * 1.5],
                            labels={
                                'account_name': 'Nome da Conta',
                                'avg_cpa': 'CPA Médio (R$)'
                            }
                        )
                        fig_bar_cpa.update_layout(xaxis_title="Nome da Conta", yaxis_title="CPA (R$)")
                        st.plotly_chart(fig_bar_cpa, use_container_width=True)
                    
                    # Gráfico de barras para métricas por conta
                    metrics_by_account = pd.melt(
                        account_summary_df,
                        id_vars=['account_name'],
                        value_vars=['total_spend', 'total_conversions', 'total_clicks', 'total_impressions'],
                        var_name='metric',
                        value_name='value'
                    )
                    
                    # Mapear nomes de métricas para exibição
                    metrics_by_account['metric'] = metrics_by_account['metric'].map({
                        'total_spend': 'Gasto Total',
                        'total_conversions': 'Total de Conversões',
                        'total_clicks': 'Total de Cliques',
                        'total_impressions': 'Total de Impressões'
                    })
                    
                    fig_metrics = px.bar(
                        metrics_by_account,
                        x='account_name',
                        y='value',
                        color='metric',
                        barmode='group',
                        title='Métricas Principais por Conta',
                        labels={
                            'account_name': 'Nome da Conta',
                            'value': 'Valor',
                            'metric': 'Métrica'
                        }
                    )
                    
                    st.plotly_chart(fig_metrics, use_container_width=True)
                
                # Tab 2: Desempenho por Campanha
                with chart_tabs[1]:
                    # Top 10 campanhas por gasto
                    top_campaigns = combined_current_data.sort_values('spend', ascending=False).head(10)
                    
                    # Gráfico de barras para desempenho de campanhas
                    fig_bar_campaign = px.bar(
                        top_campaigns,
                        x='campaign_name',
                        y='spend',
                        title='Top 10 Campanhas por Gasto',
                        color='conversions',
                        color_continuous_scale='Viridis',
                        hover_data=['clicks', 'conversions', 'cpa', 'roas'],
                        labels={
                            'campaign_name': 'Nome da Campanha',
                            'spend': 'Valor Gasto',
                            'clicks': 'Cliques',
                            'conversions': 'Conversões',
                            'cpa': 'CPA',
                            'roas': 'ROAS'
                        }
                    )
                    fig_bar_campaign.update_layout(xaxis_title="Nome da Campanha", yaxis_title="Valor Gasto (R$)")
                    st.plotly_chart(fig_bar_campaign, use_container_width=True)
                    
                    # Gráfico de dispersão para CPA vs ROAS
                    fig_scatter = px.scatter(
                        combined_current_data,
                        x='cpa',
                        y='roas',
                        size='spend',
                        color='account_name',
                        hover_name='campaign_name',
                        title='CPA vs ROAS por Campanha',
                        log_x=True,
                        labels={
                            'cpa': 'CPA (R$)',
                            'roas': 'ROAS',
                            'spend': 'Valor Gasto',
                            'account_name': 'Nome da Conta',
                            'campaign_name': 'Nome da Campanha'
                        }
                    )
                    
                    # Adicionar linhas de referência
                    fig_scatter.add_hline(y=benchmarks['roas']['bom'], line_dash="dash", line_color="green", annotation_text="ROAS Bom")
                    fig_scatter.add_hline(y=benchmarks['roas']['atencao'], line_dash="dash", line_color="orange", annotation_text="ROAS Atenção")
                    fig_scatter.add_vline(x=benchmarks['cpa']['bom'], line_dash="dash", line_color="green", annotation_text="CPA Bom")
                    fig_scatter.add_vline(x=benchmarks['cpa']['atencao'], line_dash="dash", line_color="orange", annotation_text="CPA Atenção")
                    
                    st.plotly_chart(fig_scatter, use_container_width=True)
                
                # Tab 3: Tendências
                with chart_tabs[2]:
                    # Calcular tendências com base nos dados atuais e anteriores
                    trend_data = pd.DataFrame({
                        'Período': ['Atual', 'Anterior'],
                        'Gasto': [total_spend, prev_total_spend],
                        'Conversões': [total_conversions, prev_total_conversions],
                        'Impressões': [total_impressions, prev_total_impressions],
                        'Cliques': [total_clicks, prev_total_clicks],
                        'Valor de Conversão': [total_conversion_value, prev_total_conversion_value],
                        'Alcance': [total_reach, prev_total_reach]
                    })
                    
                    # Gráfico de barras para comparação de períodos
                    fig_bar_trend = px.bar(
                        trend_data,
                        x='Período',
                        y=['Gasto', 'Conversões', 'Impressões', 'Cliques', 'Valor de Conversão', 'Alcance'],
                        title=f'Comparação: {start_date.strftime("%d/%m/%Y")} a {end_date.strftime("%d/%m/%Y")} vs. Período Anterior',
                        barmode='group',
                        labels={
                            'Período': 'Período',
                            'value': 'Valor',
                            'variable': 'Métrica'
                        }
                    )
                    
                    # Atualizar nomes dos eixos
                    fig_bar_trend.update_layout(
                        xaxis_title="Período",
                        yaxis_title="Valor",
                        legend_title="Métrica"
                    )
                    
                    st.plotly_chart(fig_bar_trend, use_container_width=True)
                    
                    # Calcular variações percentuais para exibição
                    trend_changes = pd.DataFrame({
                        'Métrica': ['Gasto', 'Conversões', 'Impressões', 'Cliques', 'Valor de Conversão', 'Alcance', 'CTR', 'CPA', 'ROAS'],
                        'Variação (%)': [delta_spend, delta_conversions, delta_impressions, delta_clicks, delta_conversion_value, delta_reach, delta_ctr, delta_cpa, delta_roas]
                    })
                    
                    # Gráfico de barras para variações percentuais
                    fig_bar_changes = px.bar(
                        trend_changes,
                        x='Métrica',
                        y='Variação (%)',
                        title='Variação Percentual em Relação ao Período Anterior',
                        color='Variação (%)',
                        color_continuous_scale=['red', 'yellow', 'green'],
                        range_color=[-50, 50]
                    )
                    
                    st.plotly_chart(fig_bar_changes, use_container_width=True)
        
        # Seção de Tabela
        with table_container:
            st.markdown("## 📋 Detalhes das Campanhas")
            
            # Preparar dados para exibição
            display_data = combined_current_data[['account_name', 'campaign_name', 'status', 'updated_time', 
                                                'spend', 'impressions', 'clicks', 'ctr', 'conversions', 
                                                'conversion_value', 'cpa', 'cpc', 'roas', 'frequency', 'reach']]
            
            # Formatar colunas
            display_data['updated_time'] = pd.to_datetime(display_data['updated_time']).dt.strftime('%d/%m/%Y %H:%M')
            display_data['spend'] = display_data['spend'].apply(lambda x: format_br(x, "R$ ", "", 2))
            display_data['ctr'] = display_data['ctr'].apply(lambda x: format_br(x*100, "", "%", 2))
            display_data['cpa'] = display_data['cpa'].apply(lambda x: format_br(x, "R$ ", "", 2) if x > 0 else "N/A")
            display_data['cpc'] = display_data['cpc'].apply(lambda x: format_br(x, "R$ ", "", 2) if x > 0 else "N/A")
            display_data['roas'] = display_data['roas'].apply(lambda x: format_br(x, "", "", 2) if x > 0 else "N/A")
            display_data['conversion_value'] = display_data['conversion_value'].apply(lambda x: format_br(x, "R$ ", "", 2) if x > 0 else "R$ 0,00")
            display_data['impressions'] = display_data['impressions'].apply(lambda x: format_br(x, "", "", 0))
            display_data['clicks'] = display_data['clicks'].apply(lambda x: format_br(x, "", "", 0))
            display_data['conversions'] = display_data['conversions'].apply(lambda x: format_br(x, "", "", 0))
            display_data['reach'] = display_data['reach'].apply(lambda x: format_br(x, "", "", 0))
            display_data['frequency'] = display_data['frequency'].apply(lambda x: format_br(x, "", "", 2))
            
            # Renomear colunas para exibição
            display_data.columns = ['Conta', 'Campanha', 'Status', 'Atualização da Campanha', 'Gasto', 
                                   'Impressões', 'Cliques', 'CTR', 'Conversões', 
                                   'Valor de Conversão', 'CPA', 'CPC', 'ROAS', 'Frequência', 'Alcance']
            
            # Exibir tabela com ordenação
            st.dataframe(display_data, use_container_width=True, )
            
            # Funcionalidade de exportação
            if st.button("Exportar dados detalhados"):
                if export_format == "CSV":
                    csv = combined_current_data.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"meta_ads_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:  # Excel
                    # Para Excel, precisaríamos de bibliotecas adicionais
                    buffer = StringIO()
                    combined_current_data.to_csv(buffer, index=False)
                    st.download_button(
                        label="Download CSV (compatível com Excel)",
                        data=buffer.getvalue(),
                        file_name=f"meta_ads_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
    else:
        st.warning("Nenhum dado encontrado para as contas e filtros selecionados.")

if __name__ == "__main__":
    main()
