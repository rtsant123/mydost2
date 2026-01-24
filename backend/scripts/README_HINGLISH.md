# Hinglish Dataset Integration

## What is this?
Script to load 1M Hinglish everyday conversations into your vector database for better RAG (Retrieval-Augmented Generation).

## Benefits:
- ✅ AI understands Hinglish naturally
- ✅ Better cultural context for Northeast India
- ✅ Improved conversational responses
- ✅ Knowledge of everyday phrases and slang

## Setup:

### 1. Install dependencies (already added to requirements.txt):
```bash
pip install datasets tqdm
```

### 2. Run the loader (locally first):
```bash
cd backend
python scripts/load_hinglish_dataset.py
```

### 3. Configuration:
Edit `scripts/load_hinglish_dataset.py`:
- `MAX_ROWS = 10000` → Start with 10k (takes ~30 min)
- `MAX_ROWS = 100000` → Medium load (takes ~5 hours)
- `MAX_ROWS = None` → Full 1M dataset (takes ~50 hours)

## How it works:

1. Downloads dataset from HuggingFace
2. Processes conversations in batches
3. Generates embeddings using sentence-transformers
4. Stores in PostgreSQL + pgvector
5. AI automatically searches these for relevant context

## After loading:

AI will use these conversations when users ask questions:
- **User**: "Teer ka result kya hai?"
- **AI**: Searches Hinglish dataset + user history
- **Response**: Natural Hinglish answer with context

## Storage:

- 10k conversations ≈ 500 MB in vector DB
- 100k conversations ≈ 5 GB in vector DB
- 1M conversations ≈ 50 GB in vector DB

## Production deployment:

**Don't run on Railway directly!** It will timeout.

Instead:
1. Run locally to generate vectors
2. Export vector data
3. Import to Railway database
4. OR run during Railway maintenance window

## Monitoring:

Check progress:
```sql
SELECT COUNT(*) FROM chat_vectors WHERE user_id = 'hinglish_dataset';
SELECT COUNT(*) FROM chat_vectors WHERE metadata->>'source' = 'Hinglish-Everyday-Conversations-1M';
```

## Dataset source:
https://huggingface.co/datasets/Abhishekcr448/Hinglish-Everyday-Conversations-1M
