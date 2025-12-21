import pymysql
from config import Config

# Database Configuration
DB_HOST = Config.DB_HOST
DB_USER = Config.DB_USER
DB_PASSWORD = Config.DB_PASSWORD
DB_NAME = Config.DB_NAME

conn = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cursor:
        # Check media table
        print("=== Checking Media Table ===")
        cursor.execute("SELECT * FROM media LIMIT 5")
        media = cursor.fetchall()
        print(f"Found {len(media)} media entries:")
        for m in media:
            print(f"  ID: {m['id_media']}, Case ID: {m['id_cas_social']}, URL: {m['file_url']}")
        
        print("\n=== Checking Cases with Media ===")
        # Check the query we're using
        cursor.execute("""
            SELECT c.id_cas_social, c.titre, 
                   (SELECT file_url FROM media WHERE id_cas_social = c.id_cas_social LIMIT 1) as first_image
            FROM cas_social c
            LIMIT 5
        """)
        cases = cursor.fetchall()
        print(f"Found {len(cases)} cases:")
        for case in cases:
            print(f"  Case ID: {case['id_cas_social']}, Title: {case['titre']}, First Image: {case['first_image']}")
            
finally:
    conn.close()
