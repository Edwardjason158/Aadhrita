# Aadhrita Wellness Dashboard

A comprehensive, AI-powered wellness tracking and analysis platform designed to help users monitor and improve their physical and mental wellbeing.

![Aadhrita Dashboard](https://images.unsplash.com/photo-1576091160550-217359f42f8c?auto=format&fit=crop&q=80&w=1200)

## 🌟 Key Features

- **Personalized Health Tracking**: Monitor sleep, stress, activity, and mood.
- **AI Wellness Assistant**: An intelligent chatbot powered by **LangGraph** & **OpenRouter** that provides personalized insights and suggestions.
- **Multilingual Support**: Fully supports **English**, **Hindi**, and **Telugu**.
- **Dynamic Analysis**: AI-driven analysis of journal entries to detect emotional tone and health signals.
- **Interactive Dashboard**: Beautiful visualizations of your health data over time.
- **Secure Authentication**: Integrated with Google Auth for seamless entry.

## 🚀 Technology Stack

### Frontend
- **React.js** (Vite)
- **Tailwind CSS** for premium styling
- **Lucide-React** for iconography
- **Axios** for API communication

### Backend
- **FastAPI** (Python)
- **LangGraph** for advanced AI agent orchestration
- **OpenRouter** (Mistral/Llama models) for LLM capabilities
- **SQLite** for reliable data storage
- **Pydantic** for robust data validation

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### 1. Clone the Repository
```bash
git clone https://github.com/Edwardjason158/Aadhrita.git
cd Aadhrita
```

### 2. Backend Setup
```bash
cd backend
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

### 3. Frontend Setup
```bash
cd ../frontend
# Install dependencies
npm install

# Configure environment variables
cp .env.example .env
# Set VITE_API_URL=http://localhost:8000
```

## 🏃 Running the Application

### Start Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Start Frontend
```bash
cd frontend
npm run dev
```

The application will be available at `http://localhost:3000`.

## 🤖 The AI Wellness Assistant

The chatbot uses a state-of-the-art **LangGraph** architecture with memory persistence. It follows a structured "Health Insight -> Suggestion -> Wellness Tips" response format.

Even without an API key, the system includes a robust **Dynamic Mock Fallback** that allows for testing local interactions, history retention, and keyword detection.

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request.

---
© 2026 Aadhrita Wellness Platform
