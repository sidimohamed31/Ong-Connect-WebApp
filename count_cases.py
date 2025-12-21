
from app import get_db

with get_db() as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as count FROM cas_social")
        count = cursor.fetchone()['count']
        print(f"TOTAL_CASES:{count}")
