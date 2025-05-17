import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('meta_api')

# Tipos de conversão a serem considerados
CONVERSION_TYPES = [
    "offsite_conversion.custom",
    "lead",
    "purchase",
    "submit_application",
    "complete_registration",
    "onsite_conversion.messaging_conversation_started_7d"  # Conversas iniciadas
]

class MetaAdsAPI:
    """
    Classe para lidar com requisições à API do Meta Ads e processamento de dados
    """
    
    def __init__(self, api_version="v22.0"):
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{api_version}"
        self.retry_count = 3
        self.retry_delay = 5  # segundos
    
    def _make_request(self, url, params):
        """
        Fazer uma requisição à API do Meta com lógica de retry
        """
        for attempt in range(self.retry_count):
            try:
                response = requests.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    return response.json()
                
                # Lidar com limitação de taxa
                if response.status_code == 429:
                    wait_time = int(response.headers.get('Retry-After', self.retry_delay))
                    logger.warning(f"Limitação de taxa. Aguardando {wait_time} segundos.")
                    time.sleep(wait_time)
                    continue
                
                # Lidar com outros erros
                logger.error(f"Falha na requisição à API: {response.status_code} - {response.text}")
                return None
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Exceção na requisição: {str(e)}")
                time.sleep(self.retry_delay)
        
        logger.error(f"Falha após {self.retry_count} tentativas")
        return None
    
    def get_account_campaigns(self, account_id, token, limit=100):
        """
        Obter campanhas para uma conta de anúncios
        """
        url = f"{self.base_url}/{account_id}/campaigns"
        params = {
            "fields": "id,name,status,start_time,stop_time,updated_time,objective",
            "limit": limit,
            "access_token": token
        }
        
        return self._make_request(url, params)
    
    def get_campaign_insights(self, campaign_id, token, start_date, end_date, fields=None):
        """
        Obter insights para uma campanha
        """
        if fields is None:
            fields = "spend,impressions,clicks,ctr,cpm,actions,action_values,frequency,reach"
            
        url = f"{self.base_url}/{campaign_id}/insights"
        params = {
            "fields": fields,
            "time_range[since]": start_date,
            "time_range[until]": end_date,
            "level": "campaign",
            "access_token": token
        }
        
        return self._make_request(url, params)
    
    def get_daily_insights(self, campaign_id, token, start_date, end_date):
        """
        Obter insights diários para uma campanha
        """
        url = f"{self.base_url}/{campaign_id}/insights"
        params = {
            "fields": "spend,impressions,clicks,actions,action_values,reach",
            "time_range[since]": start_date,
            "time_range[until]": end_date,
            "time_increment": 1,
            "level": "campaign",
            "access_token": token
        }
        
        return self._make_request(url, params)
    
    def process_campaign_data(self, campaigns_data, insights_data):
        """
        Processar e combinar dados de campanhas e insights
        """
        if not campaigns_data or not insights_data:
            return pd.DataFrame()
        
        # Processar campanhas
        campaigns = []
        for campaign in campaigns_data.get('data', []):
            campaigns.append({
                'campaign_id': campaign.get('id'),
                'campaign_name': campaign.get('name'),
                'status': campaign.get('status'),
                'objective': campaign.get('objective'),
                'start_time': campaign.get('start_time'),
                'stop_time': campaign.get('stop_time'),
                'updated_time': campaign.get('updated_time')
            })
        
        campaigns_df = pd.DataFrame(campaigns)
        
        # Processar insights
        insights = []
        for insight in insights_data.get('data', []):
            # Extrair ações (conversões) e valores
            conversions = {}
            total_conversions = 0
            conversion_value = 0
            
            if 'actions' in insight:
                for action in insight['actions']:
                    action_type = action.get('action_type')
                    if action_type in CONVERSION_TYPES:
                        value = int(action.get('value', 0))
                        conversions[action_type] = value
                        total_conversions += value
            
            if 'action_values' in insight:
                for action_value in insight['action_values']:
                    if action_value.get('action_type') in ['purchase']:
                        conversion_value += float(action_value.get('value', 0))
            
            insights.append({
                'campaign_id': insight.get('campaign_id'),
                'spend': float(insight.get('spend', 0)),
                'impressions': int(insight.get('impressions', 0)),
                'clicks': int(insight.get('clicks', 0)),
                'ctr': float(insight.get('ctr', 0)),
                'cpm': float(insight.get('cpm', 0)),
                'frequency': float(insight.get('frequency', 0)),
                'reach': int(insight.get('reach', 0)),
                'conversions': total_conversions,
                'conversion_details': conversions,
                'conversion_value': conversion_value
            })
        
        insights_df = pd.DataFrame(insights)
        
        # Mesclar dados
        if not insights_df.empty and not campaigns_df.empty:
            merged_df = pd.merge(campaigns_df, insights_df, on='campaign_id', how='inner')
            
            # Calcular métricas adicionais
            merged_df['cpc'] = merged_df.apply(
                lambda row: row['spend'] / row['clicks'] if row['clicks'] > 0 else 0, 
                axis=1
            )
            
            merged_df['cpa'] = merged_df.apply(
                lambda row: row['spend'] / row['conversions'] if row['conversions'] > 0 else 0, 
                axis=1
            )
            
            merged_df['roas'] = merged_df.apply(
                lambda row: row['conversion_value'] / row['spend'] if row['spend'] > 0 else 0, 
                axis=1
            )
            
            return merged_df
        
        return pd.DataFrame()
    
    def process_daily_data(self, daily_insights_data):
        """
        Processar dados diários de insights
        """
        if not daily_insights_data or 'data' not in daily_insights_data:
            return pd.DataFrame()
        
        daily_results = []
        
        for day_data in daily_insights_data.get('data', []):
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
    
    def get_account_data(self, account_id, token, start_date, end_date, prev_start_date, prev_end_date):
        """
        Obter dados completos para uma conta, incluindo período atual e anterior
        """
        try:
            # Obter campanhas
            campaigns_data = self.get_account_campaigns(account_id, token)
            
            if not campaigns_data or 'data' not in campaigns_data or not campaigns_data['data']:
                logger.warning(f"Nenhuma campanha encontrada para a conta {account_id}")
                return pd.DataFrame(), pd.DataFrame()
            
            # Processar cada campanha
            current_campaign_data = []
            previous_campaign_data = []
            
            for campaign in campaigns_data['data']:
                campaign_id = campaign['id']
                
                # Obter insights para o período atual
                current_insights_data = self.get_campaign_insights(
                    campaign_id, token, start_date, end_date
                )
                
                if current_insights_data and 'data' in current_insights_data and current_insights_data['data']:
                    # Processar dados desta campanha para o período atual
                    campaign_data = self.process_campaign_data(
                        {'data': [campaign]}, 
                        current_insights_data
                    )
                    
                    if not campaign_data.empty:
                        current_campaign_data.append(campaign_data)
                
                # Obter insights para o período anterior
                previous_insights_data = self.get_campaign_insights(
                    campaign_id, token, prev_start_date, prev_end_date
                )
                
                if previous_insights_data and 'data' in previous_insights_data and previous_insights_data['data']:
                    # Processar dados desta campanha para o período anterior
                    campaign_data = self.process_campaign_data(
                        {'data': [campaign]}, 
                        previous_insights_data
                    )
                    
                    if not campaign_data.empty:
                        previous_campaign_data.append(campaign_data)
            
            # Combinar todos os dados de campanhas
            current_df = pd.concat(current_campaign_data, ignore_index=True) if current_campaign_data else pd.DataFrame()
            previous_df = pd.concat(previous_campaign_data, ignore_index=True) if previous_campaign_data else pd.DataFrame()
            
            return current_df, previous_df
            
        except Exception as e:
            logger.error(f"Erro ao obter dados da conta: {str(e)}")
            return pd.DataFrame(), pd.DataFrame()
    
    def get_daily_account_data(self, account_id, token, campaign_id, start_date, end_date):
        """
        Obter dados diários para uma campanha específica
        """
        try:
            daily_insights_data = self.get_daily_insights(
                campaign_id, token, start_date, end_date
            )
            
            if daily_insights_data and 'data' in daily_insights_data:
                return self.process_daily_data(daily_insights_data)
            
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Erro ao obter dados diários: {str(e)}")
            return pd.DataFrame()