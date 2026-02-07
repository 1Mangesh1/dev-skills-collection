#!/usr/bin/env python3
"""Database Migration Tool"""

import sqlite3
import os
from datetime import datetime

def create_migration(name):
    """Create new migration file"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"migrations/{timestamp}_{name}.sql"
    
    os.makedirs("migrations", exist_ok=True)
    
    with open(filename, 'w') as f:
        f.write(f"""-- Migration: {name}
-- Created: {datetime.now().isoformat()}

BEGIN;

-- TODO: Add your SQL here

COMMIT;
""")
    
    print(f"✓ Created: {filename}")
    return filename

def run_migrations(db_path):
    """Apply all pending migrations"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create migrations table if doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Get applied migrations
    cursor.execute("SELECT version FROM schema_migrations")
    applied = {row[0] for row in cursor.fetchall()}
    
    # Apply pending migrations
    for filename in sorted(os.listdir("migrations")):
        if filename.endswith(".sql"):
            version = filename.replace(".sql", "")
            if version not in applied:
                with open(f"migrations/{filename}") as f:
                    cursor.execute(f.read())
                cursor.execute("INSERT INTO schema_migrations (version) VALUES (?)", (version,))
                print(f"Applied: {filename}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_migration("add_user_table")
    run_migrations("app.db")
