import requests
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials
import json
import os
from datetime import datetime
import time

# Google Sheets Setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID', '')

def get_google_sheets_client():
    """Initialize Google Sheets client using service account credentials"""
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    if not creds_json:
        raise ValueError("GOOGLE_CREDENTIALS environment variable not set")
    
    creds_dict = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client

def scrape_internshala():
    """Scrape Internshala for Data Analytics, ML, and AI internships in India"""
    internships = []
    base_url = "https://internshala.com/internships/"
    
    # Keywords for internships
    keywords = ['data-analytics', 'machine-learning', 'artificial-intelligence', 'data-science, 'prompt-engineering', 'generative-ai', 'deep-learning', 'nlp']
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for keyword in keywords:
        try:
            url = f"{base_url}{keyword}-internship/"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find internship cards
                cards = soup.find_all('div', class_='internship_meta')
                
                for card in cards[:10]:  # Limit to 10 per category
                    try:
                        title_elem = card.find('h3', class_='heading_4_5')
                        company_elem = card.find('p', class_='company_name')
                        location_elem = card.find('div', id=lambda x: x and 'location' in x)
                        stipend_elem = card.find('span', class_='stipend')
                        link_elem = card.find('a', class_='view_detail_button')
                        
                        if title_elem:
                                            # Get location first
                                                                location = location_elem.get_text(strip=True) if location_elem else 'Remote'

                                                                                    # Filter for Work from Home only
                                                                                                        wfh_keywords = ['work from home', 'remote', 'wfh', 'work-from-home', 'hybrid']
                                                                                                                            if not any(keyword in location.lower() for keyword in wfh_keywords):
                                                                                                                                                    continue
                                                                                                                                                    
                            internship = {
                                'Title': title_elem.get_text(strip=True),
                                'Company': company_elem.get_text(strip=True) if company_elem else 'N/A',
                        'Location': location,                                'Stipend': stipend_elem.get_text(strip=True) if stipend_elem else 'Unpaid',
                                'Link': f"https://internshala.com{link_elem['href']}" if link_elem else 'N/A',
                                'Source': 'Internshala',
                                'Date': datetime.now().strftime('%Y-%m-%d'),
                                'Category': keyword.replace('-', ' ').title()
                            }
                            internships.append(internship)
                    except Exception as e:
                        print(f"Error parsing internship card: {e}")
                        continue
                        
            time.sleep(2)  # Respectful scraping
            
        except Exception as e:
            print(f"Error scraping Internshala {keyword}: {e}")
            continue
    
    return internships

def scrape_indeed_india():
    """Scrape Indeed India for Data Analytics, ML, and AI internships"""
    internships = []
    base_url = "https://in.indeed.com/jobs"
    
    queries = ['Data Analytics Intern', 'Machine Learning Intern', 'AI Intern', 'Data Science Intern', 'Prompt Engineering Intern', 'Generative AI Intern', 'Deep Learning Intern', 'NLP Intern']
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for query in queries:
        try:
            params = {
                'q': query,
                'l': 'India',
                'fromage': '3',  # Last 3 days
                'sort': 'date'
            }
            
            response = requests.get(base_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find job cards
                job_cards = soup.find_all('div', class_='job_seen_beacon')
                
                for card in job_cards[:10]:  # Limit to 10 per query
                    try:
                        title_elem = card.find('h2', class_='jobTitle')
                        company_elem = card.find('span', class_='companyName')
                        location_elem = card.find('div', class_='companyLocation')
                        link_elem = title_elem.find('a') if title_elem else None
                        
                        if title_elem:
                            job_id = link_elem.get('data-jk', '') if link_elem else ''
                            internship = {
                                'Title': title_elem.get_text(strip=True),
                                'Company': company_elem.get_text(strip=True) if company_elem else 'N/A',
                                                    # Get location first
                                                                        location = location_elem.get_text(strip=True) if location_elem else 'India'

                                                                                            # Filter for Work from Home only
                                                                                                                wfh_keywords = ['work from home', 'remote', 'wfh', 'work-from-home', 'hybrid']
                                                                                                                                    if not any(keyword in location.lower() for keyword in wfh_keywords):
                                                                                                                                                            continue
                                                                                                                                                            
                        'Location': location,                                'Stipend': 'Check Link',
                                'Link': f"https://in.indeed.com/viewjob?jk={job_id}" if job_id else 'N/A',
                                'Source': 'Indeed India',
                                'Date': datetime.now().strftime('%Y-%m-%d'),
                                'Category': query
                            }
                            internships.append(internship)
                    except Exception as e:
                        print(f"Error parsing job card: {e}")
                        continue
                        
            time.sleep(2)  # Respectful scraping
            
        except Exception as e:
            print(f"Error scraping Indeed India {query}: {e}")
            continue
    
    return internships

def update_google_sheet(internships):
    """Update Google Sheets with internship data"""
    try:
        client = get_google_sheets_client()
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1
        
        # Get existing data to avoid duplicates
        existing_data = sheet.get_all_records()
        existing_links = {row.get('Link', '') for row in existing_data}
        
        # Prepare new rows
        new_rows = []
        for internship in internships:
            if internship['Link'] not in existing_links and internship['Link'] != 'N/A':
                new_rows.append([
                    internship['Title'],
                    internship['Company'],
                    internship['Location'],
                    internship['Stipend'],
                    internship['Link'],
                    internship['Source'],
                    internship['Date'],
                    internship['Category']
                ])
        
        if new_rows:
            # If sheet is empty, add headers first
            if len(existing_data) == 0:
                headers = ['Title', 'Company', 'Location', 'Stipend', 'Link', 'Source', 'Date', 'Category']
                sheet.append_row(headers)
            
            # Append new rows
            for row in new_rows:
                sheet.append_row(row)
                time.sleep(1)  # Avoid rate limiting
            
            print(f"Added {len(new_rows)} new internships to Google Sheets")
        else:
            print("No new internships to add")
            
    except Exception as e:
        print(f"Error updating Google Sheets: {e}")
        raise

def main():
    """Main function to scrape and update sheet"""
    print("Starting India Internship Scraper...")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_internships = []
    
    # Scrape Internshala
    print("\nScraping Internshala...")
    internshala_data = scrape_internshala()
    print(f"Found {len(internshala_data)} internships from Internshala")
    all_internships.extend(internshala_data)
    
    # Scrape Indeed India
    print("\nScraping Indeed India...")
    indeed_data = scrape_indeed_india()
    print(f"Found {len(indeed_data)} internships from Indeed India")
    all_internships.extend(indeed_data)
    
    # Update Google Sheets
    print(f"\nTotal internships found: {len(all_internships)}")
    if all_internships:
        print("Updating Google Sheets...")
        update_google_sheet(all_internships)
        print("✓ Scraping completed successfully!")
    else:
        print("No internships found to update")

if __name__ == "__main__":
    main()
