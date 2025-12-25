-- Optimized Sample Data: 18 Social Cases
-- This script dynamically picks a random existing ONG for each case using LIMIT 1
-- Safe to run regardless of your specific ONG IDs

-- 1. Health Cases
INSERT INTO cas_social (titre, description, adresse, statut, id_ong, date_publication)
SELECT 'عائلة تحتاج إلى علاج طبي عاجل', 'عائلة مكونة من 5 أفراد تعاني من ظروف صحية صعبة. الأب يحتاج إلى عملية جراحية عاجلة ولكن لا يملك التأمين الصحي.', 'نواكشوط، تيارت', 'Urgent', id_ong, CURDATE()
FROM ong ORDER BY RAND() LIMIT 1;

INSERT INTO cas_social (titre, description, adresse, statut, id_ong, date_publication)
SELECT 'مريض سكري يحتاج إلى دواء منتظم', 'رجل مسن يعاني من داء السكري المزمن. يحتاج إلى الأنسولين والأدوية بشكل يومي لكن دخله المحدود لا يسمح بذلك.', 'نواكشوط، توجنين', 'En cours', id_ong, DATE_SUB(CURDATE(), INTERVAL 2 DAY)
FROM ong ORDER BY RAND() LIMIT 1;

INSERT INTO cas_social (titre, description, adresse, statut, id_ong, date_publication)
SELECT 'امرأة حامل تحتاج إلى رعاية صحية', 'امرأة حامل في شهرها الثامن تعاني من مضاعفات صحية. تحتاج إلى متابعة طبية دقيقة لضمان ولادة آمنة.', 'نواكشوط، المينا', 'En cours', id_ong, DATE_SUB(CURDATE(), INTERVAL 10 DAY)
FROM ong ORDER BY RAND() LIMIT 1;

INSERT INTO cas_social (titre, description, adresse, statut, id_ong, date_publication)
SELECT 'مريضة سرطان تحتاج إلى علاج كيميائي', 'امرأة في الأربعينات تعاني من سرطان الثدي. تحتاج إلى جلسات علاج كيميائي مكلفة. الأسرة استنفدت مدخراتها.', 'نواكشوط، كرفور', 'Urgent', id_ong, CURDATE()
FROM ong ORDER BY RAND() LIMIT 1;


-- 2. Education Cases
INSERT INTO cas_social (titre, description, adresse, statut, id_ong, date_publication)
SELECT 'طفل يحتاج إلى مستلزمات مدرسية', 'طفل يتيم في السنة الرابعة ابتدائي. الأسرة غير قادرة على توفير الكتب والأدوات المدرسية.', 'نواكشوط، الميناء', 'En cours', id_ong, DATE_SUB(CURDATE(), INTERVAL 3 DAY)
FROM ong ORDER BY RAND() LIMIT 1;

INSERT INTO cas_social (titre, description, adresse, statut, id_ong, date_publication)
SELECT 'طالبة متفوقة تحتاج إلى رسوم جامعية', 'طالبة حاصلة على الباكالوريا بامتياز عاجزة عن دفع رسوم التسجيل الجامعي. حلمها دراسة الطب.', 'نواكشوط، تفرغ زينة', 'Résolu', id_ong, DATE_SUB(CURDATE(), INTERVAL 15 DAY)
FROM ong ORDER BY RAND() LIMIT 1;

INSERT INTO cas_social (titre, description, adresse, statut, id_ong, date_publication)
SELECT 'مدرسة قرآنية تحتاج إلى دعم', 'مدرسة تستقبل 50 طفلاً يتيماً. تحتاج إلى ألواح، مصاحف، وسجاد للصلاة.', 'نواكشوط، الموافقية', 'Résolu', id_ong, DATE_SUB(CURDATE(), INTERVAL 20 DAY)
FROM ong ORDER BY RAND() LIMIT 1;

INSERT INTO cas_social (titre, description, adresse, statut, id_ong, date_publication)
SELECT 'أطفال محرومون من التعليم', 'حي مهمش به 15 طفلاً خارج المدرسة. نسعى لإنشاء فصل دراسي مؤقت وتوفير معلم.', 'نواكشوط، الميناء', 'En cours', id_ong, DATE_SUB(CURDATE(), INTERVAL 6 DAY)
FROM ong ORDER BY RAND() LIMIT 1;


