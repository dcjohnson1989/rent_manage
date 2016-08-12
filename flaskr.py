import sqlite3

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

DATABASE = 'rent.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def get_db():
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()

@app.route('/')
def show_entries():
	cur = g.db.execute('select room_id, rent_price, pay_date, water_fee from rent_payment order by room_id desc')
	rents = [dict(room_id=row[0], rent_price=row[1], pay_date=row[2], water_fee=row[3]) for row in cur.fetchall()]
	return render_template('show_rent.html', rents=rents)

@app.route('/add', methods=['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	db = get_db()

	room_id = int(request.form['room_id'])
	rent_price =  int(request.form['rent_price'])
	pay_date = request.form['pay_date']
	water_fee = float(request.form['water_fee'])

	db.execute('insert into rent_payment (room_id, rent_price, pay_date, water_fee) values (?, ?, ?, ?)', [room_id, rent_price, pay_date, water_fee])
	db.commit()
	flash('New entry was successfully posted')
	return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('show_entries'))
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('login_in', None)
	flash('You were logged out')
	return redirect(url_for('show_entries'))

if __name__ == '__main__':
	app.run()