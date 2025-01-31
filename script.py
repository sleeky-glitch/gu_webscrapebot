import streamlit as st
import os
from datetime import datetime, timedelta
import glob
from deep_translator import GoogleTranslator
import re

# Set fixed current date
CURRENT_DATE = datetime(2025, 1, 30)

def highlight_text(text, search_term):
    """Highlight search term in text using markdown bold syntax"""
    if not search_term:
        return text
    
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

def search_articles(articles, query, date_filter):
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
    
    for article in articles:
        # Check date filter
        if article['date'] >= date_threshold:
            # Search in content
            if query.lower() in article['content'].lower():
                results.append(article)
    
    return results

def main():
    st.title("સમાચાર લેખ શોધ")  # "News Article Search" in Gujarati
    
    # Display current date (fixed)
    st.write(f"વર્તમાન તારીખ: {CURRENT_DATE.strftime('%d-%m-%Y')}")  # "Current Date" in Gujarati
    
    # Search input
    search_query = st.text_input(
        "શોધ શબ્દ દાખલ કરો",  # "Enter search term" in Gujarati
        key="search_input"
    )
    
    # Date filter
    date_filter = st.selectbox(
        "તારીખ દ્વારા ફિલ્ટર કરો",  # "Filter by date" in Gujarati
        ["બધો સમય", "છેલ્લા 24 કલાક", "છેલ્લા અઠવાડિયા", "છેલ્લા મહિના"]  # Date options in Gujarati
    )
    
    # Convert date filter selections to English for processing
    date_filter_mapping = {
        "બધો સમય": "All time",
        "છેલ્લા 24 કલાક": "Past 24 hours",
        "છેલ્લા અઠવાડિયા": "Past week",
        "છેલ્લા મહિના": "Past month"
    }
    
    # Load articles
    articles = load_articles()
    
    if search_query:
        results = search_articles(articles, search_query, date_filter_mapping[date_filter])
        
        st.subheader(f"{len(results)} પરિણામો મળ્યા")  # "Found x results" in Gujarati
        
        for article in results:
            with st.expander(article['title']):
                # Format the content
                formatted_content = format_article_content(article['content'])
                
                # Highlight search terms
                highlighted_content = highlight_text(formatted_content, search_query)
                
                # Display using markdown
                st.markdown(highlighted_content)

if __name__ == "__main__":
    main()
