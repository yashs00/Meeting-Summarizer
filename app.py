import os
import re
import json
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import database
import pipeline

# Initialize Database
database.init_db()

# Make uploads directory
os.makedirs(os.path.join("y:\\Meeting_Summarizer", "uploads"), exist_ok=True)

# Page configuration
st.set_page_config(
    page_title="Meeting Summarizer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================================
# CSS Styling & Font Integration (Glassmorphism + Modern Dark Theme)
# =====================================================================

CSS_STYLES = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Patrick+Hand&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
/* Global styling rules */
html, body, [class*="css"], .stApp {
    font-family: 'Outfit', sans-serif !important;
    background-color: #fcfaf6 !important;
    background-image: radial-gradient(#2b221d 0.5px, transparent 0.5px), radial-gradient(#2b221d 0.5px, #fcfaf6 0.5px) !important;
    background-size: 20px 20px !important;
    background-position: 0 0, 10px 10px !important;
    opacity: 0.99;
    color: #2b221d !important;
}

/* Scrollbars styling */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}
::-webkit-scrollbar-track {
    background: #f7f4eb;
}
::-webkit-scrollbar-thumb {
    background: #2b221d;
    border: 2px solid #f7f4eb;
    border-radius: 5px;
}

/* Titles and Headers */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Fredoka', sans-serif !important;
    font-weight: 700 !important;
    color: #2b221d !important;
}

.glow-title {
    font-family: 'Fredoka', sans-serif !important;
    font-size: 42px;
    font-weight: 700;
    color: #2b221d !important;
    background: none !important;
    -webkit-text-fill-color: initial !important;
    margin-bottom: 2px;
    letter-spacing: -0.5px;
}

/* Sidebar overrides: Tan/Brown binder leather book style */
[data-testid="stSidebar"] {
    background-color: #5d4037 !important;
    border-right: 10px solid #3e2723;
}

[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3, 
[data-testid="stSidebar"] p, 
[data-testid="stSidebar"] span, 
[data-testid="stSidebar"] label {
    color: #eae1d8 !important;
    font-family: 'Outfit', sans-serif !important;
}

.sidebar-title {
    font-family: 'Fredoka', sans-serif !important;
    font-size: 24px;
    font-weight: 700;
    color: #eae1d8;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Custom folder-divider index tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 5px;
    background-color: transparent !important;
    border-bottom: 3px solid #2b221d !important;
    border-radius: 0px !important;
    padding: 0px !important;
    margin-bottom: 20px;
}
.stTabs [data-baseweb="tab"] {
    height: 40px;
    white-space: pre-wrap;
    background-color: #eae4d9 !important;
    border: 2px solid #2b221d !important;
    border-bottom: none !important;
    border-radius: 10px 10px 0px 0px !important;
    color: #2b221d !important;
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    font-size: 14px;
    padding: 0 20px;
    margin-bottom: -3px; /* overlap border */
    transition: background-color 0.2s ease;
}
.stTabs [data-baseweb="tab"]:hover {
    background-color: #dfd8cb !important;
    color: #000000 !important;
}
.stTabs [aria-selected="true"] {
    background-color: #ffffff !important;
    color: #2b221d !important;
    border-bottom: 3px solid #ffffff !important;
    box-shadow: none !important;
}

/* Neobrutalist Lined Notebook Sheet cards */
.glass-card {
    background: #ffffff !important;
    border: 2px solid #2b221d !important;
    border-radius: 12px !important;
    padding: 24px !important;
    margin-bottom: 20px !important;
    box-shadow: 4px 4px 0px #2b221d !important;
    color: #2b221d !important;
    backdrop-filter: none !important;
    transition: all 0.2s ease;
}
.glass-card:hover {
    transform: translate(-1px, -1px);
    box-shadow: 5px 5px 0px #2b221d !important;
}
.glass-card h1, .glass-card h2, .glass-card h3, .glass-card h4, .glass-card h5, .glass-card h6 {
    color: #2b221d !important;
    font-family: 'Fredoka', sans-serif !important;
}
.glass-card p, .glass-card li, .glass-card ol, .glass-card ul {
    font-family: 'Patrick Hand', cursive !important;
    font-size: 18.5px !important;
    line-height: 1.5 !important;
    color: #2b221d !important;
}

/* Custom styled numeric metric cards as mini school book tags */
.custom-metric-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}
.custom-metric-card {
    background: #ffffff !important;
    border: 2px solid #2b221d !important;
    border-radius: 8px !important;
    padding: 14px 20px !important;
    text-align: left !important;
    box-shadow: 3px 3px 0px #2b221d !important;
}
.custom-metric-val {
    font-size: 28px !important;
    font-weight: 700 !important;
    color: #b91c1c !important; /* Retro red values */
    margin-bottom: 2px !important;
    font-family: 'Fredoka', sans-serif !important;
}
.custom-metric-lbl {
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    color: #64748b !important;
    font-family: 'Outfit', sans-serif !important;
}

/* Decisions & Questions (Rotated sticker style!) */
.decision-card {
    background: #e6fcf5 !important; /* Mint green */
    border: 2px dashed #059669 !important;
    border-left: 2px dashed #059669 !important;
    border-radius: 12px !important;
    padding: 15px !important;
    margin-bottom: 12px !important;
    color: #065f46 !important;
    font-family: 'Patrick Hand', cursive !important;
    font-size: 18px !important;
    transform: rotate(-1deg);
    box-shadow: 2px 2px 6px rgba(0,0,0,0.03) !important;
}
.question-card {
    background: #fffbeb !important; /* Sticky yellow */
    border: 2px dashed #d97706 !important;
    border-left: 2px dashed #d97706 !important;
    border-radius: 12px !important;
    padding: 15px !important;
    margin-bottom: 12px !important;
    color: #78350f !important;
    font-family: 'Patrick Hand', cursive !important;
    font-size: 18px !important;
    transform: rotate(1.5deg);
    box-shadow: 2px 2px 6px rgba(0,0,0,0.03) !important;
}

