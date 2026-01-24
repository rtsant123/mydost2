"""Initialize predictions database tables."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.predictions_db import predictions_db

if __name__ == "__main__":
    print("🚀 Initializing predictions database tables...")
    predictions_db.initialize_tables()
    print("✅ Database initialization complete!")
