import pymysql
import os
import sys

try:
    # Database connection
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='ong_connect_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    with conn.cursor() as cursor:
        print("--- Database Debug for Case 6 ---")
        cursor.execute("SELECT * FROM cas_social WHERE id_cas_social = 6")
        case = cursor.fetchone()
        if case:
            print(f"Case Title: {case['titre']}")
            cursor.execute("SELECT * FROM media WHERE id_cas_social = 6")
            medias = cursor.fetchall()
            print(f"Total Medias found: {len(medias)}")
            for i, m in enumerate(medias):
                print(f"Media {i+1}:")
                print(f"  URL: {m['file_url']}")
                full_path = os.path.join('c:\\Users\\fatimetou\\Documents\\OngWeb\\static', m['file_url'].replace('/', os.sep))
                print(f"  System Path: {full_path}")
                print(f"  File Exists: {os.path.exists(full_path)}")
        else:
            print("Case 6 NOT FOUND in database.")
            
    conn.close()
except Exception as e:
    print(f"ERROR: {str(e)}")
    sys.exit(1)
