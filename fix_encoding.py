import sys
import traceback

def main():
    try:
        with open('debug_output.txt', 'w') as f:
            f.write("Script started.\n")
            f.write(f"Python executable: {sys.executable}\n")
            f.write(f"Path: {sys.path}\n")
            
            print("Importing pymysql...", file=f)
            try:
                import pymysql
                import pymysql.cursors
                print(f"pymysql imported: {pymysql.__version__}", file=f)
            except ImportError:
                print("Failed to import pymysql!", file=f)
                return

            # Database Configuration
            DB_HOST = 'localhost'
            DB_USER = 'root'
            DB_PASSWORD = 'sidimedtop1'
            DB_NAME = 'ong_connecte'

            print("Connecting...", file=f)
            conn = pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                cursorclass=pymysql.cursors.DictCursor
            )
            print("Connected.", file=f)
            
            with conn.cursor() as cursor:
                # Alter Database
                print(f"Altering database...", file=f)
                cursor.execute(f"ALTER DATABASE {DB_NAME} CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci")
                
                tables = ['administrateur', 'ong', 'cas_social', 'beneficier', 'categorie', 'media']
                for table in tables:
                    print(f"Converting table {table}...", file=f)
                    cursor.execute(f"ALTER TABLE {table} CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            
            conn.commit()
            print("Success!", file=f)
            conn.close()

    except Exception as e:
        with open('debug_output.txt', 'a') as f:
            f.write(f"Global Error: {e}\n")
            traceback.print_exc(file=f)

if __name__ == "__main__":
    main()
