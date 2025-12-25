import pymysql

# Credentials from audit (Config)
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'sidimedtop1'
DB_NAME = 'ong_connecte'

def fix_schema():
    print("Connecting to database...")
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn.cursor() as cursor:
            print("Altering table 'ong'...")
            cursor.execute("ALTER TABLE ong MODIFY mot_de_passe VARCHAR(255) NOT NULL")
            print("Success: Column 'mot_de_passe' resized to VARCHAR(255).")
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    fix_schema()
