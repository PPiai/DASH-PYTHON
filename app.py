import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json
import requests
from typing import Dict, List, Tuple, Optional, Union
import threading
import numpy as np
import locale

# Configurar localização para o padrão brasileiro
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        pass

# Função para formatar valores no padrão brasileiro
def formatar_valor_br(valor, prefixo="R$", casas_decimais=2):
    try:
        if pd.isna(valor):
            return "-"
        return f"{prefixo} {valor:,.{casas_decimais}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return f"{prefixo} {valor}"

def formatar_numero_br(valor, casas_decimais=0):
    try:
        if pd.isna(valor):
            return "-"
        return f"{valor:,.{casas_decimais}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return f"{valor}"

# Configuração da página
st.set_page_config(
    page_title="Painel de Desempenho de Anúncios",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar CSS personalizado para um visual limpo e profissional
st.markdown("""
<style>
    .main {
        background-color: #000000 !important;
    }
    .stMetric {
        background-color: #898989 !important;
        padding: 15px;
        color: white;
        border-radius: 5px;
        box-shadow: 0 1px 3px rgba(255,255,255,0.3), 0 1px 2px rgba(255,255,255,0.3) !important;
        border-bottom: 2px solid #ffffff;
    }
    .stPlotlyChart {
        background-color: white;
        border-radius: 2px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        border-bottom: 2px solid #ffffff;
    }
    .css-1d391kg {
        padding-top: 1rem;
    }
    h1, h2, h3 {
        color: #ffffff !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: black;
        border-bottom: 2px solid #ffffff;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        color: black;
        font-weight: 800;
        border-bottom: 2px solid #ffffff;
    }
    
    /* Estilo melhorado para botões */
    .stButton > button {
        background-color: #000000;
        color: white;
        border: 2px solid #ffffff;
        border-radius: 5px;
        padding: 10px 15px;
        font-weight: 800;
        width: 100%;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #000000;
        color: red;
        border: 2px solid #ff0000;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        transform: translateY(-2px);
    }

    /* Adicionar uma borda clara ao final de cada seção */
    .section-divider {
        border-bottom: 1px solid #e0e0e0;
        margin: 20px 0;
        padding-bottom: 10px;
    }
    
    /* Melhorar o contraste dos cabeçalhos */
    .sidebar h1, .sidebar h2, .sidebar h3, .sidebar h4 {
        color: #ffffff;
        margin-bottom: 15px;
        padding-bottom: 5px;
        border-bottom: 2px solid #4e8cff;
        display: inline-block;
    }
    
    /* Estilo para as abas de navegação */
    .main-nav {
        display: flex;
        justify-content: center;
        background-color: #000000;
        gap: 10px;
        margin-bottom: 20px;
    }
    
    .nav-item {
        background-color: #ffffff;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        transition: all 0.3s;
    }
    
    .nav-item:hover, .nav-item.active {
        background-color: #4e8cff;
        color: white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# ===== Módulo de Carregamento de Dados =====
class CarregadorDados:
    """Classe para lidar com o carregamento e processamento de dados dos endpoints da API"""
    
    def __init__(self, url_google_ads: str, url_meta_ads: str):
        """Inicializar com endpoints da API"""
        
        self.url_google_ads = url_google_ads
        self.url_meta_ads = url_meta_ads
        self.hora_ultima_atualizacao = None
        self.dados = None
        self.erro = None
        
    def buscar_dados(self, url: str) -> Optional[Dict]:
        """Buscar dados da API com tratamento de erros"""
        try:
            resposta = requests.get(url, timeout=10)
            resposta.raise_for_status()  # Gerar exceção para respostas 4XX/5XX
            return resposta.json()
        except requests.exceptions.Timeout:
            self.erro = f"Erro de timeout ao conectar a {url}"
            return None
        except requests.exceptions.HTTPError as e:
            self.erro = f"Erro HTTP: {e}"
            return None
        except requests.exceptions.ConnectionError:
            self.erro = f"Erro de conexão ao conectar a {url}"
            return None
        except json.JSONDecodeError:
            self.erro = f"Formato JSON inválido de {url}"
            return None
        except Exception as e:
            self.erro = f"Erro inesperado: {str(e)}"
            return None
    
    def processar_dados_windsor(self, dados: Dict, plataforma: str) -> pd.DataFrame:
        """Processar dados do formato da API Windsor.ai"""
        # Verificar se os dados existem e têm a estrutura esperada
        if not dados or 'data' not in dados:
            return pd.DataFrame()
        
        # Converter para DataFrame
        df = pd.DataFrame(dados['data'])
        
        if df.empty:
            return df
        
        # Renomear colunas para corresponder às expectativas do nosso painel
        mapeamento_colunas = {
            'campaign': 'nome_campanha',
            'datasource': 'plataforma',
            'date': 'data',
            'clicks': 'cliques',
            'spend': 'gasto',
            'impressions': 'impressoes',
            'ad_name': 'nome_anuncio',
            'adset_name': 'nome_conjunto_anuncios',
            'reach': 'alcance',
            'actions_purchase': 'acoes_compra',
            'action_values_omni_purchase': 'valor_acoes_compra',
            'conversions': 'conversoes',
            'conversion_value': 'valor_conversao'
        }
        
        # Renomear colunas que existem nos dados
        colunas_existentes = set(df.columns).intersection(set(mapeamento_colunas.keys()))
        df = df.rename(columns={col: mapeamento_colunas[col] for col in colunas_existentes})
        
        # Garantir que a plataforma esteja corretamente definida
        if 'plataforma' in df.columns:
            # O campo datasource pode já conter o nome da plataforma
            pass
        else:
            df['plataforma'] = plataforma
        
        return df
    
    def carregar_dados(self) -> Tuple[pd.DataFrame, str]:
        """Carregar dados de ambas as fontes e retornar dataframe processado"""
        self.erro = None
        
        # Buscar dados de ambas as fontes
        dados_google = self.buscar_dados(self.url_google_ads)
        dados_meta = self.buscar_dados(self.url_meta_ads)
        
        # Se ambas as fontes falharam, retornar dataframe vazio
        if dados_google is None and dados_meta is None:
            return pd.DataFrame(), self.erro
        
        # Processar dados de cada fonte
        df_google = pd.DataFrame()
        df_meta = pd.DataFrame()
        
        if dados_google is not None:
            df_google = self.processar_dados_windsor(dados_google, 'Google Ads')
        
        if dados_meta is not None:
            df_meta = self.processar_dados_windsor(dados_meta, 'Meta Ads')
        
        # Mesclar dados
        if df_google.empty and df_meta.empty:
            return pd.DataFrame(), "Nenhum dado disponível de nenhuma fonte"
        elif df_google.empty:
            df = df_meta
        elif df_meta.empty:
            df = df_google
        else:
            # Garantir que as colunas correspondam antes da concatenação
            todas_colunas = set(df_google.columns).union(set(df_meta.columns))
            
            # Adicionar colunas ausentes com valores NaN
            for col in todas_colunas:
                if col not in df_google.columns:
                    df_google[col] = float('nan')
                if col not in df_meta.columns:
                    df_meta[col] = float('nan')
            
            # Concatenar os dataframes
            df = pd.concat([df_google, df_meta], ignore_index=True)
        
        # Converter strings de data para objetos datetime
        if 'data' in df.columns:
            df['data'] = pd.to_datetime(df['data'])
        
        # Converter valores numéricos
        colunas_numericas = ['gasto', 'cliques', 'impressoes', 'alcance', 
                            'acoes_compra', 'valor_acoes_compra', 
                            'conversoes', 'valor_conversao']
        
        for col in colunas_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calcular métricas derivadas com base nos dados disponíveis
        # CTR (Taxa de cliques)
        if 'cliques' in df.columns and 'impressoes' in df.columns:
            df['ctr'] = (df['cliques'] / df['impressoes'] * 100).round(2)
        
        # CPC (Custo por clique)
        if 'gasto' in df.columns and 'cliques' in df.columns:
            df['cpc'] = (df['gasto'] / df['cliques']).round(2)
        
        # CPM (Custo por mil impressões)
        if 'gasto' in df.columns and 'impressoes' in df.columns:
            df['cpm'] = (df['gasto'] / df['impressoes'] * 1000).round(2)
        
        # CPA (Custo por aquisição) - Google
        if 'gasto' in df.columns and 'conversoes' in df.columns:
            df['cpa'] = (df['gasto'] / df['conversoes']).round(2)
        
        # CPA (Custo por aquisição) - Meta
        if 'gasto' in df.columns and 'acoes_compra' in df.columns:
            mask = df['plataforma'] == 'Meta Ads'
            if mask.any():
                df.loc[mask, 'cpa'] = (df.loc[mask, 'gasto'] / df.loc[mask, 'acoes_compra']).round(2)
        
        # ROAS (Retorno sobre investimento em anúncios) - Google
        if 'valor_conversao' in df.columns and 'gasto' in df.columns:
            mask = df['plataforma'] == 'Google Ads'
            if mask.any():
                df.loc[mask, 'roas'] = (df.loc[mask, 'valor_conversao'] / df.loc[mask, 'gasto']).round(2)
        
        # ROAS (Retorno sobre investimento em anúncios) - Meta
        if 'valor_acoes_compra' in df.columns and 'gasto' in df.columns:
            mask = df['plataforma'] == 'Meta Ads'
            if mask.any():
                df.loc[mask, 'roas'] = (df.loc[mask, 'valor_acoes_compra'] / df.loc[mask, 'gasto']).round(2)
        
        self.dados = df
        self.hora_ultima_atualizacao = datetime.now()
        
        return df, self.erro

# ===== Módulo de Visualização =====
class Visualizador:
    """Classe para lidar com a visualização de dados"""
    
    @staticmethod
    def criar_metricas_kpi(df: pd.DataFrame, prev_df: Optional[pd.DataFrame] = None) -> Dict:
        """Criar métricas KPI com indicadores de delta"""
        metricas = {}
        
        if df.empty:
            return metricas
        
        # Calcular métricas atuais
        metricas['gasto_total'] = df['gasto'].sum()
        
        if 'impressoes' in df.columns:
            metricas['impressoes_totais'] = df['impressoes'].sum()
        else:
            metricas['impressoes_totais'] = 0
            
        if 'cliques' in df.columns:
            metricas['cliques_totais'] = df['cliques'].sum()
        else:
            metricas['cliques_totais'] = 0
            
        if 'impressoes' in df.columns and 'cliques' in df.columns and df['impressoes'].sum() > 0:
            metricas['ctr_medio'] = (df['cliques'].sum() / df['impressoes'].sum() * 100)
        else:
            metricas['ctr_medio'] = 0
        
        # Calcular conversões totais (combinando Google e Meta)
        metricas['conversoes_totais'] = 0
        if 'conversoes' in df.columns:
            google_mask = df['plataforma'] == 'Google Ads'
            if google_mask.any():
                metricas['conversoes_totais'] += df.loc[google_mask, 'conversoes'].sum()
        
        if 'acoes_compra' in df.columns:
            meta_mask = df['plataforma'] == 'Meta Ads'
            if meta_mask.any():
                metricas['conversoes_totais'] += df.loc[meta_mask, 'acoes_compra'].sum()
        
        # Calcular CPA médio
        if metricas['conversoes_totais'] > 0:
            metricas['cpa_medio'] = metricas['gasto_total'] / metricas['conversoes_totais']
        else:
            metricas['cpa_medio'] = 0
        
        # Calcular receita total (combinando Google e Meta)
        metricas['receita_total'] = 0
        if 'valor_conversao' in df.columns:
            google_mask = df['plataforma'] == 'Google Ads'
            if google_mask.any():
                metricas['receita_total'] += df.loc[google_mask, 'valor_conversao'].sum()
        
        if 'valor_acoes_compra' in df.columns:
            meta_mask = df['plataforma'] == 'Meta Ads'
            if meta_mask.any():
                metricas['receita_total'] += df.loc[meta_mask, 'valor_acoes_compra'].sum()
        
        # Calcular ROAS médio
        if metricas['gasto_total'] > 0:
            metricas['roas_medio'] = metricas['receita_total'] / metricas['gasto_total']
        else:
            metricas['roas_medio'] = 0
        
        # Calcular deltas se os dados anteriores estiverem disponíveis
        if prev_df is not None and not prev_df.empty:
            metricas_anteriores = {}
            metricas_anteriores['gasto_total'] = prev_df['gasto'].sum() if 'gasto' in prev_df.columns else 0
            
            if 'impressoes' in prev_df.columns:
                metricas_anteriores['impressoes_totais'] = prev_df['impressoes'].sum()
            else:
                metricas_anteriores['impressoes_totais'] = 0
                
            if 'cliques' in prev_df.columns:
                metricas_anteriores['cliques_totais'] = prev_df['cliques'].sum()
            else:
                metricas_anteriores['cliques_totais'] = 0
                
            if ('impressoes' in prev_df.columns and 'cliques' in prev_df.columns and 
                prev_df['impressoes'].sum() > 0):
                metricas_anteriores['ctr_medio'] = (prev_df['cliques'].sum() / prev_df['impressoes'].sum() * 100)
            else:
                metricas_anteriores['ctr_medio'] = 0
            
            # Calcular conversões totais anteriores
            metricas_anteriores['conversoes_totais'] = 0
            if 'conversoes' in prev_df.columns:
                google_mask = prev_df['plataforma'] == 'Google Ads'
                if google_mask.any():
                    metricas_anteriores['conversoes_totais'] += prev_df.loc[google_mask, 'conversoes'].sum()
            
            if 'acoes_compra' in prev_df.columns:
                meta_mask = prev_df['plataforma'] == 'Meta Ads'
                if meta_mask.any():
                    metricas_anteriores['conversoes_totais'] += prev_df.loc[meta_mask, 'acoes_compra'].sum()
            
            # Calcular CPA médio anterior
            if metricas_anteriores['conversoes_totais'] > 0:
                metricas_anteriores['cpa_medio'] = metricas_anteriores['gasto_total'] / metricas_anteriores['conversoes_totais']
            else:
                metricas_anteriores['cpa_medio'] = 0
            
            # Calcular receita total anterior
            metricas_anteriores['receita_total'] = 0
            if 'valor_conversao' in prev_df.columns:
                google_mask = prev_df['plataforma'] == 'Google Ads'
                if google_mask.any():
                    metricas_anteriores['receita_total'] += prev_df.loc[google_mask, 'valor_conversao'].sum()
            
            if 'valor_acoes_compra' in prev_df.columns:
                meta_mask = prev_df['plataforma'] == 'Meta Ads'
                if meta_mask.any():
                    metricas_anteriores['receita_total'] += prev_df.loc[meta_mask, 'valor_acoes_compra'].sum()
            
            # Calcular ROAS médio anterior
            if metricas_anteriores['gasto_total'] > 0:
                metricas_anteriores['roas_medio'] = metricas_anteriores['receita_total'] / metricas_anteriores['gasto_total']
            else:
                metricas_anteriores['roas_medio'] = 0
            
            # Calcular mudanças percentuais
            for chave in list(metricas):
                if metricas_anteriores.get(chave, 0) != 0:
                    delta = ((metricas[chave] - metricas_anteriores[chave]) / metricas_anteriores[chave] * 100)
                    metricas[f"{chave}_delta"] = delta
                else:
                    metricas[f"{chave}_delta"] = 0
        
        return metricas
    
    @staticmethod
    def criar_grafico_gasto_vs_conversoes(df: pd.DataFrame) -> go.Figure:
        """Criar gráfico de linha mostrando gasto vs conversões ao longo do tempo"""
        if df.empty or 'data' not in df.columns:
            # Retornar figura vazia se não houver dados
            return go.Figure()
        
        # Agrupar por data
        dados_diarios = df.groupby('data').agg({
            'gasto': 'sum'
        }).reset_index()
        
        # Calcular conversões por dia (combinando Google e Meta)
        conversoes_por_dia = {}
        
        # Processar dados do Google Ads
        if 'conversoes' in df.columns:
            google_df = df[df['plataforma'] == 'Google Ads']
            if not google_df.empty:
                google_conversoes = google_df.groupby('data')['conversoes'].sum().reset_index()
                for _, row in google_conversoes.iterrows():
                    data = row['data']
                    if data not in conversoes_por_dia:
                        conversoes_por_dia[data] = 0
                    conversoes_por_dia[data] += row['conversoes']
        
        # Processar dados do Meta Ads
        if 'acoes_compra' in df.columns:
            meta_df = df[df['plataforma'] == 'Meta Ads']
            if not meta_df.empty:
                meta_conversoes = meta_df.groupby('data')['acoes_compra'].sum().reset_index()
                for _, row in meta_conversoes.iterrows():
                    data = row['data']
                    if data not in conversoes_por_dia:
                        conversoes_por_dia[data] = 0
                    conversoes_por_dia[data] += row['acoes_compra']
        
        # Adicionar conversões ao dataframe diário
        dados_diarios['conversoes'] = dados_diarios['data'].map(conversoes_por_dia).fillna(0)
        
        # Criar figura com eixo y secundário
        fig = go.Figure()
        
        # Adicionar linha de gasto
        fig.add_trace(
            go.Scatter(
                x=dados_diarios['data'],
                y=dados_diarios['gasto'],
                name='Gasto',
                line=dict(color='#1f77b4', width=2),
                hovertemplate='Data: %{x}<br>Gasto: R$ %{y:.2f}<extra></extra>'
            )
        )
        
        # Adicionar linha de conversões
        fig.add_trace(
            go.Scatter(
                x=dados_diarios['data'],
                y=dados_diarios['conversoes'],
                name='Conversões',
                line=dict(color='#ff7f0e', width=2, dash='dot'),
                hovertemplate='Data: %{x}<br>Conversões: %{y}<extra></extra>'
            )
        )
        
        # Atualizar layout
        fig.update_layout(
            title='Gasto e Conversões ao Longo do Tempo',
            xaxis_title='Data',
            yaxis_title='Gasto (R$)',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode="x unified",
            margin=dict(l=20, r=20, t=40, b=20),
            height=400
        )
        
        return fig
    
    @staticmethod
    def criar_grafico_desempenho_campanha(df: pd.DataFrame) -> go.Figure:
        """Criar gráfico de barras comparando o desempenho por campanha"""
        if df.empty or 'nome_campanha' not in df.columns:
            # Retornar figura vazia se não houver dados
            return go.Figure()
        
        # Agrupar por campanha e somar métricas
        metricas_para_agregar = {'gasto': 'sum'}
        if 'cliques' in df.columns:
            metricas_para_agregar['cliques'] = 'sum'
        
        # Adicionar conversões específicas por plataforma
        if 'conversoes' in df.columns or 'acoes_compra' in df.columns:
            # Criar uma coluna temporária para armazenar todas as conversões
            df['total_conversoes'] = 0
            
            # Adicionar conversões do Google
            if 'conversoes' in df.columns:
                google_mask = df['plataforma'] == 'Google Ads'
                if google_mask.any():
                    df.loc[google_mask, 'total_conversoes'] += df.loc[google_mask, 'conversoes']
            
            # Adicionar conversões do Meta
            if 'acoes_compra' in df.columns:
                meta_mask = df['plataforma'] == 'Meta Ads'
                if meta_mask.any():
                    df.loc[meta_mask, 'total_conversoes'] += df.loc[meta_mask, 'acoes_compra']
            
            metricas_para_agregar['total_conversoes'] = 'sum'
            
        dados_campanha = df.groupby('nome_campanha').agg(metricas_para_agregar).reset_index()
        
        # Ordenar por gasto para melhor visualização
        dados_campanha = dados_campanha.sort_values('gasto', ascending=False)
        
        # Limitar a 10 campanhas para melhor visualização
        if len(dados_campanha) > 10:
            dados_campanha = dados_campanha.head(10)
        
        # Criar figura
        fig = go.Figure()
        
        # Adicionar barras de gasto
        fig.add_trace(
            go.Bar(
                x=dados_campanha['nome_campanha'],
                y=dados_campanha['gasto'],
                name='Gasto',
                marker_color='#1f77b4',
                hovertemplate='Campanha: %{x}<br>Gasto: R$ %{y:.2f}<extra></extra>'
            )
        )
        
        # Adicionar barras de cliques se disponível
        if 'cliques' in dados_campanha.columns:
            fig.add_trace(
                go.Bar(
                    x=dados_campanha['nome_campanha'],
                    y=dados_campanha['cliques'],
                    name='Cliques',
                    marker_color='#ff7f0e',
                    hovertemplate='Campanha: %{x}<br>Cliques: %{y}<extra></extra>'
                )
            )
        
        # Adicionar barras de conversões se disponível
        if 'total_conversoes' in dados_campanha.columns:
            fig.add_trace(
                go.Bar(
                    x=dados_campanha['nome_campanha'],
                    y=dados_campanha['total_conversoes'],
                    name='Conversões',
                    marker_color='#2ca02c',
                    hovertemplate='Campanha: %{x}<br>Conversões: %{y}<extra></extra>'
                )
            )
        
        # Atualizar layout
        fig.update_layout(
            title='Comparação de Desempenho por Campanha (Top 10)',
            xaxis_title='Campanha',
            yaxis_title='Valor',
            barmode='group',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=20, r=20, t=40, b=20),
            height=400
        )
        
        return fig
    
    @staticmethod
    def criar_grafico_distribuicao_plataforma(df: pd.DataFrame) -> go.Figure:
        """Criar gráfico de pizza mostrando a distribuição de orçamento entre plataformas"""
        if df.empty or 'plataforma' not in df.columns:
            # Retornar figura vazia se não houver dados
            return go.Figure()
        
        # Agrupar por plataforma e somar gasto
        dados_plataforma = df.groupby('plataforma').agg({
            'gasto': 'sum'
        }).reset_index()
        
        # Criar figura
        fig = go.Figure(
            go.Pie(
                labels=dados_plataforma['plataforma'],
                values=dados_plataforma['gasto'],
                hole=0.4,
                marker=dict(colors=['#1f77b4', '#ff7f0e']),
                textinfo='label+percent',
                hoverinfo='label+value',
                hovertemplate='Plataforma: %{label}<br>Gasto: R$ %{value:.2f}<extra></extra>'
            )
        )
        
        # Atualizar layout
        fig.update_layout(
            title='Distribuição de Orçamento por Plataforma',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.1,
                xanchor="center",
                x=0.5
            ),
            margin=dict(l=20, r=20, t=40, b=20),
            height=400
        )
        
        return fig
    
    @staticmethod
    def criar_grafico_cliques_diarios(df: pd.DataFrame) -> go.Figure:
        """Criar gráfico de linha mostrando cliques ao longo do tempo por plataforma"""
        if df.empty or 'data' not in df.columns or 'cliques' not in df.columns:
            # Retornar figura vazia se não houver dados
            return go.Figure()
        
        # Agrupar por data e plataforma, somar cliques
        cliques_diarios = df.groupby(['data', 'plataforma']).agg({
            'cliques': 'sum'
        }).reset_index()
        
        # Criar figura
        fig = px.line(
            cliques_diarios, 
            x='data', 
            y='cliques', 
            color='plataforma',
            title='Cliques Diários por Plataforma',
            labels={'data': 'Data', 'cliques': 'Cliques', 'plataforma': 'Plataforma'},
            line_shape='linear',
            render_mode='svg'
        )
        
        # Atualizar layout
        fig.update_layout(
            xaxis_title='Data',
            yaxis_title='Cliques',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode="x unified",
            margin=dict(l=20, r=20, t=40, b=20),
            height=400
        )
        
        return fig
    
    @staticmethod
    def criar_grafico_tendencia_ctr(df: pd.DataFrame) -> go.Figure:
        """Criar gráfico de linha mostrando a tendência de CTR ao longo do tempo por plataforma"""
        if df.empty or 'data' not in df.columns or 'cliques' not in df.columns or 'impressoes' not in df.columns:
            # Retornar figura vazia se não houver dados
            return go.Figure()
        
        # Calcular CTR diário por plataforma
        df_temp = df.copy()
        df_temp['ctr'] = (df_temp['cliques'] / df_temp['impressoes'] * 100).round(2)
        
        ctr_diario = df_temp.groupby(['data', 'plataforma']).agg({
            'ctr': 'mean'
        }).reset_index()
        
        # Criar figura
        fig = px.line(
            ctr_diario, 
            x='data', 
            y='ctr', 
            color='plataforma',
            title='Tendência de CTR por Plataforma',
            labels={'data': 'Data', 'ctr': 'CTR (%)', 'plataforma': 'Plataforma'},
            line_shape='linear',
            render_mode='svg'
        )
        
        # Atualizar layout
        fig.update_layout(
            xaxis_title='Data',
            yaxis_title='CTR (%)',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode="x unified",
            margin=dict(l=20, r=20, t=40, b=20),
            height=400
        )
        
        return fig

# ===== Funções para páginas específicas =====
def mostrar_pagina_geral(dados_filtrados):
    """Mostrar a página geral com dados de ambas as plataformas"""
    # Criar visualizador
    visualizador = Visualizador()
    
    # Seção de métricas KPI
    st.subheader("Indicadores Chave de Desempenho")
    
    # Calcular métricas KPI com deltas
    metricas = visualizador.criar_metricas_kpi(dados_filtrados, st.session_state.dados_anteriores)
    
    # Exibir métricas em colunas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Gasto Total",
            formatar_valor_br(metricas.get('gasto_total', 0)),
            f"{metricas.get('gasto_total_delta', 0):+.1f}%" if 'gasto_total_delta' in metricas else None
        )
        
        st.metric(
            "Total de Cliques",
            formatar_numero_br(metricas.get('cliques_totais', 0)),
            f"{metricas.get('cliques_totais_delta', 0):+.1f}%" if 'cliques_totais_delta' in metricas else None
        )
    
    with col2:
        st.metric(
            "Total de Impressões",
            formatar_numero_br(metricas.get('impressoes_totais', 0)),
            f"{metricas.get('impressoes_totais_delta', 0):+.1f}%" if 'impressoes_totais_delta' in metricas else None
        )
        
        st.metric(
            "CTR Médio",
            f"{metricas.get('ctr_medio', 0):.2f}%".replace('.', ','),
            f"{metricas.get('ctr_medio_delta', 0):+.1f}%".replace('.', ',') if 'ctr_medio_delta' in metricas else None
        )
    
    with col3:
        st.metric(
            "Total de Conversões",
            formatar_numero_br(metricas.get('conversoes_totais', 0)),
            f"{metricas.get('conversoes_totais_delta', 0):+.1f}%" if 'conversoes_totais_delta' in metricas else None
        )
        
        st.metric(
            "CPA Médio",
            formatar_valor_br(metricas.get('cpa_medio', 0)),
            f"{metricas.get('cpa_medio_delta', 0):+.1f}%" if 'cpa_medio_delta' in metricas else None,
            delta_color="inverse"  # CPA menor é melhor
        )
    
    with col4:
        st.metric(
            "Receita Total",
            formatar_valor_br(metricas.get('receita_total', 0)),
            f"{metricas.get('receita_total_delta', 0):+.1f}%" if 'receita_total_delta' in metricas else None
        )
        
        st.metric(
            "ROAS Médio",
            f"{metricas.get('roas_medio', 0):.2f}".replace('.', ','),
            f"{metricas.get('roas_medio_delta', 0):+.1f}%" if 'roas_medio_delta' in metricas else None
        )
    
    # Seção de gráficos
    st.subheader("Análise de Desempenho")
    
    # Criar abas para diferentes visualizações de gráficos
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Série Temporal", "Comparação de Campanhas", "Distribuição por Plataforma", "Cliques Diários", "Tendência de CTR"])
    
    with tab1:
        # Gasto vs Conversões ao longo do tempo
        grafico_gasto_conv = visualizador.criar_grafico_gasto_vs_conversoes(dados_filtrados)
        st.plotly_chart(grafico_gasto_conv, use_container_width=True)
    
    with tab2:
        # Comparação de desempenho de campanha
        grafico_campanha = visualizador.criar_grafico_desempenho_campanha(dados_filtrados)
        st.plotly_chart(grafico_campanha, use_container_width=True)
    
    with tab3:
        # Distribuição por plataforma
        grafico_plataforma = visualizador.criar_grafico_distribuicao_plataforma(dados_filtrados)
        st.plotly_chart(grafico_plataforma, use_container_width=True)
    
    with tab4:
        # Cliques diários por plataforma
        grafico_cliques = visualizador.criar_grafico_cliques_diarios(dados_filtrados)
        st.plotly_chart(grafico_cliques, use_container_width=True)
    
    with tab5:
        # Tendência de CTR
        grafico_ctr = visualizador.criar_grafico_tendencia_ctr(dados_filtrados)
        st.plotly_chart(grafico_ctr, use_container_width=True)
    
    # Tabela de dados
    st.subheader("Tabela de Dados")
    
    if not dados_filtrados.empty:
        # Agrupar por campanha e plataforma
        metricas_para_agregar = {
            'gasto': 'sum',
            'cliques': 'sum'
        }
        
        if 'impressoes' in dados_filtrados.columns:
            metricas_para_agregar['impressoes'] = 'sum'
        
        # Adicionar conversões específicas por plataforma
        if 'conversoes' in dados_filtrados.columns or 'acoes_compra' in dados_filtrados.columns:
            # Criar uma coluna temporária para armazenar todas as conversões
            dados_filtrados['total_conversoes'] = 0
            
            # Adicionar conversões do Google
            if 'conversoes' in dados_filtrados.columns:
                google_mask = dados_filtrados['plataforma'] == 'Google Ads'
                if google_mask.any():
                    dados_filtrados.loc[google_mask, 'total_conversoes'] += dados_filtrados.loc[google_mask, 'conversoes']
            
            # Adicionar conversões do Meta
            if 'acoes_compra' in dados_filtrados.columns:
                meta_mask = dados_filtrados['plataforma'] == 'Meta Ads'
                if meta_mask.any():
                    dados_filtrados.loc[meta_mask, 'total_conversoes'] += dados_filtrados.loc[meta_mask, 'acoes_compra']
            
            metricas_para_agregar['total_conversoes'] = 'sum'
        
        # Adicionar receita específica por plataforma
        if 'valor_conversao' in dados_filtrados.columns or 'valor_acoes_compra' in dados_filtrados.columns:
            # Criar uma coluna temporária para armazenar toda a receita
            dados_filtrados['receita_total'] = 0
            
            # Adicionar receita do Google
            if 'valor_conversao' in dados_filtrados.columns:
                google_mask = dados_filtrados['plataforma'] == 'Google Ads'
                if google_mask.any():
                    dados_filtrados.loc[google_mask, 'receita_total'] += dados_filtrados.loc[google_mask, 'valor_conversao']
            
            # Adicionar receita do Meta
            if 'valor_acoes_compra' in dados_filtrados.columns:
                meta_mask = dados_filtrados['plataforma'] == 'Meta Ads'
                if meta_mask.any():
                    dados_filtrados.loc[meta_mask, 'receita_total'] += dados_filtrados.loc[meta_mask, 'valor_acoes_compra']
            
            metricas_para_agregar['receita_total'] = 'sum'
        
        dados_tabela = dados_filtrados.groupby(['nome_campanha', 'plataforma']).agg(metricas_para_agregar).reset_index()
        
        # Calcular métricas derivadas
        if 'impressoes' in dados_tabela.columns and 'cliques' in dados_tabela.columns:
            dados_tabela['ctr'] = (dados_tabela['cliques'] / dados_tabela['impressoes'] * 100).round(2)
        
        if 'cliques' in dados_tabela.columns and 'gasto' in dados_tabela.columns:
            dados_tabela['cpc'] = (dados_tabela['gasto'] / dados_tabela['cliques']).round(2)
        
        if 'impressoes' in dados_tabela.columns and 'gasto' in dados_tabela.columns:
            dados_tabela['cpm'] = (dados_tabela['gasto'] / dados_tabela['impressoes'] * 1000).round(2)
        
        if 'total_conversoes' in dados_tabela.columns and 'gasto' in dados_tabela.columns:
            dados_tabela['cpa'] = (dados_tabela['gasto'] / dados_tabela['total_conversoes']).round(2)
        
        if 'receita_total' in dados_tabela.columns and 'gasto' in dados_tabela.columns:
            dados_tabela['roas'] = (dados_tabela['receita_total'] / dados_tabela['gasto']).round(2)
        
        # Formatar para exibição
        dados_exibicao = dados_tabela.copy()
        
        # Formatar valores no padrão brasileiro
        if 'gasto' in dados_exibicao.columns:
            dados_exibicao['gasto'] = dados_exibicao['gasto'].apply(lambda x: formatar_valor_br(x))
        
        if 'cliques' in dados_exibicao.columns:
            dados_exibicao['cliques'] = dados_exibicao['cliques'].apply(lambda x: formatar_numero_br(x))
        
        if 'impressoes' in dados_exibicao.columns:
            dados_exibicao['impressoes'] = dados_exibicao['impressoes'].apply(lambda x: formatar_numero_br(x))
        
        if 'total_conversoes' in dados_exibicao.columns:
            dados_exibicao['total_conversoes'] = dados_exibicao['total_conversoes'].apply(lambda x: formatar_numero_br(x))
        
        if 'receita_total' in dados_exibicao.columns:
            dados_exibicao['receita_total'] = dados_exibicao['receita_total'].apply(lambda x: formatar_valor_br(x))
        
        if 'ctr' in dados_exibicao.columns:
            dados_exibicao['ctr'] = dados_exibicao['ctr'].apply(lambda x: f"{x:.2f}%".replace('.', ','))
        
        if 'cpc' in dados_exibicao.columns:
            dados_exibicao['cpc'] = dados_exibicao['cpc'].apply(lambda x: formatar_valor_br(x))
        
        if 'cpm' in dados_exibicao.columns:
            dados_exibicao['cpm'] = dados_exibicao['cpm'].apply(lambda x: formatar_valor_br(x))
        
        if 'cpa' in dados_exibicao.columns:
            dados_exibicao['cpa'] = dados_exibicao['cpa'].apply(lambda x: formatar_valor_br(x))
        
        if 'roas' in dados_exibicao.columns:
            dados_exibicao['roas'] = dados_exibicao['roas'].apply(lambda x: f"{x:.2f}".replace('.', ','))
        
        # Renomear colunas para exibição
        mapeamento_colunas = {
            'nome_campanha': 'Campanha',
            'plataforma': 'Plataforma',
            'gasto': 'Gasto',
            'cliques': 'Cliques',
            'impressoes': 'Impressões',
            'total_conversoes': 'Conversões',
            'receita_total': 'Receita',
            'ctr': 'CTR',
            'cpc': 'CPC',
            'cpm': 'CPM',
            'cpa': 'CPA',
            'roas': 'ROAS'
        }
        
        dados_exibicao = dados_exibicao.rename(columns=mapeamento_colunas)
        
        st.dataframe(dados_exibicao, use_container_width=True)
        
        # Adicionar botão de download
        csv = dados_tabela.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar Dados como CSV",
            data=csv,
            file_name="dados_desempenho_anuncios.csv",
            mime="text/csv",
        )
    else:
        st.info("Nenhum dado disponível para os filtros selecionados.")

def mostrar_pagina_google_ads(dados_filtrados):
    """Mostrar a página específica para Google Ads"""
    # Filtrar apenas dados do Google Ads
    dados_google = dados_filtrados[dados_filtrados['plataforma'] == 'Google Ads'].copy()
    
    if dados_google.empty:
        st.warning("Nenhum dado do Google Ads disponível para os filtros selecionados.")
        return
    
    # Criar visualizador
    visualizador = Visualizador()
    
    # Seção de métricas KPI
    st.subheader("Indicadores Chave de Desempenho")
    
    # Calcular métricas KPI
    metricas = {}
    metricas['gasto_total'] = dados_google['gasto'].sum()
    metricas['impressoes_totais'] = dados_google['impressoes'].sum() if 'impressoes' in dados_google.columns else 0
    metricas['cliques_totais'] = dados_google['cliques'].sum() if 'cliques' in dados_google.columns else 0
    
    if 'impressoes' in dados_google.columns and 'cliques' in dados_google.columns and dados_google['impressoes'].sum() > 0:
        metricas['ctr_medio'] = (dados_google['cliques'].sum() / dados_google['impressoes'].sum() * 100)
    else:
        metricas['ctr_medio'] = 0
    
    if 'conversoes' in dados_google.columns:
        metricas['conversoes_totais'] = dados_google['conversoes'].sum()
    else:
        metricas['conversoes_totais'] = 0
    
    if 'conversoes' in dados_google.columns and dados_google['conversoes'].sum() > 0:
        metricas['cpa_medio'] = dados_google['gasto'].sum() / dados_google['conversoes'].sum()
    else:
        metricas['cpa_medio'] = 0
    
    if 'valor_conversao' in dados_google.columns:
        metricas['receita_total'] = dados_google['valor_conversao'].sum()
    else:
        metricas['receita_total'] = 0
    
    if metricas['gasto_total'] > 0 and metricas['receita_total'] > 0:
        metricas['roas_medio'] = metricas['receita_total'] / metricas['gasto_total']
    else:
        metricas['roas_medio'] = 0
    
    # Exibir métricas em colunas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Gasto Total",
            formatar_valor_br(metricas.get('gasto_total', 0))
        )
        
        st.metric(
            "Total de Cliques",
            formatar_numero_br(metricas.get('cliques_totais', 0))
        )
    
    with col2:
        st.metric(
            "Total de Impressões",
            formatar_numero_br(metricas.get('impressoes_totais', 0))
        )
        
        st.metric(
            "CTR Médio",
            f"{metricas.get('ctr_medio', 0):.2f}%".replace('.', ',')
        )
    
    with col3:
        st.metric(
            "Total de Conversões",
            formatar_numero_br(metricas.get('conversoes_totais', 0))
        )
        
        st.metric(
            "CPA Médio",
            formatar_valor_br(metricas.get('cpa_medio', 0))
        )
    
    with col4:
        st.metric(
            "Receita Total",
            formatar_valor_br(metricas.get('receita_total', 0))
        )
        
        st.metric(
            "ROAS Médio",
            f"{metricas.get('roas_medio', 0):.2f}".replace('.', ',')
        )
    
    # Seção de gráficos
    st.subheader("Análise de Desempenho")
    
    # Criar gráficos específicos para Google Ads
    # Gráfico de tendência de conversões ao longo do tempo
    if 'data' in dados_google.columns and 'conversoes' in dados_google.columns:
        conversoes_diarias = dados_google.groupby('data').agg({
            'conversoes': 'sum',
            'gasto': 'sum'
        }).reset_index()
        
        fig_conversoes = go.Figure()
        
        fig_conversoes.add_trace(
            go.Scatter(
                x=conversoes_diarias['data'],
                y=conversoes_diarias['conversoes'],
                name='Conversões',
                line=dict(color='#2ca02c', width=2),
                hovertemplate='Data: %{x}<br>Conversões: %{y}<extra></extra>'
            )
        )
        
        fig_conversoes.add_trace(
            go.Scatter(
                x=conversoes_diarias['data'],
                y=conversoes_diarias['gasto'],
                name='Gasto',
                line=dict(color='#1f77b4', width=2, dash='dot'),
                yaxis='y2',
                hovertemplate='Data: %{x}<br>Gasto: R$ %{y:.2f}<extra></extra>'
            )
        )
        
        fig_conversoes.update_layout(
            title='Conversões e Gasto ao Longo do Tempo - Google Ads',
            xaxis_title='Data',
            yaxis_title='Conversões',
            yaxis2=dict(
                title='Gasto (R$)',
                overlaying='y',
                side='right'
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode="x unified",
            margin=dict(l=20, r=20, t=40, b=20),
            height=400
        )
        
        st.plotly_chart(fig_conversoes, use_container_width=True)
    
    # Gráfico de desempenho por campanha
    if 'nome_campanha' in dados_google.columns:
        # Agrupar por campanha
        dados_campanha = dados_google.groupby('nome_campanha').agg({
            'gasto': 'sum',
            'cliques': 'sum',
            'conversoes': 'sum' if 'conversoes' in dados_google.columns else None,
            'valor_conversao': 'sum' if 'valor_conversao' in dados_google.columns else None
        }).reset_index()
        
        # Remover colunas None
        dados_campanha = dados_campanha.dropna(axis=1)
        
        # Calcular ROAS se possível
        if 'valor_conversao' in dados_campanha.columns and 'gasto' in dados_campanha.columns:
            dados_campanha['roas'] = (dados_campanha['valor_conversao'] / dados_campanha['gasto']).round(2)
        
        # Ordenar por gasto
        dados_campanha = dados_campanha.sort_values('gasto', ascending=False)
        
        # Limitar a 10 campanhas
        if len(dados_campanha) > 10:
            dados_campanha = dados_campanha.head(10)
        
        # Criar gráfico de barras para ROAS por campanha
        if 'roas' in dados_campanha.columns:
            fig_roas = px.bar(
                dados_campanha,
                x='nome_campanha',
                y='roas',
                title='ROAS por Campanha (Top 10)',
                labels={'nome_campanha': 'Campanha', 'roas': 'ROAS'},
                color='roas',
                color_continuous_scale='Viridis'
            )
            
            fig_roas.update_layout(
                xaxis_title='Campanha',
                yaxis_title='ROAS',
                coloraxis_showscale=False,
                margin=dict(l=20, r=20, t=40, b=20),
                height=400
            )
            
            st.plotly_chart(fig_roas, use_container_width=True)
    
    # Tabela de dados do Google Ads
    st.subheader("Tabela de Dados")
    
    if not dados_google.empty:
        # Agrupar por campanha
        metricas_para_agregar = {
            'gasto': 'sum',
            'cliques': 'sum',
            'impressoes': 'sum' if 'impressoes' in dados_google.columns else None,
            'conversoes': 'sum' if 'conversoes' in dados_google.columns else None,
            'valor_conversao': 'sum' if 'valor_conversao' in dados_google.columns else None
        }
        
        # Remover None
        metricas_para_agregar = {k: v for k, v in metricas_para_agregar.items() if v is not None}
        
        dados_tabela = dados_google.groupby('nome_campanha').agg(metricas_para_agregar).reset_index()
        
        # Calcular métricas derivadas
        if 'impressoes' in dados_tabela.columns and 'cliques' in dados_tabela.columns:
            dados_tabela['ctr'] = (dados_tabela['cliques'] / dados_tabela['impressoes'] * 100).round(2)
        
        if 'cliques' in dados_tabela.columns and 'gasto' in dados_tabela.columns:
            dados_tabela['cpc'] = (dados_tabela['gasto'] / dados_tabela['cliques']).round(2)
        
        if 'impressoes' in dados_tabela.columns and 'gasto' in dados_tabela.columns:
            dados_tabela['cpm'] = (dados_tabela['gasto'] / dados_tabela['impressoes'] * 1000).round(2)
        
        if 'conversoes' in dados_tabela.columns and 'gasto' in dados_tabela.columns:
            dados_tabela['cpa'] = (dados_tabela['gasto'] / dados_tabela['conversoes']).round(2)
        
        if 'valor_conversao' in dados_tabela.columns and 'gasto' in dados_tabela.columns:
            dados_tabela['roas'] = (dados_tabela['valor_conversao'] / dados_tabela['gasto']).round(2)
        
        # Formatar para exibição
        dados_exibicao = dados_tabela.copy()
        
        # Formatar valores no padrão brasileiro
        colunas_para_formatar = {
            'gasto': lambda x: formatar_valor_br(x),
            'cliques': lambda x: formatar_numero_br(x),
            'impressoes': lambda x: formatar_numero_br(x),
            'conversoes': lambda x: formatar_numero_br(x),
            'valor_conversao': lambda x: formatar_valor_br(x),
            'ctr': lambda x: f"{x:.2f}%".replace('.', ','),
            'cpc': lambda x: formatar_valor_br(x),
            'cpm': lambda x: formatar_valor_br(x),
            'cpa': lambda x: formatar_valor_br(x),
            'roas': lambda x: f"{x:.2f}x".replace('.', ',')
        }
        
        for col, func in colunas_para_formatar.items():
            if col in dados_exibicao.columns:
                dados_exibicao[col] = dados_exibicao[col].apply(func)
        
        # Renomear colunas para exibição
        mapeamento_colunas = {
            'nome_campanha': 'Campanha',
            'gasto': 'Gasto',
            'cliques': 'Cliques',
            'impressoes': 'Impressões',
            'conversoes': 'Conversões',
            'valor_conversao': 'Receita',
            'ctr': 'CTR',
            'cpc': 'CPC',
            'cpm': 'CPM',
            'cpa': 'CPA',
            'roas': 'ROAS'
        }
        
        dados_exibicao = dados_exibicao.rename(columns=mapeamento_colunas)
        
        st.dataframe(dados_exibicao, use_container_width=True)
        
        # Adicionar botão de download
        csv = dados_tabela.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar Dados do Google Ads como CSV",
            data=csv,
            file_name="dados_google_ads.csv",
            mime="text/csv",
        )
    else:
        st.info("Nenhum dado do Google Ads disponível para os filtros selecionados.")

def mostrar_pagina_meta_ads(dados_filtrados):
    """Mostrar a página específica para Meta Ads"""
    # Filtrar apenas dados do Meta Ads
    dados_meta = dados_filtrados[dados_filtrados['plataforma'] == 'Meta Ads'].copy()
    
    if dados_meta.empty:
        st.warning("Nenhum dado do Meta Ads disponível para os filtros selecionados.")
        return
    
    # Criar visualizador
    visualizador = Visualizador()
    
    # Seção de métricas KPI
    st.subheader("Indicadores Chave de Desempenho")
    
    # Calcular métricas KPI
    metricas = {}
    metricas['gasto_total'] = dados_meta['gasto'].sum()
    metricas['impressoes_totais'] = dados_meta['impressoes'].sum() if 'impressoes' in dados_meta.columns else 0
    metricas['cliques_totais'] = dados_meta['cliques'].sum() if 'cliques' in dados_meta.columns else 0
    
    if 'impressoes' in dados_meta.columns and 'cliques' in dados_meta.columns and dados_meta['impressoes'].sum() > 0:
        metricas['ctr_medio'] = (dados_meta['cliques'].sum() / dados_meta['impressoes'].sum() * 100)
    else:
        metricas['ctr_medio'] = 0
    
    if 'acoes_compra' in dados_meta.columns:
        metricas['conversoes_totais'] = dados_meta['acoes_compra'].sum()
    else:
        metricas['conversoes_totais'] = 0
    
    if 'acoes_compra' in dados_meta.columns and dados_meta['acoes_compra'].sum() > 0:
        metricas['cpa_medio'] = dados_meta['gasto'].sum() / dados_meta['acoes_compra'].sum()
    else:
        metricas['cpa_medio'] = 0
    
    if 'valor_acoes_compra' in dados_meta.columns:
        metricas['receita_total'] = dados_meta['valor_acoes_compra'].sum()
    else:
        metricas['receita_total'] = 0
    
    if metricas['gasto_total'] > 0 and metricas['receita_total'] > 0:
        metricas['roas_medio'] = metricas['receita_total'] / metricas['gasto_total']
    else:
        metricas['roas_medio'] = 0
    
    # Exibir métricas em colunas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Gasto Total",
            formatar_valor_br(metricas.get('gasto_total', 0))
        )
        
        st.metric(
            "Total de Cliques",
            formatar_numero_br(metricas.get('cliques_totais', 0))
        )
    
    with col2:
        st.metric(
            "Total de Impressões",
            formatar_numero_br(metricas.get('impressoes_totais', 0))
        )
        
        st.metric(
            "CTR Médio",
            f"{metricas.get('ctr_medio', 0):.2f}%".replace('.', ',')
        )
    
    with col3:
        st.metric(
            "Total de Conversões",
            formatar_numero_br(metricas.get('conversoes_totais', 0))
        )
        
        st.metric(
            "CPA Médio",
            formatar_valor_br(metricas.get('cpa_medio', 0))
        )
    
    with col4:
        st.metric(
            "Receita Total",
            formatar_valor_br(metricas.get('receita_total', 0))
        )
        
        st.metric(
            "ROAS Médio",
            f"{metricas.get('roas_medio', 0):.2f}".replace('.', ',')
        )
    
    # Seção de gráficos
    st.subheader("Análise de Desempenho")
    
    # Criar gráficos específicos para Meta Ads
    # Gráfico de tendência de alcance e impressões ao longo do tempo
    if 'data' in dados_meta.columns and 'alcance' in dados_meta.columns and 'impressoes' in dados_meta.columns:
        alcance_diario = dados_meta.groupby('data').agg({
            'alcance': 'sum',
            'impressoes': 'sum'
        }).reset_index()
        
        fig_alcance = go.Figure()
        
        fig_alcance.add_trace(
            go.Scatter(
                x=alcance_diario['data'],
                y=alcance_diario['alcance'],
                name='Alcance',
                line=dict(color='#ff7f0e', width=2),
                hovertemplate='Data: %{x}<br>Alcance: %{y}<extra></extra>'
            )
        )
        
        fig_alcance.add_trace(
            go.Scatter(
                x=alcance_diario['data'],
                y=alcance_diario['impressoes'],
                name='Impressões',
                line=dict(color='#1f77b4', width=2, dash='dot'),
                hovertemplate='Data: %{x}<br>Impressões: %{y}<extra></extra>'
            )
        )
        
        fig_alcance.update_layout(
            title='Alcance e Impressões ao Longo do Tempo - Meta Ads',
            xaxis_title='Data',
            yaxis_title='Valor',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode="x unified",
            margin=dict(l=20, r=20, t=40, b=20),
            height=400
        )
        
        st.plotly_chart(fig_alcance, use_container_width=True)
    
    # Gráfico de desempenho por conjunto de anúncios
    if 'nome_conjunto_anuncios' in dados_meta.columns:
        # Agrupar por conjunto de anúncios
        dados_conjunto = dados_meta.groupby('nome_conjunto_anuncios').agg({
            'gasto': 'sum',
            'cliques': 'sum',
            'acoes_compra': 'sum' if 'acoes_compra' in dados_meta.columns else None,
            'valor_acoes_compra': 'sum' if 'valor_acoes_compra' in dados_meta.columns else None
        }).reset_index()
        
        # Remover colunas None
        dados_conjunto = dados_conjunto.dropna(axis=1)
        
        # Calcular ROAS se possível
        if 'valor_acoes_compra' in dados_conjunto.columns and 'gasto' in dados_conjunto.columns:
            dados_conjunto['roas'] = (dados_conjunto['valor_acoes_compra'] / dados_conjunto['gasto']).round(2)
        
        # Ordenar por gasto
        dados_conjunto = dados_conjunto.sort_values('gasto', ascending=False)
        
        # Limitar a 10 conjuntos
        if len(dados_conjunto) > 10:
            dados_conjunto = dados_conjunto.head(10)
        
        # Criar gráfico de barras para gasto por conjunto de anúncios
        fig_conjunto = px.bar(
            dados_conjunto,
            x='nome_conjunto_anuncios',
            y='gasto',
            title='Gasto por Conjunto de Anúncios (Top 10)',
            labels={'nome_conjunto_anuncios': 'Conjunto de Anúncios', 'gasto': 'Gasto (R$)'},
            color='gasto',
            color_continuous_scale='Blues'
        )
        
        fig_conjunto.update_layout(
            xaxis_title='Conjunto de Anúncios',
            yaxis_title='Gasto (R$)',
            coloraxis_showscale=False,
            margin=dict(l=20, r=20, t=40, b=20),
            height=400
        )
        
        st.plotly_chart(fig_conjunto, use_container_width=True)
    
    # Tabela de dados do Meta Ads
    st.subheader("Tabela de Dados")
    
    if not dados_meta.empty:
        # Agrupar por campanha e conjunto de anúncios
        metricas_para_agregar = {
            'gasto': 'sum',
            'cliques': 'sum',
            'impressoes': 'sum' if 'impressoes' in dados_meta.columns else None,
            'alcance': 'sum' if 'alcance' in dados_meta.columns else None,
            'acoes_compra': 'sum' if 'acoes_compra' in dados_meta.columns else None,
            'valor_acoes_compra': 'sum' if 'valor_acoes_compra' in dados_meta.columns else None
        }
        
        # Remover None
        metricas_para_agregar = {k: v for k, v in metricas_para_agregar.items() if v is not None}
        
        dados_tabela = dados_meta.groupby(['nome_campanha', 'nome_conjunto_anuncios']).agg(metricas_para_agregar).reset_index()
        
        # Calcular métricas derivadas
        if 'impressoes' in dados_tabela.columns and 'cliques' in dados_tabela.columns:
            dados_tabela['ctr'] = (dados_tabela['cliques'] / dados_tabela['impressoes'] * 100).round(2)
        
        if 'cliques' in dados_tabela.columns and 'gasto' in dados_tabela.columns:
            dados_tabela['cpc'] = (dados_tabela['gasto'] / dados_tabela['cliques']).round(2)
        
        if 'impressoes' in dados_tabela.columns and 'gasto' in dados_tabela.columns:
            dados_tabela['cpm'] = (dados_tabela['gasto'] / dados_tabela['impressoes'] * 1000).round(2)
        
        if 'acoes_compra' in dados_tabela.columns and 'gasto' in dados_tabela.columns:
            dados_tabela['cpa'] = (dados_tabela['gasto'] / dados_tabela['acoes_compra']).round(2)
        
        if 'valor_acoes_compra' in dados_tabela.columns and 'gasto' in dados_tabela.columns:
            dados_tabela['roas'] = (dados_tabela['valor_acoes_compra'] / dados_tabela['gasto']).round(2)
        
        # Formatar para exibição
        dados_exibicao = dados_tabela.copy()
        
        # Formatar valores no padrão brasileiro
        colunas_para_formatar = {
            'gasto': lambda x: formatar_valor_br(x),
            'cliques': lambda x: formatar_numero_br(x),
            'impressoes': lambda x: formatar_numero_br(x),
            'alcance': lambda x: formatar_numero_br(x),
            'acoes_compra': lambda x: formatar_numero_br(x),
            'valor_acoes_compra': lambda x: formatar_valor_br(x),
            'ctr': lambda x: f"{x:.2f}%".replace('.', ','),
            'cpc': lambda x: formatar_valor_br(x),
            'cpm': lambda x: formatar_valor_br(x),
            'cpa': lambda x: formatar_valor_br(x),
            'roas': lambda x: f"{x:.2f}x".replace('.', ',')
        }
        
        for col, func in colunas_para_formatar.items():
            if col in dados_exibicao.columns:
                dados_exibicao[col] = dados_exibicao[col].apply(func)
        
        # Renomear colunas para exibição
        mapeamento_colunas = {
            'nome_campanha': 'Campanha',
            'nome_conjunto_anuncios': 'Conjunto de Anúncios',
            'gasto': 'Gasto',
            'cliques': 'Cliques',
            'impressoes': 'Impressões',
            'alcance': 'Alcance',
            'acoes_compra': 'Conversões',
            'valor_acoes_compra': 'Receita',
            'ctr': 'CTR',
            'cpc': 'CPC',
            'cpm': 'CPM',
            'cpa': 'CPA',
            'roas': 'ROAS'
        }
        
        dados_exibicao = dados_exibicao.rename(columns=mapeamento_colunas)
        
        st.dataframe(dados_exibicao, use_container_width=True)
        
        # Adicionar botão de download
        csv = dados_tabela.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar Dados do Meta Ads como CSV",
            data=csv,
            file_name="dados_meta_ads.csv",
            mime="text/csv",
        )
    else:
        st.info("Nenhum dado do Meta Ads disponível para os filtros selecionados.")

# ===== Aplicação Principal =====
def main():
    """Função principal da aplicação"""
    # Inicializar estado da sessão para persistência de dados
    if 'carregador_dados' not in st.session_state:
        st.session_state.carregador_dados = CarregadorDados(
            url_google_ads="https://connectors.windsor.ai/google_ads?api_key=c168624686715dd94fc7b034c450d42c39ea&date_from=2025-03-01&date_to=2028-03-01&fields=ad_name,campaign,clicks,conversion_value,conversions,date,impressions,spend&select_accounts=304-359-3631&_renderer=json",
            url_meta_ads="https://connectors.windsor.ai/facebook?api_key=c168624686715dd94fc7b034c450d42c39ea&date_from=2025-03-01&date_to=2028-03-01&fields=action_values_omni_purchase,actions_purchase,ad_name,adset_name,campaign,clicks,date,impressions,reach,spend&select_accounts=922812376352170&_renderer=json"
        )
    
    if 'dados_anteriores' not in st.session_state:
        st.session_state.dados_anteriores = pd.DataFrame()
    
    if 'dados_atuais' not in st.session_state:
        st.session_state.dados_atuais = pd.DataFrame()
    
    if 'ultima_atualizacao' not in st.session_state:
        st.session_state.ultima_atualizacao = None
    
    if 'atualizacao_automatica' not in st.session_state:
        st.session_state.atualizacao_automatica = True
    
    if 'pagina_atual' not in st.session_state:
        st.session_state.pagina_atual = "Geral"
    
    # Cabeçalho
    st.title("Painel de Desempenho de Publicidade Digital")
    
    # Navegação entre páginas
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 Visão Geral", use_container_width=True):
            st.session_state.pagina_atual = "Geral"
    with col2:
        if st.button("🔍 Google Ads", use_container_width=True):
            st.session_state.pagina_atual = "Google Ads"
    with col3:
        if st.button("📱 Meta Ads", use_container_width=True):
            st.session_state.pagina_atual = "Meta Ads"
    
    # Barra lateral para filtros e controles
    with st.sidebar:
        # Configuração de fonte de dados
        st.subheader("Fontes de Dados")
        st.caption("Dados do Meta e Google Ads")
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        # Entradas de intervalo de datas para URLs da API
        
        # Atualizar URLs da API com novos intervalos de datas
        url_google_ads = f"https://connectors.windsor.ai/google_ads?api_key=c168624686715dd94fc7b034c450d42c39ea&date_from=2025-03-01&date_to=2028-03-01&fields=ad_name,campaign,clicks,conversion_value,conversions,date,impressions,spend&select_accounts=304-359-3631&_renderer=json"
        url_meta_ads = f"https://connectors.windsor.ai/facebook?api_key=c168624686715dd94fc7b034c450d42c39ea&date_from=2025-03-01&date_to=2028-03-01&fields=action_values_omni_purchase,actions_purchase,ad_name,adset_name,campaign,clicks,date,impressions,reach,spend&select_accounts=922812376352170&_renderer=json"
        
        # Atualizar fontes de dados se alteradas
        if (url_google_ads != st.session_state.carregador_dados.url_google_ads or 
            url_meta_ads != st.session_state.carregador_dados.url_meta_ads):
            st.session_state.carregador_dados = CarregadorDados(
                url_google_ads=url_google_ads,
                url_meta_ads=url_meta_ads
            )
        
        # Controles de atualização
        st.subheader("Atualização de Dados")
        
        # Usar colunas para os botões
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Atualizar"):
                with st.spinner("Atualizando dados..."):
                    # Armazenar dados anteriores para cálculos de delta
                    st.session_state.dados_anteriores = st.session_state.dados_atuais.copy() if not st.session_state.dados_atuais.empty else None
                    
                    # Carregar novos dados
                    df, erro = st.session_state.carregador_dados.carregar_dados()
                    
                    if erro:
                        st.error(f"Erro ao carregar dados: {erro}")
                    else:
                        st.session_state.dados_atuais = df
                        st.session_state.ultima_atualizacao = datetime.now()
                        st.success("Dados atualizados com sucesso!")
        
        with col2:
            st.session_state.atualizacao_automatica = st.checkbox(
                "🔄 Auto", 
                value=st.session_state.atualizacao_automatica,
                help="Atualização automática a cada 5 minutos"
            )
        
        if st.session_state.ultima_atualizacao:
            st.info(f"Última atualização: {st.session_state.ultima_atualizacao.strftime('%d/%m/%Y %H:%M:%S')}")

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        # Adicionar filtros apenas se tivermos dados
        if not st.session_state.dados_atuais.empty:
            st.subheader("Filtros")
            
            # Filtro de intervalo de datas
            if 'data' in st.session_state.dados_atuais.columns:
                data_min = st.session_state.dados_atuais['data'].min().date()
                data_max = st.session_state.dados_atuais['data'].max().date()
                
                intervalo_data = st.date_input(
                    "Filtrar Intervalo de Data",
                    value=(data_min, data_max),
                    min_value=data_min,
                    max_value=data_max,
                    key="filtro_intervalo_data"
                )
                
                # Lidar com seleção de data única
                if isinstance(intervalo_data, tuple) and len(intervalo_data) == 2:
                    data_inicio, data_fim = intervalo_data
                else:
                    data_inicio = data_fim = intervalo_data
            else:
                data_inicio = data_fim = None
            
            # Filtro de plataforma
            if 'plataforma' in st.session_state.dados_atuais.columns:
                plataformas = st.session_state.dados_atuais['plataforma'].unique().tolist()
                plataformas_selecionadas = plataformas
            else:
                plataformas_selecionadas = None
            
            # Filtro de campanha
            if 'nome_campanha' in st.session_state.dados_atuais.columns:
                campanhas = st.session_state.dados_atuais['nome_campanha'].unique().tolist()
                campanhas_selecionadas = st.multiselect(
                    "Campanha",
                    options=campanhas,
                    default=campanhas
                )
            else:
                campanhas_selecionadas = None
            
            # Aplicar filtros aos dados
            dados_filtrados = st.session_state.dados_atuais.copy()
            
            if data_inicio and data_fim and 'data' in dados_filtrados.columns:
                dados_filtrados = dados_filtrados[
                    (dados_filtrados['data'].dt.date >= data_inicio) & 
                    (dados_filtrados['data'].dt.date <= data_fim)
                ]
            
            if plataformas_selecionadas and 'plataforma' in dados_filtrados.columns:
                dados_filtrados = dados_filtrados[dados_filtrados['plataforma'].isin(plataformas_selecionadas)]
            
            if campanhas_selecionadas and 'nome_campanha' in dados_filtrados.columns:
                dados_filtrados = dados_filtrados[dados_filtrados['nome_campanha'].isin(campanhas_selecionadas)]
        else:
            dados_filtrados = pd.DataFrame()
    
    # Área de conteúdo principal
    if st.session_state.dados_atuais.empty:
        st.warning("Nenhum dado disponível. Verifique seus endpoints de API e clique em 'Atualizar'.")
        
        # Adicionar um botão para carregar dados de exemplo para demonstração
        if st.button("Carregar Dados de Exemplo"):
            with st.spinner("Carregando dados de exemplo..."):
                # Criar dados de exemplo
                datas = pd.date_range(start='2025-04-01', end='2025-09-30')
                campanhas = ['Reconhecimento de Marca', 'Retargeting', 'Conversão', 'Prospecção']
                plataformas = ['Google Ads', 'Meta Ads']
                
                dados = []
                for data in datas:
                    for campanha in campanhas:
                        for plataforma in plataformas:
                            # Gerar dados aleatórios
                            cliques = int(np.random.normal(100, 30))
                            gasto = round(np.random.normal(50, 15), 2)
                            impressoes = cliques * 50
                            conversoes = int(cliques * 0.05)
                            receita = gasto * 3
                            
                            if plataforma == 'Meta Ads':
                                dados.append({
                                    'data': data,
                                    'nome_campanha': campanha,
                                    'nome_conjunto_anuncios': f'Conjunto {campanha}',
                                    'nome_anuncio': f'Anúncio {campanha} {data.day}',
                                    'plataforma': plataforma,
                                    'cliques': cliques,
                                    'gasto': gasto,
                                    'impressoes': impressoes,
                                    'alcance': int(impressoes * 0.7),
                                    'acoes_compra': conversoes,
                                    'valor_acoes_compra': receita
                                })
                            else:
                                dados.append({
                                    'data': data,
                                    'nome_campanha': campanha,
                                    'nome_anuncio': f'Anúncio {campanha} {data.day}',
                                    'plataforma': plataforma,
                                    'cliques': cliques,
                                    'gasto': gasto,
                                    'impressoes': impressoes,
                                    'conversoes': conversoes,
                                    'valor_conversao': receita
                                })
                
                df_exemplo = pd.DataFrame(dados)
                st.session_state.dados_atuais = df_exemplo
                st.session_state.ultima_atualizacao = datetime.now()
                dados_filtrados = df_exemplo
                st.success("Dados de exemplo carregados com sucesso!")
                st.rerun()
    else:
        # Mostrar a página selecionada
        if st.session_state.pagina_atual == "Geral":
            mostrar_pagina_geral(dados_filtrados)
        elif st.session_state.pagina_atual == "Google Ads":
            mostrar_pagina_google_ads(dados_filtrados)
        elif st.session_state.pagina_atual == "Meta Ads":
            mostrar_pagina_meta_ads(dados_filtrados)
    
    # Lógica de atualização automática
    if st.session_state.atualizacao_automatica:
        # Verificar se é hora de atualizar (a cada 5 minutos)
        if (st.session_state.ultima_atualizacao is None or 
            (datetime.now() - st.session_state.ultima_atualizacao).total_seconds() >= 300):
            # Usar um placeholder para mostrar o status de atualização
            placeholder_atualizacao = st.empty()
            placeholder_atualizacao.info("Atualizando dados automaticamente...")
            
            # Armazenar dados anteriores para cálculos de delta
            st.session_state.dados_anteriores = st.session_state.dados_atuais.copy() if not st.session_state.dados_atuais.empty else None
            
            # Carregar novos dados
            df, erro = st.session_state.carregador_dados.carregar_dados()
            
            if erro:
                placeholder_atualizacao.error(f"Erro ao carregar dados: {erro}")
            else:
                st.session_state.dados_atuais = df
                st.session_state.ultima_atualizacao = datetime.now()
                placeholder_atualizacao.success("Dados atualizados com sucesso!")
                
                # Limpar a mensagem após 3 segundos
                time.sleep(3)
                placeholder_atualizacao.empty()
                
                # Executar novamente o aplicativo para mostrar dados atualizados
                st.rerun()

if __name__ == "__main__":
    main()
    
