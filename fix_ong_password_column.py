from app import get_db_connection

def fix_schema():
    print("Connecting to database...")
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            print("Altering table 'ong'...")
            # Increase password column size to support hashes (usually ~100 chars, so 255 is safe)
            cursor.execute("ALTER TABLE ong MODIFY mot_de_passe VARCHAR(255) NOT NULL")
            print("Success: Column 'mot_de_passe' resized to VARCHAR(255).")
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_schema()
