
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
            
            # Fetch social cases for this ONG
            cursor.execute("""
                SELECT * FROM cas_social 
                WHERE id_ong=%s 
                ORDER BY date_publication DESC
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
