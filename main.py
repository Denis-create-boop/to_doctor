import os
import re
import secrets
import sqlite3
from pathlib import Path
from datetime import datetime, date, timedelta, time
from flask import Flask, render_template, request, redirect, url_for, abort, session, g
from werkzeug.middleware.proxy_fix import ProxyFix

ROOT = Path(__file__).resolve().parent
app = Flask(__name__, instance_relative_config=True)
Path(app.instance_path).mkdir(parents=True, exist_ok=True)
secret_file = Path(app.instance_path) / 'secret.key'
if not os.environ.get('SECRET_KEY') and not secret_file.exists():
    try:
        with secret_file.open('x') as f:
            f.write(secrets.token_hex(32))
        secret_file.chmod(0o600)
    except FileExistsError:
        pass
app.config.update(SECRET_KEY=os.environ.get('SECRET_KEY') or secret_file.read_text(), DATABASE=str(Path(app.instance_path)/'clinic.sqlite3'), SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax', MAX_CONTENT_LENGTH=16384)
# Only trust proxy headers in the known development environment.
if os.environ.get('CODESPACE_NAME'):
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)
    app.config['SESSION_COOKIE_SECURE'] = True

SPECIALTIES = [
 ('terapevts','Терапия','Терапевт','✚','Общее самочувствие и профилактика',0),
 ('surgeons','Хирургия','Хирург','✦','Консультация хирурга',0),
 ('ophthalmologists','Офтальмология','Офтальмолог','◉','Зрение и здоровье глаз',0),
 ('ents','Оториноларингология','ЛОР','◌','Ухо, горло и нос',1),
 ('traumatologists','Травматология','Травматолог','✧','Травмы и восстановление',2),
 ('dantists','Стоматология','Стоматолог','◇','Здоровье зубов и дёсен',1),
 ('pediatricians','Педиатрия','Педиатр','♡','Здоровье детей',2),
 ('orthopedics','Ортопедия','Ортопед','⌁','Суставы и опорно-двигательная система',2),
 ('neurologists','Неврология','Невролог','⌘','Нервная система',0),
 ('cardiologists','Кардиология','Кардиолог','♥','Сердце и сосуды',2),
 ('genicologists','Гинекология','Гинеколог','❀','Женское здоровье',0),
 ('psychiatrists','Психиатрия','Психиатр','☼','Психическое здоровье',1),
 ('narcologists','Наркология','Нарколог','✺','Консультация специалиста',2),
 ('urologists','Урология','Уролог','◈','Мочевыделительная система',2),
 ('praktologists','Проктология','Проктолог','✣','Консультация специалиста',1),
 ('pulmanologists','Пульмонология','Пульмонолог','≈','Органы дыхания',0),
]
# Fictional demonstration names, not verified medical professionals.
NAMES = [
  [
    "Вересова Алиса Михайловна",
    "Ладомиров Артём Олегович",
    "Светлогоров Кирилл Ильич",
    "Яснопольский Максим Андреевич",
    "Речникова Софья Павловна",
    "Миролюбова Дарья Романовна"
  ],
  [
    "Лазурина Полина Игоревна",
    "Зоринцев Матвей Сергеевич",
    "Ветлин Даниил Аркадьевич",
    "Озерцова Ева Николаевна",
    "Луговец Тимур Алексеевич",
    "Рассветов Глеб Денисович"
  ],
  [
    "Тихолесов Марк Антонович",
    "Серебрина Вера Дмитриевна",
    "Мелодин Оскар Львович",
    "Кленовский Илья Петрович",
    "Янтарева Милана Викторовна",
    "Ветроградов Роман Юрьевич"
  ]
]
CODES = [
 ['bublic','prokopenco','andropov','krinin','resnicova','tronina'],
 ['siczhina','polezhaykin','subin','dicareva','sidorov','tihonov'],
 ['sviridov','sonina','timoshuck','kuchui','agafonova','smirnov'],
]
SLOTS = [f'{h:02d}:{m:02d}' for h in range(8,12) for m in (0,30)] + ['12:00']
DAYS = 30

def db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'], timeout=10)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys=ON')
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    conn = g.pop('db',None)
    if conn is not None:
        conn.close()

