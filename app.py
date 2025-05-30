import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import re
from time import sleep

# Set page config
st.set_page_config(
    page_title="Meta Ads Campaign Manager",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #1877F2;
    }
    .sub-header {
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    .stButton button {
        background-color: #000000;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #ffffff;
        color: black;
        border-radius: 5px;
        border-color: #ff0000;
    }
    .success-message {
        background-color: #e6f7e6;
        color: #2e7d32;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    .error-message {
        background-color: #ffebee;
        color: #c62828;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    .upload-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }
    .validation-section {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #c3e6c3;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if 'page' not in st.session_state:
    st.session_state.page = 'Create Ads'

# Function to validate URL
def is_valid_url(url):
    if not url:
        return False
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

def is_valid_driveurl(url):
    if not url:
        return False
    url_pattern_drive = re.compile(
        r'^https?://'  # http:// ou https://
        r'(?:www\.)?'  # opcional www
        r'drive\.google\.com'  # domínio fixo do Google Drive
        r'(?:/[\w\-./?=&%]*)?$',  # caminhos e parâmetros permitidos
        re.IGNORECASE
    )
    return url_pattern_drive.match(url)

# Function to send data to webhook
def send_to_webhook(data, endpoint_url):
    try:
        response = requests.post(
            endpoint_url,
            json=data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            return True, "Dados enviados com sucesso!"
        else:
            return False, f"Erro: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Erro: {str(e)}"

# Function for Create Ads page
def show_create_ads_page():
    st.markdown('<h1 class="main-header">🧩 Criar Anúncios</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Crie anúncios baseados em conjuntos de anúncios existentes</p>', unsafe_allow_html=True)
    
    # Initialize session state for ads data if it doesn't exist
    if 'ads_df' not in st.session_state:
        st.session_state.ads_df = pd.DataFrame(columns=[
            "ID Adset", "Nome Anúncio", "Tipo de Anúncio", "ID da Página do Facebook",
            "Status do Anúncio", "Link de Destino", "Texto do Anúncio", 
            "Call to Action (CTA)", "BM Conectada", "ID Conta de Anúncios"
        ])
    
    # Create the data editor
    edited_df = st.data_editor(
        st.session_state.ads_df,
        column_config={
            "ID Adset": st.column_config.NumberColumn("ID Adset", required=True),
            "Nome Anúncio": st.column_config.TextColumn("Nome Anúncio", required=True),
            "Tipo de Anúncio": st.column_config.SelectboxColumn(
                "Tipo de Anúncio", 
                options=["Image", "Video", "Carousel"], 
                required=True
            ),
            "ID da Página do Facebook": st.column_config.NumberColumn("ID da Página do Facebook", required=True),
            "Status do Anúncio": st.column_config.SelectboxColumn(
                "Status do Anúncio", 
                options=["ACTIVE", "PAUSED"], 
                required=True
            ),
            "Link de Destino": st.column_config.TextColumn("Link de Destino", required=True),
            "Texto do Anúncio": st.column_config.TextColumn("Texto do Anúncio", required=True),
            "Call to Action (CTA)": st.column_config.SelectboxColumn(
                "Call to Action (CTA)", 
                options=["BUY_NOW", "LEARN_MORE", "SIGN_UP", "DOWNLOAD", "GET_QUOTE", 
                        "CONTACT_US", "APPLY_NOW", "BOOK_NOW", "GET_OFFER", "SUBSCRIBE", "WATCH_MORE"], 
                required=True
            ),
            "BM Conectada": st.column_config.SelectboxColumn(
                "BM Conectada", 
                options=["Piai & Associados", "V4 Ferraz & Co"], 
                required=True
            ),
            "ID Conta de Anúncios": st.column_config.NumberColumn("ID Conta de Anúncios", required=True)
        },
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True
    )
    
    # Update the session state with the edited DataFrame
    st.session_state.ads_df = edited_df
    
    # Upload sections
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("📷 **Upload de Imagem / Vídeo**")
        st.markdown("Link do Drive da Imagem")
        image_links = st.text_area(
            "Adicione a URL do drive de sua Imagem / Vídeo Aqui",
            placeholder="https://drive.google.com/file/d/exemplo-exemplo/view?usp=drive_link",
            value="http://drive.google.com/open?id=COLE_O_ID_AQUI",
            height=100,
            help="Certifique-se de que o arquivo esteja compartilhado.",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("🎬 **Upload de Thumbnail de Vídeo**")
        st.markdown("Link do Drive da Thumbnail (Caso tipo de anúncio = vídeo)")
        thumbnail_link = st.text_area(
            "Adicione a URL do drive de sua Thumbnail Aqui",
            placeholder="https://drive.google.com/file/d/exemplo-exemplo/view?usp=drive_link",
            value="http://drive.google.com/open?id=COLE_O_ID_AQUI",
            height=100,
            help="Certifique-se de que o arquivo esteja compartilhado.",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    
    validation_messages = []
    
    # Validate DataFrame
    if not st.session_state.ads_df.empty:
        for index, row in st.session_state.ads_df.iterrows():
            # Check for missing required fields
            for col in st.session_state.ads_df.columns:
                if pd.isna(row[col]) or row[col] == "":
                    validation_messages.append(f"❌ Linha {index+1}: {col} é obrigatório")
            
            # Validate destination link
            if not pd.isna(row["Link de Destino"]) and row["Link de Destino"]:
                if not is_valid_url(row["Link de Destino"]):
                    validation_messages.append(f"❌ Linha {index+1}: Link de Destino deve ser uma URL válida")
    
    # Validate image links
    if image_links:
        for line_num, link in enumerate(image_links.strip().split('\n'), 1):
            if link.strip() and not is_valid_driveurl(link.strip()):
                validation_messages.append(f"❌ Link de Imagem linha {line_num}: URL inválida || Verifique se o link da imagem é de um drive")
    
    # Validate thumbnail link
    if thumbnail_link and not is_valid_driveurl(thumbnail_link.strip()):
        validation_messages.append("❌ Link de Thumbnail: URL inválida || Faça upload da Imagem no google Drive")
    
    if validation_messages:
        for msg in validation_messages:
            st.markdown(msg)
    else:
        st.markdown("✅ Todos os campos estão válidos!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Submit button
    st.divider()
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        submit_button = st.button("🚀 Enviar Anúncios", type="primary", use_container_width=True)
    
    # Process form submission
    if submit_button:
        if st.session_state.ads_df.empty:
            st.error("Por favor, adicione pelo menos um anúncio antes de enviar.")
        elif validation_messages:
            st.error("Por favor, corrija os erros de validação antes de enviar.")
        else:
            # Prepare data for submission
            ads_data = st.session_state.ads_df.to_dict('records')
            
            # Add image and thumbnail links
            image_urls = [link.strip() for link in image_links.split('\n') if link.strip()] if image_links else []
            thumbnail_url = thumbnail_link.strip() if thumbnail_link else ""
            
            for ad in ads_data:
                ad["Imagens"] = image_urls
                ad["Thumbnail (Video)"] = thumbnail_url
                ad["SubmissionTime"] = str(datetime.now())
            
            # Prepare final payload
            payload = {
                "tipo_requisicao": "criar_anuncio",
                "dados": ads_data,
                "timestamp": str(datetime.now())
            }
            
            # Send to webhook
            webhook_url = "https://ferrazpiai-n8n-editor.uyk8ty.easypanel.host/webhook-test/e78ecade-5474-4877-93a6-f91980088282"
            success, message = send_to_webhook(payload, webhook_url)
            
            if success:
                st.markdown("✅ Envio feito com sucesso!")
                st.markdown(f'<div class="success-message">{message}</div>', unsafe_allow_html=True)
                # Clear form after successful submission
                st.session_state.ads_df = pd.DataFrame(columns=[
                    "Nome Anúncio", "Tipo de Anúncio", "ID da Página do Facebook", 
                    "Status do Anúncio", "Link de Destino", "Texto do Anúncio", 
                    "Call to Action (CTA)", "BM Conectada", "ID Conta de Anúncios"
                ])
                sleep(5)
                st.rerun()
            else:
                st.markdown(f'<div class="error-message">{message}</div>', unsafe_allow_html=True)
            
            st.subheader("📋 Preview JSON")
            st.json(payload, expanded=False)

# Function for Create Campaigns page
def show_create_campaigns_page():
    st.markdown('<h1 class="main-header">🚀 Criar Campanhas</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Crie campanhas completas com entrada manual ou templates</p>', unsafe_allow_html=True)
    
    # Campaign templates
    templates = {
        "Lead Gen for Real Estate": {
            "Tipo de Campanha": "ABO",
            "Objetivo da Campanha": "LEAD_GENERATION",
            "Status da Campanha": "ACTIVE",
            "Tipo de Otimização": "LEAD_GENERATION",
            "Cobrança do Adset": "IMPRESSIONS",
            "Estratégia de Lance": "LOWEST_COST_WITHOUT_CAP",
            "Tipo de Anúncio": "Image",
            "CTA": "LEARN_MORE",
            "Tipo de Destino": "WEBSITE"
        },
        "E-commerce Conversions": {
            "Tipo de Campanha": "CBO",
            "Objetivo da Campanha": "SALES",
            "Status da Campanha": "ACTIVE",
            "Tipo de Otimização": "CONVERSIONS",
            "Cobrança do Adset": "IMPRESSIONS",
            "Estratégia de Lance": "COST_CAP",
            "Tipo de Anúncio": "Carousel",
            "CTA": "BUY_NOW",
            "Tipo de Destino": "WEBSITE"
        }
    }
    
    # Template selection
    st.subheader("📋 Template de Campanha (Opcional)")
    selected_template = st.selectbox(
        "Selecione um template ou crie do zero",
        ["Criar do zero"] + list(templates.keys())
    )
    
    # Initialize form values based on template
    if selected_template != "Criar do zero" and selected_template in templates:
        template_data = templates[selected_template]
    else:
        template_data = {}
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Info Geral da Campanha", "⚙️ Configurações do Ad Set", "🎨 Info Criativa", "🎯 Segmentação de Audiência"])
    
    with tab1:
        st.subheader("Informações Gerais da Campanha")
        
        col1, col2 = st.columns(2)
        with col1:
            page_id = st.number_input("ID da Página", min_value=1, value=None, placeholder="Digite o ID da Página")
            ad_account_id = st.number_input("ID da Conta de Anúncios", min_value=1, value=None, placeholder="Digite o ID da Conta")
        
        with col2:
            campaign_type = st.selectbox(
                "Tipo de Campanha",
                ["ABO", "CBO", "ADV+"],
                index=["ABO", "CBO", "ADV+"].index(template_data.get("Tipo de Campanha", "ABO"))
            )
        
        campaign_name = st.text_input("Nome da Campanha", placeholder="Digite o Nome da Campanha")
        
        campaign_objective = st.selectbox(
            "Objetivo da Campanha",
            ["AWARENESS", "TRAFFIC", "ENGAGEMENT", "LEAD_GENERATION", "APP_PROMOTION", "SALES"],
            index=["AWARENESS", "TRAFFIC", "ENGAGEMENT", "LEAD_GENERATION", "APP_PROMOTION", "SALES"].index(template_data.get("Objetivo da Campanha", "AWARENESS"))
        )
    
    with tab2:
        st.subheader("Configurações do Ad Set")
        
        col1, col2 = st.columns(2)
        with col1:
            campaign_status = st.selectbox(
                "Status da Campanha",
                ["ACTIVE", "PAUSED"],
                index=["ACTIVE", "PAUSED"].index(template_data.get("Status da Campanha", "ACTIVE"))
            )
            
            ad_set_name = st.text_input("Nome do Ad Set", placeholder="Digite o Nome do Ad Set")
        
        # Dynamic optimization options based on campaign objective
        optimization_options = {
            "AWARENESS": ["IMPRESSIONS", "REACH", "BRAND_AWARENESS"],
            "TRAFFIC": ["LINK_CLICKS", "LANDING_PAGE_VIEWS"],
            "ENGAGEMENT": ["POST_ENGAGEMENT", "PAGE_LIKES", "EVENT_RESPONSES"],
            "LEAD_GENERATION": ["LEAD_GENERATION", "CONVERSIONS"],
            "APP_PROMOTION": ["APP_INSTALLS", "APP_EVENTS"],
            "SALES": ["CONVERSIONS", "CATALOG_SALES", "VALUE"]
        }
        
        current_optimization_options = optimization_options.get(campaign_objective, ["IMPRESSIONS"])
        
        with col2:
            optimization_type = st.selectbox(
                "Tipo de Otimização",
                current_optimization_options,
                index=current_optimization_options.index(template_data.get("Tipo de Otimização", current_optimization_options[0]))
            )
        
        # Dynamic billing event options
        billing_event_options = ["IMPRESSIONS", "LINK_CLICKS", "THRUPLAY", "TWO_SECOND_CONTINUOUS_VIDEO_VIEWS"]
        
        col1, col2 = st.columns(2)
        with col1:
            billing_event = st.selectbox(
                "Cobrança do Adset",
                billing_event_options,
                index=billing_event_options.index(template_data.get("Cobrança do Adset", "IMPRESSIONS"))
            )
        
        # Bid strategy options
        bid_strategy_options = ["LOWEST_COST_WITHOUT_CAP", "COST_CAP", "LOWEST_COST_WITH_BID_CAP"]
        
        with col2:
            bid_strategy = st.selectbox(
                "Estratégia de Lance",
                bid_strategy_options,
                index=bid_strategy_options.index(template_data.get("Estratégia de Lance", "LOWEST_COST_WITHOUT_CAP"))
            )
        
        col1, col2 = st.columns(2)
        with col1:
            daily_budget = st.number_input("Orçamento Diário", min_value=1.0, step=0.5, format="%.2f")
        
        with col2:
            bid_cap = st.number_input("Valor Máximo de Lance (Opcional)", min_value=0.1, step=0.1, format="%.2f", value=None)
    
    with tab3:
        st.subheader("Informações Criativas")
        
        col1, col2 = st.columns(2)
        with col1:
            ad_type = st.selectbox(
                "Tipo de Anúncio",
                ["Image", "Video", "Carousel"],
                index=["Image", "Video", "Carousel"].index(template_data.get("Tipo de Anúncio", "Image"))
            )
            
            ad_name = st.text_input("Nome do Anúncio", placeholder="Digite o Nome do Anúncio")
        
        with col2:
            destination_link = st.text_input("Link de Destino", placeholder="https://exemplo.com")
        
        ad_text = st.text_area("Texto do Anúncio", placeholder="Digite o texto do seu anúncio aqui...")
        
        col1, col2 = st.columns(2)
        with col1:
            # CTA options
            cta_options = ["BUY_NOW", "LEARN_MORE", "SIGN_UP", "DOWNLOAD", "GET_QUOTE", "CONTACT_US", "APPLY_NOW", "BOOK_NOW", "GET_OFFER", "SUBSCRIBE", "WATCH_MORE"]
            
            cta = st.selectbox(
                "Call to Action",
                cta_options,
                index=cta_options.index(template_data.get("CTA", "LEARN_MORE"))
            )
        
        with col2:
            # Destination type options
            destination_type_options = ["WEBSITE", "MESSENGER", "WHATSAPP", "INSTAGRAM_PROFILE", "APP", "PHONE_CALL", "SHOP"]
            
            destination_type = st.selectbox(
                "Tipo de Destino",
                destination_type_options,
                index=destination_type_options.index(template_data.get("Tipo de Destino", "WEBSITE"))
            )
        
        # Upload sections for campaigns
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("📷 **Upload de Imagem / Vídeo**")
            st.markdown("Link do Drive da Imagem")
            campaign_image_links = st.text_area(
                "Adicione a URL do drive de sua Imagem / Vídeo Aqui",
                placeholder="https://drive.google.com/file/d/...",
                height=100,
                label_visibility="collapsed",
                key="campaign_images"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("🎬 **Upload de Thumbnail de Vídeo**")
            st.markdown("Link do Drive da Thumbnail")
            campaign_thumbnail_link = st.text_area(
                "Adicione a URL do drive de sua Thumbnail Aqui",
                placeholder="https://drive.google.com/file/d/...",
                height=100,
                label_visibility="collapsed",
                key="campaign_thumbnail"
            )
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.subheader("Segmentação de Audiência")
        
        col1, col2 = st.columns(2)
        with col1:
            connected_bm = st.selectbox(
                "Conta em Qual BM?",
                ["Piai & Associados", "V4 Ferraz & Co"]
            )
        
        col1, col2 = st.columns(2)
        with col1:
            min_age = st.number_input("Idade Mínima", min_value=13, max_value=65, value=18)
        
        with col2:
            max_age = st.number_input("Idade Máxima", min_value=13, max_value=65, value=65)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            city = st.text_input("Cidade", placeholder="ex: São Paulo")
        
        with col2:
            state = st.text_input("Estado (SP, AL, MT...)", placeholder="ex: SP, RJ")
        
        with col3:
            country = st.text_input("País (BR, Us...)", placeholder="ex: BR, US")
        
        radius = st.slider("Raio de Distância (Milhas)", min_value=1, max_value=18, value=9)
    
    # Validation warnings
    st.subheader("⚠️ Validação")
    
    # Check for compatibility between objective and optimization
    valid_combinations = {
        "AWARENESS": ["IMPRESSIONS", "REACH", "BRAND_AWARENESS"],
        "TRAFFIC": ["LINK_CLICKS", "LANDING_PAGE_VIEWS"],
        "ENGAGEMENT": ["POST_ENGAGEMENT", "PAGE_LIKES", "EVENT_RESPONSES"],
        "LEAD_GENERATION": ["LEAD_GENERATION", "CONVERSIONS"],
        "APP_PROMOTION": ["APP_INSTALLS", "APP_EVENTS"],
        "SALES": ["CONVERSIONS", "CATALOG_SALES", "VALUE"]
    }
    
    if campaign_objective and optimization_type:
        if optimization_type not in valid_combinations.get(campaign_objective, []):
            st.warning(f"⚠️ O tipo de otimização '{optimization_type}' pode não ser compatível com o objetivo da campanha '{campaign_objective}'.")
    
    # Check for compatibility between CTA and destination type
    incompatible_cta_destination = {
        "BUY_NOW": ["PHONE_CALL"],
        "LEARN_MORE": [],
        "SIGN_UP": ["PHONE_CALL"],
        "DOWNLOAD": ["PHONE_CALL", "MESSENGER"],
        "GET_QUOTE": ["APP"],
        "CONTACT_US": [],
        "APPLY_NOW": ["PHONE_CALL"],
        "BOOK_NOW": ["APP"],
        "GET_OFFER": ["PHONE_CALL"],
        "SUBSCRIBE": ["PHONE_CALL"],
        "WATCH_MORE": ["PHONE_CALL"]
    }
    
    if cta and destination_type:
        if destination_type in incompatible_cta_destination.get(cta, []):
            st.warning(f"⚠️ O CTA '{cta}' pode não ser compatível com o tipo de destino '{destination_type}'.")
    
    # Submit button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        submit_button = st.button("🚀 Enviar Campanha", type="primary", use_container_width=True)
    
    # Process form submission
    if submit_button:
        # Validate required fields
        required_fields = {
            "ID da Página": page_id,
            "ID da Conta de Anúncios": ad_account_id,
            "Nome da Campanha": campaign_name,
            "Nome do Ad Set": ad_set_name,
            "Nome do Anúncio": ad_name,
            "Link de Destino": destination_link,
            "Texto do Anúncio": ad_text
        }
        
        missing_fields = [field for field, value in required_fields.items() if not value]
        
        # Validate URL format for Destination Link
        invalid_url = False
        if destination_link and not is_valid_url(destination_link):
            invalid_url = True
        
        if missing_fields:
            st.error(f"Por favor, preencha todos os campos obrigatórios: {', '.join(missing_fields)}")
        elif invalid_url:
            st.error("Link de Destino deve ser uma URL válida começando com http:// ou https://")
        else:
            # Prepare image and thumbnail links
            image_urls = [link.strip() for link in campaign_image_links.split('\n') if link.strip()] if campaign_image_links else []
            thumbnail_url = campaign_thumbnail_link.strip() if campaign_thumbnail_link else ""
            
            # Prepare data for submission
            campaign_data = {
                "ID da Página": page_id,
                "ID da Conta de Anúncios": ad_account_id,
                "Tipo de Campanha": campaign_type,
                "Nome da Campanha": campaign_name,
                "Objetivo da Campanha": campaign_objective,
                "Status da Campanha": campaign_status,
                "Nome do Ad Set": ad_set_name,
                "Tipo de Otimização": optimization_type,
                "Cobrança do Adset": billing_event,
                "Estratégia de Lance": bid_strategy,
                "Orçamento Diário": daily_budget,
                "Valor Máximo de Lance": bid_cap,
                "Tipo de Anúncio": ad_type,
                "Nome do Anúncio": ad_name,
                "Texto do Anúncio": ad_text,
                "Link de Destino": destination_link,
                "CTA": cta,
                "Tipo de Destino": destination_type,
                "Imagens": image_urls,
                "Thumbnail (Video)": thumbnail_url,
                "Conta em Qual BM?": connected_bm,
                "Idade Mínima": min_age,
                "Idade Máxima": max_age,
                "Cidade": city,
                "Estado (SP, AL, MT...)": state,
                "País (BR, EUA...)": country,
                "Raio de Distância": radius,
                "SubmissionTime": str(datetime.now())
            }
            
            # Prepare final payload
            payload = {
                "tipo_requisicao": "criar_campanha",
                "dados": campaign_data,
                "timestamp": str(datetime.now())
            }
            
            # Send to webhook
            webhook_url = "https://ferrazpiai-n8n-editor.uyk8ty.easypanel.host/webhook-test/e78ecade-5474-4877-93a6-f91980088282"
            success, message = send_to_webhook(payload, webhook_url)
            
            if success:
                st.markdown(f'<div class="success-message">{message}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="error-message">{message}</div>', unsafe_allow_html=True)

            # Display JSON preview
            st.subheader("📋 Preview JSON")
            st.json(payload,expanded=False)

# Function for Documentation page
def show_documentation_page():
    st.markdown('<h1 class="main-header">📚 Documentação Interativa</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Aprenda sobre componentes do Meta Ads e melhores práticas</p>', unsafe_allow_html=True)
    
    # Create tabs for different documentation sections
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎯 Objetivos de Campanha", 
        "⚙️ Tipos de Otimização", 
        "💰 Eventos de Cobrança", 
        "📊 Estratégias de Lance", 
        "🔘 CTAs", 
        "🌐 Tipos de Destino"
    ])
    
    with tab1:
        st.header("Objetivos de Campanha")
        st.markdown("""
        Os objetivos de campanha definem a meta principal da sua campanha publicitária. O objetivo escolhido determinará quais opções de otimização e formatos de anúncio estarão disponíveis.
        """)
        
        objectives_data = {
            "Objetivo": ["Awareness", "Traffic", "Engagement", "Leads", "App Promotion", "Sales"],
            "Descrição": [
                "Aumentar o reconhecimento da marca e alcançar um público mais amplo",
                "Direcionar tráfego para seu site, app ou outro destino",
                "Fazer com que mais pessoas interajam com seu conteúdo ou página",
                "Coletar informações de leads de pessoas interessadas",
                "Aumentar instalações de app ou engajamento com seu app",
                "Impulsionar vendas no seu site, app ou através de mensagens"
            ],
            "Melhor Para": [
                "Marcas novas, lançamentos de produtos ou entrada em novos mercados",
                "Blogs, marketing de conteúdo ou direcionamento de visitas ao site",
                "Crescimento de presença nas redes sociais ou promoção de conteúdo",
                "Marketing B2B, empresas de serviços ou registros de eventos",
                "Desenvolvedores de apps móveis ou empresas com aplicativos",
                "Empresas de e-commerce ou marketing de resposta direta"
            ]
        }
        
        st.table(pd.DataFrame(objectives_data))
        
        with st.expander("Saiba Mais Sobre Objetivos de Campanha"):
            st.markdown("""
            ### Awareness (Consciência)
            - **Foco**: Alcance e reconhecimento da marca
            - **Métricas**: Impressões, alcance, brand lift
            - **Exemplo**: Uma nova marca de moda querendo se apresentar a potenciais clientes
            
            ### Traffic (Tráfego)
            - **Foco**: Visitas ao site ou app
            - **Métricas**: Cliques no link, visualizações da página de destino
            - **Exemplo**: Um blog promovendo seus artigos mais recentes
            
            ### Engagement (Engajamento)
            - **Foco**: Interações com conteúdo
            - **Métricas**: Engajamento com posts, curtidas de página, visualizações de vídeo
            - **Exemplo**: Um restaurante promovendo seu cardápio ou eventos
            
            ### Leads
            - **Foco**: Geração de leads e coleta de informações
            - **Métricas**: Preenchimento de formulários, mensagens
            - **Exemplo**: Uma imobiliária coletando informações de contato de potenciais compradores
            
            ### App Promotion (Promoção de App)
            - **Foco**: Instalações e engajamento com app
            - **Métricas**: Instalações de app, eventos de app
            - **Exemplo**: Um desenvolvedor de jogos móveis promovendo um novo jogo
            
            ### Sales (Vendas)
            - **Foco**: Conversões e compras
            - **Métricas**: Compras, adicionar ao carrinho, checkout iniciado
            - **Exemplo**: Uma loja de e-commerce promovendo produtos
            """)
    
    with tab2:
        st.header("Tipos de Otimização")
        st.markdown("""
        Os tipos de otimização (ou metas de desempenho) informam ao algoritmo do Meta qual ação específica você quer que os usuários realizem. Isso ajuda o Meta a mostrar seus anúncios para pessoas mais propensas a realizar essa ação.
        """)
        
        optimization_data = {
            "Tipo de Otimização": [
                "Impressions", 
                "Reach", 
                "Link Clicks",
                "Landing Page Views", 
                "Post Engagement", 
                "Video Views", 
                "Lead Generation", 
                "Conversions", 
                "App Installs", 
                "App Events", 
                "Catalog Sales", 
                "Value"
            ],
            "Descrição": [
                "Maximizar o número de vezes que seu anúncio é exibido",
                "Mostrar seu anúncio para o máximo número de pessoas únicas",
                "Obter o máximo de cliques para seu destino",
                "Obter visitas ao seu site que carregam completamente",
                "Obter o máximo de curtidas, comentários, compartilhamentos ou outras interações",
                "Fazer com que pessoas assistam ao seu conteúdo de vídeo",
                "Coletar o máximo de leads através de formulários do Meta",
                "Impulsionar ações específicas no seu site ou app",
                "Obter o máximo de instalações de app",
                "Impulsionar ações específicas dentro do seu app",
                "Impulsionar vendas do seu catálogo de produtos",
                "Maximizar o valor total de compra"
            ],
            "Compatível Com": [
                "Awareness",
                "Awareness",
                "Traffic",
                "Traffic",
                "Engagement",
                "Engagement",
                "Leads",
                "Leads, Sales",
                "App Promotion",
                "App Promotion",
                "Sales",
                "Sales"
            ]
        }
        
        st.table(pd.DataFrame(optimization_data))
    
    with tab3:
        st.header("Eventos de Cobrança")
        st.markdown("""
        Os eventos de cobrança determinam como o Meta cobra pelos seus anúncios. Diferentes metas de otimização podem ter diferentes eventos de cobrança disponíveis.
        """)
        
        billing_data = {
            "Evento de Cobrança": ["Impressions (CPM)", "Link Clicks (CPC)", "Thruplay", "Two-Second Continuous Video Views"],
            "Descrição": [
                "Você paga por cada 1.000 impressões (vezes que seu anúncio é exibido)",
                "Você paga quando alguém clica no seu anúncio",
                "Você paga quando alguém assiste seu vídeo por pelo menos 15 segundos ou até o final",
                "Você paga quando alguém assiste pelo menos 2 segundos contínuos do seu vídeo"
            ],
            "Compatível Com": [
                "Todos os tipos de otimização",
                "Apenas otimização de Link Clicks",
                "Apenas otimização de Video Views",
                "Apenas otimização de Video Views"
            ],
            "Melhor Para": [
                "Campanhas de brand awareness, alcance, ou quando você confia na otimização do Meta",
                "Campanhas de tráfego quando você quer pagar apenas por cliques reais",
                "Campanhas de vídeo quando você quer espectadores engajados",
                "Campanhas de vídeo quando você quer exposição mais ampla de vídeo"
            ]
        }
        
        st.table(pd.DataFrame(billing_data))
    
    with tab4:
        st.header("Estratégias de Lance")
        st.markdown("""
        As estratégias de lance determinam como o Meta gerencia seus lances no leilão de anúncios. Diferentes estratégias oferecem níveis variados de controle sobre custos versus volume.
        """)
        
        bid_data = {
            "Estratégia de Lance": [
                "Highest Volume or Value (anteriormente Lowest Cost)", 
                "Cost per Result Goal (anteriormente Cost Cap)", 
                "Bid Cap", 
                "ROAS Goal"
            ],
            "Descrição": [
                "Meta automaticamente faz lances para obter o máximo de resultados dentro do seu orçamento",
                "Meta tenta manter seu custo médio por resultado em ou abaixo do seu alvo",
                "Define um valor máximo estrito que você pagará por cada resultado",
                "Meta tenta alcançar seu retorno alvo sobre gasto com anúncios"
            ],
            "Nível de Controle": [
                "Baixo controle, alta automação",
                "Controle médio, automação média",
                "Alto controle, baixa automação",
                "Controle médio, focado em valor"
            ],
            "Melhor Para": [
                "Maioria dos anunciantes, especialmente ao começar",
                "Anunciantes com alvos específicos de CPA que ainda querem volume",
                "Anunciantes com limites rígidos de custo que não podem exceder",
                "E-commerce com otimização baseada em valor"
            ]
        }
        
        st.table(pd.DataFrame(bid_data))
    
    with tab5:
        st.header("Call to Action (CTA) Buttons")
        st.markdown("""
        Os botões de Call to Action orientam os usuários sobre qual ação tomar após ver seu anúncio. O CTA certo pode impactar significativamente sua taxa de conversão.
        """)
        
        cta_data = {
            "Botão CTA": [
                "Learn More", 
                "Shop Now", 
                "Sign Up", 
                "Download", 
                "Get Quote", 
                "Contact Us", 
                "Apply Now", 
                "Book Now", 
                "Get Offer", 
                "Subscribe", 
                "Watch More"
            ],
            "Melhor Para": [
                "Awareness, conteúdo educacional, posts de blog",
                "E-commerce, páginas de produtos, catálogos",
                "Inscrições em newsletter, criação de conta",
                "Apps, PDFs, recursos, ferramentas",
                "Serviços que requerem preços personalizados",
                "Atendimento ao cliente, consultas",
                "Candidaturas a emprego, solicitações de empréstimo",
                "Agendamentos, reservas, eventos",
                "Promoções, descontos, ofertas especiais",
                "Memberships, serviços recorrentes",
                "Conteúdo de vídeo, webinars, tutoriais"
            ],
            "Destinos Compatíveis": [
                "Website, Instagram Profile",
                "Website, Shop",
                "Website, Instant Form",
                "App, Website",
                "Website, Messenger, WhatsApp",
                "Website, Messenger, WhatsApp, Phone Call",
                "Website, Instant Form",
                "Website, Messenger",
                "Website, Shop",
                "Website",
                "Website, Video"
            ]
        }
        
        st.table(pd.DataFrame(cta_data))
    
    with tab6:
        st.header("Tipos de Destino")
        st.markdown("""
        O tipo de destino determina para onde os usuários irão após clicar no seu anúncio. Escolher o destino certo é crucial para proporcionar uma experiência de usuário fluida.
        """)
        
        destination_data = {
            "Tipo de Destino": [
                "Website", 
                "App", 
                "Messenger", 
                "WhatsApp", 
                "Instagram Profile", 
                "Phone Call", 
                "Shop"
            ],
            "Descrição": [
                "Direciona usuários para uma página web ou landing page",
                "Direciona usuários para baixar ou abrir um app",
                "Abre uma conversa no Messenger com seu negócio",
                "Abre uma conversa no WhatsApp com seu negócio",
                "Leva usuários para seu perfil do Instagram",
                "Inicia uma ligação telefônica para seu negócio",
                "Leva usuários para sua Meta Shop ou catálogo"
            ],
            "Melhor Para": [
                "Maioria dos tipos de campanha, especialmente quando você tem um site forte",
                "Promoção de app ou quando seu app oferece a melhor experiência",
                "Comunicação direta, atendimento ao cliente ou vendas personalizadas",
                "Comunicação direta, especialmente para audiências internacionais",
                "Construir seguidores sociais ou mostrar conteúdo visual",
                "Negócios locais ou serviços que requerem conversa direta",
                "Negócios de e-commerce usando recursos de compras do Meta"
            ],
            "Requisitos": [
                "URL válida do site, landing page otimizada para mobile",
                "App registrado no Meta, listagem na app store",
                "Página do Facebook com Messenger habilitado",
                "Conta WhatsApp Business conectada ao Meta",
                "Conta comercial do Instagram vinculada à Página do Facebook",
                "Número de telefone válido",
                "Catálogo de produtos configurado no Commerce Manager"
            ]
        }
        
        st.table(pd.DataFrame(destination_data))
    
    # Compatibility table
    st.header("📊 Tabela de Compatibilidade")
    st.markdown("""
    Esta tabela mostra as combinações recomendadas de Objetivo da Campanha, Meta de Otimização, Estratégia de Lance, CTA e Tipo de Destino.
    """)
    
    compatibility_data = {
        "Objetivo da Campanha": [
            "AWARENESS",
            "TRAFFIC",
            "ENGAGEMENT",
            "LEADS",
            "APP PROMOTION",
            "SALES"
        ],
        "Meta de Otimização": [
            "REACH",
            "LINK_CLICKS",
            "POST_ENGAGEMENT",
            "LEAD_GENERATION",
            "APP_INSTALLS",
            "CONVERSIONS"
        ],
        "Estratégia de Lance Sugerida": [
            "HIGHEST_VOLUME",
            "HIGHEST_VOLUME",
            "HIGHEST_VOLUME",
            "COST_PER_RESULT",
            "COST_PER_RESULT",
            "COST_PER_RESULT"
        ],
        "CTA Recomendado": [
            "LEARN_MORE",
            "LEARN_MORE",
            "WATCH_MORE",
            "SIGN_UP",
            "DOWNLOAD",
            "BUY_NOW"
        ],
        "Destinos Comuns": [
            "WEBSITE",
            "WEBSITE",
            "WEBSITE, ON-POST",
            "WEBSITE, INSTANT_FORM",
            "APP",
            "WEBSITE, SHOP"
        ]
    }
    
    st.table(pd.DataFrame(compatibility_data))

# Sidebar navigation
with st.sidebar:
    # Use the new logo URL (you can replace this with the correct URL when available)
    st.image("https://i.postimg.cc/T2k1kpM0/Chat-GPT-Image-29-de-mai-de-2025-17-52-00-Editado.png", width=300)
    st.title("Meta Ads Manager")
    
    # Navigation buttons
    if st.button("🧩 Criar Anúncios", key="nav_create_ads", use_container_width=True):
        st.session_state.page = 'Create Ads'
    
    if st.button("🚀 Criar Campanhas", key="nav_create_campaigns", use_container_width=True):
        st.session_state.page = 'Create Campaigns'
    
    if st.button("📚 Documentação", key="nav_documentation", use_container_width=True):
        st.session_state.page = 'Documentation'
    
    st.divider()
    st.caption("© 2025 GTBOT")

# Main content based on selected page
if st.session_state.page == 'Create Ads':
    show_create_ads_page()
elif st.session_state.page == 'Create Campaigns':
    show_create_campaigns_page()
elif st.session_state.page == 'Documentation':
    show_documentation_page()
