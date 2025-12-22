from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, jsonify
import pymysql
import pymysql.cursors
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from functools import wraps


from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['LOGO_FOLDER'], exist_ok=True)

# Database Configuration (Now from Config)
DB_HOST = app.config['DB_HOST']
DB_USER = app.config['DB_USER']
DB_PASSWORD = app.config['DB_PASSWORD']
DB_NAME = app.config['DB_NAME']

from contextlib import contextmanager

# ... imports ...

@contextmanager
def get_db():
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        yield conn
    finally:
        conn.close()

def get_db_connection():
    # Legacy wrapper for parts not yet refactored or manual usage
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def init_db():
    # Connect without database first to create it if it doesn't exist
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD)
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    finally:
        conn.close()

    # Now connect to the database and create tables
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Administrateur
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS administrateur (
                    id_admin INT AUTO_INCREMENT PRIMARY KEY,
                    nom VARCHAR(100) NOT NULL,
                    email VARCHAR(150) UNIQUE NOT NULL,
                    mot_de_passe VARCHAR(255) NOT NULL
                )
            """)
            
            # Ong
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ong (
                    id_ong INT AUTO_INCREMENT PRIMARY KEY,
                    nom_ong VARCHAR(150) NOT NULL,
                    adresse VARCHAR(255) NOT NULL,
                    telephone VARCHAR(20) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    domaine_intervation VARCHAR(200) NOT NULL,
                    statut_de_validation ENUM('enattente', 'validé', 'rejetée') DEFAULT 'enattente',
                    update_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    logo_url VARCHAR(255),
                    mot_de_passe VARCHAR(40) NOT NULL
                )
            """)

            # CasSocial
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cas_social (
                    id_cas_social INT AUTO_INCREMENT PRIMARY KEY,
                    titre VARCHAR(150) NOT NULL,
                    description TEXT,
                    adresse VARCHAR(255),
                    date_publication DATE,
                    statut ENUM('En cours', 'Résolu', 'Urgent') DEFAULT 'En cours',
                    id_ong INT,
                    FOREIGN KEY (id_ong) REFERENCES ong(id_ong) ON DELETE CASCADE
                )
            """)

            # Beneficier
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS beneficier (
                    id_beneficiaire INT AUTO_INCREMENT PRIMARY KEY,
                    nom VARCHAR(100) NOT NULL,
                    prenom VARCHAR(100),
                    adresse VARCHAR(255),
                    description_situation TEXT,
                    id_cas_social INT,
                    FOREIGN KEY (id_cas_social) REFERENCES cas_social(id_cas_social) ON DELETE CASCADE
                )
            """)

            # Categorie
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categorie (
                    idCategorie INT AUTO_INCREMENT PRIMARY KEY,
                    nomCategorie VARCHAR(100) NOT NULL,
                    description TEXT NOT NULL
                )
            """)

            # Media
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS media (
                    id_media INT AUTO_INCREMENT PRIMARY KEY,
                    id_cas_social INT,
                    file_url VARCHAR(255) NOT NULL,
                    description_media TEXT,
                    FOREIGN KEY (id_cas_social) REFERENCES cas_social(id_cas_social) ON DELETE CASCADE
                )
            """)
            # --- Fix/Enforce UTF8MB4 for Arabic Support ---
            # Ensure the database itself uses utf8mb4
            cursor.execute(f"ALTER DATABASE {DB_NAME} CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci")
            
            # Convert all specific tables to utf8mb4 to fix "Incorrect string value" errors
            tables_to_fix = ['administrateur', 'ong', 'cas_social', 'beneficier', 'categorie', 'media']
            for table in tables_to_fix:
                try:
                    cursor.execute(f"ALTER TABLE {table} CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                except Exception as e:
                    print(f"Warning: Could not alter table {table}. It might not exist yet. Error: {e}")
            
            # --- Specific Fixes ---
            # Increase logo_url size to 255
            try:
                cursor.execute("ALTER TABLE ong MODIFY logo_url VARCHAR(255)")
            except Exception as e:
                print(f"Warning: Could not resize logo_url. Error: {e}")

            # Seed Default Categories if empty
            cursor.execute("SELECT COUNT(*) as count FROM categorie")
            if cursor.fetchone()['count'] == 0:
                default_categories = [
                    ('Santé', 'Domaine de la santé'), 
                    ('Éducation', 'Domaine de l\'éducation'), 
                    ('Logement', 'Domaine du logement'), 
                    ('Alimentation', 'Domaine de l\'alimentation')
                ]
                cursor.executemany("INSERT INTO categorie (nomCategorie, description) VALUES (%s, %s)", default_categories)
                print("Default categories seeded.")

        conn.commit()
    finally:
        conn.close()

# --- Translations ---

TRANSLATIONS = {
    'ar': {
        'title': 'ONG Connect',
        'dashboard': 'لوحة التحكم',
        'administrators': 'المسؤولون',
        'ngos': 'المنظمات الخيرية',
        'social_cases': 'الحالات الاجتماعية',
        'beneficiaries': 'المستفيدون',
        'categories': 'الفئات',
        'media': 'الوسائط',
        'add_new': 'إضافة جديد',
        'edit': 'تعديل',
        'delete': 'حذف',
        'save': 'حفظ',
        'cancel': 'إلغاء',
        'confirm_delete': 'هل أنت متأكد أنك تريد حذف هذا العنصر؟',
        'actions': 'إجراءات',
        'name': 'الاسم',
        'email': 'البريد الإلكتروني',
        'password': 'كلمة المرور',
        'address': 'العنوان',
        'phone': 'الهاتف',
        'domain': 'مجالات التدخل',
        'status': 'الحالة',
        'description': 'الوصف',
        'date': 'التاريخ',
        'title_field': 'العنوان',
        'first_name': 'الاسم الأول',
        'last_name': 'الاسم الأخير',
        'file_url': 'رابط الملف',
        'welcome': 'مرحباً بك في ONG Connect',
        'language': 'اللغة',
        'switch_lang': 'Français',
        'home': 'الرئيسية',
        'no_records': 'لا توجد سجلات.',
        'success_add': 'تمت الإضافة بنجاح',
        'success_edit': 'تم التعديل بنجاح',
        'success_delete': 'تم الحذف بنجاح',
        'select_domain': '-- اختر المجال --',
        'select_domains': 'اختر مجالاً واحداً أو أكثر',
        'Santé': 'الصحة',
        'Éducation': 'التعليم',
        'Logement': 'الإسكان',
        'Alimentation': 'التغذية',
        # Status - ONG
        'enattente': 'قيد الانتظار',
        'validé': 'تم التوثيق',
        'rejetée': 'مرفوض',
        # Status - Case
        'En cours': 'قيد الإنجاز',
        'Résolu': 'تم الإنجاز',
        'Urgent': 'عاجل',
        # General
        'search': 'بحث...',
        'logout': 'تسجيل الخروج',
        'profile': 'الملف الشخصي',
        'view_details': 'عرض التفاصيل',
        'donor_visitor': 'متبرع / زائر',
        'donor_desc': 'تصفح الحالات الاجتماعية وساهم في إحداث تغيير.',
        'enter': 'دخول',
        'ong_access': 'فضاء المنظمات',
        'ong_desc': 'سجل الدخول لإدارة منظمتك ونشر الحالات.',
        'connect': 'تسجيل الدخول',
        'login_desc': 'أدخل بيانات الاعتماد للوصول إلى مساحتك.',
        'no_account': 'ليس لديك حساب؟',
        'register_now': 'سجل الآن',
        'dashboard_intro': 'تصفح أحدث الحالات الاجتماعية التي تم الإبلاغ عنها من قبل شركائنا.',
        'current_logo': 'الشعار الحالي',
        'impact_tracking': 'تتبع أثرنا',
        'impact_desc': 'انظر كم عدد الأرواح التي لمستها جهودنا المشتركة.',
        'view_beneficiaries_stats': 'عرض إحصائيات المستفيدين',
        'total_beneficiaries': 'إجمالي المستفيدين',
        'top_ongs_impact': 'المنظمات الأكثر تأثيراً',
        'my_profile': 'ملفي الشخصي',
        'my_cases': 'حالاتي الاجتماعية',
        'add_case': 'إضافة حالة جديدة',
        'total_cases': 'إجمالي الحالات',
        'urgent_cases': 'الحالات العاجلة',
        'resolved_cases': 'الحالات المحلولة',
        'case_details': 'تفاصيل الحالة',
        'back_to_profile': 'العودة للملف الشخصي',
        'no_cases': 'لا توجد حالات اجتماعية بعد',
        'start_adding': 'ابدأ بإضافة حالتك الأولى',
        'publication_date': 'تاريخ النشر',
        'beneficiaries_list': 'قائمة المستفيدين',
        'media_gallery': 'معرض الوسائط',
        'latest_cases': 'أحدث الحالات',
        'all': 'الكل',
        'by_category': 'التوزيع حسب القطاع',
        'by_ong': 'التوزيع حسب المنظمة',
        'beneficiary_subtitle': 'متابعة وإدارة المستفيدين المساعدين',
        'ong_subtitle': 'نظرة عامة وإحصائيات المنظمات الشريكة',
        'filters': 'المرشحات',
        'filters_desc': 'استخدم المرشحات لتحديث الرسوم البيانية في الوقت الفعلي.',
        'reset_filters': 'إعادة تعيين',
        'reset_filters_long': 'إعادة تعيين المرشحات',
        'registered_orgs': 'المنظمات المسجلة',
        'validated_ongs': 'المنظمات الموثقة',
        'verification_req': 'مراجعة مطلوبة',
        'sector_impact': 'الأثر حسب القطاع',
        'validation_state': 'حالة التوثيق',
        'detailed_registry': 'السجل التفصيلي',
        'total_ongs': 'إجمالي المنظمات',
        'active': 'نشطة',
        'verification': 'التحقق',
        'contact': 'معلومات الاتصال',
        'admin_login': 'تسجيل دخول المسؤول',
        'admin_login_desc': 'المساحة المخصصة للمسؤولين',
    },
    'fr': {
        'title': 'ONG Connect',
        'dashboard': 'Tableau de bord',
        'administrators': 'Administrateurs',
        'ngos': 'ONGs',
        'social_cases': 'Cas Sociaux',
        'beneficiaries': 'Bénéficiaires',
        'categories': 'Catégories',
        'media': 'Médias',
        'add_new': 'Ajouter nouveau',
        'edit': 'Modifier',
        'delete': 'Supprimer',
        'save': 'Enregistrer',
        'cancel': 'Annuler',
        'confirm_delete': 'Êtes-vous sûr de vouloir supprimer cet élément ?',
        'actions': 'Actions',
        'name': 'Nom',
        'email': 'Email',
        'password': 'Mot de passe',
        'address': 'Adresse',
        'phone': 'Téléphone',
        'domain': 'Domaines d\'intervention',
        'status': 'Statut',
        'description': 'Description',
        'date': 'Date',
        'title_field': 'Titre',
        'first_name': 'Prénom',
        'last_name': 'Nom',
        'file_url': 'URL du fichier',
        'welcome': 'Bienvenue sur ONG Connect',
        'language': 'Langue',
        'switch_lang': 'العربية',
        'home': 'Accueil',
        'no_records': 'Aucun enregistrement.',
        'success_add': 'Ajouté avec succès',
        'success_edit': 'Modifié avec succès',
        'success_delete': 'Supprimé avec succès',
        'select_domain': '-- Sélectionner le domaine --',
        'select_domains': 'Sélectionnez un ou plusieurs domaines',
        'Santé': 'Santé',
        'Éducation': 'Éducation',
        'Logement': 'Logement',
        'Alimentation': 'Alimentation',
        # Status - ONG
        'enattente': 'En attente',
        'validé': 'Validé',
        'rejetée': 'Rejeté',
        # Status - Case
        'En cours': 'En cours',
        'Résolu': 'Résolu',
        'Urgent': 'Urgent',
        # General
        'search': 'Rechercher...',
        'logout': 'Déconnexion',
        'profile': 'Profil',
        'view_details': 'Voir détails',
        'donor_visitor': 'Donateur / Visiteur',
        'donor_desc': 'Découvrez les cas sociaux et contribuez à faire la différence.',
        'enter': 'Entrer',
        'ong_access': 'Espace ONG',
        'ong_desc': 'Connectez-vous pour gérer votre ONG et publier des cas.',
        'connect': 'Se connecter',
        'login_desc': 'Entrez vos identifiants pour accéder à votre espace.',
        'no_account': 'Pas encore de compte ?',
        'register_now': 'Inscrivez-vous maintenant',
        'dashboard_intro': 'Parcourez les derniers cas sociaux signalés par nos ONGs partenaires.',
        'current_logo': 'Logo actuel',
        'impact_tracking': 'Suivi de notre impact',
        'impact_desc': 'Voyez combien de vies ont été touchées par nos efforts collectifs.',
        'view_beneficiaries_stats': 'Voir les statistiques des bénéficiaires',
        'total_beneficiaries': 'Total des bénéficiaires',
        'top_ongs_impact': 'ONGs les plus impactantes',
        'my_profile': 'Mon profil',
        'my_cases': 'Mes cas sociaux',
        'add_case': 'Ajouter un cas',
        'total_cases': 'Total des cas',
        'urgent_cases': 'Cas urgents',
        'resolved_cases': 'Cas résolus',
        'case_details': 'Détails du cas',
        'back_to_profile': 'Retour au profil',
        'no_cases': 'Aucun cas social pour le moment',
        'start_adding': 'Commencez par ajouter votre premier cas',
        'publication_date': 'Date de publication',
        'beneficiaries_list': 'Liste des bénéficiaires',
        'media_gallery': 'Galerie média',
        'latest_cases': 'Derniers Cas',
        'all': 'Tous',
        'by_category': 'Distribution par Secteur',
        'by_ong': 'Distribution par ONG',
        'beneficiary_subtitle': 'Suivi et gestion des bénéficiaires assistés',
        'ong_subtitle': 'Vue d\'ensemble et statistiques des organisations partenaires',
        'filters': 'Filtres',
        'filters_desc': 'Utilisez les filtres pour affiner les graphiques en temps réel.',
        'reset_filters': 'Réinitialiser',
        'reset_filters_long': 'Réinitialiser les filtres',
        'registered_orgs': 'Organisations inscrites',
        'validated_ongs': 'ONGs validées',
        'verification_req': 'Vérification requise',
        'sector_impact': 'Impact par Secteur',
        'validation_state': 'État des Validations',
        'detailed_registry': 'Registre Détaillé',
        'total_ongs': 'Total ONGs',
        'active': 'Active',
        'verification': 'Vérification',
        'contact': 'Contact',
        'admin_login': 'Connexion Admin',
        'admin_login_desc': 'Espace réservé aux administrateurs',
    }
}

@app.before_request
def before_request():
    if 'lang' not in session:
        session['lang'] = 'ar'

@app.context_processor
def inject_conf_var():
    lang = session.get('lang', 'ar')
    return dict(
        lang=lang,
        t=TRANSLATIONS[lang],
        dir='rtl' if lang == 'ar' else 'ltr'
    )

# --- Decorators ---

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'admin':
            flash("Accès réservé aux administrateurs.", "danger")
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        with get_db() as conn:
            with conn.cursor() as cursor:
                # Todo: Use hashing in production
                cursor.execute("SELECT * FROM administrateur WHERE email=%s AND mot_de_passe=%s", (email, password))
                admin = cursor.fetchone()
                
                if admin:
                    session['user_type'] = 'admin'
                    session['user_id'] = admin['id_admin']
                    session['user_name'] = admin['nom']
                    flash('Bienvenue Administrateur.', 'success')
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash('Email ou mot de passe incorrect.', 'danger')
                    
    return render_template('admin/login.html')

@app.route('/create_default_admin')
def create_default_admin():
    # Helper to bootstrap admin - remove in production or protect
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM administrateur WHERE email='admin@ongconnect.com'")
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO administrateur (nom, email, mot_de_passe) VALUES ('Admin', 'admin@ongconnect.com', 'admin123')")
                    conn.commit()
                    return "Default admin created: admin@ongconnect.com / admin123"
                return "Admin already exists"
    except Exception as e:
        return f"Error: {e}"

@app.route('/set_language/<lang_code>')
def set_language(lang_code):
    if lang_code in ['ar', 'fr']:
        session['lang'] = lang_code
    return redirect(request.referrer or url_for('index'))

@app.route('/')
def index():
    return render_template('landing.html')

def get_pagination_iter(current_page, total_pages, left_edge=1, right_edge=1, left_current=1, right_current=1):
    """
    Generates a list of page numbers and None for ellipses.
    Example: 1 ... 4 5 6 ... 10
    """
    if total_pages <= 1:
        return []
    
    # If total pages is small, just show all
    if total_pages <= 7:
        return list(range(1, total_pages + 1))

    pages = []
    last = 0

    for num in range(1, total_pages + 1):
        if (num <= left_edge) or \
           (num > total_pages - right_edge) or \
           (abs(num - current_page) <= left_current): # Use left_current for both sides for simplicity/symmetry
            
            if last + 1 != num:
                pages.append(None) # Ellipsis
            pages.append(num)
            last = num
            
    return pages

@app.route('/public/dashboard')
def public_dashboard():
    page = request.args.get('page', 1, type=int)
    per_page = 3 # Adjusted to 3 so pagination is visible with few cases
    offset = (page - 1) * per_page
    
    with get_db() as conn:
        with conn.cursor() as cursor:
            # Count total cases
            cursor.execute("SELECT COUNT(*) as count FROM cas_social")
            total_cases = cursor.fetchone()['count']
            total_pages = (total_cases + per_page - 1) // per_page
            
            # Ensure page is within bounds
            if page < 1: page = 1
            if total_pages > 0 and page > total_pages: page = total_pages

            # Recalculate offset if page changed
            offset = (page - 1) * per_page

            # Fetch cases for current page
            sql = """
                SELECT c.*, o.nom_ong, o.logo_url, m.file_url 
                FROM cas_social c 
                LEFT JOIN ong o ON c.id_ong = o.id_ong
                LEFT JOIN (
                    SELECT id_cas_social, MIN(file_url) as file_url 
                    FROM media 
                    GROUP BY id_cas_social
                ) m ON c.id_cas_social = m.id_cas_social
                ORDER BY c.date_publication DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (per_page, offset))
            cases = cursor.fetchall()

            # Fetch random/latest ONGs for the dashboard
            cursor.execute("SELECT * FROM ong ORDER BY update_at DESC LIMIT 6")
            ongs = cursor.fetchall()
    
    pagination_iter = get_pagination_iter(page, total_pages)

    return render_template('public/dashboard.html', 
                         cases=cases, 
                         page=page, 
                         current_page=page, 
                         total_pages=total_pages,
                         pagination_iter=pagination_iter,
                         ongs=ongs)

@app.route('/public/beneficiaries')
def public_beneficiaries():
    with get_db() as conn:
        with conn.cursor() as cursor:
            # Fetch Statistics for initial render
            cursor.execute("SELECT COUNT(*) as count FROM beneficier")
            total_beneficiaries = cursor.fetchone()['count']
            
            # Fetch ONGs for filter
            cursor.execute("SELECT id_ong, nom_ong FROM ong ORDER BY nom_ong")
            ongs = cursor.fetchall()
            
            # Fetch Categories (Domains) from the categorie table
            cursor.execute("SELECT nomCategorie FROM categorie ORDER BY nomCategorie")
            categories = [c['nomCategorie'] for c in cursor.fetchall()]
            
            # Fetch Unique Locations (from beneficier or cas_social)
            cursor.execute("SELECT DISTINCT adresse FROM beneficier WHERE adresse IS NOT NULL AND adresse != ''")
            locations = [l['adresse'] for l in cursor.fetchall()]
            
    return render_template('public/beneficiaries.html', 
                         total_beneficiaries=total_beneficiaries,
                         filter_ongs=ongs,
                         filter_categories=categories,
                         filter_locations=locations)

@app.route('/api/stats/beneficiaries')
def api_beneficiary_stats():
    ong_id = request.args.get('ong_id')
    category = request.args.get('category')
    location = request.args.get('location')
    
    with get_db() as conn:
        with conn.cursor() as cursor:
            # Base query
            query = """
                SELECT b.id_beneficiaire, b.adresse as b_adresse, o.id_ong, o.nom_ong, o.domaine_intervation 
                FROM beneficier b
                JOIN cas_social c ON b.id_cas_social = c.id_cas_social
                JOIN ong o ON c.id_ong = o.id_ong
                WHERE 1=1
            """
            params = []
            
            if ong_id:
                query += " AND o.id_ong = %s"
                params.append(ong_id)
            if location:
                query += " AND (b.adresse LIKE %s OR c.adresse LIKE %s)"
                params.append(f"%{location}%")
                params.append(f"%{location}%")
            if category:
                query += " AND o.domaine_intervation LIKE %s"
                params.append(f"%{category}%")
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Process results for stats
            total = len(results)
            by_ong = {}
            by_category = {}
            by_location = {}
            
            for row in results:
                # By ONG
                ong_name = row['nom_ong']
                by_ong[ong_name] = by_ong.get(ong_name, 0) + 1
                
                # By Location (Simplistic: just use the address or first part)
                loc = row['b_adresse'] or "Inconnu"
                # If it's a long address, maybe try to extract city. For now, use as is.
                by_location[loc] = by_location.get(loc, 0) + 1
                
                # By Category (Domain)
                domains = [d.strip() for d in row['domaine_intervation'].split(',')]
                for d in domains:
                    if d:
                        by_category[d] = by_category.get(d, 0) + 1
            
            lang_code = session.get('lang', 'ar')
            t = TRANSLATIONS[lang_code]

            # Convert to list for Chart.js
            stats = {
                'total': total,
                'by_ong': [{'label': k, 'value': v} for k, v in sorted(by_ong.items(), key=lambda x: x[1], reverse=True)[:10]],
                'by_category': [{'label': t.get(k, k), 'value': v} for k, v in by_category.items()],
                'by_location': [{'label': k, 'value': v} for k, v in sorted(by_location.items(), key=lambda x: x[1], reverse=True)[:10]]
            }
            
            return jsonify(stats)


@app.route('/public/case/<int:id>')
def public_case_details(id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Fetch Case Details with ONG info
            sql = """
                SELECT c.*, o.nom_ong, o.logo_url, o.email as ong_email, o.telephone as ong_phone, o.adresse as ong_address
                FROM cas_social c
                LEFT JOIN ong o ON c.id_ong = o.id_ong
                WHERE c.id_cas_social = %s
            """
            cursor.execute(sql, (id,))
            case = cursor.fetchone()
            
            if not case:
                return "Case not found", 404
            
            # Fetch all media for this case
            cursor.execute("SELECT * FROM media WHERE id_cas_social = %s", (id,))
            media_list = cursor.fetchall()
            
    finally:
        conn.close()
    return render_template('public/case_details.html', case=case, media_list=media_list)


@app.route('/ong/login', methods=['GET', 'POST'])
def ong_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM ong WHERE email=%s AND mot_de_passe=%s", (email, password))
                ong = cursor.fetchone()
                
                if ong:
                    # Check validation status
                    status = ong.get('statut_de_validation', 'enattente')
                    
                    if status == 'validé':
                        session['user_type'] = 'ong'
                        session['user_id'] = ong['id_ong']
                        session['user_name'] = ong['nom_ong']
                        # Redirect to profile dashboard
                        return redirect(url_for('ong_profile'))
                    elif status == 'rejetée':
                         flash('Votre compte a été rejeté par un administrateur.', 'danger')
                    else: # enattente
                         flash('Votre compte est en attente de validation par un administrateur.', 'warning')

                else:
                    flash('Compte introuvable ou mot de passe incorrect', 'danger')
        finally:
            conn.close()
            
    return render_template('ong/login.html')

@app.route('/ong/profile')
def ong_profile():
    # Check if user is logged in as ONG
    if session.get('user_type') != 'ong':
        flash('Please login to access your profile', 'warning')
        return redirect(url_for('ong_login'))
    
    ong_id = session.get('user_id')
    
    with get_db() as conn:
        with conn.cursor() as cursor:
            # Fetch ONG details
            cursor.execute("SELECT * FROM ong WHERE id_ong=%s", (ong_id,))
            ong = cursor.fetchone()
            
            if not ong:
                flash('ONG not found', 'danger')
                session.clear()
                return redirect(url_for('ong_login'))
            
            # Fetch social cases for this ONG with first media image
            cursor.execute("""
                SELECT c.*, 
                       (SELECT file_url FROM media WHERE id_cas_social = c.id_cas_social LIMIT 1) as first_image
                FROM cas_social c
                WHERE c.id_ong=%s 
                ORDER BY c.date_publication DESC
            """, (ong_id,))
            cases = cursor.fetchall()
            
            # Calculate stats
            total_cases = len(cases)
            urgent_cases = sum(1 for case in cases if case['statut'] == 'Urgent')
            resolved_cases = sum(1 for case in cases if case['statut'] == 'Résolu')
    
    return render_template('ong/profile.html', 
                          ong=ong, 
                          cases=cases,
                          total_cases=total_cases,
                          urgent_cases=urgent_cases,
                          resolved_cases=resolved_cases)

@app.route('/ong/case/<int:id>')
def ong_case_details(id):
    # Check if user is logged in as ONG
    if session.get('user_type') != 'ong':
        flash('Please login to access case details', 'warning')
        return redirect(url_for('ong_login'))
    
    ong_id = session.get('user_id')
    
    with get_db() as conn:
        with conn.cursor() as cursor:
            # Fetch case details (ensure it belongs to this ONG)
            cursor.execute("""
                SELECT * FROM cas_social 
                WHERE id_cas_social=%s AND id_ong=%s
            """, (id, ong_id))
            case = cursor.fetchone()
            
            if not case:
                flash(TRANSLATIONS[session.get('lang', 'ar')].get('no_records', 'Case not found or access denied'), 'danger')
                return redirect(url_for('ong_profile'))
            
            # Fetch media for this case
            cursor.execute("SELECT * FROM media WHERE id_cas_social=%s", (id,))
            media_list = cursor.fetchall()
            
            # Fetch beneficiaries for this case
            cursor.execute("SELECT * FROM beneficier WHERE id_cas_social=%s", (id,))
            beneficiaries = cursor.fetchall()
    
    return render_template('ong/case_details.html', 
                          case=case, 
                          media_list=media_list, 
                          beneficiaries=beneficiaries)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
def admin_dashboard():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM administrateur")
            admins_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM ong")
            ngos_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM cas_social")
            cases_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM beneficier")
            beneficiaries_count = cursor.fetchone()['count']
            
            counts = {
                'admins': admins_count,
                'ngos': ngos_count,
                'cases': cases_count,
                'beneficiaries': beneficiaries_count
            }
    finally:
        conn.close()
    return render_template('index.html', counts=counts)



@app.route('/api/verify_ong_password', methods=['POST'])
def verify_ong_password():
    data = request.get_json()
    ong_id = data.get('ong_id')
    password = data.get('password')
    
    if not ong_id or not password:
        return {'success': False, 'message': 'Missing data'}, 400
        
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Note: storing passwords in plain text as per existing implementation
            cursor.execute("SELECT id_ong FROM ong WHERE id_ong=%s AND mot_de_passe=%s", (ong_id, password))
            result = cursor.fetchone()
            
            if result:
                # Set authorization in session for Edit actions
                session['authorized_ong_id'] = int(ong_id)
                return {'success': True}
            else:
                return {'success': False, 'message': 'Mot de passe incorrect'}, 401
    finally:
        conn.close()

@app.route('/api/verify_admin_credentials', methods=['POST'])
def verify_admin_credentials():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return {'success': False, 'message': 'Missing credentials'}, 400
        
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Todo: hash check in production
            cursor.execute("SELECT * FROM administrateur WHERE email=%s AND mot_de_passe=%s", (email, password))
            admin = cursor.fetchone()
            
            if admin:
                return {'success': True}
            else:
                return {'success': False, 'message': 'Invalid credentials'}, 401
    finally:
        conn.close()

# --- CRUD Routes ---

# 1. Administrateur
@app.route('/admins')
@admin_required
def list_admins():
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM administrateur")
            admins = cursor.fetchall()
    return render_template('administrateur/list.html', admins=admins)

@app.route('/admins/add', methods=['GET', 'POST'])
@admin_required
def add_admin():
    if request.method == 'POST':
        with get_db() as conn:
            with conn.cursor() as cursor:
                sql = "INSERT INTO administrateur (nom, email, mot_de_passe) VALUES (%s, %s, %s)"
                cursor.execute(sql, (request.form['nom'], request.form['email'], request.form['mot_de_passe']))
            conn.commit()
            flash(TRANSLATIONS[session.get('lang', 'ar')]['success_add'], 'success')
        return redirect(url_for('list_admins'))
    return render_template('administrateur/form.html', action='add')

@app.route('/admins/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_admin(id):
    conn = get_db_connection()
    try:
        if request.method == 'POST':
            with conn.cursor() as cursor:
                sql = "UPDATE administrateur SET nom=%s, email=%s, mot_de_passe=%s WHERE id_admin=%s"
                cursor.execute(sql, (request.form['nom'], request.form['email'], request.form['mot_de_passe'], id))
            conn.commit()
            flash(TRANSLATIONS[session.get('lang', 'ar')]['success_edit'], 'success')
            return redirect(url_for('list_admins'))
        else:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM administrateur WHERE id_admin=%s", (id,))
                admin = cursor.fetchone()
            if not admin:
                return "Admin not found", 404
            return render_template('administrateur/form.html', action='edit', admin=admin)
    finally:
        conn.close()

@app.route('/admins/delete/<int:id>')
@admin_required
def delete_admin(id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM administrateur WHERE id_admin=%s", (id,))
        conn.commit()
        flash(TRANSLATIONS[session.get('lang', 'ar')]['success_delete'], 'success')
    finally:
        conn.close()
    return redirect(url_for('list_admins'))

@app.route('/admin/action/<action>/<int:id>', methods=['GET', 'POST'])
def admin_ong_action(action, id):
    # This Action now requires implicit authentication via POST params if not logged in options
    # Or purely POST as per the prompt logic "needs email and password of admin"
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Verify Creds
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                 cursor.execute("SELECT * FROM administrateur WHERE email=%s AND mot_de_passe=%s", (email, password))
                 if not cursor.fetchone():
                     flash("Identifiants administrateur incorrects.", "danger")
                     return redirect(url_for('list_ngos'))
                     
                 # If valid admin, proceed
                 new_status = ''
                 if action == 'validate':
                    new_status = 'validé'
                 elif action == 'reject':
                    new_status = 'rejetée'
                 else:
                    return redirect(url_for('list_ngos'))

                 cursor.execute("UPDATE ong SET statut_de_validation=%s WHERE id_ong=%s", (new_status, id))
            conn.commit()
            flash(f"Statut de l'ONG mis à jour: {new_status}", 'success')
        finally:
            conn.close()
        return redirect(url_for('list_ngos'))

    # If GET, check if logged in as Admin (Legacy backup)
    if session.get('user_type') == 'admin':
         # Allow direct action if already logged in? Or enforce stricter check?
         # User request: "l effet ... est besoin de email et mot de passe d un admin"
         # Maybe stick to requiring prompt unless we want to be nice.
         # For consistency with the "Modal Everywhere" UI, we likely won't hit GET.
         # But if they type URL manually?
         pass
         
    # Fallback / Error
    flash("Action requires POST with credentials.", "warning")
    return redirect(url_for('list_ngos'))


# 2. ONG
@app.route('/ngos')
def list_ngos():
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM ong")
            ngos = cursor.fetchall()
            
            # Fetch categories for filter
            cursor.execute("SELECT nomCategorie FROM categorie ORDER BY nomCategorie")
            categories = [c['nomCategorie'] for c in cursor.fetchall()]

    return render_template('ong/list.html', ngos=ngos, filter_categories=categories)

@app.route('/api/stats/ongs')
def api_ong_stats():
    category = request.args.get('category')
    status = request.args.get('status')
    
    with get_db() as conn:
        with conn.cursor() as cursor:
            query = "SELECT * FROM ong WHERE 1=1"
            params = []
            
            if category:
                query += " AND domaine_intervation LIKE %s"
                params.append(f"%{category}%")
            if status:
                query += " AND statut_de_validation = %s"
                params.append(status)
                
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            total = len(results)
            valid = sum(1 for r in results if r['statut_de_validation'] == 'validé')
            pending = sum(1 for r in results if r['statut_de_validation'] == 'enattente')
            rejected = sum(1 for r in results if r['statut_de_validation'] == 'rejetée')
            
            by_category = {}
            for r in results:
                domains = [d.strip() for d in r['domaine_intervation'].split(',')]
                for d in domains:
                    if d:
                        by_category[d] = by_category.get(d, 0) + 1
            
            lang_code = session.get('lang', 'ar')
            t = TRANSLATIONS[lang_code]

            stats = {
                'total': total,
                'valid': valid,
                'pending': pending,
                'rejected': rejected,
                'by_category': [{'label': t.get(k, k), 'value': v} for k, v in by_category.items()],
                'by_status': [
                    {'label': t['validé'], 'value': valid},
                    {'label': t['enattente'], 'value': pending},
                    {'label': t['rejetée'], 'value': rejected}
                ]
            }
            return jsonify(stats)

@app.route('/ngos/add', methods=['GET', 'POST'])
def add_ong():
    if request.method == 'POST':
        # Validate Logo Presence
        if 'logo' not in request.files or request.files['logo'].filename == '':
            flash('Logo is mandatory for new ONGs.', 'danger')
            return redirect(request.url)
            
        try:
            with get_db() as conn:
                with conn.cursor() as cursor:
                    # Handle multiple domain selections
                    domains = request.form.getlist('domaine_intervation')
                    domains_str = ','.join(domains) if domains else ''
                    
                    sql = """
                        INSERT INTO ong (nom_ong, adresse, telephone, email, domaine_intervation, mot_de_passe)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        request.form['nom_ong'],
                        request.form['adresse'],
                        request.form['telephone'],
                        request.form['email'],
                        domains_str,
                        request.form['mot_de_passe']
                    ))
                    ong_id = cursor.lastrowid
                    
                    # Handle Logo Upload
                    if 'logo' in request.files:
                        file = request.files['logo']
                        if file and file.filename != '':
                            filename = secure_filename(file.filename)
                            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                            unique_filename = f"logo_{timestamp}_{filename}"
                            file_path = os.path.join(app.config['LOGO_FOLDER'], unique_filename)
                            file.save(file_path)
                            
                            web_path = f"uploads/logos/{unique_filename}"
                            cursor.execute("UPDATE ong SET logo_url=%s WHERE id_ong=%s", (web_path, ong_id))

                conn.commit()
                
                # Auto-login REMOVED -> Now wait for admin validation
                # session['user_type'] = 'ong'
                # session['user_id'] = ong_id
                # session['user_name'] = request.form['nom_ong']
                
                flash('Compte créé avec succès! Votre compte est en attente de validation par un administrateur.', 'info')
                return redirect(url_for('ong_login'))
        except Exception as e:
             # Basic error handling for duplicate email or other insertion errors
             flash(f"Error adding NGO: {e}", 'danger')
             return redirect(request.url)
        
        return redirect(url_for('ong_profile'))  # Redirect to profile dashboard

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM categorie")
            categories = cursor.fetchall()
        return render_template('ong/form.html', action='add', categories=categories)

