import streamlit as st
import os
from datetime import datetime, timedelta
import glob
from deep_translator import GoogleTranslator
import re
from transformers import AutoModelForCausalLM, AutoTokenizer

# Set fixed current date
CURRENT_DATE = datetime(2025, 1, 30)

# Initialize Mixtral model
@st.cache_resource
def load_mixtral_model():
    tokenizer = AutoTokenizer.from_pretrained("mistralai/Mixtral-8x7B-Instruct-v0.1")
    model = AutoModelForCausalLM.from_pretrained("mistralai/Mixtral-8x7B-Instruct-v0.1")
    return model, tokenizer

def process_natural_language_query(query, model, tokenizer):
    """Process natural language query using Mixtral"""
    prompt = f"""
    Extract search parameters from the following query:
    Query: {query}

    Return in format:
    - search_terms: [main keywords to search]
    - date_range: [time period to search: "All time", "Past 24 hours", "Past week", "Past month"]
    """

    inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(**inputs, max_length=200)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Parse the response
    search_terms = []
    date_range = "All time"

    # Extract search terms
    if "search_terms:" in response.lower():
        terms = response.lower().split("search_terms:")[1].split("date_range:")[0]
        search_terms = [term.strip() for term in terms.split(",") if term.strip()]

    # Extract date range
    if "date_range:" in response.lower():
        date_text = response.lower().split("date_range:")[1].strip()
        if "24 hours" in date_text or "day" in date_text:
            date_range = "Past 24 hours"
        elif "week" in date_text:
            date_range = "Past week"
        elif "month" in date_text:
            date_range = "Past month"

    return search_terms, date_range

# [Previous translation and highlighting functions remain the same]

def main():
    st.title("સમાચાર લેખ શોધ")

    # Display current date
    st.write(f"વર્તમાન તારીખ: {CURRENT_DATE.strftime('%d-%m-%Y')}")

    # Load Mixtral model
    model, tokenizer = load_mixtral_model()

    # Natural language input
    nl_query = st.text_input(
        "તમારી શોધ દાખલ કરો (દા.ત. 'ગઈકાલના ક્રિકેટ સમાચાર બતાવો')",
        key="nl_input"
    )

    if nl_query:
        # Process natural language query
        search_terms, date_range = process_natural_language_query(nl_query, model, tokenizer)

        # Translate search terms if in English
        translated_terms = [translate_to_gujarati(term) for term in search_terms]

        # Load and search articles
        articles = load_articles()
        results = []

        for term, translated_term in zip(search_terms, translated_terms):
            term_results = search_articles(articles, term, translated_term, date_range)
            results.extend(term_results)

        # Remove duplicates
        results = list({article['title']: article for article in results}.values())

        st.subheader(f"{len(results)} પરિણામો મળ્યા")

        for article in results:
            with st.expander(article['title']):
                formatted_content = format_article_content(article['content'])

                # Highlight all search terms and their translations
                highlighted_content = formatted_content
                for term, translated_term in zip(search_terms, translated_terms):
                    highlighted_content = highlight_text(
                        highlighted_content,
                        term,
                        translated_term
                    )

                st.markdown(highlighted_content)

if __name__ == "__main__":
    main()
