import streamlit as st
from open import create_brochure as open_brochure
from close import create_brochure as close_brochure
import time

# Page configuration
st.set_page_config(
    page_title="AI Brochure Generator",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling and readability
st.markdown("""
    <style>
    /* Input field styling */
    .stTextInput > div > div > input {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 10px;
        border: 1px solid #ddd;
        color: #333333;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        background-color: #2e6fdf;
        color: white;
        font-weight: bold;
        padding: 12px 20px;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #1c4fa3;
        transform: translateY(-2px);
    }
    
    /* Main content area */
    .main {
        padding: 2rem;
        background-color: #f8f9fa;
    }
    
    /* Output container */
    .output-container {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 20px 0;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: grey;
    }
    
    /* Text */
    p {
        color:white;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.markdown("""
    <h1 style='text-align: center; 
               color: grey;
               padding: 20px;'>
        ✨ AI Brochure Generator
    </h1>
    """, unsafe_allow_html=True)

# Subtitle
st.markdown("""
    <p style='text-align: center; font-size: 1.2em; color: white;'>
        Transform your company information into engaging brochures! 
    </p>
    """, unsafe_allow_html=True)

# Create two columns for inputs
col1, col2 = st.columns(2)

with col1:
    model_choice = st.selectbox(
        "🤖 Select Model",
        ["Open", "Closed"],
        index=0,
        help="Choose the AI model for generating your brochure"
    )

with col2:
    company_name = st.text_input(
        "🏢 Company Name",
        placeholder="Enter your company name",
        help="Enter your company's full legal name"
    )

url = st.text_input(
    "🌍 Company Website URL",
    placeholder="https://www.example.com",
    help="Enter your company's website URL"
)

# Create a container for the brochure output
output_container = st.empty()

def display_markdown_with_typing(text, container, delay=0.02):
    """Function to display markdown text with a typing effect."""
    current_text = ""
    lines = text.split('\n')
    
    for line in lines:
        for char in line:
            current_text += char
            container.markdown(
                f"""
                <div style='
                    background-color: grey;
                    color: black;
                    padding: 20px;
                    border-radius: 8px;
                    border: 1px solid #e0e0e0;
                    font-family: "IBM Plex Mono", monospace;
                    line-height: 1.6;
                '>
                    {current_text}
                </div>
                """,
                unsafe_allow_html=True
            )
            time.sleep(delay)
        current_text += '\n'

if st.button("✨ Generate Beautiful Brochure ✨"):
    if company_name and url:
        with st.spinner(" Creating..."):
            try:
                # Get brochure content based on model choice
                if model_choice == "Open":
                    brochure_content = open_brochure(company_name, url)
                else:
                    brochure_content = close_brochure(company_name, url)
                
                # Format the content with markdown
                formatted_content = f"""
                

                {brochure_content}

                ---
                    Completed 
                """
                
                # Display with typing effect
                display_markdown_with_typing(formatted_content, output_container)
                
            except Exception as e:
                st.error(f"🚨 Oops! Something went wrong: {str(e)}")
    else:
        st.warning("⚠️ Please enter both Company Name and URL!")