@app.route('/ngos/edit/<int:id>', methods=['GET', 'POST'])
def edit_ong(id):
    # Check authorization (must be logged in as that ONG, Admin, or have temporarily verified password)
    authorized = False
    if session.get('user_type') == 'admin':
        authorized = True
    elif session.get('user_type') == 'ong' and session.get('user_id') == id:
        authorized = True
    elif session.get('authorized_ong_id') == id:
        authorized = True
        
    if not authorized:
        flash("Veuillez entrer le mot de passe de l'ONG pour modifier.", "warning")
        return redirect(url_for('list_ngos'))

    with get_db() as conn:
        try:
            if request.method == 'POST':
                with conn.cursor() as cursor:
                    # Handle multiple domain selections
                    domains = request.form.getlist('domaine_intervation')
                    domains_str = ','.join(domains) if domains else ''
                    
                    sql = """
                        UPDATE ong SET nom_ong=%s, adresse=%s, telephone=%s, email=%s, domaine_intervation=%s, mot_de_passe=%s
                        WHERE id_ong=%s
                    """
                    cursor.execute(sql, (
                        request.form['nom_ong'],
                        request.form['adresse'],
                        request.form['telephone'],
                        request.form['email'],
                        domains_str,
                        request.form['mot_de_passe'],
                        id
                    ))
                
                    # Handle Logo Upload Update
                    if 'logo' in request.files:
                        file = request.files['logo']
                        if file and file.filename != '':
                            filename = secure_filename(file.filename)
                            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                            unique_filename = f"logo_{timestamp}_{filename}"
                            file_path = os.path.join(app.config['LOGO_FOLDER'], unique_filename)
                            file.save(file_path)
                            
                            web_path = f"uploads/logos/{unique_filename}"
                            cursor.execute("UPDATE ong SET logo_url=%s WHERE id_ong=%s", (web_path, id))

                conn.commit()
                flash(TRANSLATIONS[session.get('lang', 'ar')]['success_edit'], 'success')
                return redirect(url_for('list_ngos'))
            else:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM ong WHERE id_ong=%s", (id,))
                    ong = cursor.fetchone()
                    
                    # Fetch categories for the dropdown
                    cursor.execute("SELECT * FROM categorie")
                    categories = cursor.fetchall()
                    
                if not ong:
                    return "NGO not found", 404
                return render_template('ong/form.html', action='edit', ong=ong, categories=categories)
        except Exception as e:
            flash(f"Error: {e}", "danger")
            return redirect(url_for('list_ngos'))

