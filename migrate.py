import sqlite3
from app.database import get_db_connection

def add_comments_column():
    try:
        with get_db_connection() as conn:
            # Add the comments column as a TEXT field with a safe empty string default
            conn.execute("ALTER TABLE tbl_amortization_detail ADD COLUMN comments TEXT DEFAULT ''")
            conn.commit()
        print("🚀 Migration Successful: 'comments' column added to tbl_amortization_detail.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("⚠️ Note: 'comments' column already exists in the database schema.")
        else:
            print(f"❌ Structural Operational Error: {str(e)}")

if __name__ == '__main__':
    add_comments_column()