-- 3. Housing Cases
INSERT INTO cas_social (titre, description, adresse, statut, id_ong, date_publication)
SELECT 'منزل متضرر يحتاج للترميم', 'منزل عائلة فقيرة تضرر بسبب الأمطار. السقف مهدد بالانهيار والجدران متصدعة.', 'نواكشوط، السبخة', 'En cours', id_ong, DATE_SUB(CURDATE(), INTERVAL 7 DAY)
FROM ong ORDER BY RAND() LIMIT 1;

INSERT INTO cas_social (titre, description, adresse, statut, id_ong, date_publication)
SELECT 'عائلة نازحة تحتاج إلى مأوى', 'عائلة نازحة تعيش في العراء. يحتاجون إلى خيمة أو غرفة مؤقتة لحمايتهم من البرد.', 'نواكشوط، الرياض', 'Urgent', id_ong, CURDATE()
FROM ong ORDER BY RAND() LIMIT 1;

INSERT INTO cas_social (titre, description, adresse, statut, id_ong, date_publication)
SELECT 'عائلة بدون كهرباء', 'عائلة فقيرة انقطعت عنها الكهرباء منذ 3 أشهر بسبب الديون. الأطفال يدرسون على الشموع.', 'نواكشوط، دار النعيم', 'Urgent', id_ong, CURDATE()
FROM ong ORDER BY RAND() LIMIT 1;

INSERT INTO cas_social (titre, description, adresse, statut, id_ong, date_publication)
SELECT 'ترميم سقف متهالك', 'منزل يأوي أيتاماً وسقفه متهالك جداً. نحتاج مواد بناء لإصلاحه قبل موسم الأمطار.', 'نواكشوط، توجنين', 'En cours', id_ong, DATE_SUB(CURDATE(), INTERVAL 5 DAY)
FROM ong ORDER BY RAND() LIMIT 1;


-- 4. Food & Water Cases
INSERT INTO cas_social (titre, description, adresse, statut, id_ong, date_publication)
SELECT 'أرملة تحتاج إلى مساعدة غذائية', 'أرملة تعيل 4 أطفال ولا تملك دخلاً. تحتاج سلة غذائية شهرية (أرز، سكر، زيت).', 'نواكشوط، عرفات', 'Urgent', id_ong, CURDATE()
FROM ong ORDER BY RAND() LIMIT 1;

INSERT INTO cas_social (titre, description, adresse, statut, id_ong, date_publication)
SELECT 'عائلة بدون ماء شرب', 'حي نائي لا يصله الماء. السكان يشترون الماء بأسعار غالية. نحتاج حفر بئر أو خزان.', 'نواكشوط، عرفات', 'Urgent', id_ong, CURDATE()
FROM ong ORDER BY RAND() LIMIT 1;

INSERT INTO cas_social (titre, description, adresse, statut, id_ong, date_publication)
SELECT 'إفطار لأسرة متعففة', 'أسرة لا تجد قوت يومها. نحتاج توفير مواد غذائية أساسية لهم.', 'نواكشوط، لكصر', 'En cours', id_ong, DATE_SUB(CURDATE(), INTERVAL 4 DAY)
FROM ong ORDER BY RAND() LIMIT 1;

INSERT INTO cas_social (titre, description, adresse, statut, id_ong, date_publication)
SELECT 'حفر بئر لقرية', 'قرية صغيرة تعاني من العطش. حفر بئر سطحي سيوفر الماء لـ 20 عائلة.', 'الداخل', 'En cours', id_ong, DATE_SUB(CURDATE(), INTERVAL 30 DAY)
FROM ong ORDER BY RAND() LIMIT 1;


-- 5. Misc Cases
INSERT INTO cas_social (titre, description, adresse, statut, id_ong, date_publication)
SELECT 'شاب معاق يحتاج كرسي متحرك', 'شاب أصيب بشلل ويحتاج كرسي متحرك للتنقل والذهاب للعمل.', 'نواكشوط، تيارت', 'En cours', id_ong, DATE_SUB(CURDATE(), INTERVAL 4 DAY)
FROM ong ORDER BY RAND() LIMIT 1;

INSERT INTO cas_social (titre, description, adresse, statut, id_ong, date_publication)
SELECT 'مركز محو أمية للنساء', 'تجهيز قاعة لتعليم النساء القراءة والكتابة. نحتاج طاولات وسبورة.', 'نواكشوط، تيارت', 'Résolu', id_ong, DATE_SUB(CURDATE(), INTERVAL 25 DAY)
FROM ong ORDER BY RAND() LIMIT 1;
