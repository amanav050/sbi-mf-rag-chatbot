---
title: SBI MF RAG Chatbot
emoji: 💰
colorFrom: indigo
colorTo: green
sdk: docker
app_port: 8000
pinned: false
---

# SBI MF RAG Chatbot

A production-ready, facts-only RAG chatbot for SBI Mutual Fund schemes. Provides cited, factual answers from official SBI MF documents.






# SBI MF RAG Chatbot

A production-ready, facts-only RAG (Retrieval-Augmented Generation) chatbot that answers queries about SBI Mutual Fund schemes using only official public sources.

## 🎯 Overview

This chatbot provides factual information about SBI Mutual Fund schemes through a sophisticated RAG pipeline that:
- Scrapes official SBI MF web pages and documents
- Processes content through chunking and embedding
- Stores vectors in Chroma Cloud for fast retrieval
- Generates responses using Groq's Llama 3.1 model
- Always cites sources and provides no investment advice

## 📊 Selected AMC & Schemes

**AMC:** SBI Mutual Fund (sbimf.com)

**Schemes Covered:**
- SBI Large Cap Fund
- SBI Flexicap Fund  
- SBI ELSS Tax Saver Fund
- SBI Small Cap Fund

## 🏗️ Architecture Overview

The system follows a complete RAG pipeline:

```
scrape → chunk → embed → store → retrieve → LLM → cite
```

1. **Scraping**: Daily automated scraping of scheme pages and FAQs from sbimf.com
2. **Chunking**: Text is broken into 512-character overlapping chunks
3. **Embedding**: Local bge-small-en-v1.5 model creates 384-dimensional vectors
4. **Storage**: Vectors stored in Chroma Cloud for similarity search
5. **Retrieval**: Query embedding finds top 5 most relevant chunks
6. **LLM**: Groq's Llama 3.1 generates factual responses
7. **Citation**: All responses include source URLs and last updated dates

## 🛠️ Tech Stack

| Component | Tool | Version |
|---|---|---|
| HTML Scraping | requests + BeautifulSoup4 | 2.31.0 + 4.12.3 |
| PDF Ingestion | PyMuPDF + pdfplumber | 1.24.1 + 0.11.0 |
| Chunking | LangChain RecursiveCharacterTextSplitter | 0.1.20 |
| Embedding | sentence-transformers bge-small-en-v1.5 | 2.7.0 |
| Vector DB | Chroma Cloud | 0.5.0 |
| Scheduler | GitHub Actions CRON | - |
| LLM | Groq API - llama-3.1-8b-instant | 0.9.0 |
| API | FastAPI + uvicorn | 0.111.0 + 0.30.1 |
| UI | Plain HTML + CSS + JS | - |
| Rate Limiting | slowapi | 0.1.9 |

## 🚀 Setup Instructions

### Prerequisites
- Python 3.11+
- Valid API keys for Chroma Cloud and Groq

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "RAG ChatBOT"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Add API keys to .env**
   ```bash
   # Create .env file with:
   CHROMA_API_KEY=your_chroma_api_key_here
   CHROMA_TENANT=f0d857c0-c00b-4742-bf30-d9a10400d176
   CHROMA_DATABASE=sbi_mf_rag
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. **Run initial data ingestion**
   ```bash
   # Ingest HTML sources (daily)
   python ingestion/router.py --mode dynamic
   
   # Ingest PDF sources (one-time)
   python ingestion/router.py --mode static
   
   # Run chunking
   python ingestion/phase_3_chunker/chunker.py
   
   # Run embedding
   python ingestion/phase_4_embedder/embedder.py
   
   # Store in vector database
   python ingestion/phase_5_vector_db/vector_db.py
   ```

5. **Start the server**
   ```bash
   python -m api.phase_10_fastapi.main
   ```

6. **Open the UI**
   Navigate to http://127.0.0.1:8000 in your browser

## ⚠️ Disclaimer

**Facts-only. No investment advice.** This chatbot provides factual information sourced from official SBI Mutual Fund documents and web pages. It does not provide investment recommendations, financial advice, or opinions. Always consult with a qualified financial advisor before making investment decisions.

## 🚫 Known Limitations

- **Source-dependent**: Only answers questions based on scraped SBI MF content
- **No real-time data**: NAV values and performance data are only as current as the last scrape
- **English only**: Supports queries in English language only
- **Factual responses**: Cannot provide opinions, predictions, or investment advice
- **Rate limited**: API is rate-limited to 10 requests per minute per IP
- **Static PDFs**: PDF documents require manual re-ingestion for updates

## 📁 Project Structure

```
sbi-mf-rag-chatbot/
├── docs/                    # Architecture documentation
├── corpus/                  # Source URLs and metadata
├── ingestion/              # Data processing pipeline
├── query/                  # Query processing components
├── api/                    # FastAPI server
├── ui/                     # Web interface
├── scheduler/              # GitHub Actions workflows
└── phase_results/          # Implementation results
```

## 🔧 Maintenance

- **Daily ingestion**: Automatically runs via GitHub Actions at 9:15 AM IST
- **Manual PDF updates**: Trigger manual workflow when new PDFs are available
- **Monitoring**: Check GitHub Actions logs for ingestion status
- **API usage**: Monitor Groq API usage to avoid rate limits

## 📞 Support

For issues related to:
- **Content accuracy**: Visit https://www.sbimf.com
- **Technical issues**: Check GitHub Issues or create a new one
- **API keys**: Ensure valid keys in .env file

---

**Version**: 1.0.0  
**Last Updated**: 2026-04-15
