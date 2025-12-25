import pymysql
from config import Config
import random
from datetime import datetime, timedelta

# Sample Data in Arabic
sample_cases = [
    # Health
    {
        'titre': 'عائلة تحتاج إلى علاج طبي عاجل',
        'description': 'عائلة مكونة من 5 أفراد تعاني من ظروف صحية صعبة. الأب يحتاج إلى عملية جراحية عاجلة ولكن لا يملك التأمين الصحي.',
        'adresse': 'نواكشوط، تيارت',
        'statut': 'Urgent',
        'domain': 'Santé'
    },
    {
        'titre': 'مريض سكري يحتاج إلى دواء',
        'description': 'رجل مسن يعاني من داء السكري المزمن. يحتاج إلى الأنسولين والأدوية بشكل يومي لكن دخله المحدود لا يسمح بذلك.',
        'adresse': 'نواكشوط، توجنين',
        'statut': 'En cours',
        'domain': 'Santé'
    },
    {
        'titre': 'امرأة حامل تحتاج رعاية',
        'description': 'امرأة حامل في شهرها الثامن تعاني من مضاعفات. تحتاج إلى متابعة طبية دقيقة لضمان ولادة آمنة.',
        'adresse': 'نواكشوط، المينا',
        'statut': 'En cours',
        'domain': 'Santé'
    },
    {
        'titre': 'علاج كيميائي لمريضة سرطان',
        'description': 'امرأة تعاني من سرطان الثدي وتحتاج جلسات علاج كيميائي. التكلفة باهظة والأسرة استنفدت مدخراتها.',
        'adresse': 'نواكشوط، كرفور',
        'statut': 'Urgent',
        'domain': 'Santé'
    },

    # Education
    {
        'titre': 'مستلزمات مدرسية للأيتام',
        'description': 'طفل يتيم في المرحلة الابتدائية. الأسرة غير قادرة على توفير الكتب والأدوات المدرسية لمواصلة تعليمه.',
        'adresse': 'نواكشوط، الميناء',
        'statut': 'En cours',
        'domain': 'Éducation'
    },
    {
        'titre': 'رسوم جامعية لطالبة',
        'description': 'طالبة متفوقة حصلت على البكالوريا لكنها عاجزة عن دفع رسوم التسجيل الجامعي. حلمها دراسة الطب.',
        'adresse': 'نواكشوط، تفرغ زينة',
        'statut': 'Résolu',
        'domain': 'Éducation'
    },
    {
        'titre': 'دعم مدرسة قرآنية',
        'description': 'محضرة تستقبل أطفالاً محتاجين. تحتاج إلى ألواح وحصير ومصاحف لتعليم الأطفال.',
        'adresse': 'نواكشوط، الموافقية',
        'statut': 'Résolu',
        'domain': 'Éducation'
    },
    {
        'titre': 'فصل دراسي مؤقت',
        'description': 'حي عشوائي به 15 طفلاً خارج المدرسة. نحتاج لبناء فصل مؤقت وتوفير أدوات تعليمية.',
        'adresse': 'نواكشوط، دار النعيم',
        'statut': 'En cours',
        'domain': 'Éducation'
    },

    # Housing & Living
    {
        'titre': 'ترميم منزل متهالك',
        'description': 'منزل أسرة فقيرة تضرر من الأمطار. السقف يوشك على السقوط ويحتاج ترميماً عاجلاً قبل موسم الخريف.',
        'adresse': 'نواكشوط، السبخة',
        'statut': 'En cours',
        'domain': 'Logement'
    },
    {
        'titre': 'مأوى لعائلة نازحة',
        'description': 'عائلة نازحة تعيش في العراء. يحتاجون خيمة أو غرفة بسيطة لحمايتهم وأطفالهم من البرد.',
        'adresse': 'نواكشوط، الرياض',
        'statut': 'Urgent',
        'domain': 'Logement'
    },
    {
        'titre': 'توصيل الكهرباء لمنزل',
        'description': 'أسرة تعيش في الظلام منذ 3 أشهر بسبب تراكم الفواتير. الأطفال لا يجدون ضوءاً للمذاكرة.',
        'adresse': 'نواكشوط، دار النعيم',
        'statut': 'Urgent',
        'domain': 'Logement'
    },
    {
        'titre': 'بناء غرفتين من الطوب',
        'description': 'عائلة كبيرة تعيش في كوخ صفيح. الهدف بناء غرفتين إسمنتيتين لتوفير سكن لائق.',
        'adresse': 'نواكشوط، توجنين',
        'statut': 'En cours',
        'domain': 'Logement'
    },

    # Food & Water
    {
        'titre': 'سلة غذائية لأرملة',
        'description': 'أرملة تعيل 4 أطفال. تحتاج سلة غذائية شهرية (أرز، زيت، سكر) لضمان قوت يومهم.',
        'adresse': 'نواكشوط، عرفات',
        'statut': 'Urgent',
        'domain': 'Alimentation'
    },
    {
        'titre': 'ماء صالح للشرب',
        'description': 'حي نائي لا تصله المياه. السكان يشترون الماء المالح. نحتاج حفر بئر سطحي أو خزان.',
        'adresse': 'نواكشوط، الترحيل',
        'statut': 'Urgent',
        'domain': 'Alimentation'
    },
    {
        'titre': 'إفطار صائم لأسرة',
        'description': 'أسرة متعففة لا تجد ما تفطر عليه. نحتاج توفير مواد غذائية أساسية لهم.',
        'adresse': 'نواكشوط، لكصر',
        'statut': 'En cours',
        'domain': 'Alimentation'
    }
]

def get_connection():
    return pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def main():
    print("Connecting to database...")
    try:
        conn = get_connection()
    except Exception as e:
        print(f"Error connecting to DB: {e}")
        return

    try:
        with conn.cursor() as cursor:
            # 1. Fetch valid ONG IDs
            print("Fetching existing ONGs...")
            cursor.execute("SELECT id_ong, nom_ong FROM ong")
            ongs = cursor.fetchall()
            
            if not ongs:
                print("❌ No ONGs found in database! Please create an ONG first.")
                return

            print(f"✅ Found {len(ongs)} ONGs.")
            ong_ids = [ong['id_ong'] for ong in ongs]

            # 2. Insert Cases
            print("\nInserting sample cases...")
            count = 0
            
            for case in sample_cases:
                # Randomly assign an ONG
                random_ong_id = random.choice(ong_ids)
                
                # Random date between today and 30 days ago
                days_ago = random.randint(0, 30)
                pub_date = datetime.now() - timedelta(days=days_ago)

                sql = """
                    INSERT INTO cas_social (titre, description, adresse, statut, id_ong, date_publication)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    case['titre'],
                    case['description'],
                    case['adresse'],
                    case['statut'],
                    random_ong_id,
                    pub_date
                ))
                count += 1
            
            conn.commit()
            print(f"\n✅ Successfully added {count} sample cases!")
            print("Refresh your dashboard to see the new data.")

    except Exception as e:
        print(f"❌ Error during insertion: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
