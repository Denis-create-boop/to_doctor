from flask import Flask, render_template, request
import json
from datetime import datetime
from datetime import date as DATE
import calendar



app = Flask(__name__)

@app.route('/')
def index():
    ls = {'title': 'base'}
    return render_template('base.html', ls=ls)

@app.route('/terapevts')
def terapevts():
    ls = {'title': 'terapevts'}
    return render_template('terapevts/terapevts_base.html', ls=ls)


@app.route('/surgeons')
def surgeons():
    ls = {'title': 'surgeons'}
    return render_template('surgeons/surgeons_base.html', ls=ls)

@app.route('/ophthalmologists')
def ophthalmologists():
    ls = {'title': 'ophthalmologists'}
    return render_template('ophthalmologists/ophthalmologists_base.html', ls=ls)

@app.route('/ents')
def ents():
    ls = {'title': 'ents'}
    return render_template('ents/ents_base.html', ls=ls)


@app.route('/traumatologists')
def traumatologists():
    ls = {'title': 'traumatologist'}
    return render_template('traumatologists/traumatologists_base.html', ls=ls)


@app.route('/dantists')
def dantists():
    ls = {'title': 'dantists'}
    return render_template('dantists/dantists_base.html', ls=ls)


@app.route('/pediatricians')
def pediatricians():
    ls = {'title': 'pediatricians'}
    return render_template('pediatricians/pediatricians_base.html', ls=ls)


@app.route('/orthopedics')
def orthopedics():
    ls = {'title': 'orthopedics'}
    return render_template('orthopedics/orthopedics_base.html', ls=ls)


@app.route('/neurologists')
def neurologists():
    ls = {'title': 'neurologists'}
    return render_template('neurologists/neurologists_base.html', ls=ls)


@app.route('/cardiologists')
def cardiologists():
    ls = {'title': 'cardiologists'}
    return render_template('cardiologists/cardiologists_base.html', ls=ls)


@app.route('/genicologists')
def genicologists():
    ls = {'title': 'genicologists'}
    return render_template('genicologists/genicologists_base.html', ls=ls)


@app.route('/psychiatrists')
def psychiatrists():
    ls = {'title': 'psychiatrists'}
    return render_template('psychiatrists/psychiatrists_base.html', ls=ls)


@app.route('/narcologists')
def narcologists():
    ls = {'title': 'narcologists'}
    return render_template('narcologists/narcologists_base.html', ls=ls)


@app.route('/urologists')
def urologists():
    ls = {'title': 'urologists'}
    return render_template('urologists/urologists_base.html', ls=ls)


@app.route('/praktologists')
def praktologists():
    ls = {'title': 'praktologists'}
    return render_template('praktologists/praktologists_base.html', ls=ls)


@app.route('/pulmanologists')
def pulmanologists():
    ls = {'title': 'pulmanologists'}
    return render_template('pulmanologists/pulmanologists_base.html', ls=ls)


@app.route('/calendar/<doctor>/<name>/<doctor_name>/')
def calendar_name(doctor, name, doctor_name):
    ls = {'title': 'calendar', 'doctor': doctor, 'name': name, 'doctor_name': doctor_name, 'month': 'Выберите месяй на которую хотите записаться', 
          'day': 'Выберите число'}
    months = {1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель', 5: 'Май', 6: 'Июнь', 7: 'Июль', 
              8: 'Август', 9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'}
    month = datetime.now().month
    return render_template('calendar.html', ls=ls, months=months, month=month)


@app.route('/process_data/<index>/<doctor>/<name>/<doctor_name>/', methods=['POST', 'GET'])
def doit(index, doctor, name, doctor_name):
    ls = {'title': name, 'index': int(index), 'doctor': doctor, 'doctor_name': doctor_name, 0: 'понедельник', 1: 'вторник', 2: 'среда', 3: 'четверг',
          4: 'пятница', 5: 'суббота', 6: 'воскресенье', 'DATE': DATE.today().day}
    data = calendar.monthcalendar(year=2025, month=int(index))
    date = datetime
    return render_template('index.html', ls=ls, data=data, date=date)


@app.route('/<doctor>/<name>/<month>/<day>/<doctor_name>/', methods=['POST', 'GET'])
def day(doctor, name, month, day, doctor_name):
    ls = {'title': 'time', 'doctor_name': doctor_name, 'name': name, 'month': month, 'day': day, 
          'doctor': doctor}
    cal = {}
    try:
        with open(f'data/{doctor}/{name}.json', 'r') as file:
            cal = json.load(file)
    except:
        with open('data/data.json', 'r') as file:
            write = json.load(file)

        with open(f'data/{doctor}/{name}.json', 'w') as file:
            json.dump(write, file)

        with open(f'data/{doctor}/{name}.json', 'r') as file:
            cal = json.load(file)

    times = cal[month][day]
    return render_template('time.html', ls=ls, times=times)


@app.route('/write/<doctor>/<name>/<month>/<day>/<time>/<doctor_name>/', methods=['POST', 'GET'])
def writes(doctor, name, month, day, time, doctor_name, wrong=''):
    ls = {'title': 'write', 'doctor_name': doctor_name, 'doctor': doctor, 'name': name, 'month': month, 
          'day': day, 'time': time}
    return render_template('write.html', ls=ls, wrong=wrong)


@app.route('/write_data/<doctor>/<name>/<month>/<day>/<time>/<doctor_name>/', methods=['POST'])
def write_data(doctor, name, month, day, time, doctor_name):
    name_form = request.form.get('writer')
    write = {}
    ls = {'title': 'write', 'doctor_name': doctor_name, 'name': name, 'month': month, 'day': day, 
    'time': time}
    
    with open(f'data/{doctor}/{name}.json', 'r') as file:
        write = json.load(file)
    
    if name_form != '':
        write[month][day][time] = name_form

        with open(f'data/{doctor}/{name}.json', 'w') as file:
            json.dump(write, file)

        return render_template('answer.html', ls=ls)

    else:
        wrong = 'Вы не ввели ФИО'
        return writes(doctor, name, month, day, time, doctor_name, wrong)


if __name__ == '__main__':
    app.run()