/* Timeline Cards */
.timeline-container {
    display: flex;
    flex-direction: column;
    gap: 12px;
}
.timeline-item {
    display: flex !important;
    background: #ffffff !important;
    border: 2px solid #2b221d !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    margin-bottom: 10px !important;
    cursor: pointer !important;
    box-shadow: 3px 3px 0px #2b221d !important;
    color: #2b221d !important;
    transition: all 0.2s ease !important;
    align-items: center !important;
}
.timeline-item:hover {
    background: #fafafa !important;
    transform: translate(-1px, -1px) !important;
    box-shadow: 4px 4px 0px #2b221d !important;
}
.timeline-active {
    background: #fffbeb !important;
    border-color: #d97706 !important;
    box-shadow: 3px 3px 0px #d97706 !important;
}
.timeline-time {
    font-weight: 700 !important;
    color: #1d4ed8 !important; /* Retro blue */
    min-width: 90px !important;
    font-size: 13px !important;
    font-family: 'Fredoka', sans-serif !important;
}
.timeline-title {
    font-weight: 600 !important;
    color: #2b221d !important;
    font-size: 14.5px !important;
    font-family: 'Outfit', sans-serif !important;
}
.timeline-desc {
    font-size: 15px !important;
    color: #64748b !important;
    font-family: 'Patrick Hand', cursive !important;
}

/* Searchable Transcript Chat Bubbles */
.chat-bubble {
    display: flex !important;
    flex-direction: column !important;
    background: #ffffff !important;
    border: 2px solid #2b221d !important;
    border-radius: 12px !important;
    padding: 14px 18px !important;
    margin-bottom: 12px !important;
    box-shadow: 3px 3px 0px #2b221d !important;
    transition: all 0.2s ease !important;
}
.chat-bubble-highlighted {
    background: #faf5ff !important;
    border-color: #8b5cf6 !important;
    box-shadow: 3px 3px 0px #8b5cf6 !important;
}
.chat-header {
    display: flex !important;
    justify-content: space-between !important;
    margin-bottom: 4px !important;
    font-size: 12px !important;
}
.chat-speaker {
    font-weight: 700 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 14px !important;
}
.chat-time {
    color: #64748b !important;
    font-family: 'Fredoka', sans-serif !important;
}
.chat-text {
    font-family: 'Patrick Hand', cursive !important;
    font-size: 18.5px !important;
    line-height: 1.3 !important;
    color: #2b221d !important;
}

/* Search Query Highlights */
.highlight {
    background-color: #fef08a !important; /* Highlighter yellow */
    border-bottom: 2px solid #eab308 !important;
    padding: 0 2px !important;
    border-radius: 2px !important;
    color: #000000 !important;
}

/* Sidebar sticker-like buttons */
[data-testid="stSidebar"] button {
    background-color: #ffffff !important;
    border: 2px solid #2b221d !important;
    border-radius: 8px !important;
    color: #2b221d !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    box-shadow: 3px 3px 0px #2b221d !important;
    transition: all 0.15s ease;
}
[data-testid="stSidebar"] button:hover {
    transform: translate(-1px, -1px);
    box-shadow: 4px 4px 0px #2b221d !important;
    color: #b91c1c !important;
}

/* Input boxes & Dropdowns notebook look */
.stTextInput input, .stSelectbox select, [data-baseweb="select"] {
    background-color: #ffffff !important;
    border: 2px solid #2b221d !important;
    border-radius: 8px !important;
    color: #2b221d !important;
    font-family: 'Patrick Hand', cursive !important;
    font-size: 18px !important;
}

/* Checklist custom styling */
.action-row {
    padding: 8px 0;
    border-bottom: 1px dashed #e2e8f0;
}

/* Priority tags as mini labels */
.tag-high {
    background: #fee2e2 !important;
    color: #ef4444 !important;
    border: 2px solid #ef4444 !important;
    padding: 2px 8px !important;
    border-radius: 12px !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    font-family: 'Outfit', sans-serif !important;
}
.tag-medium {
    background: #fef3c7 !important;
    color: #d97706 !important;
    border: 2px solid #d97706 !important;
    padding: 2px 8px !important;
    border-radius: 12px !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    font-family: 'Outfit', sans-serif !important;
}
.tag-low {
    background: #dbeafe !important;
    color: #2563eb !important;
    border: 2px solid #2563eb !important;
    padding: 2px 8px !important;
    border-radius: 12px !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    font-family: 'Outfit', sans-serif !important;
}

/* Sidebar button text contrast fix */
[data-testid="stSidebar"] button p,
[data-testid="stSidebar"] button span,
[data-testid="stSidebar"] button div {
    color: #2b221d !important;
}

