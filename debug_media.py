import pymysql

# Database connection
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='ong_connect_db',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cursor:
        # Check all media in the database
        cursor.execute("SELECT * FROM media")
        all_media = cursor.fetchall()
        print("All media in database:")
        for media in all_media:
            print(f"  ID: {media['id_media']}, Case ID: {media['id_cas_social']}, File: {media['file_url']}")
        
        print("\n" + "="*50 + "\n")
        
        # Check media for case ID 6 (from the URL in the screenshot)
        cursor.execute("SELECT * FROM media WHERE id_cas_social = 6")
        case_media = cursor.fetchall()
        print("Media for Case ID 6:")
        if case_media:
            for media in case_media:
                print(f"  ID: {media['id_media']}, File: {media['file_url']}")
        else:
            print("  No media found!")
        
        print("\n" + "="*50 + "\n")
        
        # Check the case details
        cursor.execute("""
            SELECT c.*, o.nom_ong, o.logo_url 
            FROM cas_social c
            LEFT JOIN ong o ON c.id_ong = o.id_ong
            WHERE c.id_cas_social = 6
        """)
        case = cursor.fetchone()
        print("Case 6 details:")
        if case:
            print(f"  Title: {case['titre']}")
            print(f"  ONG: {case['nom_ong']}")
            print(f"  ONG Logo: {case['logo_url']}")
        else:
            print("  Case not found!")
            
finally:
    conn.close()
