import streamlit as st
import os
from datetime import datetime
import openai

# Set fixed current date
CURRENT_DATE = datetime(2025, 1, 30)

# Initialize session state for language if not exists
if 'language' not in st.session_state:
    st.session_state.language = 'en'

# Translations dictionary
TRANSLATIONS = {
    'en': {
        'title': "News Article Generator",
        'current_date': "Current Date",
        'prompt_label': "Enter your prompt:",
        'prompt_placeholder': "Enter a prompt for generating a news article...",
        'generate_button': "Generate Article",
        'generated_article': "Generated Article:",
        'please_enter_prompt': "Please enter a prompt.",
        'api_key_missing': "OpenAI API key not found. Please set OPENAI_API_KEY in secrets or environment variables.",
        'auth_success': "Successfully authenticated with OpenAI!",
        'generation_failed': "Failed to generate text: ",
        'temperature_label': "Creativity Level:",
        'max_tokens_label': "Maximum Length:",
        'model_label': "Select Model:",
        'settings': "Generation Settings",
        'clear_button': "Clear Output",
        'copy_button': "Copy to Clipboard",
        'copied': "Copied!",
        'history': "Generation History",
        'no_history': "No generation history yet."
    },
    'gu': {
        'title': "સમાચાર લેખ જનરેટર",
        'current_date': "વર્તમાન તારીખ",
        'prompt_label': "તમારું પ્રોમ્પ્ટ લખો:",
        'prompt_placeholder': "સમાચાર લેખ જનરેટ કરવા માટે પ્રોમ્પ્ટ દાખલ કરો...",
        'generate_button': "લેખ જનરેટ કરો",
        'generated_article': "જનરેટ થયેલ લેખ:",
        'please_enter_prompt': "કૃપા કરીને પ્રોમ્પ્ટ દાખલ કરો.",
        'api_key_missing': "OpenAI API કી મળી નથી. કૃપા કરીને OPENAI_API_KEY સેટ કરો.",
        'auth_success': "OpenAI સાથે સફળતાપૂર્વક પ્રમાણિત થયું!",
        'generation_failed': "ટેક્સ્ટ જનરેટ કરવામાં નિષ્ફળ: ",
        'temperature_label': "ક્રિએટિવિટી લેવલ:",
        'max_tokens_label': "મહત્તમ લંબાઈ:",
        'model_label': "મોડેલ પસંદ કરો:",
        'settings': "જનરેશન સેટિંગ્સ",
        'clear_button': "આઉટપુટ સાફ કરો",
        'copy_button': "ક્લિપબોર્ડ પર કૉપિ કરો",
        'copied': "કૉપિ થયું!",
        'history': "જનરેશન ઇતિહાસ",
        'no_history': "હજુ સુધી કોઈ જનરેશન ઇતિહાસ નથી."
    }
}

# Initialize session state for history
if 'history' not in st.session_state:
    st.session_state.history = []

def authenticate_openai():
    """Authenticate with OpenAI using API key"""
    openai_api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        st.error(TRANSLATIONS[st.session_state.language]['api_key_missing'])
        st.stop()

    openai.api_key = openai_api_key
    return True

def generate_text(prompt, model="gpt-3.5-turbo", temperature=0.7, max_tokens=500):
    """Generate text using OpenAI's API"""
    try:
        if model.startswith("gpt"):
            # Using chat completion for GPT models
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        else:
            # Using completion for other models
            response = openai.Completion.create(
                engine=model,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].text.strip()
    except Exception as e:
        st.error(f"{TRANSLATIONS[st.session_state.language]['generation_failed']}{str(e)}")
        return None

def main():
    # Language selector in the sidebar
    st.sidebar.selectbox(
        "Choose Language / ભાષા પસંદ કરો",
        options=['English', 'ગુજરાતી'],
        key='language_selector',
        on_change=lambda: setattr(
            st.session_state,
            'language',
            'gu' if st.session_state.language_selector == 'ગુજરાતી' else 'en'
        )
    )

    # Get current language translations
    t = TRANSLATIONS[st.session_state.language]

    # Main title
    st.title(t['title'])

    # Authenticate
    if authenticate_openai():
        st.success(t['auth_success'])

    # Current date
    st.write(f"{t['current_date']}: {CURRENT_DATE.strftime('%d-%m-%Y')}")

    # Sidebar settings
    st.sidebar.subheader(t['settings'])

    model = st.sidebar.selectbox(
        t['model_label'],
        options=["gpt-3.5-turbo", "gpt-4", "text-davinci-003"]
    )

    temperature = st.sidebar.slider(
        t['temperature_label'],
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1
    )

    max_tokens = st.sidebar.slider(
        t['max_tokens_label'],
        min_value=100,
        max_value=2000,
        value=500,
        step=100
    )

    # Main content area
    prompt = st.text_area(t['prompt_label'], t['prompt_placeholder'])

    col1, col2 = st.columns([1, 4])

    if col1.button(t['generate_button']):
        if prompt:
            result = generate_text(prompt, model, temperature, max_tokens)
            if result:
                # Add to history
                st.session_state.history.append({
                    'prompt': prompt,
                    'result': result,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

                st.subheader(t['generated_article'])
                st.write(result)

                # Copy button
                if st.button(t['copy_button']):
                    st.write(t['copied'])
        else:
            st.warning(t['please_enter_prompt'])

    if col2.button(t['clear_button']):
        st.session_state.history = []

    # History section
    st.subheader(t['history'])
    if st.session_state.history:
        for item in reversed(st.session_state.history):
            with st.expander(f"{item['timestamp']} - {item['prompt'][:50]}..."):
                st.write(item['result'])
    else:
        st.write(t['no_history'])

if __name__ == "__main__":
    main()
