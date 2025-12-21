import pymysql
from app import get_db, app
from config import Config

def check_create_admin():
    with app.app_context():
        try:
            with get_db() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM administrateur")
                    admins = cursor.fetchall()
                    print(f"Found {len(admins)} admins.")
                    
                    if not admins:
                        print("Creating default admin...")
                        # In a real app, hash this password!
                        cursor.execute("INSERT INTO administrateur (nom, email, mot_de_passe) VALUES (%s, %s, %s)", 
                                     ('Admin', 'admin@ongconnect.com', 'admin123'))
                        conn.commit()
                        print("Default admin created: admin@ongconnect.com / admin123")
                    else:
                        print("Admin account exists.")
                        for admin in admins:
                            print(f"Admin: {admin['email']} (ID: {admin['id_admin']})")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_create_admin()
