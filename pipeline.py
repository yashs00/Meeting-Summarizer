import os
import time
import json
from pydantic import BaseModel, Field
from typing import List, Optional
import google.generativeai as genai
from openai import OpenAI

# =====================================================================
# Pydantic Schemas for Structured Output
# =====================================================================

class ActionItem(BaseModel):
    task: str = Field(description="The concrete task to be performed.")
    owner: str = Field(description="The person responsible for this task.")
    due_date: str = Field(description="The due date or timeframe for this task.")
    priority: str = Field(description="Priority: 'High', 'Medium', or 'Low'")
    confidence: int = Field(description="Confidence score between 0 and 100.")

class Topic(BaseModel):
    topic: str = Field(description="The name of the discussion topic.")
    summary: str = Field(description="A brief summary of what was discussed.")
    start_time: str = Field(description="Start timestamp (e.g., '0:00' or '2:15').")
    end_time: str = Field(description="End timestamp (e.g., '1:30' or '3:45').")

class SpeakerAnalytic(BaseModel):
    speaker: str = Field(description="Name of the speaker.")
    words_spoken: int = Field(description="Total word count spoken by this speaker.")
    talk_percentage: float = Field(description="Percentage of total speaking time/words.")
    sentiment: str = Field(description="Overall sentiment: 'Positive', 'Neutral', or 'Negative'")

class DialogueEntry(BaseModel):
    speaker: str = Field(description="Name of the speaker.")
    text: str = Field(description="The text spoken by the speaker.")
    start: float = Field(description="Start time in seconds.")
    end: float = Field(description="End time in seconds.")

class MeetingAnalysis(BaseModel):
    summary: str = Field(description="3-5 sentence executive summary of the meeting.")
    objectives: List[str] = Field(description="Core goals/objectives of the meeting.")
    key_decisions: List[str] = Field(description="List of explicit decisions made.")
    action_items: List[ActionItem] = Field(description="List of action items with details.")
    open_questions: List[str] = Field(description="List of unresolved questions or open issues.")
    topics: List[Topic] = Field(description="Topic segmentation with timestamps.")
    speaker_analytics: List[SpeakerAnalytic] = Field(description="Analytics per speaker.")

class PipelineResult(BaseModel):
    transcript: List[DialogueEntry] = Field(description="List of speaker-separated dialogue entries.")
    analysis: MeetingAnalysis = Field(description="Extracted meeting intelligence report.")

# =====================================================================
# Demo Data Generator
# =====================================================================

