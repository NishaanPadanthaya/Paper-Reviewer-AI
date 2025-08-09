# PaperReviewer AI – SmartResearch using AI Agents

🧠 **Discover and analyze research papers with AI Agentic powered summaries**

A full-stack application that searches arXiv for research papers and generates structured summaries using Google's Gemini 2.5 Flash model, orchestrated by CrewAI agents.

![PaperReviewer AI](https://img.shields.io/badge/AI-Powered-blue) ![React](https://img.shields.io/badge/React-18-61dafb) ![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688) ![CrewAI](https://img.shields.io/badge/CrewAI-Agents-purple)

## ✨ Features

- 🔍 **Smart Paper Discovery**: Search arXiv with natural language queries
- 🤖 **AI-Powered Summaries**: Structured analysis with Problem, Methodology, Findings, and Limitations
- 🎨 **Modern UI**: Beautiful, responsive interface with smooth animations
- ⚡ **Fast & Reliable**: Built with FastAPI backend and React frontend
- 🔄 **Real-time Processing**: Live updates during paper analysis

## 🏗️ Architecture

### Tech Stack
- **Frontend**: React 18 + TypeScript + Vite + Custom CSS
- **Backend**: FastAPI + Python 3.10+
- **AI Orchestration**: CrewAI with specialized agents
- **LLM**: Google Gemini 2.5 Flash (via google-genai SDK)
- **Data Source**: arXiv API (python-arxiv library)

### AI Agents
1. **SearchAgent**: Finds relevant papers using arXiv search tool
2. **SummaryAgent**: Generates structured summaries using Gemini 2.5 Flash

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+
- **Python** 3.10+
- **Google Gemini API Key** ([Get one here](https://ai.google.dev/))

### 1. Clone & Setup
```bash
git clone <your-repo-url>
cd PaperReviewer-AI
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\Activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env and set:
# GEMINI_API_KEY=your_api_key_here
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Run the Application
```bash
# Terminal 1: Start Backend (from project root)
python backend/app/main.py

# Terminal 2: Start Frontend
cd frontend
npm run dev
```







```


