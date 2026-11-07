# AI Customer Support Assistant

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-chatbot-project-s9b7mct9njjszjpazbacg9.streamlit.app/)
[![CI Tests](https://github.com/ruksana-ux/AI-CHATBOT-PROJECT/actions/workflows/tests.yml/badge.svg)](https://github.com/ruksana-ux/AI-CHATBOT-PROJECT/actions/workflows/tests.yml)
[![GitHub](https://img.shields.io/badge/GitHub-ruksana--ux%2FAI--CHATBOT--PROJECT-blue?logo=github)](https://github.com/ruksana-ux/AI-CHATBOT-PROJECT)

> 🌐 **Live Demo**: [https://ai-chatbot-project-s9b7mct9njjszjpazbacg9.streamlit.app/](https://ai-chatbot-project-s9b7mct9njjszjpazbacg9.streamlit.app/)

A production-ready AI Customer Support Chatbot built strictly following the guidelines without any third-party orchestration frameworks like LangChain. The assistant uses **Ollama** or **Hugging Face Transformers** for model inference, grounds policy answers strictly on company FAQs, and securely validates customer identity before releasing order information.

---

## 🚀 Key Features

### 1. Customer Query Handling
- **Interactive Chat Interface**: Modern web chat interface powered by Streamlit (`app.py`) and a command-line chat interface (`cli.py`).
- **Conversational Memory**: Maintains full conversation history across multiple turns during a session.
- **Clarifying Ambiguity**: Automatically asks polite clarifying questions whenever a customer's query is vague or lacks context.

### 2. FAQ Assistant
- **Knowledge Base**: Store company policies in `data/faqs.json` (and `faqs.json`) covering:
  - **Shipping** (timelines, international delivery)
  - **Returns** (30-day window, conditions)
  - **Refunds** (processing duration, original payment method)
  - **Product Policies** (warranties, cancellation rules)
- **Strict Grounding**: Answers policy questions strictly from company FAQ data—**never invents policies**.
- **Transparency**: Explicitly admits when requested information is unavailable and directs the customer to human support.

### 3. Order Status Checker
- **Sample Orders Store**: Sample order database stored in `data/orders.json` (and `orders.json`).
- **Identity & Order Number Validation**: Verifies **both** the Order ID (e.g. `ORD1002`) and the customer's identity (email address) before disclosing any details.
- **Function Execution**: Calls the Python function `check_order_status(order_id, email)` to retrieve:
  - Order status (e.g., *Shipped*, *Processing*, *Delivered*)
  - Estimated delivery date
  - Product details and quantity
- If a customer asks *"Where is my order ORD1002?"* without an email, the assistant protects privacy by asking for their email to verify identity before retrieving the order.

---

## 📂 Project Structure

```text
├── app.py              # Streamlit Web Chat Interface
├── cli.py              # Terminal / CLI Chat Interface
├── assistant.py        # Core Customer Support Assistant Logic
├── tools.py            # Python data functions (check_order_status, load_faqs, load_orders)
├── llm_engine.py       # Pure Python LLM loader for Ollama & Hugging Face Transformers
├── test_assistant.py   # Comprehensive automated test suite
├── requirements.txt    # Project dependencies
├── .env.example        # Environment variable template
├── .gitignore          # Git ignore configuration
└── data/
    ├── faqs.json       # Company FAQs (shipping, returns, refunds, product policies)
    └── orders.json     # Sample customer orders with identity verification fields
```

---

## 🛠️ Installation & Local Setup

### 1. Clone or Open the Repository
```bash
git clone https://github.com/ruksana-ux/AI-CHATBOT-PROJECT.git
cd AI-CHATBOT-PROJECT
```

### 2. Create and Activate a Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

---

## 🧠 LLM Model Configuration

You can use either **Ollama** (local offline) or **Hugging Face Transformers** (cloud or local). Configure in `.env` or directly through the Web UI sidebar:

### Option A: Ollama (Default & Recommended for Local)
1. Install [Ollama](https://ollama.ai) and pull a model:
   ```bash
   ollama run llama3.2
   ```
2. Keep the following in your `.env`:
   ```ini
   LLM_PROVIDER=ollama
   OLLAMA_MODEL=llama3.2
   OLLAMA_HOST=http://127.0.0.1:11434
   ```

### Option B: Hugging Face Transformers
1. Get a free token from [Hugging Face Settings](https://huggingface.co/settings/tokens).
2. Set in your `.env`:
   ```ini
   LLM_PROVIDER=huggingface
   HF_TOKEN=hf_your_actual_token_here
   HF_MODEL=meta-llama/Llama-3.2-3B-Instruct
   HF_USE_LOCAL=false
   ```
*(Set `HF_USE_LOCAL=true` if you want to run a local transformers pipeline with PyTorch)*

---

## 💻 Running the Assistant

### Web Chat Interface (Streamlit)
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`. You can toggle model settings, view the FAQ and order database in the sidebar, and chat with the assistant.

### Terminal Chat Interface (CLI)
```bash
python cli.py
```

---

## 🧪 Running Automated Tests

Run the test suite to verify FAQ grounding, identity verification, ambiguity handling, and multi-turn state:
```bash
python test_assistant.py
```

---

## 🌐 How to Deploy Using GitHub

### Step 1: Initialize Git and Commit
```bash
git init
git add .
git commit -m "Initial commit: AI Customer Support Assistant"
```

### Step 2: Push to GitHub
1. Go to [GitHub](https://github.com/new) and create a new repository (e.g. `ai-customer-support-assistant`).
2. Run the commands provided by GitHub:
   ```bash
   git branch -M main
   git remote add origin https://github.com/<your-username>/ai-customer-support-assistant.git
   git push -u origin main
   ```

### Step 3: 1-Click Free Deployment on Streamlit Community Cloud
Streamlit Cloud offers free, instantaneous hosting directly connected to your GitHub repository:
1. Visit [share.streamlit.io](https://share.streamlit.io/) and sign in with your GitHub account.
2. Click **"New app"**.
3. Select:
   - **Repository**: `<your-username>/ai-customer-support-assistant`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. Expand **Advanced Settings**:
   - If using Hugging Face, add your secret:
     ```text
     LLM_PROVIDER = "huggingface"
     HF_TOKEN = "your_hf_token"
     HF_MODEL = "meta-llama/Llama-3.2-3B-Instruct"
     ```
5. Click **"Deploy!"**. Your chatbot will be live with a shareable public URL!

### Alternative: Deploy on Hugging Face Spaces
1. Go to [Hugging Face Spaces](https://huggingface.co/spaces) and click **"Create new Space"**.
2. Select **Streamlit** as the Space SDK.
3. Link your GitHub repository or push directly via Git.