def get_demo_meeting_data():
    """Returns a highly detailed mock PipelineResult dataset for local testing/grading."""
    transcript = [
        {"speaker": "Sarah (PM)", "text": "Good morning team. Welcome to the kickoff for Meeting Summarizer. Today we need to align on the core components, our database schema, and finalize the timeline for our first MVP release.", "start": 0.0, "end": 15.0},
        {"speaker": "David (Backend)", "text": "Thanks Sarah. On the backend, I've designed the SQLite schema. We'll store meetings, transcripts, and analysis in JSON format. I also evaluated Gemini and OpenAI. Gemini is much easier for audio because it handles native transcription and diarization in one go, whereas OpenAI requires Whisper first, then passing transcripts to GPT-4o.", "start": 15.0, "end": 42.0},
        {"speaker": "Sarah (PM)", "text": "That makes sense, David. Let's make sure we support both, but highly recommend Gemini in the sidebar. What about the frontend? Alex, how is the Streamlit interface coming along?", "start": 42.0, "end": 58.0},
        {"speaker": "Alex (Frontend)", "text": "It's looking really clean. I'm injecting custom CSS for a glassmorphic dark theme, with a deep indigo/cyan gradient. I'm also using Outfit as our primary font. I've designed metrics cards, a timeline component, and Plotly charts for speaker analytics. I'll make the action items list interactive so users can check them off directly in the app.", "start": 58.0, "end": 88.0},
        {"speaker": "Sarah (PM)", "text": "I love the interactive checklist idea, Alex. Can we also include a RAG chat interface? Users frequently want to query meetings, like asking what someone said about a specific topic.", "start": 88.0, "end": 105.0},
        {"speaker": "David (Backend)", "text": "Yes, we can build a simple context-retrieval pipeline. Since meeting transcripts are small enough to fit in the LLM's context window, we can just feed the entire transcript and any extra reference documents straight into the prompt. It's fast, cheap, and very accurate.", "start": 105.0, "end": 130.0},
        {"speaker": "Sarah (PM)", "text": "Perfect. Let's set the target release date for the MVP. Can we have the prototype ready by next Friday, July 17th?", "start": 130.0, "end": 142.0},
        {"speaker": "Alex (Frontend)", "text": "Next Friday is doable for the frontend if the database and pipeline integration are ready by Tuesday. David, does that work for you?", "start": 142.0, "end": 165.0},
        {"speaker": "David (Backend)", "text": "Yes, I'll have the database operations and the Gemini/OpenAI pipelines wrapped up by Monday evening. That gives us plenty of time to integrate.", "start": 165.0, "end": 185.0},
        {"speaker": "Sarah (PM)", "text": "Excellent. Let's document our key decisions. First, we use SQLite for persistence. Second, we support both Gemini and OpenAI, recommending Gemini. Third, our MVP date is July 17th. I'll take care of updating the project board and sharing the specs with stakeholders.", "start": 185.0, "end": 210.0},
        {"speaker": "Alex (Frontend)", "text": "Sounds great. I'll focus on the custom CSS styling and polished UI elements this weekend.", "start": 210.0, "end": 225.0},
        {"speaker": "Sarah (PM)", "text": "Awesome. Let's wrap up and get to work. Thanks, everyone!", "start": 225.0, "end": 240.0}
    ]
    
    analysis = {
        "summary": "The product team held a kickoff meeting for Meeting Summarizer to align on architecture, UI designs, and milestones. They decided to persist meeting data in SQLite, use Gemini for the backend AI pipeline, and implement a glassmorphic dashboard. The team scheduled the MVP prototype release for next Friday, July 17th.",
        "objectives": [
            "Align on core components and backend architecture.",
            "Establish the database persistence schema.",
            "Finalize the Streamlit frontend layout and visual styles.",
            "Agree on a timeline and release date for the prototype."
        ],
        "key_decisions": [
            "Use SQLite for local meeting metadata and analysis persistence.",
            "Provide dual API support (Gemini and OpenAI) with a preference for Gemini's single-pass pipeline.",
            "Target next Friday, July 17th, 2026 for the MVP prototype release."
        ],
        "action_items": [
            {"task": "Complete SQLite database schema and backend API pipelines", "owner": "David (Backend)", "due_date": "2026-07-13", "priority": "High", "confidence": 95},
            {"task": "Implement custom CSS glassmorphism and main Streamlit tabs", "owner": "Alex (Frontend)", "due_date": "2026-07-14", "priority": "High", "confidence": 90},
            {"task": "Build RAG chat query context logic and file exports", "owner": "David (Backend)", "due_date": "2026-07-15", "priority": "Medium", "confidence": 85},
            {"task": "Update the project board and distribute meeting specs", "owner": "Sarah (PM)", "due_date": "2026-07-11", "priority": "Low", "confidence": 98}
        ],
        "open_questions": [
            "Should we support uploading large audio files (>50MB) via chunked streaming?",
            "How should we represent real-time speaker sentiment fluctuations in the dashboard?"
        ],
        "topics": [
            {"topic": "Introduction & Objectives", "summary": "Kickoff discussion and outline of goals.", "start_time": "0:00", "end_time": "0:15"},
            {"topic": "Backend Architecture", "summary": "Discussion of SQLite storage schema and API performance.", "start_time": "0:15", "end_time": "0:58"},
            {"topic": "Frontend UI & Styling", "summary": "Planning Streamlit glassmorphic theme and Plotly components.", "start_time": "0:58", "end_time": "1:30"},
            {"topic": "Timeline & Action Assignments", "summary": "Finalizing the July 17th MVP milestone and action owners.", "start_time": "1:30", "end_time": "4:00"}
        ],
        "speaker_analytics": [
            {"speaker": "Sarah (PM)", "words_spoken": 142, "talk_percentage": 37.5, "sentiment": "Positive"},
            {"speaker": "David (Backend)", "words_spoken": 128, "talk_percentage": 33.8, "sentiment": "Neutral"},
            {"speaker": "Alex (Frontend)", "words_spoken": 109, "talk_percentage": 28.7, "sentiment": "Positive"}
        ]
    }
    
    return {
        "transcript": transcript,
        "analysis": analysis
    }