@app.route('/ngos/delete/<int:id>', methods=['POST'])
def delete_ong(id):
    # Password verification required for delete
    password = request.form.get('password')
    
    # Allow admin to delete without password (or with admin functionality, but user asked for password flow)
    # The requirement: "put the password of the ong they want to modify"
    # We will enforce password check unless it's a logged-in Admin session doing a bypass (optional, but safer to require password)
    
    # If user is admin, allow
    is_admin = session.get('user_type') == 'admin'
    
    if not is_admin:
         if not password:
            flash("Mot de passe requis pour la suppression.", "danger")
            return redirect(url_for('list_ngos'))
            
         conn = get_db_connection()
         try:
             with conn.cursor() as cursor:
                 cursor.execute("SELECT id_ong FROM ong WHERE id_ong=%s AND mot_de_passe=%s", (id, password))
                 if not cursor.fetchone():
                     flash("Mot de passe incorrect.", "danger")
                     return redirect(url_for('list_ngos'))
         finally:
             conn.close()

    with get_db() as conn:
        with conn.cursor() as cursor:
            # 1. Fetch all cases for this ONG to clean up their media files
            cursor.execute("SELECT id_cas_social FROM cas_social WHERE id_ong=%s", (id,))
            cases = cursor.fetchall()
            
            for case in cases:
                case_id = case['id_cas_social']
                # Fetch media for each case
                cursor.execute("SELECT file_url FROM media WHERE id_cas_social=%s", (case_id,))
                media_files = cursor.fetchall()
                for media in media_files:
                    if media['file_url']:
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(media['file_url']))
                        # Since file_url might be "uploads/media/...", basename ensures we target the right file in UPLOAD_FOLDER
                        # Or safer:
                        full_path = os.path.join('static', media['file_url'])
                        if os.path.exists(full_path):
                            try:
                                os.remove(full_path)
                            except Exception as e:
                                print(f"Error deleting file {full_path}: {e}")

            # 2. Delete ONG (Cascade will remove cases and media DB records, but we cleaned files first)
            cursor.execute("DELETE FROM ong WHERE id_ong=%s", (id,))
            conn.commit()
            
    flash(TRANSLATIONS[session.get('lang', 'ar')]['success_delete'], 'success')
    return redirect(url_for('list_ngos'))

