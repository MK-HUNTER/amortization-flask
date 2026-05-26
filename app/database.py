import sqlite3
from flask import current_app

def get_db_connection():
    db_file = current_app.config['DB_FILE']
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tbl_amortization_detail (
                loan_id VARCHAR(50) PRIMARY KEY,
                loan_name VARCHAR(100) NOT NULL,
                principal NUMERIC(15, 2) NOT NULL,
                rate NUMERIC(5, 2) NOT NULL,
                term_years INT NOT NULL,
                balloon_years INT NOT NULL,
                start_date DATE NOT NULL,
                total_interest NUMERIC(15, 2),
                total_paid NUMERIC(15, 2)
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tbl_amortization_calc (
                loan_id VARCHAR(50),
                month_index INT,
                date DATE,
                opening_bal NUMERIC(15, 2),
                payment NUMERIC(15, 2),
                principal_paid NUMERIC(15, 2),
                interest_paid NUMERIC(15, 2),
                closing_bal NUMERIC(15, 2),
                PRIMARY KEY (loan_id, month_index),
                FOREIGN KEY (loan_id) REFERENCES tbl_amortization_detail(loan_id) ON DELETE CASCADE
            );
        """)
        conn.commit()