# =====================================================================
# AI Pipelines
# =====================================================================

def run_gemini_pipeline(audio_path: str, api_key: str, model_name: str = "gemini-3.5-flash") -> dict:
    """
    Executes the Gemini processing pipeline.
    Reads audio file bytes and sends them inline to transcribe,
    diarize, and perform structured analysis.
    """
    # 1. Configure API
    genai.configure(api_key=api_key)
    
    # 2. Get MIME type
    ext = os.path.splitext(audio_path)[1].lower()
    mime_type = "audio/mp3"
    if ext == ".wav":
        mime_type = "audio/wav"
    elif ext == ".m4a":
        mime_type = "audio/mp4"
        
    # 3. Read raw bytes
    with open(audio_path, "rb") as f:
        audio_data = f.read()
        
    # 4. Generate structured content
    # Define generation config for structured JSON output mapped to Pydantic schema
    generation_config = genai.types.GenerationConfig(
        response_mime_type="application/json",
        response_schema=PipelineResult,
        temperature=0.2
    )
    
    prompt = """
    You are a highly capable AI meeting intelligence agent.
    Your task is to analyze this audio file and return a fully detailed report.
    
    You must:
    1. Transcribe the audio recording, differentiating speakers (Speaker A, Speaker B, etc., or actual names if they introduce themselves or are referred to).
    2. Break the transcript into dialogue entries, specifying the speaker, the exact text spoken, and start/end times in seconds.
    3. Fill in the meeting intelligence report including:
       - An executive summary.
       - Meeting objectives.
       - Key decisions made.
       - Action items with owners, priority, and confidence.
       - Open questions left unanswered.
       - Segmented topics with start and end times.
       - Analytics on each speaker (words spoken, estimated talk percentage, overall sentiment).
       
    Return the result strictly conforming to the JSON schema.
    """
    
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(
        [
            {
                "mime_type": mime_type,
                "data": audio_data
            },
            prompt
        ],
        generation_config=generation_config
    )
    
    result_json = json.loads(response.text)
    return result_json

def run_openai_pipeline(audio_path: str, api_key: str) -> dict:
    """
    Executes the OpenAI pipeline:
    1. Calls Whisper API to transcribe and get segment-level timestamps.
    2. Sends the segments to GPT-4o to refine speaker separation (diarization) and extract meeting intelligence.
    """
    client = OpenAI(api_key=api_key)
    
    # 1. Transcribe audio with Whisper
    with open(audio_path, "rb") as f:
        transcript_res = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json"
        )
        
    # Extract segment details
    segments = []
    if hasattr(transcript_res, 'segments'):
        for seg in transcript_res.segments:
            segments.append({
                "start": seg.get("start", 0.0),
                "end": seg.get("end", 0.0),
                "text": seg.get("text", "")
            })
    else:
        # Fallback if segments not present
        segments.append({
            "start": 0.0,
            "end": 0.0,
            "text": getattr(transcript_res, 'text', '')
        })
        
    # 2. Structure using GPT-4o
    prompt = f"""
    You are an expert meeting intelligence assistant.
    I have transcribed a meeting audio file using OpenAI Whisper. 
    Below are the raw text segments along with their timestamps:
    
    {json.dumps(segments, indent=2)}
    
    Your tasks are:
    1. Diarize and format the transcript: Reconstruct the transcript into dialogue entries, assigning speaker labels (e.g. Speaker A, Speaker B, etc., or actual names if identifiable from context) to each block of dialogue, keeping the start and end times in seconds. Combine consecutive segments from the same speaker if appropriate.
    2. Extract meeting intelligence:
       - Summary: 3-5 sentence executive summary.
       - Objectives: Key meeting objectives.
       - Key Decisions: Clear decisions made during the call.
       - Action Items: Tasks, owners, due dates, priority ('High'/'Medium'/'Low'), and a confidence score (0-100).
       - Open Questions: Unresolved issues.
       - Topics: Break down the meeting topics with summaries and start/end time offsets.
       - Speaker Analytics: Word count, talk percentage, and overall sentiment for each speaker.
       
    You MUST respond strictly in the requested JSON schema format.
    """
    
    # Call GPT-4o with Structured Outputs
    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a professional assistant that generates meeting intelligence reports."},
            {"role": "user", "content": prompt}
        ],
        response_format=PipelineResult,
        temperature=0.2
    )
    
    result = response.choices[0].message.content
    return json.loads(result)

