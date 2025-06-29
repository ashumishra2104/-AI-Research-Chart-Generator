import streamlit as st
import requests
import json
import os

# Page configuration
st.set_page_config(
    page_title="AI Research & Chart Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .step-box {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        background-color: #f9f9f9;
    }
    .research-box {
        background-color: #f0f8ff;
        border-left-color: #4CAF50;
    }
    .code-box {
        background-color: #fff5f5;
        border-left-color: #FF6B6B;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'research_data' not in st.session_state:
    st.session_state.research_data = None
if 'chart_code' not in st.session_state:
    st.session_state.chart_code = None

def search_web(query):
    """Simple web search using a public API"""
    try:
        # Using a simple search API that doesn't require complex dependencies
        search_url = f"https://api.duckduckgo.com/?q={query}&format=json&no_redirect=1"
        
        # Make the request
        response = requests.get(search_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Extract relevant results
            results = []
            if 'AbstractText' in data and data['AbstractText']:
                results.append(f"Summary: {data['AbstractText']}")
            
            if 'RelatedTopics' in data:
                for topic in data['RelatedTopics'][:3]:
                    if isinstance(topic, dict) and 'Text' in topic:
                        results.append(f"Related: {topic['Text']}")
            
            return "\n\n".join(results) if results else f"Basic search completed for: {query}"
        else:
            return f"Search completed for: {query}. Please provide more specific terms for better results."
    except Exception as e:
        return f"Web search for '{query}' completed. Manual research may be needed for specific data."

def call_openai_api(messages):
    """Call OpenAI API using requests"""
    try:
        # Get API key
        api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
        if not api_key:
            return "❌ OpenAI API key not found. Please add it in Streamlit secrets."
        
        # Prepare the request
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4-1106-preview",
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 2000
        }
        
        # Make the API call
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"API Error: {response.status_code}. Please check your API key and try again."
            
    except Exception as e:
        return f"Error calling OpenAI API: {str(e)}"

def research_agent(query):
    """Research agent that searches for data"""
    st.markdown("""
    <div class="step-box research-box">
        <h3>🔍 RESEARCH AGENT WORKING...</h3>
        <p>Searching for data related to your query...</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Search for information
    search_results = search_web(query)
    
    # Use OpenAI to analyze and structure the data
    messages = [
        {
            "role": "system",
            "content": """You are a research specialist. Analyze the query and provide structured data that can be used for visualization. 

If you have search results, extract numerical data. If not, provide typical/example data that would answer the query.

Format your response as:
1. Data Summary
2. Key Numbers/Statistics  
3. Recommended Chart Type
4. Data Structure for Visualization

Be specific with numbers, dates, and sources when available."""
        },
        {
            "role": "user",
            "content": f"Query: {query}\n\nSearch Results: {search_results}\n\nPlease provide structured data for visualization."
        }
    ]
    
    response = call_openai_api(messages)
    return response

def chart_generator_agent(research_data, original_query):
    """Chart generator that creates Python code"""
    st.markdown("""
    <div class="step-box code-box">
        <h3>📊 CHART GENERATOR WORKING...</h3>
        <p>Creating Python code for your visualization...</p>
    </div>
    """, unsafe_allow_html=True)
    
    messages = [
        {
            "role": "system",
            "content": """You are a data visualization expert. Create complete, runnable Python code using matplotlib that users can copy and run locally.

Your code must include:
1. All necessary imports (matplotlib.pyplot as plt, pandas as pd, numpy as np)
2. Data setup (create sample data if needed)
3. Professional chart creation with proper styling
4. Clear labels, titles, and formatting
5. plt.show() at the end

Choose the appropriate chart type (line, bar, scatter, pie, etc.) based on the data and query.

Make the code self-contained and ready to run."""
        },
        {
            "role": "user",
            "content": f"Original Query: {original_query}\n\nResearch Data: {research_data}\n\nCreate complete Python visualization code."
        }
    ]
    
    response = call_openai_api(messages)
    return response

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Research & Chart Generator</h1>
        <p>AI-Powered Data Research and Visualization Code Generator</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📋 How it works")
        st.markdown("""
        1. **🔍 Research**: AI searches for your data
        2. **📊 Generate**: AI creates Python chart code  
        3. **📝 Copy**: Copy code to run locally
        """)
        
        st.header("💡 Example Queries")
        example_queries = [
            "Top 10 most populated countries bar chart",
            "UK GDP past 3 years line chart", 
            "Bitcoin price trend last 6 months",
            "Global temperature trends decade",
            "IPL winners last 5 years scores"
        ]
        
        for query in example_queries:
            if st.button(f"📝 {query}", key=query, use_container_width=True):
                st.session_state.selected_query = query
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
    if not api_key:
        st.error("❌ OpenAI API key not found!")
        st.info("Please add your OpenAI API key in Streamlit secrets:")
        st.code('OPENAI_API_KEY = "sk-your-key-here"')
        st.stop()
    else:
        st.success("✅ AI System Ready!")
    
    # Main input
    user_query = st.text_input(
        "🎯 What would you like to research and visualize?",
        value=st.session_state.get('selected_query', ''),
        placeholder="e.g., Show me top 10 most populated countries with a bar chart"
    )
    
    # Generate button
    if st.button("🚀 Generate Research & Chart Code", type="primary", use_container_width=True):
        if user_query:
            # Reset previous results
            st.session_state.research_data = None
            st.session_state.chart_code = None
            
            # Step 1: Research
            with st.spinner("🔍 Researching data..."):
                research_data = research_agent(user_query)
                if research_data:
                    st.session_state.research_data = research_data
            
            # Display research results
            if st.session_state.research_data:
                st.markdown("""
                <div class="step-box research-box">
                    <h3>🔍 Research Results</h3>
                </div>
                """, unsafe_allow_html=True)
                st.write(st.session_state.research_data)
                
                # Step 2: Generate chart code
                with st.spinner("📊 Generating chart code..."):
                    chart_code = chart_generator_agent(st.session_state.research_data, user_query)
                    if chart_code:
                        st.session_state.chart_code = chart_code
                
                # Display chart code
                if st.session_state.chart_code:
                    st.markdown("""
                    <div class="step-box code-box">
                        <h3>📊 Generated Chart Code</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.code(st.session_state.chart_code, language='python')
                    
                    st.success("🎉 Chart code generated successfully!")
                    st.info("💡 Copy the code above and run it in your local Python environment.")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Python Code",
                        data=st.session_state.chart_code,
                        file_name=f"chart_{user_query[:20].replace(' ', '_')}.py",
                        mime="text/plain"
                    )
        else:
            st.warning("⚠️ Please enter a query!")
    
    # Show previous results
    if st.session_state.research_data and st.session_state.chart_code:
        st.markdown("---")
        st.header("📋 Previous Results")
        
        with st.expander("View Research Data"):
            st.write(st.session_state.research_data)
        
        with st.expander("View Chart Code"):
            st.code(st.session_state.chart_code, language='python')

if __name__ == "__main__":
    main()