@app.route('/ngos/details/<int:id>')
def detail_ong(id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Fetch ONG details
            cursor.execute("SELECT * FROM ong WHERE id_ong=%s", (id,))
            ong = cursor.fetchone()
            
            if not ong:
                return "NGO not found", 404
                
            # Fetch associated social cases with their first image
            cursor.execute("""
                SELECT c.*, 
                       (SELECT file_url FROM media WHERE id_cas_social = c.id_cas_social LIMIT 1) as first_image
                FROM cas_social c
                WHERE c.id_ong=%s
            """, (id,))
            cases = cursor.fetchall()
            
    finally:
        conn.close()
    return render_template('ong/details.html', ong=ong, cases=cases)

# 3. Cas Social
@app.route('/cases')
def list_cases():
    # Security: If ONG is logged in, show only their cases
    # If Admin is logged in, show all cases
    user_type = session.get('user_type')
    user_id = session.get('user_id')
    
    if user_type == 'admin':
        query = "SELECT c.*, o.nom_ong FROM cas_social c LEFT JOIN ong o ON c.id_ong = o.id_ong"
        params = ()
    elif user_type == 'ong':
        query = "SELECT c.*, o.nom_ong FROM cas_social c LEFT JOIN ong o ON c.id_ong = o.id_ong WHERE c.id_ong = %s"
        params = (user_id,)
    else:
        # For security, redirect unauthorized users to the public view
        flash("Veuillez vous connecter pour accéder à cette page.", "warning")
        return redirect(url_for('public_dashboard'))

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            cases = cursor.fetchall()
            
    return render_template('cas_social/list.html', cases=cases)

@app.route('/cases/add', methods=['GET', 'POST'])
def add_case():
    with get_db() as conn:
        try:
            if request.method == 'POST':
                with conn.cursor() as cursor:
                    sql = """
                        INSERT INTO cas_social (titre, description, adresse, date_publication, statut, id_ong)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        request.form['titre'],
                        request.form['description'],
                        request.form['adresse'],
                        request.form['date_publication'],
                        request.form['statut'],
                        request.form['id_ong']
                    ))
                    case_id = cursor.lastrowid

                    # Handle Media Uploads
                    if 'media' in request.files:
                        files = request.files.getlist('media')
                        for file in files:
                            if file and file.filename != '':
                                filename = secure_filename(file.filename)
                                # Create unique filename to prevent overwrites
                                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                                unique_filename = f"{timestamp}_{filename}"
                                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                                file.save(file_path)

                                # Save to media table
                                # URL path relative to static folder
                                web_path = f"uploads/media/{unique_filename}"
                                media_sql = "INSERT INTO media (id_cas_social, file_url, description_media) VALUES (%s, %s, %s)"
                                cursor.execute(media_sql, (case_id, web_path, "Media for case " + str(case_id)))
                conn.commit()
                flash(TRANSLATIONS[session.get('lang', 'ar')]['success_add'], 'success')
                return redirect(url_for('list_cases'))
            else:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM ong")
                    ngos = cursor.fetchall()
                return render_template('cas_social/form.html', action='add', ngos=ngos)
        except Exception as e:
            conn.rollback()
            flash(f"Error adding Case: {e}", 'danger')
            return redirect(url_for('list_cases'))

@app.route('/cases/edit/<int:id>', methods=['GET', 'POST'])
def edit_case(id):
    # Fetch case to check ownership
    conn = get_db_connection() 
    # Use separate connection for preliminary check to avoid nesting issues or just simple query
    try:
        with conn.cursor() as cursor:
             cursor.execute("SELECT id_ong FROM cas_social WHERE id_cas_social=%s", (id,))
             result = cursor.fetchone()
             if not result:
                 return "Case not found", 404
             case_ong_id = result['id_ong']
    finally:
        conn.close()

    # Authorization Check
    authorized = False
    if session.get('user_type') == 'admin':
        authorized = True
    elif session.get('user_type') == 'ong' and session.get('user_id') == case_ong_id:
        authorized = True
    elif session.get('authorized_ong_id') == case_ong_id:
        authorized = True
        
    if not authorized:
        flash("Veuillez entrer le mot de passe de l'ONG associée pour modifier.", "warning")
        # Redirect based on where they likely came from, or default to public dashboard
        return redirect(request.referrer or url_for('public_dashboard'))

    with get_db() as conn:
        try:
            if request.method == 'POST':
                with conn.cursor() as cursor:
                    sql = """
                        UPDATE cas_social SET titre=%s, description=%s, adresse=%s, date_publication=%s, statut=%s, id_ong=%s
                        WHERE id_cas_social=%s
                    """
                    cursor.execute(sql, (
                        request.form['titre'],
                        request.form['description'],
                        request.form['adresse'],
                        request.form['date_publication'],
                        request.form['statut'],
                        request.form['id_ong'],
                        id
                    ))

                    # Handle New Media Uploads
                    if 'media' in request.files:
                        files = request.files.getlist('media')
                        for file in files:
                            if file and file.filename != '':
                                filename = secure_filename(file.filename)
                                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                                unique_filename = f"{timestamp}_{filename}"
                                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                                file.save(file_path)

                                web_path = f"uploads/media/{unique_filename}"
                                media_sql = "INSERT INTO media (id_cas_social, file_url, description_media) VALUES (%s, %s, %s)"
                                cursor.execute(media_sql, (id, web_path, "Media for case " + str(id)))

                conn.commit()
                flash(TRANSLATIONS[session.get('lang', 'ar')]['success_edit'], 'success')
                return redirect(url_for('list_cases'))
            else:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM cas_social WHERE id_cas_social=%s", (id,))
                    case = cursor.fetchone()
                    cursor.execute("SELECT * FROM ong")
                    ngos = cursor.fetchall()
                    # Fetch existing media
                    cursor.execute("SELECT * FROM media WHERE id_cas_social=%s", (id,))
                    media_list = cursor.fetchall()
                    
                if not case:
                    return "Case not found", 404
                return render_template('cas_social/form.html', action='edit', case=case, ngos=ngos, media_list=media_list)
        except Exception as e:
            conn.rollback()
            flash(f"Error editing case: {e}", 'danger')
            return redirect(url_for('list_cases'))

@app.route('/cases/update-status/<int:id>', methods=['POST'])
def update_case_status(id):
    """Quick status update endpoint for AJAX calls"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['En cours', 'Résolu', 'Urgent']:
            return {'success': False, 'message': 'Invalid status'}, 400
        
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE cas_social SET statut=%s WHERE id_cas_social=%s",
                    (new_status, id)
                )
            conn.commit()
        
        return {'success': True, 'message': 'Status updated successfully'}
    except Exception as e:
        return {'success': False, 'message': str(e)}, 500