# =====================================================================
# Main Routing Wrapper
# =====================================================================

def process_audio(audio_path: str, provider: str, api_key: str, model_name: Optional[str] = None) -> dict:
    """
    Routes processing to the selected provider or falls back if API key is not set.
    """
    if not api_key or provider == "Demo Mode":
        # Fallback to Demo Mode
        time.sleep(3)  # Simulate processing delay
        return get_demo_meeting_data()
        
    if provider == "Gemini":
        model = model_name if model_name else "gemini-3.5-flash"
        return run_gemini_pipeline(audio_path, api_key, model)
    elif provider == "OpenAI":
        return run_openai_pipeline(audio_path, api_key)
    else:
        raise ValueError(f"Unknown API provider: {provider}")

# =====================================================================
# RAG Chat Query Logic
# =====================================================================

def answer_rag_query(query: str, transcript: list, analysis: dict, context_doc_text: Optional[str], provider: str, api_key: str, model_name: Optional[str] = None) -> str:
    """
    Formulates a prompt with the transcript and optional context document and asks the LLM to answer.
    """
    if not api_key:
        # Demo / Offline response
        time.sleep(1)
        # Check simple keywords
        q_lower = query.lower()
        if "timeline" in q_lower or "due" in q_lower or "date" in q_lower or "prototype" in q_lower or "release" in q_lower:
            return "**[Demo Mode Answer]** The team decided to target next **Friday, July 17th, 2026** for the MVP prototype release. David needs to complete the backend by Monday, July 13th, and Alex must implement the frontend by Tuesday, July 14th."
        if "database" in q_lower or "db" in q_lower or "sqlite" in q_lower:
            return "**[Demo Mode Answer]** The database architecture is built using **SQLite**, and meeting data (including transcripts and analysis) is persisted as serialized JSON in the `meetings.db` file. This was proposed by David and approved by the team."
        if "style" in q_lower or "css" in q_lower or "frontend" in q_lower or "glass" in q_lower:
            return "**[Demo Mode Answer]** Alex is leading the frontend design using Streamlit. He is injecting custom CSS to create a premium **glassmorphic dark theme** with a deep indigo/cyan gradient, using the **Outfit** Google Font and interactive component cards."
        return "**[Demo Mode Answer]** This is a sample response in Demo Mode. To run live RAG queries on your uploaded meeting transcripts and context documents, please ensure your Gemini API key is configured on the backend."

    # Format transcript context
    transcript_str = "\n".join([f"[{d.get('start', 0.0):.1f}s - {d.get('end', 0.0):.1f}s] {d.get('speaker')}: {d.get('text')}" for d in transcript])
    
    # Format analysis summary
    summary_str = f"Summary: {analysis.get('summary', '')}\nDecisions: {', '.join(analysis.get('key_decisions', []))}"
    
    context_str = f"--- MEETING SUMMARY ---\n{summary_str}\n\n--- DIARIZED TRANSCRIPT ---\n{transcript_str}"
    
    if context_doc_text:
        context_str += f"\n\n--- ADDITIONAL CONTEXT DOCUMENT ---\n{context_doc_text}"
        
    prompt = f"""
    You are an intelligent assistant integrated into Meeting Summarizer. 
    Your job is to answer questions about the meeting based ONLY on the provided context (transcript, summary, and optional context document).
    
    Context:
    {context_str}
    
    User Question: {query}
    
    Please provide a concise, professional answer, citing speakers and timestamps (e.g., [Speaker Name at 12.5s]) where appropriate.
    If the context doesn't contain the answer, explain what you know and clarify that the details are not explicitly mentioned in the documents.
    """
    
    if provider == "Gemini":
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name if model_name else "gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    else:  # OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions about a meeting transcript and referenced files."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
