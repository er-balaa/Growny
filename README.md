# Growny: Lightweight Personal Productivity Assistant

Growny is a high-performance, AI-powered personal productivity assistant that allows users to create tasks, notes, and reminders using natural language. It is designed to be simple, fast, and production-ready while demonstrating real-world usage of Large Language Models (LLMs) and vector-based semantic search.

---

## Problem Statement

Most traditional productivity tools rely on rigid input forms, manual categorization, and keyword-based search. This creates friction during task entry, reduces flexibility, and makes information retrieval inefficient.

Growny solves this by allowing users to interact in plain English while the system automatically understands intent, structures data, and retrieves information intelligently.

---

## Solution Overview

Growny uses a natural language–driven workflow powered by a Google Large Language Model (Gemini). User input is converted into structured data, stored efficiently, and enriched with vector embeddings to enable semantic search.

---

## Key Features

- Natural language input for tasks, notes, and reminders  
- LLM-based intent detection and entity extraction  
- Structured storage using Supabase PostgreSQL  
- Semantic search powered by vector embeddings  
- Python-based backend API for AI orchestration  
- Secure Google authentication  
- Clean, modular, and scalable architecture  

---

## How the System Works

1. User enters text in natural language  
2. React frontend sends the request to a Python backend API  
3. Backend calls Google Gemini with a strict system prompt  
4. LLM returns structured JSON output  
5. Data is validated and stored in Supabase PostgreSQL  
6. Vector embeddings are generated and saved  
7. Relevant records are retrieved using similarity search  

---

## Architecture Overview

User  
↓  
React Frontend  
↓  
Python Backend API (FastAPI / Flask)  
↓  
Google Gemini LLM  
↓  
Supabase PostgreSQL + pgvector  

---

## Technology Stack

### Frontend
- React  
- JavaScript  

### Backend
- Python (FastAPI or Flask)  
- REST-based API design  

### Artificial Intelligence
- Google Gemini API  
- Embedding models for vector generation  

### Database
- Supabase PostgreSQL  
- pgvector for semantic search  

### Authentication
- Google Authentication  

### Deployment
- Frontend: Vercel / Netlify  
- Backend: Cloud-hosted Python service  

---

## Authentication Flow

1. User signs in using Google Authentication  
2. Client receives a secure authentication token  
3. Token is verified by the Python backend  
4. User ID is associated with all database records  

---

## Database Design

A single-table schema is used for simplicity and performance:

- id  
- user_id  
- type (task | note | reminder)  
- title  
- description  
- date  
- time  
- priority  
- embedding (vector)  
- created_at  

---

## Example Usage

**Input**

Remind me to submit the hackathon report tomorrow at 10 AM

**LLM Output**

```json
{
  "type": "reminder",
  "title": "Submit hackathon report",
  "description": null,
  "date": "2026-01-22",
  "time": "10:00",
  "priority": null
}
Performance & Scalability
Lightweight React frontend ensures fast UI response

Python backend handles AI calls efficiently

LLM usage limited to create/update operations

Indexed vector similarity search using pgvector

Scales to thousands of records per user without degradation

Use Cases
Personal task management

Note organization

Reminder scheduling

Semantic search across personal data

Relevance for Hiring & Hackathons
Growny demonstrates:

Practical integration of Google LLMs

Clean frontend–backend separation

Production-oriented Python API design

Real-world use of vector databases

Secure authentication and data handling

This project is ideal for technical interviews, AI hackathons, and portfolio reviews.

Future Enhancements
Voice-based input

Calendar and notification integration

AI-generated daily summaries

Mobile application support

Collaborative and team-based workflows

Conclusion
Growny is a practical example of how React, Python APIs, Google LLMs, and Supabase can be combined to build a scalable, intelligent, and user-friendly productivity system centered around natural language interaction.