import os
import re
import json
import pandas as pd
import numpy as np
import torch
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import nltk
from nltk.tokenize import sent_tokenize
import logging
from tqdm import tqdm
import sys
from concurrent.futures import ThreadPoolExecutor
import threading
import nltk
import os
import re
import nltk
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s', 
    handlers=[
        logging.FileHandler("sentiment_analysis.log", encoding="utf-8", mode='w')
    ]
)

# Add a separate handler for console with appropriate encoding handling
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(console_handler)

# --- BLOC DE CONFIGURARE ȘI DESCĂRCARE NLTK (VERSIUNE CORECTATĂ) ---

def download_nltk_resource(resource_name, resource_path_to_find, downloader_arg):
    """Funcție ajutătoare pentru a verifica și descărca o resursă NLTK."""
    try:
        logging.info(f"Verificare resursă NLTK '{resource_name}' la '{resource_path_to_find}'...")
        nltk.data.find(resource_path_to_find)
        logging.info(f"Resursa NLTK '{resource_name}' este deja disponibilă.")
        return True
    except LookupError:
        logging.warning(f"Resursa NLTK '{resource_name}' nu a fost găsită. Se încearcă descărcarea '{downloader_arg}'...")
        try:
            nltk.download(downloader_arg, quiet=True) # quiet=True pentru a evita GUI dacă e posibil
            logging.info(f"Descărcarea pentru '{downloader_arg}' a fost inițiată. Se reverifică...")
            # Este important să reverificăm, deoarece nltk.download() nu ridică mereu erori clare la eșec
            nltk.data.find(resource_path_to_find)
            logging.info(f"Resursa NLTK '{resource_name}' este acum disponibilă după descărcare.")
            return True
        except Exception as e_download:
            # Aceasta poate fi LookupError dacă descărcarea nu a reușit să facă resursa găsibilă,
            # sau altă eroare (ex: de rețea, deși nltk.download le maschează adesea)
            logging.error(f"Descărcarea sau reverificarea pentru '{downloader_arg}' a eșuat: {e_download}")
            return False
    except Exception as e_find_initial:
        logging.error(f"Eroare neașteptată la căutarea inițială a resursei '{resource_name}': {e_find_initial}")
        return False

# Încercăm să descărcăm 'punkt_tab' mai întâi, deoarece eroarea îl cere specific
logging.info("--- Început configurare resurse NLTK ---")
punkt_tab_ok = download_nltk_resource(
    resource_name="punkt_tab",
    resource_path_to_find='tokenizers/punkt_tab',
    downloader_arg='punkt_tab'
)

if not punkt_tab_ok:
    logging.warning("Nu s-a putut obține 'punkt_tab'. Se încearcă cu resursa 'punkt' standard.")
    punkt_ok = download_nltk_resource(
        resource_name="punkt",
        resource_path_to_find='tokenizers/punkt',
        downloader_arg='punkt'
    )
    if not punkt_ok:
        logging.error("NICI 'punkt_tab', NICI 'punkt' nu au putut fi obținute. Tokenizarea propozițiilor probabil va eșua.")
else:
    # Dacă punkt_tab_ok este True, nu mai este necesar să încercăm și punkt separat,
    # presupunând că 'punkt_tab' este ceea ce caută în mod specific.
    pass

logging.info("--- Sfârșit configurare resurse NLTK ---")

# Adăugăm calea pentru a importa DatabaseCRUD
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.DatabaseCRUD import DatabaseCRUD

