import streamlit as st
import os
from datetime import datetime, timedelta
import glob
from deep_translator import GoogleTranslator
import re

# Set fixed current date
CURRENT_DATE = datetime(2025, 1, 30)

def highlight_text(text, search_term, is_gujarati=False):
    """Highlight search term in text using markdown bold syntax"""
    if not search_term:
        return text
    
    # If searching in Gujarati mode, ensure search term is in Gujarati
    if is_gujarati and not any('\u0A80' <= c <= '\u0AFF' for c in search_term):
        translator = GoogleTranslator(source='auto', target='gu')
        search_term = translator.translate(search_term)
    
    # Case insensitive replacement
    pattern = re.compile(re.escape(search_term), re.IGNORECASE)
    return pattern.sub(lambda m: f"**{m.group()}**", text)

def format_article_content(content):
    """Format the article content for better readability"""
    # Extract title, date, link, and main content
    title_match = re.search(r'Title:\s*(.+?)(?=\n|$)', content)
    date_match = re.search(r'Date:\s*(.+?)(?=\n|$)', content)
    link_match = re.search(r'Link:\s*(.+?)(?=\n|$)', content)
    
    # Format the content
    formatted_content = ""
    
    # Add title if found
    if title_match:
        formatted_content += f"### {title_match.group(1)}\n\n"
    
    # Add date if found
    if date_match:
        formatted_content += f"**Date:** {date_match.group(1)}\n\n"
    
    # Add formatted link if found
    if link_match:
        formatted_content += f"[Link to news article]({link_match.group(1)})\n\n"
    
    # Extract and clean main content
    main_content = re.sub(r'Title:.+\n|Date:.+\n|Link:.+\n', '', content).strip()
    
    # Format paragraphs
    paragraphs = main_content.split('\n\n')
    formatted_content += '\n\n'.join(para.replace('\n', ' ').strip() for para in paragraphs)
    
    return formatted_content

def load_articles(data_folder="data"):
    """Load all articles from text files in the data folder"""
    articles = []
    for file_path in glob.glob(os.path.join(data_folder, "*.txt")):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Split content into individual articles based on separator
            individual_articles = content.split("=======================================")
            
            for article in individual_articles:
                if article.strip():  # Skip empty articles
                    # Extract date using regex
                    date_match = re.search(r'Date:\s*(\d{2}-\d{2}-\d{4})', article)
                    if date_match:
                        date_str = date_match.group(1)
                        date = datetime.strptime(date_str, '%d-%m-%Y')
                        
                        # Extract title
                        title_match = re.search(r'Title:\s*(.+?)(?=\n|$)', article)
                        title = title_match.group(1) if title_match else "Untitled"
                        
                        articles.append({
                            'date': date,
                            'title': title,
                            'content': article.strip()
                        })
    return articles

def translate_text(text, target_lang):
    """Translate text to target language"""
    try:
        translator = GoogleTranslator(source='auto', target=target_lang)
        return translator.translate(text)
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return text

def search_articles(articles, query, language, date_filter):
    """Search articles based on query and filters"""
    results = []
    
    # Use fixed current date instead of datetime.now()
    current_date = CURRENT_DATE
    
    # Convert date filter to timedelta
    if date_filter == "Past 24 hours":
        date_threshold = current_date - timedelta(days=1)
    elif date_filter == "Past week":
        date_threshold = current_date - timedelta(weeks=1)
    elif date_filter == "Past month":
        date_threshold = current_date - timedelta(days=30)
    else:
        date_threshold = datetime.min
    
    # Translate query if language is Gujarati
    search_query = query
    if language == "gu":
        search_query = translate_text(query, 'gu')
    
    for article in articles:
        # Check date filter
        if article['date'] >= date_threshold:
            # Search in content
            if search_query.lower() in article['content'].lower():
                results.append(article)
    
    return results

def main():
    st.title("News Article Search")
    
    # Display current date (fixed)
    st.write(f"Current Date: {CURRENT_DATE.strftime('%d-%m-%Y')}")
    
    # Language selection
    language = st.selectbox(
        "Select Language",
        ["English", "ગુજરાતી (Gujarati)"],
        format_func=lambda x: x
    )
    
    # Convert language selection to code
    lang_code = "en" if language == "English" else "gu"
    
    # Search input
    search_query = st.text_input(
        "Enter search term",
        key="search_input"
    )
    
    # Date filter
    date_filter = st.selectbox(
        "Filter by date",
        ["All time", "Past 24 hours", "Past week", "Past month"]
    )
    
    # Load articles
    articles = load_articles()
    
    if search_query:
        results = search_articles(articles, search_query, lang_code, date_filter)
        
        st.subheader(f"Found {len(results)} results")
        
        for article in results:
            with st.expander(article['title']):
                # Format and translate content based on selected language
                content = article['content']
                if lang_code != "gu":  # If English is selected, translate from Gujarati
                    content = translate_text(content, 'en')
                
                # Format the content
                formatted_content = format_article_content(content)
                
                # Highlight search terms
                highlighted_content = highlight_text(
                    formatted_content, 
                    search_query, 
                    is_gujarati=(lang_code == "gu")
                )
                
                # Display using markdown
                st.markdown(highlighted_content)

if __name__ == "__main__":
    main()