def init_db():
    conn = db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS doctors (
      id INTEGER PRIMARY KEY, specialty TEXT NOT NULL, code TEXT NOT NULL,
      name TEXT NOT NULL, UNIQUE(specialty, code)
    );
    CREATE TABLE IF NOT EXISTS appointments (
      id INTEGER PRIMARY KEY, doctor_id INTEGER NOT NULL REFERENCES doctors(id),
      visit_date TEXT NOT NULL, visit_time TEXT NOT NULL,
      patient_name TEXT NOT NULL, snils TEXT, birth_date TEXT, reference TEXT NOT NULL UNIQUE,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(doctor_id, visit_date, visit_time)
    );
    """)
    columns = {r['name'] for r in conn.execute('PRAGMA table_info(appointments)')}
    for column in ('snils', 'birth_date'):
        if column not in columns:
            conn.execute(f'ALTER TABLE appointments ADD COLUMN {column} TEXT')
    for slug, label, role, icon, desc, group in SPECIALTIES:
        conn.executemany('INSERT INTO doctors(specialty,code,name) VALUES(?,?,?) ON CONFLICT(specialty,code) DO UPDATE SET name=excluded.name',
            [(slug,code,name) for code,name in zip(CODES[group],NAMES[group])])
    conn.commit()

def now():
    return datetime.now()

def valid_date(value):
    try:
        day = date.fromisoformat(value or '')
    except ValueError:
        return None
    today = now().date()
    return day if today <= day <= today + timedelta(days=DAYS-1) else None

def slots_for(doctor_id, day):
    occupied = {r['visit_time'] for r in db().execute(
        'SELECT visit_time FROM appointments WHERE doctor_id=? AND visit_date=?',(doctor_id,day.isoformat()))}
    current = now()
    return [{'time':s,'available':s not in occupied and datetime.combine(day,time.fromisoformat(s))>current,
             'occupied':s in occupied} for s in SLOTS]

def get_doctor(doctor_id):
    row = db().execute('SELECT * FROM doctors WHERE id=?',(doctor_id,)).fetchone()
    if row is None: abort(404)
    return row

def csrf():
    if 'csrf' not in session: session['csrf'] = secrets.token_urlsafe(32)
    return session['csrf']

@app.after_request
def security(response):
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Referrer-Policy']='same-origin'
    response.headers['X-Frame-Options']='DENY'
    response.headers['Cache-Control']='no-store'
    return response

@app.get('/')
def index():
    return render_template('home.html', specialties=SPECIALTIES)

@app.get('/specialty/<slug>')
@app.get('/<slug>')
def specialty(slug):
    spec = next((s for s in SPECIALTIES if s[0]==slug),None)
    if spec is None: abort(404)
    doctors = db().execute('SELECT * FROM doctors WHERE specialty=? ORDER BY id',(slug,)).fetchall()
    return render_template('doctors.html',spec=spec,doctors=doctors)

@app.route('/book/<int:doctor_id>',methods=['GET','POST'])
def book(doctor_id):
    doctor=get_doctor(doctor_id)
    spec=next(s for s in SPECIALTIES if s[0]==doctor['specialty'])
    today=now().date()
    dates=[today+timedelta(days=i) for i in range(DAYS)]
    raw=request.form.get('day') if request.method=='POST' else request.args.get('day')
    day=valid_date(raw) if raw else today
    if day is None: abort(400)
    error=''
    name=''
    selected=''
    snils=''
    birth_date=''
    status=200
    if request.method=='POST':
        if not secrets.compare_digest(request.form.get('csrf',''),session.get('csrf','invalid')):
            abort(400)
        name=' '.join(request.form.get('patient_name','').split())
        selected=request.form.get('visit_time','')
        snils=request.form.get('snils','').strip()
        birth_date=request.form.get('birth_date','').strip()
        digits=re.sub(r'[ -]', '', snils)
        try:
            born=date.fromisoformat(birth_date)
            valid_birth=date(1900,1,1)<=born<=today
        except ValueError:
            valid_birth=False
        if not 3<=len(name)<=120:
            error='Введите ФИО (от 3 до 120 символов).'
        elif not re.fullmatch(r'[0-9]{11}',digits):
            error='Введите СНИЛС: 11 цифр.'
        elif not valid_birth:
            error='Укажите корректную дату рождения, не позднее сегодняшнего дня.'
        elif selected not in SLOTS or datetime.combine(day,time.fromisoformat(selected))<=now():
            error='Выберите доступное время в будущем.'
        else:
            reference=secrets.token_urlsafe(24)
            try:
                with db():
                    db().execute('INSERT INTO appointments(doctor_id,visit_date,visit_time,patient_name,snils,birth_date,reference) VALUES(?,?,?,?,?,?,?)',
                        (doctor_id,day.isoformat(),selected,name,digits,born.isoformat(),reference))
                session['last_booking']=reference
                return redirect(url_for('confirmation'))
            except sqlite3.IntegrityError:
                error='Это время уже занято. Пожалуйста, выберите другое.'
                status=409
        if not error: status=200
        elif status!=409: status=400
    return render_template('booking.html',doctor=doctor,spec=spec,dates=dates,day=day,slots=slots_for(doctor_id,day),csrf=csrf(),error=error,name=name,selected=selected,snils=snils,birth_date=birth_date,today=today),status

@app.get('/confirmation')
def confirmation():
    reference=session.get('last_booking')
    row=db().execute('SELECT a.visit_date,a.visit_time,d.name,d.specialty FROM appointments a JOIN doctors d ON d.id=a.doctor_id WHERE a.reference=?',(reference,)).fetchone()
    if row is None: return redirect(url_for('index'))
    spec=next(s for s in SPECIALTIES if s[0]==row['specialty'])
    return render_template('confirmation.html',booking=row,spec=spec)

@app.cli.command('init-db')
def init_command():
    init_db()
    print('SQLite initialized')

with app.app_context():
    init_db()

if __name__=='__main__':
    app.run(host='0.0.0.0',port=5000)