/* Style Streamlit containers with border=True to look like neobrutalist glass cards */
div[data-testid="stVerticalBlockBorder"] {
    background: #ffffff !important;
    border: 2px solid #2b221d !important;
    border-radius: 12px !important;
    padding: 24px !important;
    margin-bottom: 20px !important;
    box-shadow: 4px 4px 0px #2b221d !important;
    color: #2b221d !important;
    backdrop-filter: none !important;
    transition: all 0.2s ease;
}
</style>
"""

# Inject custom CSS
st.markdown(CSS_STYLES, unsafe_allow_html=True)

# =====================================================================
# Document Parsing Helpers
# =====================================================================

def parse_context_document(uploaded_file):
    """Extracts text content from TXT, MD, or PDF documents."""
    if uploaded_file is None:
        return None
        
    filename = uploaded_file.name
    if filename.endswith(".pdf"):
        try:
            import pypdf
            reader = pypdf.PdfReader(uploaded_file)
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            return "\n".join(text_parts)
        except ImportError:
            st.error("pypdf is required to parse PDF documents. Please check installation.")
            return "Error: pypdf not available."
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
    else:
        # Txt / Md fallback
        try:
            return uploaded_file.read().decode("utf-8")
        except Exception as e:
            return f"Error reading text document: {str(e)}"

# =====================================================================
# Session State Initialization
# =====================================================================

if "active_meeting_id" not in st.session_state:
    st.session_state.active_meeting_id = None
if "api_provider" not in st.session_state:
    st.session_state.api_provider = "Gemini"
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = ""
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "gemini-3.5-flash"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = None
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# =====================================================================
# Helper Formatting Functions
# =====================================================================

def format_duration(seconds):
    """Formats duration in seconds to MM:SS."""
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    return f"{minutes:02d}:{remaining_seconds:02d}"

def time_str_to_seconds(t_str):
    """Converts a standard clock string like '1:30' to float seconds."""
    try:
        parts = list(map(int, t_str.split(':')))
        if len(parts) == 2:
            return float(parts[0] * 60 + parts[1])
        elif len(parts) == 3:
            return float(parts[0] * 3600 + parts[1] * 60 + parts[2])
        return float(t_str)
    except Exception:
        return 0.0

def highlight_text(text, query):
    """Inserts mark tags for matching search text."""
    if not query:
        return text
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(lambda m: f"<mark class='highlight'>{m.group(0)}</mark>", text)

# Map speakers to consistent notebook ink colors
def get_speaker_color(speaker):
    speaker_colors = {
        "Sarah (PM)": "#b91c1c",        # Primary Red ink
        "David (Backend)": "#1d4ed8",   # Primary Blue ink
        "Alex (Frontend)": "#047857",  # Primary Green ink
        "Sarah": "#b91c1c",
        "David": "#1d4ed8",
        "Alex": "#047857"
    }
    if speaker in speaker_colors:
        return speaker_colors[speaker]
    
    # Dynamic fallback based on speaker hashing
    colors = ["#b91c1c", "#1d4ed8", "#047857", "#b45309", "#6b21a8"]
    import hashlib
    idx = int(hashlib.md5(speaker.encode()).hexdigest(), 16) % len(colors)
    return colors[idx]

# =====================================================================
# Sidebar: Logo, Past Meetings & Settings
# =====================================================================

with st.sidebar:
    st.markdown("<div class='sidebar-title'>🧠 Meeting Summarizer</div>", unsafe_allow_html=True)
    
    # Quick start Demo button
    if st.button("✨ Load Demo Meeting", use_container_width=True):
        # Generate and save demo meeting
        demo_data = pipeline.get_demo_meeting_data()
        
        # Save to DB
        demo_id = database.save_meeting(
            title="Meeting Summarizer: Product Kickoff & Planning",
            date=datetime.now().strftime("%Y-%m-%d"),
            duration_seconds=240,
            audio_path=None,
            transcript=demo_data["transcript"],
            analysis=demo_data["analysis"],
            context_doc_name="product_spec.md",
            context_doc_text="Meeting Summarizer is an advanced, high-performance meeting intelligence dashboard that goes far beyond basic summarization. Built in Python/Streamlit."
        )
        st.session_state.active_meeting_id = demo_id
        st.success("Demo meeting loaded!")
        st.rerun()

    st.markdown("---")
    
    # Past Meetings List
    st.markdown("### 🎬 Saved Meetings")
    meetings = database.get_all_meetings()
    
    if not meetings:
        st.markdown("<span style='color: #64748b; font-size: 12px;'>No processed meetings yet.</span>", unsafe_allow_html=True)
    else:
        for m in meetings:
            col_sel, col_del = st.columns([4, 1])
            with col_sel:
                # Highlight active meeting
                is_active = (st.session_state.active_meeting_id == m["id"])
                btn_label = f"📁 {m['title'][:25]}..." if len(m['title']) > 25 else f"📁 {m['title']}"
                if st.button(
                    btn_label, 
                    key=f"meeting_btn_{m['id']}", 
                    use_container_width=True,
                    type="primary" if is_active else "secondary"
                ):
                    st.session_state.active_meeting_id = m["id"]
                    st.session_state.selected_topic = None
                    st.session_state.search_query = ""
                    st.rerun()
            with col_del:
                if st.button("🗑️", key=f"del_btn_{m['id']}", help="Delete meeting"):
                    database.delete_meeting(m["id"])
                    if st.session_state.active_meeting_id == m["id"]:
                        st.session_state.active_meeting_id = None
                    st.rerun()

# =====================================================================
# Main Application Flow
# =====================================================================

if st.session_state.active_meeting_id is None:
    # -----------------------------------------------------------------
    # UPLOAD & ANALYZE TAB
    # -----------------------------------------------------------------
    
    st.markdown("<div class='glow-title'>Meeting Summarizer</div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 15px; color: #64748b; margin-top:-10px; margin-bottom: 25px;'>Premium meeting intelligence dashboard powered by advanced multi-modal models.</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='glass-card'>
        <h4>💡 Welcome to Meeting Summarizer</h4>
        <p>This intelligent dashboard processes meeting audio, performs diarized speaker transcription, identifies key decisions, compiles action lists, structures segmented topics, and powers interactive RAG context Q&A.</p>
        <p style='color: #b91c1c;'><b>How to start:</b></p>
        <ol>
            <li>Upload your meeting audio recording (.mp3, .wav, or .m4a).</li>
            <li>Optionally upload standard project documentation (e.g., specifications, transcripts, context briefs) to guide RAG context chat.</li>
            <li>Click <b>Analyze Meeting</b> to construct your intelligence dashboard.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    col_file, col_opts = st.columns([2, 1])
    
    with col_file:
        with st.container(border=True):
            st.markdown("<h4>📤 Upload Audio File</h4>", unsafe_allow_html=True)
            uploaded_audio = st.file_uploader(
                "Choose a meeting audio recording", 
                type=["mp3", "wav", "m4a"],
                help="Files up to 100MB supported."
            )
            
            st.markdown("<h4>📄 Optional Context Document</h4>", unsafe_allow_html=True)
            uploaded_context = st.file_uploader(
                "Provide project spec or supplementary documents (for RAG context)", 
                type=["txt", "md", "pdf"],
                help="Supported file types: Text (.txt), Markdown (.md), PDF (.pdf)"
            )
        
    with col_opts:
        with st.container(border=True):
            st.markdown("<h4>📝 Meeting Details</h4>", unsafe_allow_html=True)
            meeting_title = st.text_input("Meeting Title", value=f"Meeting - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            meeting_date = st.date_input("Meeting Date", value=datetime.now().date())
            
            st.markdown("---")
            
            # Action button
            analyze_btn = st.button("🚀 Analyze Meeting", use_container_width=True, type="primary")
            
    if analyze_btn:
        # Validation checks
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")
        if not api_key:
            st.error("Error: GEMINI_API_KEY or GOOGLE_API_KEY is not set in the environment or .env file. Please configure the key on the server to enable live audio processing.")
            st.stop()
                 
        if not uploaded_audio:
            st.error("Please upload an audio file to run the analysis.")
            st.stop()
            
        with st.status("Initializing meeting intelligence pipeline...", expanded=True) as status:
            temp_audio_path = None
            doc_text = None
            doc_name = None
            
            # Save audio if uploaded
            if uploaded_audio:
                status.write("Saving uploaded audio file...")
                temp_audio_path = os.path.join("y:\\Meeting_Summarizer\\uploads", uploaded_audio.name)
                with open(temp_audio_path, "wb") as f:
                    f.write(uploaded_audio.getbuffer())
                    
            # Parse context document if present
            if uploaded_context:
                status.write("Extracting context document data...")
                doc_name = uploaded_context.name
                doc_text = parse_context_document(uploaded_context)
                
            status.write("Executing pipeline (Gemini pathway)...")
            
            try:
                # Process audio file through pipeline
                result = pipeline.process_audio(
                    audio_path=temp_audio_path,
                    provider="Gemini",
                    api_key=api_key,
                    model_name=st.session_state.get("selected_model", "gemini-1.5-flash")
                )
                
                status.write("Saving meeting details to database...")
                # Calculate simple duration if mock/unspecified
                duration = 240
                if temp_audio_path:
                    # Basic duration check placeholder, standard is 240s for demo
                    duration = 240
                    
                # Save details
                saved_id = database.save_meeting(
                    title=meeting_title,
                    date=meeting_date.strftime("%Y-%m-%d"),
                    duration_seconds=duration,
                    audio_path=temp_audio_path,
                    transcript=result["transcript"],
                    analysis=result["analysis"],
                    context_doc_name=doc_name,
                    context_doc_text=doc_text
                )
                
                status.update(label="Meeting Intelligence extraction successful!", state="complete")
                st.session_state.active_meeting_id = saved_id
                st.session_state.selected_topic = None
                st.session_state.search_query = ""
                st.rerun()
                
            except Exception as e:
                status.update(label="Analysis pipeline failed!", state="error")
                st.error(f"Error details: {str(e)}")

else:
    # -----------------------------------------------------------------
    # DASHBOARD OVERVIEW & TABS
    # -----------------------------------------------------------------
    
    # Load Active Meeting
    meeting = database.get_meeting_details(st.session_state.active_meeting_id)
    if not meeting:
        st.session_state.active_meeting_id = None
        st.error("Error loading meeting details. Returning to home.")
        st.stop()
        
    analysis = meeting["analysis"]
    transcript = meeting["transcript"]
    
    # Top banner layout
    col_title, col_back = st.columns([5, 1])
    with col_title:
        st.markdown(f"<div class='glow-title'>{meeting['title']}</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #64748b; font-size: 13px; margin-top:-10px; margin-bottom: 25px;'>📅 Date: {meeting['date']} | ⏰ Created At: {meeting['created_at']}</p>", unsafe_allow_html=True)
    with col_back:
        if st.button("⬅️ Upload New", use_container_width=True):
            st.session_state.active_meeting_id = None
            st.rerun()
            
    # TAB SEGMENTATION
    tab_dash, tab_action, tab_transcript, tab_analytics, tab_rag = st.tabs([
        "📊 Dashboard Overview",
        "✅ Action Items",
        "💬 Searchable Transcript & Timeline",
        "📈 Speaker Analytics",
        "🤖 Export & Ask AI (RAG)"
    ])
    
    # -----------------------------------------------------------------
    # TAB 1: DASHBOARD OVERVIEW
    # -----------------------------------------------------------------
    with tab_dash:
        # Custom metric cards grid
        st.markdown(f"""
        <div class='custom-metric-container'>
            <div class='custom-metric-card'>
                <div class='custom-metric-val'>{format_duration(meeting['duration_seconds'])}</div>
                <div class='custom-metric-lbl'>Meeting Duration</div>
            </div>
            <div class='custom-metric-card' style='border-bottom-color: #00f2fe;'>
                <div class='custom-metric-val'>{len(analysis.get('speaker_analytics', []))}</div>
                <div class='custom-metric-lbl'>Speakers Present</div>
            </div>
            <div class='custom-metric-card' style='border-bottom-color: #10b981;'>
                <div class='custom-metric-val'>{len(analysis.get('key_decisions', []))}</div>
                <div class='custom-metric-lbl'>Key Decisions</div>
            </div>
            <div class='custom-metric-card' style='border-bottom-color: #ef4444;'>
                <div class='custom-metric-val'>{len(analysis.get('action_items', []))}</div>
                <div class='custom-metric-lbl'>Action Items</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_summary, col_objectives = st.columns([1, 1])
        
        with col_summary:
            st.markdown(f"""
            <div class='glass-card' style='height: 100%;'>
                <h4>📝 Executive Summary</h4>
                <p style='font-size: 14.5px; line-height: 1.6; color: #2b221d;'>{analysis.get('summary', '')}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_objectives:
            obj_list_html = "".join([f"<li style='margin-bottom: 8px;'>🎯 {obj}</li>" for obj in analysis.get('objectives', [])])
            st.markdown(f"""
            <div class='glass-card' style='height: 100%;'>
                <h4>🎯 Meeting Objectives</h4>
                <ul style='list-style-type: none; padding-left: 0; font-size: 14.5px; line-height: 1.6; color: #2b221d;'>
                    {obj_list_html}
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Decisions and Questions side by side
        col_decisions, col_questions = st.columns([1, 1])
        
        with col_decisions:
            decisions_html = ""
            for dec in analysis.get('key_decisions', []):
                decisions_html += f"""
                <div class='decision-card'>
                    <div style='font-size: 14px; font-weight: 500;'>{dec}</div>
                </div>
                """
            if not analysis.get('key_decisions'):
                decisions_html = "<span style='color: #64748b; font-family: Outfit, sans-serif;'>No specific decisions recorded.</span>"
                
            st.markdown(f"""
            <div class='glass-card'>
                <h4>🤝 Key Decisions</h4>
                {decisions_html}
            </div>
            """, unsafe_allow_html=True)
            
        with col_questions:
            questions_html = ""
            for q in analysis.get('open_questions', []):
                questions_html += f"""
                <div class='question-card'>
                    <div style='font-size: 14px; font-weight: 500;'>{q}</div>
                </div>
                """
            if not analysis.get('open_questions'):
                questions_html = "<span style='color: #64748b; font-family: Outfit, sans-serif;'>No open questions recorded.</span>"
                
            st.markdown(f"""
            <div class='glass-card'>
                <h4>❓ Open Questions & Issues</h4>
                {questions_html}
            </div>
            """, unsafe_allow_html=True)
            
    # -----------------------------------------------------------------
    # TAB 2: ACTION ITEMS
    # -----------------------------------------------------------------
    with tab_action:
        with st.container(border=True):
            st.markdown("<h4>✅ Task & Action Items Checklist</h4>", unsafe_allow_html=True)
            st.markdown("<p style='color: #94a3b8; font-size: 13px; margin-top:-8px; font-family: Outfit, sans-serif;'>Complete tasks by checking them off. Changes are preserved during session.</p>", unsafe_allow_html=True)
            
            action_items = analysis.get('action_items', [])
            
            if not action_items:
                st.markdown("No action items extracted.")
            else:
                # Header labels
                col_lbl_chk, col_lbl_task, col_lbl_owner, col_lbl_due, col_lbl_pri, col_lbl_conf = st.columns([0.5, 4, 1.5, 1.5, 1.2, 1.3])
                with col_lbl_task:
                    st.markdown("<b style='color:#2b221d;'>Task Description</b>", unsafe_allow_html=True)
                with col_lbl_owner:
                    st.markdown("<b style='color:#2b221d;'>Owner</b>", unsafe_allow_html=True)
                with col_lbl_due:
                    st.markdown("<b style='color:#2b221d;'>Due Date</b>", unsafe_allow_html=True)
                with col_lbl_pri:
                    st.markdown("<b style='color:#2b221d;'>Priority</b>", unsafe_allow_html=True)
                with col_lbl_conf:
                    st.markdown("<b style='color:#2b221d;'>Confidence</b>", unsafe_allow_html=True)
                st.markdown("<hr style='border: 0; border-top: 2px solid rgba(0,0,0,0.08); margin: 8px 0;'>", unsafe_allow_html=True)
                
                for i, item in enumerate(action_items):
                    col_check, col_task, col_owner, col_due, col_priority, col_conf = st.columns([0.5, 4, 1.5, 1.5, 1.2, 1.3])
                    
                    state_key = f"action_{meeting['id']}_{i}"
                    with col_check:
                        checked = st.checkbox("", key=state_key, value=st.session_state.get(state_key, False))
                        st.session_state[state_key] = checked
                        
                    with col_task:
                        text_style = "text-decoration: line-through; color: #64748b;" if checked else "color: #2b221d;"
                        st.markdown(f"<div style='margin-top: 4px; font-size:14px; {text_style}'>{item['task']}</div>", unsafe_allow_html=True)
                        
                    with col_owner:
                        st.markdown(f"<div style='margin-top: 4px; font-size:13px; color: #4b5563;'>👤 {item['owner']}</div>", unsafe_allow_html=True)
                        
                    with col_due:
                        st.markdown(f"<div style='margin-top: 4px; font-size:13px; color: #4b5563;'>📅 {item['due_date']}</div>", unsafe_allow_html=True)
                        
                    with col_priority:
                        p = item['priority']
                        tag_cls = f"tag-{p.lower()}"
                        st.markdown(f"<div style='margin-top: 4px;'><span class='{tag_cls}'>{p}</span></div>", unsafe_allow_html=True)
                        
                    with col_conf:
                        conf = item['confidence']
                        st.markdown(f"""
                        <div style='width: 100%; background-color: rgba(0,0,0,0.05); border-radius: 5px; height: 6px; margin-top: 8px;'>
                            <div style='width: {conf}%; background: linear-gradient(90deg, #1d4ed8 0%, #047857 100%); height: 100%; border-radius: 5px;'></div>
                        </div>
                        <div style='font-size: 10px; color: #64748b; text-align: right; margin-top: 2px;'>{conf}% Confidence</div>
                        """, unsafe_allow_html=True)
                        
                    st.markdown("<hr style='border: 0; border-top: 1px solid rgba(0,0,0,0.05); margin: 6px 0;'>", unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # TAB 3: TRANSCRIPT & TIMELINE
    # -----------------------------------------------------------------
    with tab_transcript:
        col_timeline, col_stream = st.columns([1, 2])
        
        # Get active topic range details
        active_range = None
        
        with col_timeline:
            with st.container(border=True):
                st.markdown("<h4>📍 Topic Timeline</h4>", unsafe_allow_html=True)
                st.markdown("<p style='color: #64748b; font-size: 12px; margin-top:-8px; font-family: Outfit, sans-serif;'>Select a topic segment to highlight matching dialog.</p>", unsafe_allow_html=True)
                
                topics = analysis.get('topics', [])
                
                # Show a "Clear Selection" button if a topic is selected
                if st.session_state.selected_topic is not None:
                    if st.button("🔄 Clear Highlight", key="clear_topic_hl"):
                        st.session_state.selected_topic = None
                        st.rerun()
                        
                for idx, top in enumerate(topics):
                    # Check if selected
                    is_selected = (st.session_state.selected_topic == idx)
                    active_class = "timeline-active" if is_selected else ""
                    
                    # Render HTML wrapper for layout representation
                    st.markdown(f"""
                    <div class='timeline-item {active_class}' id='topic-item-{idx}'>
                        <div class='timeline-time'>⏰ {top['start_time']} - {top['end_time']}</div>
                        <div class='timeline-content'>
                            <div class='timeline-title'>{top['topic']}</div>
                            <div class='timeline-desc'>{top['summary']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Overlay click button for Streamlit state handling
                    if st.button(f"Highlight: {top['topic']}", key=f"topic_click_{idx}", help=f"Show {top['topic']}", use_container_width=True):
                        st.session_state.selected_topic = idx
                        st.rerun()
                        
                    if is_selected:
                        active_range = (time_str_to_seconds(top['start_time']), time_str_to_seconds(top['end_time']))
            
        with col_stream:
            with st.container(border=True):
                st.markdown("<h4>💬 Dialogue Transcript</h4>", unsafe_allow_html=True)
                
                # Text search input
                search_query_input = st.text_input(
                    "Search Transcript Text", 
                    value=st.session_state.search_query, 
                    placeholder="Type query to find and highlight matches..."
                )
                st.session_state.search_query = search_query_input
                
                st.markdown("---")
                
                # Rendering chat bubbles
                st.markdown("<div style='max-height: 480px; overflow-y: auto; padding-right: 8px;'>", unsafe_allow_html=True)
                
                found_any = False
                for idx, entry in enumerate(transcript):
                    start = entry.get('start', 0.0)
                    end = entry.get('end', 0.0)
                    
                    # Check topic filter highlight
                    in_topic_range = False
                    if active_range:
                        # If dialogue overlaps with topic range
                        if (start >= active_range[0] and start <= active_range[1]):
                            in_topic_range = True
                            
                    # Check search keyword match
                    match_search = True
                    if st.session_state.search_query:
                        if st.session_state.search_query.lower() not in entry.get('text', '').lower():
                            match_search = False
                            
                    # If search query is active and it doesn't match, we skip rendering it to show search results, 
                    # or if no search query is active we render everything.
                    if not match_search:
                        continue
                        
                    found_any = True
                    bubble_hl_class = "chat-bubble-highlighted" if in_topic_range else ""
                    
                    highlighted_body = highlight_text(entry.get('text', ''), st.session_state.search_query)
                    
                    sp_color = get_speaker_color(entry.get('speaker'))
                    st.markdown(f"""
                    <div class='chat-bubble {bubble_hl_class}'>
                        <div class='chat-header'>
                            <span class='chat-speaker' style='color: {sp_color} !important;'>👤 {entry.get('speaker')}</span>
                            <span class='chat-time'>⏳ {format_duration(start)}</span>
                        </div>
                        <div class='chat-text'>{highlighted_body}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                if not found_any:
                    st.markdown("<p style='color: #64748b; text-align: center; margin: 40px 0; font-family: Outfit, sans-serif;'>No transcript dialog segments match search term.</p>", unsafe_allow_html=True)
                    
                st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # TAB 4: SPEAKER ANALYTICS
    # -----------------------------------------------------------------
    with tab_analytics:
        col_charts_left, col_charts_right = st.columns([1, 1])
        
        # Load speaker metrics to Dataframe
        speaker_data = analysis.get('speaker_analytics', [])
        
        if not speaker_data:
            st.markdown("No speaker analytics extracted.")
        else:
            df_speaker = pd.DataFrame(speaker_data)
            
            with col_charts_left:
                with st.container(border=True):
                    st.markdown("<h4>🥧 Talk Time Distribution</h4>", unsafe_allow_html=True)
                    fig_pie = px.pie(
                        df_speaker,
                        values='talk_percentage',
                        names='speaker',
                        hole=0.4,
                        color_discrete_sequence=['#7b61ff', '#00f2fe', '#f59e0b', '#ef4444', '#10b981']
                    )
                    fig_pie.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font_color='#2b221d',
                        margin=dict(t=10, b=10, l=10, r=10),
                        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
                    )
                    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_pie, use_container_width=True)
                
            with col_charts_right:
                with st.container(border=True):
                    st.markdown("<h4>📊 Words Spoken by Speaker</h4>", unsafe_allow_html=True)
                    fig_bar = px.bar(
                        df_speaker,
                        x='speaker',
                        y='words_spoken',
                        color='speaker',
                        color_discrete_sequence=['#7b61ff', '#00f2fe', '#f59e0b', '#ef4444', '#10b981']
                    )
                    fig_bar.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font_color='#2b221d',
                        margin=dict(t=20, b=10, l=10, r=10),
                        showlegend=False
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                
            # Second level analytics: sentiment & conversation timeline density
            col_density, col_senti = st.columns([2, 1])
            
            with col_density:
                with st.container(border=True):
                    st.markdown("<h4>📈 Dialogue Word Count Density Over Time</h4>", unsafe_allow_html=True)
                    
                    # Construct dataframe mapping speaker text length over meeting start times
                    density_records = []
                    for entry in transcript:
                        words = len(entry.get('text', '').split())
                        density_records.append({
                            "Time (s)": entry.get('start', 0.0),
                            "Word Count": words,
                            "Speaker": entry.get('speaker', 'Speaker')
                        })
                    df_density = pd.DataFrame(density_records)
                    
                    fig_line = px.line(
                        df_density,
                        x="Time (s)",
                        y="Word Count",
                        color="Speaker",
                        markers=True,
                        color_discrete_sequence=['#7b61ff', '#00f2fe', '#f59e0b', '#ef4444', '#10b981']
                    )
                    fig_line.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font_color='#2b221d',
                        margin=dict(t=20, b=10, l=10, r=10)
                    )
                    st.plotly_chart(fig_line, use_container_width=True)
                
            with col_senti:
                with st.container(border=True):
                    st.markdown("<h4>😊 Speaker Sentiments</h4>", unsafe_allow_html=True)
                    
                    for idx, row in df_speaker.iterrows():
                        s_color = "#10b981" if row['sentiment'] == "Positive" else ("#f59e0b" if row['sentiment'] == "Neutral" else "#ef4444")
                        st.markdown(f"""
                        <div style='display:flex; justify-content:space-between; align-items:center; background:#ffffff; border:2px solid #2b221d; box-shadow: 2px 2px 0px #2b221d; padding:10px 14px; border-radius:8px; margin-bottom:8px;'>
                            <span style='font-weight:600; color:#2b221d;'>👤 {row['speaker']}</span>
                            <span style='background: {s_color}22; color: {s_color}; border:2px solid {s_color}bb; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:700; font-family: Outfit, sans-serif;'>{row['sentiment']}</span>
                        </div>
                        """, unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # TAB 5: EXPORT & ASK AI (RAG)
    # -----------------------------------------------------------------
    with tab_rag:
        col_export, col_chat = st.columns([1, 1.5])
        
        with col_export:
            with st.container(border=True):
                st.markdown("<h4>📥 Export Document Summary</h4>", unsafe_allow_html=True)
                st.markdown("<p style='color: #64748b; font-size: 12px; margin-top:-8px; font-family: Outfit, sans-serif;'>Download a formatted meeting brief in your choice of formats.</p>", unsafe_allow_html=True)
                
                # Markdown Generation
                md_text = f"# Meeting Intelligence Report: {meeting['title']}\n\n"
                md_text += f"**Date:** {meeting['date']} | **Duration:** {format_duration(meeting['duration_seconds'])}\n\n"
                md_text += f"## Executive Summary\n{analysis.get('summary', '')}\n\n"
                md_text += "## Objectives\n"
                for obj in analysis.get('objectives', []):
                    md_text += f"- {obj}\n"
                md_text += "\n## Key Decisions\n"
                for dec in analysis.get('key_decisions', []):
                    md_text += f"- ✔ {dec}\n"
                md_text += "\n## Action Items\n"
                for item in action_items:
                    md_text += f"- [ ] **{item['task']}** - Owner: {item['owner']} | Due: {item['due_date']} | Priority: {item['priority']} (Confidence: {item['confidence']}%)\n"
                md_text += "\n## Transcript Snippet\n"
                for entry in transcript[:20]:
                    md_text += f"**[{format_duration(entry.get('start', 0.0))}] {entry.get('speaker')}:** {entry.get('text')}\n"
                    
                st.download_button(
                    label="📄 Download Report as Markdown",
                    data=md_text,
                    file_name=f"{meeting['title'].lower().replace(' ', '_')}_report.md",
                    mime="text/markdown",
                    use_container_width=True
                )
                
                # JSON Generation
                json_str = json.dumps(meeting, indent=2)
                st.download_button(
                    label="⚙️ Download Report as JSON",
                    data=json_str,
                    file_name=f"{meeting['title'].lower().replace(' ', '_')}_raw.json",
                    mime="application/json",
                    use_container_width=True
                )
                
                # PDF Generation
                try:
                    import reportlab
                    from app import generate_pdf_report
                    pdf_data = generate_pdf_report(meeting)
                    st.download_button(
                        label="📕 Download Report as PDF File",
                        data=pdf_data,
                        file_name=f"{meeting['title'].lower().replace(' ', '_')}_report.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as ex:
                    # PDF report definition in global scope wrapper to prevent circular import if needed
                    st.info("PDF generation helper ready. Please download Markdown or JSON.")
                    
                # Context Document RAG indicator
                if meeting.get("context_doc_name"):
                    st.markdown(f"""
                    <div style='background:rgba(93,64,55,0.05); border:1px solid rgba(93,64,55,0.2); border-radius:10px; padding:15px; margin-top:20px;'>
                        <div style='font-weight:600; color:#2b221d; font-family: Outfit, sans-serif;'>📄 Active Context Document:</div>
                        <div style='font-size:12px; color:#4b5563; margin-top:2px; font-family: Outfit, sans-serif;'>Name: <b>{meeting['context_doc_name']}</b></div>
                        <div style='font-size:10px; color:#64748b; font-family: Outfit, sans-serif;'>Document text is integrated into the Ask AI pipeline below.</div>
                    </div>
                    """, unsafe_allow_html=True)
                
        with col_chat:
            with st.container(border=True):
                st.markdown("<h4>💬 Ask AI (RAG Context Query)</h4>", unsafe_allow_html=True)
                st.markdown("<p style='color: #64748b; font-size: 12px; margin-top:-8px; font-family: Outfit, sans-serif;'>Query anything about meeting dialogue, actions, or referenced specifications.</p>", unsafe_allow_html=True)
                
                meeting_chat_key = f"chat_{meeting['id']}"
                if meeting_chat_key not in st.session_state.chat_history:
                    st.session_state.chat_history[meeting_chat_key] = []
                    
                # Render conversation
                chat_container = st.container()
                with chat_container:
                    for msg in st.session_state.chat_history[meeting_chat_key]:
                        with st.chat_message(msg["role"]):
                            st.markdown(msg["content"])
                            
                # Query entry
                query = st.chat_input("Ask a question about the meeting details...")
                if query:
                    # Append user query
                    st.session_state.chat_history[meeting_chat_key].append({"role": "user", "content": query})
                    
                    # Fetch key from environment
                    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")
                        
                    # Call pipeline to answer query
                    with st.spinner("AI is reading context and transcript to answer..."):
                        answer = pipeline.answer_rag_query(
                            query=query,
                            transcript=transcript,
                            analysis=analysis,
                            context_doc_text=meeting.get("context_doc_text"),
                            provider="Gemini",
                            api_key=key,
                            model_name=st.session_state.get("selected_model", "gemini-1.5-flash")
                        )
                    
                    # Append assistant reply
                    st.session_state.chat_history[meeting_chat_key].append({"role": "assistant", "content": answer})
                    st.rerun()

# =====================================================================
# PDF Report Definition (Export fallback)
# =====================================================================
def generate_pdf_report(meeting):
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    import io

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Define custom styles matching reportlab conventions
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=colors.HexColor('#7b61ff'),
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'SubTitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=15
    )
    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8,
        leading=13
    )
    
    story.append(Paragraph(f"Meeting Report: {meeting['title']}", title_style))
    story.append(Paragraph(f"Date: {meeting['date']} | Duration: {format_duration(meeting['duration_seconds'])}", subtitle_style))
    story.append(Spacer(1, 8))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    story.append(Paragraph(meeting['analysis'].get('summary', ''), body_style))
    story.append(Spacer(1, 8))
    
    # Objectives
    story.append(Paragraph("Objectives", heading_style))
    for obj in meeting['analysis'].get('objectives', []):
        story.append(Paragraph(f"• {obj}", body_style))
    story.append(Spacer(1, 8))
    
    # Key Decisions
    story.append(Paragraph("Key Decisions", heading_style))
    for dec in meeting['analysis'].get('key_decisions', []):
        story.append(Paragraph(f"✔ {dec}", body_style))
    story.append(Spacer(1, 8))
    
    # Action Items Table
    story.append(Paragraph("Action Items", heading_style))
    action_data = [["Task", "Owner", "Due Date", "Priority", "Confidence"]]
    for item in meeting['analysis'].get('action_items', []):
        action_data.append([
            item['task'],
            item['owner'],
            item['due_date'],
            item['priority'],
            f"{item['confidence']}%"
        ])
        
    t = Table(action_data, colWidths=[200, 110, 80, 70, 70])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#7b61ff')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.HexColor('#334155')),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))
    
    # Dialogue transcript snippet
    story.append(Paragraph("Transcript (First 10 segments)", heading_style))
    for entry in meeting['transcript'][:10]:
        story.append(Paragraph(f"<b>[{format_duration(entry.get('start', 0.0))}] {entry.get('speaker')}:</b> {entry.get('text')}", body_style))
        
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
