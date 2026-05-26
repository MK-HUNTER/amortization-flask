import math
from datetime import datetime, timedelta
from app.database import get_db_connection

def calculate_amortization_engine(loan_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tbl_amortization_detail WHERE loan_id = ?", (loan_id,))
    loan = cursor.fetchone()
    if not loan:
        conn.close()
        return

    principal = float(loan['principal'])
    annual_rate = float(loan['rate'])
    term_years = int(loan['term_years'])
    balloon_years = int(loan['balloon_years'])

    try:
        start_dt = datetime.strptime(loan['start_date'], '%Y-%m-%d')
    except ValueError:
        start_dt = datetime.today()

    r = (annual_rate / 100.0) / 12.0
    N = term_years * 12

    if r > 0:
        base_emi = principal * (r * math.pow(1 + r, N)) / (math.pow(1 + r, N) - 1)
    else:
        base_emi = principal / N

    cursor.execute("DELETE FROM tbl_amortization_calc WHERE loan_id = ?", (loan_id,))

    current_bal = principal
    running_interest = 0.0
    running_paid = 0.0
    target_months = balloon_years * 12 if (0 < balloon_years < term_years) else N

    for i in range(1, target_months + 1):
        month_date = (start_dt + timedelta(days=(i-1)*30.4375)).strftime('%Y-%m-%d')
        opening_bal = current_bal
        interest_payment = opening_bal * r

        if i == target_months and 0 < balloon_years < term_years:
            principal_payment = opening_bal
            emi_payment = principal_payment + interest_payment
            closing_bal = 0.0
        else:
            emi_payment = base_emi
            if emi_payment > (opening_bal + interest_payment):
                emi_payment = opening_bal + interest_payment
            principal_payment = emi_payment - interest_payment
            closing_bal = opening_bal - principal_payment
            if closing_bal < 0.01:
                closing_bal = 0.0

        cursor.execute("""
            INSERT INTO tbl_amortization_calc 
            (loan_id, month_index, date, opening_bal, payment, principal_paid, interest_paid, closing_bal)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (loan_id, i, month_date, round(opening_bal, 2), round(emi_payment, 2), 
              round(principal_payment, 2), round(interest_payment, 2), round(closing_bal, 2)))

        running_interest += interest_payment
        running_paid += emi_payment
        current_bal = closing_bal

        if current_bal <= 0:
            break

    cursor.execute("""
        UPDATE tbl_amortization_detail 
        SET total_interest = ?, total_paid = ? 
        WHERE loan_id = ?
    """, (round(running_interest, 2), round(running_paid, 2), loan_id))
    conn.commit()
    conn.close()