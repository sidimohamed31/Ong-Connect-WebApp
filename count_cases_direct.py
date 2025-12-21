
import pymysql

try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='sidimedtop1',
        database='ong_connecte',
        charset='utf8mb4'
    )
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as count FROM cas_social")
        count = cursor.fetchone()[0]
        print(f"TOTAL_CASES:{count}")
except Exception as e:
    print(f"ERROR:{e}")
finally:
    if 'conn' in locals():
        conn.close()
