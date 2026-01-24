"""
Load Hinglish conversations dataset into vector database for RAG.
This will help AI understand Hinglish and provide better culturally relevant responses.
"""
import os
import sys
import asyncio
from datasets import load_dataset
from tqdm import tqdm

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.vector_store_pg import VectorStoreService
from services.embedding_service import EmbeddingService

async def load_hinglish_data(batch_size=100, max_rows=10000):
    """
    Load Hinglish conversations dataset and store in vector DB.
    
    Args:
        batch_size: Number of conversations to process at once
        max_rows: Maximum number of rows to load (None for all)
    """
    print("🚀 Starting Hinglish dataset loader...")
    
    # Initialize services
    vector_store = VectorStoreService()
    embedding_service = EmbeddingService()
    
    # Load dataset
    print("📥 Loading dataset from HuggingFace...")
    try:
        ds = load_dataset("Abhishekcr448/Hinglish-Everyday-Conversations-1M", split="train")
        print(f"✅ Dataset loaded: {len(ds)} conversations")
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        print("💡 Install datasets library: pip install datasets")
        return
    
    # Limit rows if specified
    if max_rows:
        ds = ds.select(range(min(max_rows, len(ds))))
        print(f"📊 Processing first {len(ds)} conversations")
    
    # Process in batches
    successful = 0
    failed = 0
    
    for i in tqdm(range(0, len(ds), batch_size), desc="Processing batches"):
        batch = ds[i:i+batch_size]
        
        # Process each conversation in batch
        for idx, row in enumerate(zip(*batch.values())):
            try:
                # Get conversation text (adjust field names based on dataset structure)
                # Common fields: 'text', 'conversation', 'input', 'response'
                conversation_text = ""
                
                if 'text' in batch:
                    conversation_text = batch['text'][idx]
                elif 'conversation' in batch:
                    conversation_text = batch['conversation'][idx]
                elif 'input' in batch and 'response' in batch:
                    conversation_text = f"Q: {batch['input'][idx]}\nA: {batch['response'][idx]}"
                else:
                    # Try to get first text field
                    for key in batch.keys():
                        if isinstance(batch[key][idx], str) and len(batch[key][idx]) > 10:
                            conversation_text = batch[key][idx]
                            break
                
                if not conversation_text or len(conversation_text) < 10:
                    continue
                
                # Generate embedding
                embedding = await embedding_service.embed_text(conversation_text)
                
                # Store in vector database
                # Using a generic user_id for public knowledge
                vector_store.add_memory(
                    user_id="hinglish_dataset",
                    content=conversation_text,
                    embedding=embedding,
                    conversation_id=f"hinglish_{i+idx}",
                    memory_type="knowledge",
                    metadata={
                        "source": "Hinglish-Everyday-Conversations-1M",
                        "language": "hinglish",
                        "type": "conversation",
                        "batch": i // batch_size
                    }
                )
                successful += 1
                
            except Exception as e:
                failed += 1
                if failed < 10:  # Only print first few errors
                    print(f"\n⚠️ Error processing row {i+idx}: {e}")
        
        # Print progress every 10 batches
        if (i // batch_size) % 10 == 0:
            print(f"\n📊 Progress: {successful} successful, {failed} failed")
    
    print(f"\n✅ Dataset loading complete!")
    print(f"✅ Successfully loaded: {successful} conversations")
    print(f"❌ Failed: {failed} conversations")
    print(f"\n💡 AI can now use these Hinglish conversations for better context!")

if __name__ == "__main__":
    # Configuration
    BATCH_SIZE = 100
    MAX_ROWS = 10000  # Start with 10k, increase later
    
    print("=" * 60)
    print("   Hinglish Dataset Loader for MyDost")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  - Batch size: {BATCH_SIZE}")
    print(f"  - Max rows: {MAX_ROWS if MAX_ROWS else 'All'}")
    print(f"\n⚠️ This will take some time. Be patient!\n")
    
    # Run async loader
    asyncio.run(load_hinglish_data(batch_size=BATCH_SIZE, max_rows=MAX_ROWS))