@app.route('/cases/delete/<int:id>', methods=['POST'])
def delete_case(id):
    password = request.form.get('password')
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Check Case and ONG
            cursor.execute("SELECT id_ong FROM cas_social WHERE id_cas_social=%s", (id,))
            case_data = cursor.fetchone()
            if not case_data:
                flash("Cas introuvable.", "danger")
                return redirect(url_for('public_dashboard'))
                
            ong_id = case_data['id_ong']
            
            # Verify Password (unless Admin)
            is_admin = session.get('user_type') == 'admin'
            if not is_admin:
                if not password:
                    flash("Mot de passe requis.", "danger")
                    return redirect(request.referrer or url_for('public_dashboard'))
                    
                cursor.execute("SELECT id_ong FROM ong WHERE id_ong=%s AND mot_de_passe=%s", (ong_id, password))
                if not cursor.fetchone():
                    flash("Mot de passe incorrect.", "danger")
                    return redirect(request.referrer or url_for('public_dashboard'))

            # 1. Fetch associated media to delete physical files
            cursor.execute("SELECT * FROM media WHERE id_cas_social=%s", (id,))
            media_files = cursor.fetchall()
            
            for media in media_files:
                # Assuming file_url is stored relative to static/ e.g. "uploads/media/..."
                # And we need to remove it from the system
                if media['file_url']:
                    file_path = os.path.join('static', media['file_url'])
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except Exception as e:
                            print(f"could not delete file {file_path}: {e}")

            # 2. Delete the media records from DB
            cursor.execute("DELETE FROM media WHERE id_cas_social=%s", (id,))
            
            # 3. Now safe to delete the case
            cursor.execute("DELETE FROM cas_social WHERE id_cas_social=%s", (id,))
        conn.commit()
        flash(TRANSLATIONS[session.get('lang', 'ar')]['success_delete'], 'success')
    except Exception as e:
        conn.rollback()
        flash(f"Error deleting case: {e}", 'danger')
    finally:
        conn.close()
    
    # Return to the implementation reference (Edit Case page is gone, so go to dashboard or list)
    return redirect(url_for('public_dashboard'))



