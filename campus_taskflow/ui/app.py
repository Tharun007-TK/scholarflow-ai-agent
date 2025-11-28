import streamlit as st
import os
import sys
import tempfile
import json
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.colored_header import colored_header
from streamlit_option_menu import option_menu

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from campus_taskflow.adk.core import State
from campus_taskflow.agents.orchestrator import OrchestratorAgent
from campus_taskflow.tools.search_tools import EmbeddingSearchTool

st.set_page_config(
    page_title="ScholarFlow AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Professional Look ---
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.1);
    }
    div[data-testid="stMetricValue"] {
        color: #2E7D32 !important; /* Dark Green */
        font-size: 2rem !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #666666 !important;
        font-size: 1rem !important;
        font-weight: 500;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #ffffff;
        border-radius: 5px;
        color: #333;
        font-weight: 600;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50 !important;
        color: #ffffff !important;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
with st.sidebar:
    st.image("https://img.icons8.com/clouds/100/000000/student-male.png", width=100)
    st.title("ScholarFlow AI")
    
    selected = option_menu(
        "Menu",
        ["Home", "Dashboard", "Chat", "History"],
        icons=['house', 'speedometer2', 'chat-dots', 'clock-history'],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "orange", "font-size": "20px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#4CAF50"},
        }
    )
    
    st.divider()
    
    with st.expander("⚙️ Settings", expanded=True):
        api_key = st.text_input("Google API Key", type="password", help="Required for AI features")
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
            st.success("Connected")
        else:
            st.warning("Disconnected")

# --- Page Logic ---

if selected == "Home":
    colored_header(
        label="Academic Workflow Automation",
        description="Upload your course material and let the agents organize your study life.",
        color_name="green-70"
    )
    
    col1, col2 = st.columns([1, 1])
    with col1:
        uploaded_file = st.file_uploader("📄 Upload PDF Syllabus/Notes", type="pdf")
    
    with col2:
        st.info("Ready to process? Ensure your API key is set in the sidebar.")
        if uploaded_file and api_key:
            if st.button("🚀 Start TaskFlow Pipeline"):
                with st.spinner("🤖 Agents are analyzing your document..."):
                    # Save uploaded file to temp
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    # Initialize Agent and State
                    orchestrator = OrchestratorAgent()
                    state = State()
                    
                    try:
                        # Run the pipeline
                        result = orchestrator.run(state, tmp_path)
                        st.balloons()
                        st.success("Analysis Complete! Go to 'Dashboard' to view results.")
                        
                        # Store state in session for display
                        st.session_state.last_run_state = state
                        
                        # Add to history
                        if "history" not in st.session_state:
                            st.session_state.history = []
                        st.session_state.history.append({
                            "timestamp": state.history[-1]['timestamp'] if state.history else "Unknown",
                            "summary": state.get("summary")
                        })
                        
                    except Exception as e:
                        st.error(f"Pipeline failed: {str(e)}")
                    finally:
                        os.unlink(tmp_path)

elif selected == "Dashboard":
    st.header("📊 Study Dashboard")
    
    if "last_run_state" in st.session_state:
        state = st.session_state.last_run_state
        
        # Metrics
        m1, m2, m3 = st.columns(3)
        tasks = state.get("parsed_tasks", [])
        flashcards = state.get("flashcards", [])
        schedule = state.get("schedule", [])
        
        m1.metric("Tasks Found", len(tasks))
        m2.metric("Flashcards", len(flashcards))
        m3.metric("Study Sessions", len(schedule))
        
        # Apply styling to metrics
        style_metric_cards(background_color="#FFFFFF", border_left_color="#4CAF50")
        
        st.divider()
        
        tab1, tab2, tab3 = st.tabs(["📅 Schedule", "📚 Summary", "📇 Flashcards"])
        
        with tab1:
            if schedule:
                for item in schedule:
                    st.info(f"**{item['date']}**: {item['task']} ({item['duration_minutes']} mins)")
            else:
                st.write("No schedule generated yet.")
                
        with tab2:
            summary_data = state.get("summary", {})
            st.markdown(summary_data if isinstance(summary_data, str) else summary_data.get("summary", "No summary available."))
            
        with tab3:
            if flashcards:
                cols = st.columns(2)
                for i, card in enumerate(flashcards):
                    with cols[i % 2]:
                        with st.expander(f"Q: {card.get('front', 'Question')}"):
                            st.write(f"**A:** {card.get('back', 'Answer')}")
                            st.caption(f"Tags: {', '.join(card.get('tags', []))}")
            else:
                st.write("No flashcards generated.")
                
    else:
        st.warning("No data available. Please run a pipeline in 'Home' first.")

elif selected == "Chat":
    st.header("💬 Chat with Document")
    
    if "last_run_state" in st.session_state:
        # Chat interface
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask a question about your PDF..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # RAG Logic
                    rag_tool = EmbeddingSearchTool()
                    results = rag_tool.run(prompt)
                    
                    if results:
                        context = "\n".join([r['content'] for r in results])
                        # Use LLMSkill to generate answer
                        from campus_taskflow.adk.skills import LLMSkill
                        llm = LLMSkill()
                        answer = llm.execute(f"Answer the question based on the context:\nContext: {context}\nQuestion: {prompt}")
                    else:
                        answer = "I couldn't find relevant information in the document."
                    
                    st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
    else:
        st.warning("Please upload and analyze a document in 'Home' first.")

elif selected == "History":
    st.header("📜 Execution History")
    if "history" in st.session_state and st.session_state.history:
        for i, entry in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Run {len(st.session_state.history) - i}: {entry['timestamp']}"):
                st.write(entry['summary'])
    else:
        st.info("No history yet.")

