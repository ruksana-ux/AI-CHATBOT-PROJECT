"""AI Customer Support Assistant - Web Chat Interface (Streamlit)."""
import os
import streamlit as st
from dotenv import load_dotenv

from assistant import CustomerSupportAssistant
from llm_engine import OllamaModel, HuggingFaceTransformersModel
from tools import load_faqs, load_orders

load_dotenv()

st.set_page_config(
    page_title="AI Customer Support Assistant",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for polished support chat appearance
st.markdown("""
<style>
    .support-header {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        color: #1E3A8A;
    }
    .support-sub {
        color: #4B5563;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    .badge-info {
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 0.5rem 0.8rem;
        border-radius: 4px;
        font-size: 0.85rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.title("⚙️ Model Settings")
    st.caption("Load AI models using Ollama or Hugging Face Transformers. No LangChain.")

    provider = st.radio(
        "Select LLM Engine:",
        options=["Ollama", "Hugging Face Transformers"],
        index=0 if os.getenv("LLM_PROVIDER", "ollama").lower() != "huggingface" else 1
    )

    if provider == "Ollama":
        ollama_model = st.text_input(
            "Ollama Model Name:",
            value=os.getenv("OLLAMA_MODEL", "llama3.2"),
            help="E.g., llama3.2, mistral, qwen2.5"
        )
        ollama_host = st.text_input(
            "Ollama Host URL:",
            value=os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
        )
        llm = OllamaModel(model_name=ollama_model, host=ollama_host)
        is_online = llm.is_available()
        if is_online:
            st.success("🟢 Ollama daemon connected")
        else:
            st.warning("🟠 Ollama daemon offline (Rule-grounded fallback active)")
            st.caption("Start Ollama in terminal with: `ollama run llama3.2`")

    else:
        hf_model = st.text_input(
            "Hugging Face Model:",
            value=os.getenv("HF_MODEL", "meta-llama/Llama-3.2-3B-Instruct"),
            help="HF model repo or local model name"
        )
        hf_mode = st.radio(
            "Execution Mode:",
            options=["Inference API (Cloud)", "Local Transformers Pipeline"],
            index=0 if os.getenv("HF_USE_LOCAL", "false").lower() != "true" else 1
        )
        hf_token = st.text_input(
            "Hugging Face Token (HF_TOKEN):",
            value=os.getenv("HF_TOKEN", ""),
            type="password",
            help="Free token from huggingface.co/settings/tokens"
        )
        use_local = (hf_mode == "Local Transformers Pipeline")
        llm = HuggingFaceTransformersModel(
            model_name=hf_model,
            use_local_pipeline=use_local,
            hf_token=hf_token
        )
        if llm.is_available():
            st.success("🟢 Hugging Face ready")
        else:
            st.info("ℹ️ Enter your HF_TOKEN or enable local pipeline")

    st.markdown("---")
    st.subheader("📋 Sample Knowledge Base")
    with st.expander("Company FAQs"):
        st.json(load_faqs())
    with st.expander("Sample Customer Orders"):
        st.json(load_orders())

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    with col2:
        transcript_lines = []
        for msg in st.session_state.get("messages", []):
            label = "Customer" if msg["role"] == "user" else "Assistant"
            transcript_lines.append(f"{label}:\n{msg['content']}\n")
        transcript_text = "\n".join(transcript_lines)
        st.download_button(
            label="📥 Export Chat",
            data=transcript_text,
            file_name="support_chat_transcript.txt",
            mime="text/plain",
            use_container_width=True
        )

# Main Chat Interface
st.markdown('<div class="support-header">🤖 AI Customer Support Assistant</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="support-sub">Ask questions regarding shipping, returns, refunds, product warranties, or track your order status.</div>',
    unsafe_allow_html=True
)

# Initialize Assistant and History
if "assistant" not in st.session_state:
    st.session_state.assistant = CustomerSupportAssistant(llm=llm)
else:
    # Update active LLM in assistant if sidebar settings changed
    st.session_state.assistant.llm = llm

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! Welcome to Customer Support. How can I assist you today? You can ask about our shipping policies, returns, refunds, product warranties, or check an order status."
        }
    ]

# Display Conversation History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Quick Prompt Suggestions for First-time users
if len(st.session_state.messages) <= 1:
    st.markdown("**Quick questions you can try:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📦 How long does shipping take?"):
            user_text = "How long does shipping take?"
            st.session_state.messages.append({"role": "user", "content": user_text})
            with st.chat_message("user"):
                st.markdown(user_text)
            reply = st.session_state.assistant.process_message(user_text, st.session_state.messages[:-1])
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()
    with col2:
        if st.button("🔍 Where is my order ORD1002?"):
            user_text = "Where is my order ORD1002?"
            st.session_state.messages.append({"role": "user", "content": user_text})
            with st.chat_message("user"):
                st.markdown(user_text)
            reply = st.session_state.assistant.process_message(user_text, st.session_state.messages[:-1])
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()
    with col3:
        if st.button("🏷️ Do you offer student discounts?"):
            user_text = "Do you offer student discounts?"
            st.session_state.messages.append({"role": "user", "content": user_text})
            with st.chat_message("user"):
                st.markdown(user_text)
            reply = st.session_state.assistant.process_message(user_text, st.session_state.messages[:-1])
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()

# Optional Media Attachment for product quality issues
with st.expander("📎 Attach image/video (e.g. for product quality or damage verification)"):
    uploaded_files = st.file_uploader(
        "Upload photos/videos of the product:",
        type=["png", "jpg", "jpeg", "webp", "mp4", "mov"],
        accept_multiple_files=True,
        help="Upload clear photos of damaged items for quality review."
    )

# User Input
if prompt := st.chat_input("Type your question here (e.g. 'Where is order ORD1002?')..."):
    media_list = [f.name for f in (uploaded_files or [])]

    # Add user message to history
    user_display = prompt
    if media_list:
        user_display += f"\n\n*📎 Attached {len(media_list)} file(s): {', '.join(media_list)}*"

    st.session_state.messages.append({"role": "user", "content": user_display})
    with st.chat_message("user"):
        st.markdown(user_display)

    # Process through assistant with session history
    with st.chat_message("assistant"):
        with st.spinner("Assistant is thinking..."):
            history_for_turn = st.session_state.messages[:-1]
            response = st.session_state.assistant.process_message(
                prompt, history_for_turn, media_urls=media_list if media_list else None
            )
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