class HTML10KProcessor:
    """
    Clasă pentru procesarea rapoartelor 10-K în format HTML
    """
    def __init__(self):
        # Secțiunile importante din rapoartele 10-K
        self.sections_patterns = {
            "MD&A": [
                # Pattern 1 (optimizat GPC)
                r"ITEM\s+7\.\s+MANAGEMENT’S\s+DISCUSSION\s+AND\s+ANALYSIS\s+OF\s+FINANCIAL\s+CONDITION\s+AND\s+RESULTS\s+OF\s+OPERATIONS\.(.*?)(?=ITEM\s*7A\.QUANTITATIVE\s+AND\s+QUALITATIVE\s+DISCLOSURES\s+ABOUT\s+MARKET\s+RISK\.)",
                # Pattern 2 (optimizat ADM)
                r"Item\s*7\.\s*MANAGEMENT’S\s+DISCUSSION\s+AND\s+ANALYSIS\s+OF\s+FINANCIAL\s+CONDITION\s+AND\s+RESULTS\s+OF\s+OPERATIONS\s*(.*?)(?=Item\s*7A\.\s*QUANTITATIVE\s+AND\s+QUALITATIVE\s+DISCLOSURES\s+ABOUT\s+MARKET\s+RISK)",
                # Pattern 3 (NOU, specific TGT)
                r"Item\s+7\.\s+Management's\s+Discussion\s+and\s+Analysis\s+of\s+Financial\s+Condition\s+and\s+Results\s+of\s+Operations\s*(.*?)(?=Item\s+7A\.\s+Quantitative\s+and\s+Qualitative\s+Disclosures\s+About\s+Market\s+Risk)"
            ],
            "Risk_Factors": [
                # Pattern 1 (optimizat GPC)
                r"ITEM\s+1A\.\s+RISK\s+FACTORS\.(.*?)(?=ITEM\s+1B\.\s+UNRESOLVED\s+STAFF\s+COMMENTS\.|ITEM\s+1C\.\s+CYBERSECURITY\.)",
                # Pattern 2 (optimizat ADM, pare să funcționeze și pentru TGT)
                r"Item\s+1A\.\s*RISK\s+FACTORS\s*(.*?)(?=Item\s+1B\.\s*UNRESOLVED\s+STAFF\s+COMMENTS|Item\s+1C\.\s*CYBERSECURITY)"
            ],
            "Business": [
                # Pattern 1 (optimizat GPC)
                r"ITEM\s+1\.\s+BUSINESS\.(.*?)(?=ITEM\s+1A\.\s+RISK\s+FACTORS\.)",
                # Pattern 2 (optimizat ADM, pare să funcționeze și pentru TGT)
                r"Item\s+1\.\s*BUSINESS\s*(.*?)(?=Item\s+1A\.\s*RISK\s+FACTORS)"
            ],
            # "Financial_Discussion": [ ... ] # Probabil redundantă, poate fi comentată/ștearsă
        }
    def extract_text_from_html(self, file_path):
        """Extrage textul din fișierul HTML"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            
            # Parsăm HTML-ul
            soup = BeautifulSoup(content, 'html.parser')
            
            # Eliminăm script și style tags
            for script in soup(["script", "style"]):
                script.extract()
            
            # Obținem textul
            text = soup.get_text()
            
            # Curățăm textul
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
                
        except Exception as e:
            logging.error(f"Eroare la citirea fișierului HTML {file_path}: {e}")
            return ""
        

    def extract_sections(self, text):
        """Extrage secțiunile importante din textul raportului 10-K"""
        sections = {}
        logging.debug(f"Lungimea totală a textului brut (înainte de extragerea secțiunilor): {len(text)}")


        for section_name, patterns in self.sections_patterns.items():
            section_text = ""
            logging.debug(f"Încerc extragerea secțiunii: {section_name}")

            # Încearcă fiecare model regex pentru a găsi secțiunea
            for i, pattern in enumerate(patterns):
                try:
                    matches = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
                    if matches:
                        section_text = matches.group(1).strip()
                        logging.debug(f"  Patternul {i+1} pentru '{section_name}' a găsit potrivire. Lungime text extras (brut): {len(section_text)}")
                        break 
                except Exception as e:
                    logging.error(f"  Eroare la căutarea cu patternul {i+1} pentru '{section_name}': {e}")

            if section_text:
                # Curățare text suplimentară (codul tău existent)
                original_len = len(section_text)
                section_text = re.sub(r'\s+', ' ', section_text)
                section_text = re.sub(r'\.{2,}', '.', section_text)
                section_text = re.sub(r'\([Pp]age\s*\d+\)', '', section_text)
                section_text = re.sub(r'\d+\s*of\s*\d+', '', section_text)
                logging.debug(f"  Secțiunea '{section_name}': Lungime după curățare: {len(section_text)} (original: {original_len})")

                if len(section_text.strip()) < 10: # Adaugă o verificare aici
                    logging.warning(f"  Secțiunea '{section_name}' extrasă are text foarte scurt după curățare (lungime: {len(section_text.strip())}). Text: '{section_text[:100]}...'")

                sections[section_name] = section_text
            else:
                logging.warning(f"Nu s-a putut extrage secțiunea: {section_name} folosind niciun pattern.")

        return sections
    
    def process_file(self, file_path):
        """Procesează un fișier 10-K și extrage secțiunile importante"""
        logging.info(f"Procesare fișier: {file_path}")
        text = self.extract_text_from_html(file_path)
        if not text:
            logging.error(f"Extragerea textului din {file_path} a eșuat sau a returnat text gol.")
            return {"Full_Text": ""} # Returnează text gol pentru a evita erori ulterioare, dar va da scor neutru

        sections = self.extract_sections(text)

        if not sections:
            logging.warning(f"Nu s-au găsit secțiuni specifice în {file_path}. Se folosește Full_Text. Lungime Full_Text: {len(text)}")
            sections["Full_Text"] = text # Full_Text ar trebui să fie textul curățat deja la nivel de bază

        return sections

class RoBERTaFinanceAnalyzer:
    """
    Clasă pentru analiza de sentiment a textelor financiare folosind RoBERTa Finance
    """
    def __init__(self, model_name="yiyanghkust/finbert-tone", device=None):
        """
        Inițializează analizorul cu modelul specificat.
        
        Pentru modele financiare se pot folosi:
        - "yiyanghkust/finbert-tone" pentru analiza tonului (pozitiv/negativ/neutru)
        - "ProsusAI/finbert" pentru sentiment financiar
        """

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        
        # Verifică dacă modelul are suport CUDA și folosește GPU dacă este disponibil
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = device
        
        self.model.to(self.device)
        
        # Etichetele pentru model
        if model_name == "yiyanghkust/finbert-tone":
            self.labels = ["Negative", "Neutral", "Positive"]
        else:
            self.labels = ["Negative", "Neutral", "Positive"]  # Default pentru alte modele
        
        # Inițializăm un lock pentru a gestiona accesul la model în cazul procesării paralele
        self.model_lock = threading.Lock()

    def analyze_text(self, text, chunk_size=512, overlap=50):
        """
        Analizează textul și returnează scoreurile de sentiment
        
        Args:
            text: Textul de analizat
            chunk_size: Dimensiunea maximă a unui chunk pentru a se încadra în limitele modelului
            overlap: Suprapunerea între chunk-uri pentru a menține contextul
        """
        stripped_text_len = len(text.strip()) if text else 0
        logging.debug(f"analyze_text primit. Lungime text (după strip): {stripped_text_len}. Primii 50 caractere: '{text.strip()[:50]}'")

        if not text or len(text.strip()) < 10:
            logging.warning(f"Textul este prea scurt (lungime: {stripped_text_len}) pentru analiză RoBERTa. Se returnează scorul neutru implicit.")
            return {"Negative": 0.33, "Neutral": 0.34, "Positive": 0.33}  # Scor neutru implicit
        
        # Împarte textul în propoziții
        sentences = sent_tokenize(text)
        
        # Preprocesarea și împărțirea textului în chunk-uri care se încadrează în limitele modelului
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # Dacă adăugarea propoziției ar depăși chunk_size, adaugă chunk-ul curent și începe unul nou
            if len(current_chunk) + len(sentence) > chunk_size - overlap:
                chunks.append(current_chunk.strip())
                # Păstrează ultima parte a chunk-ului curent pentru suprapunere
                words = current_chunk.split()
                if len(words) > overlap:
                    current_chunk = " ".join(words[-overlap:]) + " " + sentence
                else:
                    current_chunk = sentence
            else:
                current_chunk += " " + sentence
        
        # Adaugă ultimul chunk dacă nu este gol
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        logging.debug(f"Textul a fost împărțit în {len(sentences)} propoziții și {len(chunks)} chunk-uri.")

        # Dacă nu există chunk-uri (text foarte scurt), adaugă textul ca un singur chunk
        if not chunks: # Adăugat pentru a prinde cazul când nu se formează chunks din text valid
            logging.warning(f"Nu s-au format chunk-uri din text (lungime: {stripped_text_len}). Se returnează scorul neutru implicit.")
            return {"Negative": 0.33, "Neutral": 0.34, "Positive": 0.33}
        
        # Vectorii pentru a stoca rezultatele
        all_scores = []
        
        # Procesează fiecare chunk
        with self.model_lock:  # Folosim lock pentru a evita accesul simultan la model
            with torch.no_grad():
                for chunk in chunks:
                    # Tokenizează și obține predicția
                    inputs = self.tokenizer(chunk, return_tensors="pt", truncation=True, max_length=512).to(self.device)
                    outputs = self.model(**inputs)
                    
                    # Obține scorurile pentru fiecare clasă
                    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
                    scores = probs[0].cpu().numpy()
                    
                    # Adaugă la rezultate
                    all_scores.append(scores)
        
        # Calculează media scorurilor
        if not all_scores: # Dacă, din diverse motive, nu s-a adăugat niciun scor
            logging.warning("Lista all_scores este goală după procesarea chunk-urilor. Se returnează distribuție uniformă.")
            return {label: 1/len(self.labels) for label in self.labels}

        avg_scores = np.mean(all_scores, axis=0)
        result = {label: float(score) for label, score in zip(self.labels, avg_scores)}
        logging.debug(f"Scoruri medii calculate: {result}")
        return result
    
class SentimentAnalysisManager:
    """
    Clasă pentru gestionarea analizei de sentiment pentru mai multe companii
    """
    def __init__(self, filings_dir="./sec_edgar_fillings", output_dir="./sentiment_results"):
        self.filings_dir = filings_dir
        self.output_dir = output_dir
        
        # Creează directorul de output dacă nu există
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Inițializează procesorul de documente
        self.processor = HTML10KProcessor()
        
        # Creează un model RoBERTa Finance pentru fiecare worker
        # Pentru a evita problemele de memorie și pentru a permite paralelizarea
        self.analyzer = RoBERTaFinanceAnalyzer()
        
        # Conectare la baza de date
        try:
            self.db_crud = DatabaseCRUD()
        except Exception as e:
            logging.error(f"Eroare la conectarea la baza de date: {e}")
            self.db_crud = None

    def find_filing_files(self, ticker, filing_type="10-K"):
        """
        Finds filing files for a specific ticker and report type
        
        Args:
            ticker: Company ticker symbol
            filing_type: Filing type (default "10-K")
            
        Returns:
            List of paths to filing files
        """
        filing_files = []

        # IMPORTANT FIX: Use the correct directory name with a hyphen instead of double 'l'
        base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sec-edgar-filings")
        
        # Debug the actual project directory structure
        project_dir = os.path.dirname(os.path.dirname(__file__))
        logging.info(f"Project directory: {project_dir}")
        if os.path.exists(project_dir):
            logging.info(f"Project directory contents: {os.listdir(project_dir)}")
        
        # The actual paths to the company filing directories
        company_path = os.path.join(base_path, ticker)
        filing_path = os.path.join(company_path, filing_type)
        
        logging.info(f"Looking for files in: {filing_path}")
        
        # Check if the base path exists
        if not os.path.exists(base_path):
            logging.error(f"SEC Edgar filings base directory does not exist at: {base_path}")
            return filing_files
        
        # Check if the company directory exists
        if not os.path.exists(company_path):
            logging.warning(f"Company directory not found for {ticker} at {company_path}")
            # List all available companies for debugging
            logging.info(f"Available companies: {os.listdir(base_path)}")
            return filing_files
        
        # Check if the filing type directory exists
        if not os.path.exists(filing_path):
            logging.warning(f"Filing type directory not found for {ticker}/{filing_type}")
            # List all available filing types for this company
            logging.info(f"Available filing types for {ticker}: {os.listdir(company_path)}")
            return filing_files
        
        # Look for submission folders - in your structure, these are folders like '0000070084-25-000011'
        try:
            submission_folders = [f for f in os.listdir(filing_path) if os.path.isdir(os.path.join(filing_path, f))]
            logging.info(f"Found {len(submission_folders)} submission folders for {ticker}")
            
            for folder in submission_folders:
                submission_path = os.path.join(filing_path, folder)
                
                # Look for the primary-document.html file
                html_file = os.path.join(submission_path, "primary-document.html")
                
                if os.path.exists(html_file):
                    filing_files.append(html_file)
                    logging.info(f"Found primary HTML file: {html_file}")
                else:
                    # Try the full-submission.txt file as a fallback
                    txt_file = os.path.join(submission_path, "full-submission.txt")
                    if os.path.exists(txt_file):
                        filing_files.append(txt_file)
                        logging.info(f"Found text file: {txt_file}")
                    else:
                        logging.warning(f"No report files found in {submission_path}")
            
        except Exception as e:
            logging.error(f"Error accessing directory {filing_path}: {str(e)}")
        
        if not filing_files:
            logging.warning(f"No reports found for {ticker}")
        
        return filing_files
    
    def analyze_filing(self, file_path, ticker):
        """
        Analizează un singur raport și returnează scorurile de sentiment
        
        Args:
            file_path: Calea către fișierul raportului
            ticker: Ticker-ul companiei
            
        Returns:
            Dict cu rezultatele analizei
        """
        try:
            # Procesăm fișierul pentru a extrage secțiunile
            sections = self.processor.process_file(file_path)
            
            # Analizăm fiecare secțiune
            results = {"ticker": ticker}
            section_weights = {
                "MD&A": 0.4,
                "Risk_Factors": 0.3,
                "Business": 0.15,
                "Financial_Discussion": 0.15,
                "Full_Text": 1.0  # Dacă folosim textul complet
            }
            
            weighted_positive = 0
            weighted_negative = 0
            weighted_neutral = 0
            total_weight = 0
            
            # Analizează fiecare secțiune
            for section_name, section_text in sections.items():
                sentiment = self.analyzer.analyze_text(section_text)
                
                # Adaugă la rezultate
                for label, score in sentiment.items():
                    results[f"{section_name}_{label}"] = score
                
                # Calculează scorurile ponderate
                weight = section_weights.get(section_name, 0)
                if section_name != "Full_Text" or len(sections) == 1:
                    weighted_positive += sentiment.get("Positive", 0) * weight
                    weighted_negative += sentiment.get("Negative", 0) * weight
                    weighted_neutral += sentiment.get("Neutral", 0) * weight
                    total_weight += weight
            
            # Normalizează scorurile generale
            if total_weight > 0:
                overall_positive = weighted_positive / total_weight
                overall_negative = weighted_negative / total_weight
                overall_neutral = weighted_neutral / total_weight
            else:
                overall_positive = 0
                overall_negative = 0
                overall_neutral = 0
            
            # Adaugă scorurile generale la rezultate
            results["Overall_Positive"] = overall_positive
            results["Overall_Negative"] = overall_negative
            results["Overall_Neutral"] = overall_neutral
            
            # Calculează scoruri derivate
            results["Sentiment_Score"] = overall_positive - overall_negative
            results["Confidence"] = 1 - overall_neutral
            
            # Extras anul din calea fișierului
            year_match = re.search(r'(\d{4})', os.path.basename(file_path))
            if year_match:
                results["year"] = year_match.group(1)
            else:
                results["year"] = "N/A"
            
            return results
        
        except Exception as e:
            logging.error(f"Eroare la analiza fișierului {file_path} pentru {ticker}: {e}")
            return {"ticker": ticker, "error": str(e)}
    
    def analyze_company(self, ticker):
        """
        Analizează toate rapoartele disponibile pentru o companie
        
        Args:
            ticker: Ticker-ul companiei
            
        Returns:
            Lista de rezultate pentru fiecare raport analizat
        """
        # Găsește fișierele pentru acest ticker
        filing_files = self.find_filing_files(ticker)
        
        if not filing_files:
            logging.warning(f"Nu s-au găsit rapoarte pentru {ticker}")
            return []
        
        results = []
        for file_path in filing_files:
            result = self.analyze_filing(file_path, ticker)
            results.append(result)
        
        return results
    
    def analyze_all_companies(self, tickers=None, max_workers=4):
        """
        Analizează toate companiile
        
        Args:
            tickers: Lista de ticker-uri (dacă None, se vor lua din baza de date)
            max_workers: Numărul maxim de thread-uri pentru procesare paralelă
            
        Returns:
            DataFrame cu rezultatele analizei
        """
        # Dacă nu s-a furnizat o listă de ticker-uri, o obținem din baza de date
        if tickers is None and self.db_crud is not None:
            tickers = self.db_crud.select_all_company_tickers()
        
        if not tickers:
            logging.error("Nu s-au găsit ticker-uri pentru analiză")
            return pd.DataFrame()
        
        all_results = []
        
        # Folosim ThreadPoolExecutor pentru procesare paralelă
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Pregătim task-urile pentru fiecare companie
            futures = {executor.submit(self.analyze_company, ticker): ticker for ticker in tickers}
            
            # Procesăm rezultatele pe măsură ce sunt finalizate
            for future in tqdm(futures, desc="Analizând companiile"):
                ticker = futures[future]
                try:
                    company_results = future.result()
                    all_results.extend(company_results)
                except Exception as e:
                    logging.error(f"Eroare la analiza companiei {ticker}: {e}")
        
        # Creăm un DataFrame cu toate rezultatele
        if all_results:
            results_df = pd.DataFrame(all_results)
            
            # Salvăm rezultatele
            csv_path = os.path.join(self.output_dir, "sentiment_analysis_results.csv")
            results_df.to_csv(csv_path, index=False)
            
            # Salvăm și un fișier JSON pentru analize ulterioare
            json_path = os.path.join(self.output_dir, "sentiment_analysis_results.json")
            results_df.to_json(json_path, orient="records")
            
            return results_df
        else:
            logging.warning("Nu s-au obținut rezultate de la analiza de sentiment")
            return pd.DataFrame()
    
    def generate_investment_recommendations(self, results_df=None):
        """
        Generează recomandări de investiții pe baza analizei de sentiment
        
        Args:
            results_df: DataFrame cu rezultatele analizei (dacă None, se încarcă din fișier)
            
        Returns:
            DataFrame cu recomandările de investiții
        """
        if results_df is None:
            csv_path = os.path.join(self.output_dir, "sentiment_analysis_results.csv")
            if os.path.exists(csv_path):
                results_df = pd.read_csv(csv_path)
            else:
                logging.error("Nu s-a găsit fișierul cu rezultatele analizei")
                return pd.DataFrame()
        
        if results_df.empty:
            logging.error("DataFrame-ul cu rezultatele analizei este gol")
            return pd.DataFrame()
        
        # Grupăm după ticker și calculăm media scorurilor
        grouped = results_df.groupby('ticker').agg({
            'Overall_Positive': 'mean',
            'Overall_Negative': 'mean',
            'Overall_Neutral': 'mean',
            'Sentiment_Score': 'mean',
            'Confidence': 'mean'
        }).reset_index()
        
        # Adăugăm o coloană cu recomandarea
        def get_recommendation(row):
            score = row['Sentiment_Score']
            confidence = row['Confidence']
            
            if score > 0.15 and confidence > 0.6:
                return "Strong Buy"
            elif score > 0.05 and confidence > 0.5:
                return "Buy"
            elif score < -0.15 and confidence > 0.6:
                return "Strong Sell"
            elif score < -0.05 and confidence > 0.5:
                return "Sell"
            else:
                return "Hold"
        
        grouped['Recommendation'] = grouped.apply(get_recommendation, axis=1)
        
        # Sortăm după scorul de sentiment
        grouped = grouped.sort_values(by="Sentiment_Score", ascending=False)
        
        # Salvăm recomandările
        recommendations_path = os.path.join(self.output_dir, "investment_recommendations.csv")
        grouped.to_csv(recommendations_path, index=False)
        
        return grouped

# Exemplu de utilizare
if __name__ == "__main__":
    # Inițializăm managerul de analiză
    manager = SentimentAnalysisManager()
    
    # Analizăm companiile specificate
    tickers_to_analyze = ["TGT"]  # Poți pune aici ticker-urile tale
    
    results = manager.analyze_all_companies(tickers=tickers_to_analyze)
    
    # Generăm recomandări de investiții
    recommendations = manager.generate_investment_recommendations(results)
    
    # Afișăm recomandările
    print("\nRecomandări de investiții bazate pe analiza de sentiment:")
    print(recommendations[['ticker', 'Sentiment_Score', 'Confidence', 'Recommendation']])