@app.route('/media/delete/<int:id>')
def delete_media(id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 1. Get media info to find file path and correct redirect
            cursor.execute("SELECT * FROM media WHERE id_media=%s", (id,))
            media = cursor.fetchone()
            
            if not media:
                flash("Media not found", "danger")
                return redirect(url_for('list_cases'))
                
            case_id = media['id_cas_social']
            
            # 2. Delete Physical File
            if media['file_url']:
                file_path = os.path.join('static', media['file_url'])
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Could not delete file {file_path}: {e}")
            
            # 3. Delete DB Record
            cursor.execute("DELETE FROM media WHERE id_media=%s", (id,))
            
        conn.commit()
        flash(TRANSLATIONS[session.get('lang', 'ar')]['success_delete'], 'success')
        return redirect(url_for('edit_case', id=case_id))
    finally:
        conn.close()

# 4. Beneficier
@app.route('/beneficiaries')
def list_beneficiaries():
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT b.*, c.titre as cas_titre FROM beneficier b LEFT JOIN cas_social c ON b.id_cas_social = c.id_cas_social")
            beneficiaries = cursor.fetchall()
            
            # Fetch ONGs for filter
            cursor.execute("SELECT id_ong, nom_ong FROM ong ORDER BY nom_ong")
            ongs = cursor.fetchall()
            
            # Fetch Categories
            cursor.execute("SELECT nomCategorie FROM categorie ORDER BY nomCategorie")
            categories = [c['nomCategorie'] for c in cursor.fetchall()]
            
            # Fetch Locations
            cursor.execute("SELECT DISTINCT adresse FROM beneficier WHERE adresse IS NOT NULL AND adresse != ''")
            locations = [l['adresse'] for l in cursor.fetchall()]

    return render_template('beneficier/list.html', 
                         beneficiaries=beneficiaries,
                         filter_ongs=ongs,
                         filter_categories=categories,
                         filter_locations=locations,
                         total_beneficiaries=len(beneficiaries))

@app.route('/beneficiaries/add', methods=['GET', 'POST'])
def add_beneficiary():
    with get_db() as conn:
        try:
            if request.method == 'POST':
                with conn.cursor() as cursor:
                    sql = """
                        INSERT INTO beneficier (nom, prenom, adresse, description_situation, id_cas_social)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        request.form['nom'],
                        request.form['prenom'],
                        request.form['adresse'],
                        request.form['description_situation'],
                        request.form['id_cas_social']
                    ))
                conn.commit()
                flash(TRANSLATIONS[session.get('lang', 'ar')]['success_add'], 'success')
                return redirect(url_for('list_beneficiaries'))
            else:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM cas_social")
                    cases = cursor.fetchall()
                return render_template('beneficier/form.html', action='add', cases=cases)
        except Exception as e:
            flash(f"Error: {e}", "danger")
            return redirect(url_for('list_beneficiaries'))

@app.route('/beneficiaries/edit/<int:id>', methods=['GET', 'POST'])
def edit_beneficiary(id):
    conn = get_db_connection()
    try:
        if request.method == 'POST':
            with conn.cursor() as cursor:
                sql = """
                    UPDATE beneficier SET nom=%s, prenom=%s, adresse=%s, description_situation=%s, id_cas_social=%s
                    WHERE id_beneficiaire=%s
                """
                cursor.execute(sql, (
                    request.form['nom'],
                    request.form['prenom'],
                    request.form['adresse'],
                    request.form['description_situation'],
                    request.form['id_cas_social'],
                    id
                ))
            conn.commit()
            flash(TRANSLATIONS[session.get('lang', 'ar')]['success_edit'], 'success')
            return redirect(url_for('list_beneficiaries'))
        else:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM beneficier WHERE id_beneficiaire=%s", (id,))
                beneficiary = cursor.fetchone()
                cursor.execute("SELECT * FROM cas_social")
                cases = cursor.fetchall()
            if not beneficiary:
                return "Beneficiary not found", 404
            return render_template('beneficier/form.html', action='edit', beneficiary=beneficiary, cases=cases)
    finally:
        conn.close()

@app.route('/beneficiaries/delete/<int:id>')
def delete_beneficiary(id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM beneficier WHERE id_beneficiaire=%s", (id,))
        conn.commit()
        flash(TRANSLATIONS[session.get('lang', 'ar')]['success_delete'], 'success')
    finally:
        conn.close()
    return redirect(url_for('list_beneficiaries'))

# 5. Categorie
@app.route('/categories')
def list_categories():
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM categorie")
            categories = cursor.fetchall()
    return render_template('categorie/list.html', categories=categories)


@app.route('/categories/add', methods=['GET', 'POST'])
@admin_required
def add_category():
    if request.method == 'POST':
        with get_db() as conn:
            with conn.cursor() as cursor:
                sql = "INSERT INTO categorie (nomCategorie, description) VALUES (%s, %s)"
                cursor.execute(sql, (request.form['nomCategorie'], request.form['description']))
            conn.commit()
            flash(TRANSLATIONS[session.get('lang', 'ar')]['success_add'], 'success')
        return redirect(url_for('list_categories'))
    return render_template('categorie/form.html', action='add')


@app.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_category(id):
    with get_db() as conn:
        try:
            if request.method == 'POST':
                with conn.cursor() as cursor:
                    sql = "UPDATE categorie SET nomCategorie=%s, description=%s WHERE idCategorie=%s"
                    cursor.execute(sql, (request.form['nomCategorie'], request.form['description'], id))
                conn.commit()
                flash(TRANSLATIONS[session.get('lang', 'ar')]['success_edit'], 'success')
                return redirect(url_for('list_categories'))
            else:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM categorie WHERE idCategorie=%s", (id,))
                    category = cursor.fetchone()
                if not category:
                    return "Category not found", 404
                return render_template('categorie/form.html', action='edit', category=category)
        except Exception as e:
            flash(f"Error: {e}", "danger")
            return redirect(url_for('list_categories'))


@app.route('/categories/delete/<int:id>')
@admin_required
def delete_category(id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM categorie WHERE idCategorie=%s", (id,))
        conn.commit()
        flash(TRANSLATIONS[session.get('lang', 'ar')]['success_delete'], 'success')
    return redirect(url_for('list_categories'))





if __name__ == '__main__':
    init_db()
    app.run(debug=True)
