"""
Simple app review scraper for Via Verde
Gets reviews from App Store and Google Play Store
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json
import gspread
from google.oauth2.service_account import Credentials
from textblob import TextBlob
from collections import Counter
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Warning: google.generativeai not available. Gemini AI features will be disabled.")

def get_app_store_reviews():
    """
    Apple Store reviews - ON HOLD
    Returns empty list for now
    """
    return []

def get_google_play_reviews():
    """
    Get all visible reviews from Google Play Store for Via Verde (Portuguese page)
    Focus on extracting all visible reviews while preserving original language
    """
    try:
        # Google Play Store URL for Via Verde - Portuguese page for better review access
        url = "https://play.google.com/store/apps/details?id=pt.viaverde.clientes&hl=pt_PT"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            reviews_list = []
            
            # Use the exact selectors found by inspecting the page
            # Target the main review containers
            review_selectors = [
                'div.EGFGHd',  # Main review container
                'div[data-testid="review-item"]',  # Fallback
                'div[jsname="gWDdlc"]',  # Fallback
                'div[jsname="yEVEwb"]',  # Fallback
                'div.h3YV2d'  # Last fallback - just text containers
            ]
            
            review_containers = []
            for selector in review_selectors:
                containers = soup.select(selector)
                if containers:
                    review_containers = containers
                    st.info(f"Found {len(containers)} review elements")
                    break
            
            # If no reviews found with selectors, try a more targeted approach
            if not review_containers:
                st.info("No reviews found with standard selectors. Trying alternative approach...")
                
                # Look for elements that might contain reviews, but be more selective
                all_divs = soup.find_all('div')
                for div in all_divs:
                    text = div.get_text(strip=True)
                    
                    # Skip navigation/header elements and privacy policy text
                    skip_words = [
                        'sign in with google', 'library & devices', 'payments & subscriptions', 'play pass', 'settings', 
                        'privacy policy', 'terms of service', 'search', 'help_outline', 'no data shared with third parties',
                        'learn more about how developers declare sharing', 'this app may collect these data types',
                        'location, personal info and 4 others', 'data is encrypted in transit', 'see details',
                        'flag inappropriate', 'show review history', 'more_vert', 'learn more'
                    ]
                    
                    if any(skip_word in text.lower() for skip_word in skip_words):
                        continue
                    
                    # Look for elements that contain actual user review text
                    if (len(text) > 30 and len(text) < 400 and  # Reasonable length for a review
                        any(word in text.lower() for word in ['works', 'good', 'bad', 'bom', 'mau', 'funciona', 'time', 'problem', 'issue', 'bug', 'crash', 'stable', 'unstable', 'frustrating', 'excellent', 'terrible', 'recommend', 'app', 'application', 'erro', 'erros', 'problema', 'problemas', 'funcional', 'não', 'sim', 'ótimo', 'péssimo', 'recomendo']) and
                        not any(skip_word in text.lower() for skip_word in ['google play', 'download', 'install', 'update', 'version', 'android', 'ios', 'device', 'data types', 'encrypted', 'transit', 'privacy', 'policy', 'terms', 'service']) and
                        # Must contain personal opinion words
                        any(opinion_word in text.lower() for opinion_word in ['i', 'my', 'me', 'we', 'us', 'this', 'that', 'it', 'app', 'application'])):
                        review_containers.append(div)
                        # Limit to avoid too many false positives
                        if len(review_containers) >= 10:
                            break
            
            # Process all visible reviews (no limit)
            for i, container in enumerate(review_containers):
                try:
                    # Extract rating and date from the specific header selector
                    rating = 5  # Default rating
                    
                    # Look for rating in the div.Jx4nYe element
                    rating_div = container.select_one('div.Jx4nYe')
                    if rating_div:
                        # Look for aria-label with rating information
                        rating_elements = rating_div.find_all(['div', 'span'], attrs={'aria-label': True})
                        
                        for rating_elem in rating_elements:
                            aria_label = rating_elem.get('aria-label', '')
                            if 'estrelas' in aria_label.lower() or 'stars' in aria_label.lower():
                                import re
                                numbers = re.findall(r'\d+', aria_label)
                                if numbers:
                                    rating = int(numbers[0])
                                    break
                    
                    # Extract review text
                    review_text = "Review text not available"
                    
                    # Look for the review text within the parent container
                    # First try to find div.h3YV2d within this container
                    text_container = container.select_one('div.h3YV2d')
                    if text_container:
                        review_text = text_container.get_text(strip=True)
                    else:
                        # Fallback: look for the longest meaningful text
                        all_text = container.get_text(strip=True)
                        child_text_elements = container.find_all(['span', 'div', 'p'])
                        
                        potential_texts = []
                        for child in child_text_elements:
                            child_text = child.get_text(strip=True)
                            if child_text and len(child_text) > 10:
                                potential_texts.append(child_text)
                        
                        if potential_texts:
                            # Filter texts that look like reviews
                            review_like_texts = []
                            for text in potential_texts:
                                if (len(text) > 20 and 
                                    not any(skip_word in text.lower() for skip_word in ['sign in', 'library', 'payments', 'settings', 'privacy', 'terms', 'search', 'help', 'download', 'install', 'update', 'version', 'android', 'ios'])):
                                    review_like_texts.append(text)
                            
                            if review_like_texts:
                                review_text = max(review_like_texts, key=len)
                            else:
                                review_text = max(potential_texts, key=len)
                        else:
                            review_text = all_text if len(all_text) > 10 else "Review text not available"
                    
                    # Extract date from span.bp9Aid
                    date_text = "Recent"
                    
                    if rating_div:
                        date_span = rating_div.select_one('span.bp9Aid')
                        if date_span:
                            date_text = date_span.get_text(strip=True)
                    
                    # Extract reviewer name from div.X5PpBb
                    reviewer_name = "Unknown"
                    
                    name_div = container.select_one('div.X5PpBb')
                    if name_div:
                        reviewer_name = name_div.get_text(strip=True)
                    
                    # Extract useful count from div.AJTPZc
                    useful_count = 0
                    
                    useful_div = container.select_one('div.AJTPZc')
                    if useful_div:
                        useful_text = useful_div.get_text(strip=True)
                        
                        # Look for Portuguese pattern: "Essa avaliação foi marcada como útil por 118 pessoas"
                        if 'pessoas' in useful_text:
                            import re
                            numbers = re.findall(r'\d+', useful_text)
                            if numbers:
                                useful_count = int(numbers[0])
                        # Also look for English patterns
                        elif 'people' in useful_text:
                            import re
                            numbers = re.findall(r'\d+', useful_text)
                            if numbers:
                                useful_count = int(numbers[0])
                    
                    # Validate that this looks like a real review, not navigation or privacy text
                    skip_words = [
                        'sign in with google', 'library & devices', 'payments & subscriptions', 'play pass', 'settings', 
                        'privacy policy', 'terms of service', 'search', 'help_outline', 'no data shared with third parties',
                        'learn more about how developers declare sharing', 'this app may collect these data types',
                        'location, personal info and 4 others', 'data is encrypted in transit', 'see details',
                        'flag inappropriate', 'show review history', 'more_vert', 'learn more', 'lucas dias'
                    ]
                    
                    # More lenient validation - just check basic requirements
                    if (review_text != "Review text not available" and 
                        len(review_text) > 10 and 
                        len(review_text) < 500 and
                        not any(skip_word in review_text.lower() for skip_word in skip_words)):
                        
                        # Add review
                        reviews_list.append({
                            "rating": rating,
                            "review": review_text,
                            "date": date_text,
                            "os": "Android",
                            "reviewer_name": reviewer_name,
                            "useful_count": useful_count
                        })
                    
                except Exception as e:
                    continue
            
            # If we found reviews, return them
            if reviews_list:
                st.success(f"Successfully extracted {len(reviews_list)} Android reviews")
                return reviews_list
            else:
                st.warning("No reviews found in the HTML structure")
                return []
        else:
            st.error(f"Could not access Google Play Store (status: {response.status_code})")
            return []
    
    except Exception as e:
        st.error(f"Could not get Google Play reviews: {str(e)}")
        return []

def save_to_google_sheets(reviews, sheet_url=None, credentials_json=None):
    """
    Save reviews to Google Sheets
    """
    try:
        if not credentials_json:
            st.error("❌ Google Sheets credentials not configured. Please set up credentials first.")
            return False
        
        if not reviews:
            st.warning("⚠️ No reviews to save.")
            return False
        
        # Parse credentials
        try:
            creds = Credentials.from_service_account_info(
                credentials_json,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            gc = gspread.authorize(creds)
        except Exception as e:
            st.error(f"❌ Error authenticating with Google Sheets: {str(e)}")
            return False
        
        # Create or open spreadsheet
        if sheet_url:
            try:
                # Extract spreadsheet ID from URL
                sheet_id = sheet_url.split('/')[-2]
                sheet = gc.open_by_key(sheet_id)
                
                # Try to find existing 'VV Android reviews' worksheet
                try:
                    worksheet = sheet.worksheet('VV Android reviews')
                    st.info("📝 Using existing 'VV Android reviews' sheet")
                except gspread.WorksheetNotFound:
                    # Create new worksheet named 'VV Android reviews'
                    worksheet = sheet.add_worksheet(title='VV Android reviews', rows=1000, cols=10)
                    st.success("✅ Created new 'VV Android reviews' sheet")
                
            except Exception as e:
                st.error(f"❌ Error opening spreadsheet: {str(e)}")
                return False
        else:
            # Create new spreadsheet
            try:
                sheet = gc.create(f"Via Verde Reviews - {datetime.now().strftime('%Y-%m-%d')}")
                worksheet = sheet.sheet1
                st.success(f"✅ Created new Google Sheet: {sheet.url}")
            except Exception as e:
                st.error(f"❌ Error creating new spreadsheet: {str(e)}")
                return False
        
        # Prepare data for sheets
        headers = ['Timestamp', 'Reviewer Name', 'Rating', 'Review Text', 'Date', 'Useful Count', 'OS']
        data = [headers]
        
        for review in reviews:
            row = [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                review.get('reviewer_name', 'Unknown'),
                review.get('rating', 0),
                review.get('review', ''),
                review.get('date', ''),
                review.get('useful_count', 0),
                review.get('os', 'Android')
            ]
            data.append(row)
        
        # Clear existing data and add new data
        worksheet.clear()
        worksheet.update('A1', data)
        
        st.success(f"✅ Successfully saved {len(reviews)} reviews to Google Sheets!")
        if sheet_url:
            st.info(f"📊 Sheet URL: {sheet_url}")
            st.markdown(f"[🔗 Open your Google Sheet]({sheet_url})")
        else:
            st.info(f"📊 New Sheet URL: {sheet.url}")
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error saving to Google Sheets: {str(e)}")
        return False

def analyze_sentiment(reviews):
    """
    Analyze sentiment of reviews using TextBlob
    """
    sentiments = []
    for review in reviews:
        text = review.get('review', '')
        if text and text != "Review text not available":
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            
            # Determine emotional tone
            if polarity < -0.5:
                tone = "Very Negative/Angry"
            elif polarity < -0.1:
                tone = "Negative/Frustrated"
            elif polarity < 0.1:
                tone = "Neutral"
            elif polarity < 0.5:
                tone = "Positive/Satisfied"
            else:
                tone = "Very Positive/Happy"
            
            sentiments.append({
                'reviewer_name': review.get('reviewer_name', 'Unknown'),
                'rating': review.get('rating', 0),
                'polarity': polarity,
                'subjectivity': subjectivity,
                'tone': tone,
                'review_text': text[:100] + "..." if len(text) > 100 else text
            })
    
    return sentiments

def extract_keywords(reviews, top_n=20):
    """
    Extract common keywords and phrases from reviews
    """
    # Combine all review texts
    all_text = []
    for review in reviews:
        text = review.get('review', '')
        if text and text != "Review text not available":
            all_text.append(text)
    
    if not all_text:
        return {}
    
    # Use TF-IDF to find important keywords
    vectorizer = TfidfVectorizer(
        max_features=top_n,
        stop_words=None,  # We'll handle Portuguese manually
        ngram_range=(1, 3),  # Include 1-3 word phrases
        min_df=1  # Word must appear in at least 1 review
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(all_text)
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.sum(axis=0).A1
        
        # Create keyword dictionary
        keywords = dict(zip(feature_names, scores))
        
        # Sort by importance
        sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
        
        return dict(sorted_keywords[:top_n])
    except Exception as e:
        st.warning(f"Could not extract keywords: {str(e)}")
        return {}

def find_review_patterns(reviews):
    """
    Find common patterns and similarities between reviews
    """
    patterns = {
        'common_issues': [],
        'positive_aspects': [],
        'feature_mentions': [],
        'rating_patterns': {}
    }
    
    # Define pattern keywords
    issue_keywords = [
        'erro', 'erros', 'problema', 'problemas', 'falha', 'falhas', 'bug', 'bugs',
        'não funciona', 'não está funcionando', 'crash', 'trava', 'lento', 'demora',
        'atualização', 'versão', 'instabilidade', 'instável', 'péssimo', 'terrível'
    ]
    
    positive_keywords = [
        'bom', 'boa', 'ótimo', 'ótima', 'excelente', 'funciona bem', 'rápido',
        'fácil', 'simples', 'recomendo', 'satisfeito', 'contento', 'útil'
    ]
    
    feature_keywords = [
        'estacionar', 'estacionamento', 'portagem', 'portagens', 'carregamento',
        'carregar', 'app', 'aplicação', 'interface', 'menu', 'pagamento'
    ]
    
    # Analyze each review
    for review in reviews:
        text = review.get('review', '').lower()
        rating = review.get('rating', 0)
        
        if not text or text == "review text not available":
            continue
        
        # Find issues
        for keyword in issue_keywords:
            if keyword in text:
                patterns['common_issues'].append({
                    'keyword': keyword,
                    'reviewer': review.get('reviewer_name', 'Unknown'),
                    'rating': rating,
                    'context': text[max(0, text.find(keyword)-50):text.find(keyword)+100]
                })
        
        # Find positive aspects
        for keyword in positive_keywords:
            if keyword in text:
                patterns['positive_aspects'].append({
                    'keyword': keyword,
                    'reviewer': review.get('reviewer_name', 'Unknown'),
                    'rating': rating,
                    'context': text[max(0, text.find(keyword)-50):text.find(keyword)+100]
                })
        
        # Find feature mentions
        for keyword in feature_keywords:
            if keyword in text:
                patterns['feature_mentions'].append({
                    'keyword': keyword,
                    'reviewer': review.get('reviewer_name', 'Unknown'),
                    'rating': rating,
                    'context': text[max(0, text.find(keyword)-50):text.find(keyword)+100]
                })
    
    # Count patterns
    patterns['common_issues'] = Counter([p['keyword'] for p in patterns['common_issues']]).most_common(10)
    patterns['positive_aspects'] = Counter([p['keyword'] for p in patterns['positive_aspects']]).most_common(10)
    patterns['feature_mentions'] = Counter([p['keyword'] for p in patterns['feature_mentions']]).most_common(10)
    
    # Rating patterns
    rating_counts = Counter([r.get('rating', 0) for r in reviews])
    patterns['rating_patterns'] = dict(rating_counts.most_common())
    
    return patterns

def analyze_with_gemini(reviews, gemini_api_key):
    """
    Advanced sentiment analysis and insights using Gemini AI
    """
    if not GEMINI_AVAILABLE:
        st.warning("🤖 Gemini AI is not available. Please install google-generativeai package.")
        return None
    
    if not gemini_api_key:
        return None
    
    try:
        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Combine all review texts
        all_reviews_text = []
        for review in reviews:
            text = review.get('review', '')
            if text and text != "Review text not available":
                all_reviews_text.append(f"⭐ {review.get('rating', 0)}/5 - {text}")
        
        if not all_reviews_text:
            return None
        
        # Create comprehensive prompt for Portuguese app reviews
        reviews_sample = "\n".join(all_reviews_text[:10])  # Analyze first 10 reviews
        
        prompt = f"""
        Analisa as seguintes avaliações da aplicação Via Verde (app português para portagens e estacionamento) e fornece uma análise detalhada em português:

        AVALIAÇÕES:
        {reviews_sample}

        Por favor, fornece uma análise JSON estruturada com:
        1. "sentimento_geral": Sentimento geral (muito_negativo, negativo, neutro, positivo, muito_positivo)
        2. "pontos_positivos": Lista dos principais pontos positivos mencionados
        3. "problemas_comuns": Lista dos problemas mais frequentes
        4. "funcionalidades_mencionadas": Funcionalidades do app que são mencionadas
        5. "sugestoes_melhoria": Sugestões de melhoria baseadas nas críticas
        6. "pontuacao_sentimento": Pontuação de -10 (muito negativo) a +10 (muito positivo)
        7. "resumo_executivo": Resumo de 2-3 frases em português
        8. "palavras_chave": Top 10 palavras-chave mais importantes
        9. "tendencia_emocional": Descrição da tendência emocional dos utilizadores
        10. "recomendacao": Recomendação geral baseada na análise

        Responde APENAS com JSON válido, sem texto adicional.
        """
        
        response = model.generate_content(prompt)
        
        # Try to parse JSON response
        try:
            import json
            # Clean the response (remove markdown formatting if present)
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            analysis_result = json.loads(response_text)
            return analysis_result
        except json.JSONDecodeError:
            # Fallback: return structured text analysis
            return {
                "sentimento_geral": "neutro",
                "resumo_executivo": response.text[:200] + "...",
                "pontuacao_sentimento": 0,
                "analise_completa": response.text
            }
    
    except Exception as e:
        st.error(f"Erro na análise Gemini: {str(e)}")
        return None

def analyze_individual_reviews_with_gemini(reviews, gemini_api_key):
    """
    Analyze individual reviews with Gemini for detailed sentiment
    """
    if not GEMINI_AVAILABLE:
        st.warning("🤖 Gemini AI is not available. Please install google-generativeai package.")
        return []
    
    if not gemini_api_key or not reviews:
        return []
    
    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        analyzed_reviews = []
        
        # Process reviews in batches to avoid rate limits
        batch_size = 5
        for i in range(0, min(len(reviews), 20), batch_size):  # Limit to first 20 reviews
            batch = reviews[i:i+batch_size]
            
            for review in batch:
                text = review.get('review', '')
                if text and text != "Review text not available":
                    prompt = f"""
                    Analisa esta avaliação da aplicação Via Verde e fornece análise JSON:

                    AVALIAÇÃO: "{text}"
                    RATING: {review.get('rating', 0)}/5

                    Fornece JSON com:
                    1. "sentimento": (muito_negativo, negativo, neutro, positivo, muito_positivo)
                    2. "emocao": (raiva, frustração, neutralidade, satisfação, felicidade)
                    3. "confianca": Pontuação de 0-100 sobre confiança no app
                    4. "problema_principal": Problema específico mencionado (se houver)
                    5. "aspecto_positivo": Aspecto positivo mencionado (se houver)
                    6. "pontuacao": -10 a +10

                    Responde APENAS com JSON válido.
                    """
                    
                    try:
                        response = model.generate_content(prompt)
                        response_text = response.text.strip()
                        
                        # Clean JSON response
                        if response_text.startswith('```json'):
                            response_text = response_text[7:]
                        if response_text.endswith('```'):
                            response_text = response_text[:-3]
                        
                        analysis = json.loads(response_text)
                        
                        analyzed_reviews.append({
                            'reviewer_name': review.get('reviewer_name', 'Unknown'),
                            'rating': review.get('rating', 0),
                            'review_text': text[:100] + "..." if len(text) > 100 else text,
                            'gemini_sentiment': analysis.get('sentimento', 'neutro'),
                            'emotion': analysis.get('emocao', 'neutralidade'),
                            'confidence_score': analysis.get('confianca', 50),
                            'main_problem': analysis.get('problema_principal', ''),
                            'positive_aspect': analysis.get('aspecto_positivo', ''),
                            'gemini_score': analysis.get('pontuacao', 0)
                        })
                    except Exception as e:
                        # Fallback to basic analysis
                        analyzed_reviews.append({
                            'reviewer_name': review.get('reviewer_name', 'Unknown'),
                            'rating': review.get('rating', 0),
                            'review_text': text[:100] + "..." if len(text) > 100 else text,
                            'gemini_sentiment': 'neutro',
                            'emotion': 'neutralidade',
                            'confidence_score': 50,
                            'main_problem': '',
                            'positive_aspect': '',
                            'gemini_score': 0
                        })
        
        return analyzed_reviews
    
    except Exception as e:
        st.error(f"Erro na análise individual Gemini: {str(e)}")
        return []

def group_reviews_by_rating(reviews):
    """
    Group reviews by their rating (1-5 stars)
    """
    grouped = {}
    for review in reviews:
        rating = review["rating"]
        if rating not in grouped:
            grouped[rating] = []
        grouped[rating].append(review)
    
    # Sort ratings from 5 to 1 (best to worst)
    return dict(sorted(grouped.items(), reverse=True))

def create_streamlit_app():
    """
    Create the main Streamlit app to display reviews
    """
    st.set_page_config(page_title="Via Verde Reviews", page_icon="📱")
    
    st.title("🤖 Via Verde Android Reviews")
    st.write("All visible reviews from Google Play Store (Apple Store on hold)")
    
    # Add info about the focus
    st.info("ℹ️ **Focus**: Currently showing Android reviews only. Apple Store reviews are on hold. Showing all visible reviews from the Portuguese page.")
    
    # Get reviews from Android only (Apple Store on hold)
    with st.spinner("Getting Android reviews..."):
        android_reviews = get_google_play_reviews()
        all_reviews = android_reviews  # Only Android reviews for now
    
    # Add refresh and save buttons
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col2:
        if st.button("🔄 Refresh Reviews", type="primary"):
            st.rerun()
    
    with col3:
        if st.button("💾 Save to Google Sheets"):
            st.session_state.show_sheets_config = True
    
    # Google Sheets Configuration
    if st.session_state.get('show_sheets_config', False):
        st.markdown("---")
        st.subheader("📊 Google Sheets Configuration")
        
        # Try to get credentials from secrets, fallback to manual input
        try:
            credentials_json = st.secrets["google_sheets"]["service_account_json"]
            sheet_url = st.secrets["google_sheets"]["sheet_url"]
            
            if credentials_json and credentials_json != '{"type": "service_account", ...}' and sheet_url:
                st.success("✅ Google Sheets credentials loaded from configuration")
                st.info(f"📊 Target Sheet: {sheet_url}")
                
                # Show credentials status
                if 'client_email' in credentials_json:
                    import json
                    try:
                        creds_data = json.loads(credentials_json)
                        st.write(f"🔑 Service Account: {creds_data.get('client_email', 'Unknown')}")
                    except:
                        st.write("🔑 Service Account: Configured")
            else:
                raise KeyError("Invalid credentials in secrets")
                
        except (KeyError, json.JSONDecodeError):
            st.info("ℹ️ No Google Sheets credentials found in configuration. You can:")
            st.write("1. 🔧 Configure them in `.streamlit/secrets.toml` (recommended)")
            st.write("2. 📝 Enter them manually below")
            
            # Credentials input
            st.write("**Step 1: Google Service Account Credentials**")
            st.info("💡 **How to get credentials:**\n1. Go to [Google Cloud Console](https://console.cloud.google.com/)\n2. Create a new project or select existing\n3. Enable Google Sheets API\n4. Create Service Account credentials\n5. Download JSON key file\n6. Copy the JSON content below")
            
            credentials_json = st.text_area(
                "Paste your Google Service Account JSON credentials here:",
                height=100,
                help="Paste the entire JSON content from your service account key file"
            )
            
            # Sheet URL input
            st.write("**Step 2: Google Sheet URL**")
            sheet_url = st.text_input(
                "Google Sheet URL:",
                value="https://docs.google.com/spreadsheets/d/1ZBU9dDbMhYK2qWeWvVSK1D0o_muRjtN2rXFPlpVO_UU/edit?gid=0#gid=0",
                help="Your Google Sheet URL. The app will create a new tab named 'VV Android reviews' in this sheet."
            )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("💾 Save Reviews to Sheets", type="primary"):
                if credentials_json.strip():
                    try:
                        # Parse JSON to validate
                        creds = json.loads(credentials_json)
                        
                        # Save to sheets
                        if save_to_google_sheets(all_reviews, sheet_url, creds):
                            st.session_state.show_sheets_config = False
                            st.rerun()
                    except json.JSONDecodeError:
                        st.error("❌ Invalid JSON format. Please check your credentials.")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.error("❌ Please provide Google Service Account credentials.")
        
        if st.button("❌ Cancel"):
            st.session_state.show_sheets_config = False
            st.rerun()
    
    
    # Group reviews by rating
    grouped_reviews = group_reviews_by_rating(all_reviews)
    
    # Show summary
    st.subheader("📊 Android Review Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Reviews", len(all_reviews))
    
    with col2:
        st.metric("Android Reviews", len(android_reviews))
    
    with col3:
        avg_rating = sum(review["rating"] for review in all_reviews) / len(all_reviews) if all_reviews else 0
        st.metric("Average Rating", f"{avg_rating:.1f} ⭐")
    
    # Additional metrics row
    col4, col5, col6 = st.columns(3)
    
    with col4:
        total_useful = sum(review["useful_count"] for review in all_reviews)
        st.metric("Total Useful Votes", total_useful)
    
    with col5:
        named_reviews = len([r for r in all_reviews if r["reviewer_name"] != "Unknown"])
        st.metric("Named Reviewers", named_reviews)
    
    with col6:
        avg_useful = total_useful / len(all_reviews) if all_reviews else 0
        st.metric("Avg Useful per Review", f"{avg_useful:.1f}")
    
    st.markdown("---")
    
    # Display reviews by rating (Android only)
    st.subheader("⭐ Android Reviews by Rating")
    
    if all_reviews and grouped_reviews:
        for rating in sorted(grouped_reviews.keys(), reverse=True):
            reviews_for_rating = grouped_reviews[rating]
            stars = "⭐" * rating
            
            st.write(f"### {stars} ({len(reviews_for_rating)} reviews)")
            
            # Show Android reviews with enhanced information
            for review in reviews_for_rating:
                # Create a more detailed display
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Main review content
                    reviewer_name = review['reviewer_name']
                    if reviewer_name == "Unknown":
                        reviewer_info = "**Anonymous**"
                    else:
                        reviewer_info = f"**{reviewer_name}**"
                    
                    date_info = f"({review['date']})"
                    
                    st.write(f"👤 {reviewer_info} {date_info}")
                    st.write(f"📝 {review['review']}")
                
                with col2:
                    # Useful count and rating
                    if review['useful_count'] > 0:
                        st.write(f"👍 {review['useful_count']} pessoas consideraram útil")
                    else:
                        st.write("👍 N/A")
                    
                    # Show rating with stars
                    stars = "⭐" * review['rating']
                    st.write(f"⭐ {stars} ({review['rating']}/5)")
                
                st.markdown("---")
            
            st.write("")  # Add some space between rating groups
    else:
        st.info("ℹ️ **No reviews found.** This could be due to:")
        st.write("• Google Play Store blocking automated requests")
        st.write("• Changes in the page structure")
        st.write("• Network connectivity issues")
        st.write("• Rate limiting from Google")
        st.write("")
        st.write("**Try clicking the refresh button or check back later.**")
    
    # Analysis Section
    if all_reviews and len(all_reviews) > 0:
        st.markdown("---")
        st.header("🔍 Review Analysis")
        
        # Gemini API Configuration
        st.subheader("🤖 Gemini AI Configuration")
        
        # Check if Gemini is available
        if not GEMINI_AVAILABLE:
            st.error("❌ Gemini AI is not available. Please install the package:")
            st.code("pip install google-generativeai")
            gemini_api_key = None
            use_gemini = False
        else:
            # Try to get Gemini API key from secrets, fallback to manual input
            try:
                gemini_api_key = st.secrets["gemini"]["api_key"]
                if gemini_api_key and gemini_api_key != "your_gemini_api_key_here":
                    st.success("✅ Gemini API key loaded from configuration")
                    use_gemini = st.checkbox("Enable Gemini AI Analysis", value=True)
                else:
                    st.warning("⚠️ Please configure your Gemini API key in secrets.toml")
                    gemini_api_key = st.text_input(
                        "Gemini API Key:",
                        type="password",
                        help="Enter your Google Gemini API key for advanced AI analysis. Get one at: https://makersuite.google.com/app/apikey"
                    )
                    use_gemini = st.checkbox("Enable Gemini AI Analysis", value=bool(gemini_api_key))
            except KeyError:
                st.info("ℹ️ No Gemini API key found in configuration. You can:")
                st.write("1. 🔧 Configure it in `.streamlit/secrets.toml` (recommended)")
                st.write("2. 🔑 Enter it manually below")
                gemini_api_key = st.text_input(
                    "Gemini API Key:",
                    type="password",
                    help="Enter your Google Gemini API key for advanced AI analysis. Get one at: https://makersuite.google.com/app/apikey"
                )
                use_gemini = st.checkbox("Enable Gemini AI Analysis", value=bool(gemini_api_key))
        
        # Analysis tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["😊 Sentiment Analysis", "🔑 Keywords", "📊 Patterns", "🤖 Gemini AI", "📈 Summary"])
        
        with tab1:
            st.subheader("😊 Sentiment Analysis")
            with st.spinner("Analyzing sentiment..."):
                sentiments = analyze_sentiment(all_reviews)
                
                if sentiments:
                    # Sentiment distribution
                    tone_counts = Counter([s['tone'] for s in sentiments])
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Emotional Tone Distribution:**")
                        for tone, count in tone_counts.most_common():
                            percentage = (count / len(sentiments)) * 100
                            st.write(f"• {tone}: {count} reviews ({percentage:.1f}%)")
                    
                    with col2:
                        st.write("**Sentiment Scores:**")
                        avg_polarity = np.mean([s['polarity'] for s in sentiments])
                        avg_subjectivity = np.mean([s['subjectivity'] for s in sentiments])
                        
                        st.metric("Average Polarity", f"{avg_polarity:.3f}", help="Range: -1 (very negative) to +1 (very positive)")
                        st.metric("Average Subjectivity", f"{avg_subjectivity:.3f}", help="Range: 0 (objective) to 1 (subjective)")
                    
                    # Show sentiment details
                    st.write("**Individual Review Sentiments:**")
                    for sentiment in sentiments[:10]:  # Show first 10
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.write(f"**{sentiment['reviewer_name']}** (⭐{sentiment['rating']})")
                            st.write(sentiment['review_text'])
                        with col2:
                            st.write(f"**Tone:** {sentiment['tone']}")
                        with col3:
                            st.write(f"**Score:** {sentiment['polarity']:.2f}")
                        st.divider()
        
        with tab2:
            st.subheader("🔑 Top Keywords & Phrases")
            with st.spinner("Extracting keywords..."):
                keywords = extract_keywords(all_reviews, top_n=15)
                
                if keywords:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Most Important Keywords:**")
                        for i, (keyword, score) in enumerate(list(keywords.items())[:8], 1):
                            st.write(f"{i}. **{keyword}** (score: {score:.3f})")
                    
                    with col2:
                        st.write("**Keywords 9-15:**")
                        for i, (keyword, score) in enumerate(list(keywords.items())[8:], 9):
                            st.write(f"{i}. **{keyword}** (score: {score:.3f})")
                else:
                    st.warning("No keywords could be extracted from the reviews.")
        
        with tab3:
            st.subheader("📊 Review Patterns")
            with st.spinner("Finding patterns..."):
                patterns = find_review_patterns(all_reviews)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**🚨 Common Issues:**")
                    if patterns['common_issues']:
                        for issue, count in patterns['common_issues']:
                            st.write(f"• **{issue}** (mentioned {count} times)")
                    else:
                        st.write("No common issues identified")
                    
                    st.write("**✨ Positive Aspects:**")
                    if patterns['positive_aspects']:
                        for positive, count in patterns['positive_aspects']:
                            st.write(f"• **{positive}** (mentioned {count} times)")
                    else:
                        st.write("No positive aspects identified")
                
                with col2:
                    st.write("**🔧 Feature Mentions:**")
                    if patterns['feature_mentions']:
                        for feature, count in patterns['feature_mentions']:
                            st.write(f"• **{feature}** (mentioned {count} times)")
                    else:
                        st.write("No feature mentions identified")
                    
                    st.write("**⭐ Rating Distribution:**")
                    for rating, count in patterns['rating_patterns'].items():
                        percentage = (count / len(all_reviews)) * 100
                        st.write(f"• {rating} stars: {count} reviews ({percentage:.1f}%)")
        
        with tab4:
            st.subheader("🤖 Gemini AI Analysis")
            
            if use_gemini and gemini_api_key:
                with st.spinner("🤖 Gemini is analyzing your reviews..."):
                    # Overall analysis
                    gemini_analysis = analyze_with_gemini(all_reviews, gemini_api_key)
                    
                    if gemini_analysis:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**🎯 Sentimento Geral:**")
                            sentiment = gemini_analysis.get('sentimento_geral', 'neutro')
                            score = gemini_analysis.get('pontuacao_sentimento', 0)
                            
                            if sentiment in ['muito_positivo', 'positivo']:
                                st.success(f"😊 {sentiment.title()} ({score}/10)")
                            elif sentiment in ['muito_negativo', 'negativo']:
                                st.error(f"😞 {sentiment.title()} ({score}/10)")
                            else:
                                st.info(f"😐 {sentiment.title()} ({score}/10)")
                            
                            st.write("**📝 Resumo Executivo:**")
                            st.write(gemini_analysis.get('resumo_executivo', 'N/A'))
                            
                            st.write("**🎭 Tendência Emocional:**")
                            st.write(gemini_analysis.get('tendencia_emocional', 'N/A'))
                        
                        with col2:
                            st.write("**✅ Pontos Positivos:**")
                            pontos_positivos = gemini_analysis.get('pontos_positivos', [])
                            if pontos_positivos:
                                for ponto in pontos_positivos[:5]:  # Show top 5
                                    st.write(f"• {ponto}")
                            else:
                                st.write("Nenhum ponto positivo identificado")
                            
                            st.write("**❌ Problemas Comuns:**")
                            problemas = gemini_analysis.get('problemas_comuns', [])
                            if problemas:
                                for problema in problemas[:5]:  # Show top 5
                                    st.write(f"• {problema}")
                            else:
                                st.write("Nenhum problema comum identificado")
                        
                        st.write("**🔧 Funcionalidades Mencionadas:**")
                        funcionalidades = gemini_analysis.get('funcionalidades_mencionadas', [])
                        if funcionalidades:
                            cols = st.columns(min(len(funcionalidades), 3))
                            for i, func in enumerate(funcionalidades):
                                with cols[i % 3]:
                                    st.write(f"• {func}")
                        else:
                            st.write("Nenhuma funcionalidade específica mencionada")
                        
                        st.write("**💡 Sugestões de Melhoria:**")
                        sugestoes = gemini_analysis.get('sugestoes_melhoria', [])
                        if sugestoes:
                            for sugestao in sugestoes[:3]:  # Show top 3
                                st.info(f"💡 {sugestao}")
                        else:
                            st.write("Nenhuma sugestão específica identificada")
                        
                        st.write("**🔑 Palavras-Chave Mais Importantes:**")
                        palavras_chave = gemini_analysis.get('palavras_chave', [])
                        if palavras_chave:
                            st.write(", ".join(palavras_chave[:10]))
                        else:
                            st.write("Nenhuma palavra-chave identificada")
                        
                        st.write("**📋 Recomendação Geral:**")
                        recomendacao = gemini_analysis.get('recomendacao', 'N/A')
                        st.success(f"🎯 {recomendacao}")
                        
                        # Individual reviews analysis
                        st.write("---")
                        st.write("**🔍 Análise Individual de Avaliações:**")
                        
                        individual_analysis = analyze_individual_reviews_with_gemini(all_reviews, gemini_api_key)
                        
                        if individual_analysis:
                            for analysis in individual_analysis[:10]:  # Show first 10
                                col1, col2, col3 = st.columns([3, 1, 1])
                                
                                with col1:
                                    st.write(f"**{analysis['reviewer_name']}** (⭐{analysis['rating']}/5)")
                                    st.write(analysis['review_text'])
                                    
                                    if analysis['main_problem']:
                                        st.write(f"🚨 **Problema:** {analysis['main_problem']}")
                                    if analysis['positive_aspect']:
                                        st.write(f"✅ **Positivo:** {analysis['positive_aspect']}")
                                
                                with col2:
                                    sentiment = analysis['gemini_sentiment']
                                    if sentiment in ['muito_positivo', 'positivo']:
                                        st.success(f"😊 {sentiment}")
                                    elif sentiment in ['muito_negativo', 'negativo']:
                                        st.error(f"😞 {sentiment}")
                                    else:
                                        st.info(f"😐 {sentiment}")
                                    
                                    st.write(f"**Emoção:** {analysis['emotion']}")
                                
                                with col3:
                                    st.write(f"**Score:** {analysis['gemini_score']}/10")
                                    st.write(f"**Confiança:** {analysis['confidence_score']}%")
                                
                                st.divider()
                    else:
                        st.error("❌ Não foi possível obter análise do Gemini. Verifique sua API key.")
            else:
                st.info("🤖 **Gemini AI Analysis** está disponível!")
                st.write("Para usar a análise avançada com IA:")
                st.write("1. 🔑 Obtenha uma API key gratuita em: https://makersuite.google.com/app/apikey")
                st.write("2. ✅ Insira a API key acima")
                st.write("3. ✅ Marque 'Enable Gemini AI Analysis'")
                st.write("4. 🔄 Recarregue a página")
                st.write("")
                st.write("**Benefícios da análise Gemini:**")
                st.write("• 🧠 Compreensão avançada de contexto em português")
                st.write("• 🎯 Identificação precisa de problemas e pontos positivos")
                st.write("• 💡 Sugestões de melhoria baseadas em IA")
                st.write("• 📊 Análise emocional detalhada")
                st.write("• 🔍 Insights sobre confiança dos utilizadores")
        
        with tab5:
            st.subheader("📈 Analysis Summary")
            
            # Overall statistics
            total_reviews = len(all_reviews)
            avg_rating = np.mean([r.get('rating', 0) for r in all_reviews])
            total_useful = sum([r.get('useful_count', 0) for r in all_reviews])
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Reviews", total_reviews)
            with col2:
                st.metric("Average Rating", f"{avg_rating:.1f} ⭐")
            with col3:
                st.metric("Total Useful Votes", total_useful)
            with col4:
                st.metric("Avg Useful per Review", f"{total_useful/total_reviews:.1f}")
            
            # Quick insights
            st.write("**🔍 Quick Insights:**")
            
            # Most common rating
            most_common_rating = max(patterns['rating_patterns'].items(), key=lambda x: x[1])
            st.write(f"• Most common rating: **{most_common_rating[0]} stars** ({most_common_rating[1]} reviews)")
            
            # Sentiment insight
            if sentiments:
                most_common_tone = Counter([s['tone'] for s in sentiments]).most_common(1)[0]
                st.write(f"• Most common sentiment: **{most_common_tone[0]}** ({most_common_tone[1]} reviews)")
            
            # Top keyword
            if keywords:
                top_keyword = list(keywords.items())[0]
                st.write(f"• Most important keyword: **{top_keyword[0]}**")
            
            # Issues vs positives
            total_issues = sum([count for _, count in patterns['common_issues']])
            total_positives = sum([count for _, count in patterns['positive_aspects']])
            
            if total_issues > 0 or total_positives > 0:
                st.write(f"• Issues mentioned: {total_issues} times")
                st.write(f"• Positive aspects mentioned: {total_positives} times")
                
                if total_issues > total_positives:
                    st.warning("⚠️ More issues than positive aspects mentioned")
                elif total_positives > total_issues:
                    st.success("✅ More positive aspects than issues mentioned")
                else:
                    st.info("ℹ️ Balanced mention of issues and positive aspects")

if __name__ == "__main__":
    create_streamlit_app()
