import os
import json
import cloudscraper
from bs4 import BeautifulSoup
import time

CATEGORIES = {
    "BSHND": "https://nust.edu.pk/faq-category/bshnd-admissions-faqs/",
    "MBBS": "https://nust.edu.pk/faq-category/mbbs-admissions-faqs/",
    "UG": "https://nust.edu.pk/faqs/"
}

def scrape_category(category_name, base_url, scraper):
    faqs = []
    current_url = base_url
    page = 1
    while current_url:
        print(f"Scraping {category_name} - Page {page} - {current_url}")
        response = scraper.get(current_url)
        if response.status_code != 200:
            print(f"Failed to fetch {current_url} - Status: {response.status_code}")
            break
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all faq cards
        cards = soup.find_all('div', class_='card')
        for card in cards:
            # Question is inside span in button
            btn = card.find('button', class_='btn-link')
            if not btn: continue
            q_span = btn.find('span')
            if not q_span: continue
            question = q_span.text.strip()
            
            # Answer is inside card-body
            body = card.find('div', class_='card-body')
            if not body: continue
            answer = body.get_text(separator=' ', strip=True)
            
            # Clean up extra spaces
            answer = ' '.join(answer.split())
            
            if question and answer:
                faqs.append({
                    "category": category_name,
                    "question": question,
                    "answer": answer
                })
        
        # Check for next page
        next_link = soup.find('link', rel='next')
        if next_link and next_link.get('href'):
            current_url = next_link['href']
            page += 1
            time.sleep(1) # Be nice to the server
        else:
            current_url = None
            
    return faqs

def main():
    scraper = cloudscraper.create_scraper()
    all_faqs = []
    
    os.makedirs('data', exist_ok=True)
    
    for cat_name, url in CATEGORIES.items():
        faqs = scrape_category(cat_name, url, scraper)
        all_faqs.extend(faqs)
        print(f"Total extracted for {cat_name}: {len(faqs)}")
        
    with open('data/nust_faqs.json', 'w', encoding='utf-8') as f:
        json.dump(all_faqs, f, indent=4)
        print(f"Successfully saved {len(all_faqs)} total FAQs to data/nust_faqs.json")

if __name__ == '__main__':
    main()
