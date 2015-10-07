from flask import Flask
from flask import request
from flask import render_template
from flask import g
from datetime import datetime, timedelta
import sqlite3
import string
import random
import json

app = Flask(__name__)

database = 'skynet.db'

@app.route('/feedback')
@app.route('/feedback/')
def getFleets():

	fleets = query_db('select fleetid, fcname, description, created from fleets')

	return json.dumps([dict(ix) for ix in fleets])


@app.route('/feedback/<fleetid>')
def results(fleetid):

	feedback = query_db('select pilotid, pilotname, shiptypename, rating, feedback from participants where fleetid =?', [fleetid])

	return json.dumps( [dict(ix) for ix in feedback] )


@app.route('/fleet')
@app.route('/fleet/')
def default():
	return render_template('skynet-landing.html')

@app.route('/new', methods=['POST'])
@app.route('/new/', methods=['POST'])
def new():
	#grap data from the POST
	data = json.loads(request.data)
	
	#generate a fleetid
	fleetid = ''.join(random.choice(string.ascii_uppercase) for i in range(10))
	fcname =  data['fcname']
	description = data['description']

	#create a new fleet record
	insert_db('insert into fleets (fleetid, fcname, description, created) values (?, ?, ?, datetime("now"))',
			[fleetid,
			fcname,
			description])


	payload = {'url': 'http://feabell.com:5000/fleet/'+fleetid}
	return json.dumps(payload)
	

@app.route('/fleet/<fleetid>', methods=['GET', 'POST'])
def main(fleetid):
	if request.method == 'GET':
		if check_valid(fleetid, request.headers.get('Eve-Alliancename', None)) and new_pilot(fleetid, request.headers.get('Eve-Charid', None)):
			name = get_fc_name(fleetid)
			description = get_fleet_desc(fleetid)
			return render_template('skynet.html', name=name, description=description, fleetid=fleetid)
		else:
			return render_template('skynet-error.html')
	elif request.method == 'POST':
		if check_valid(fleetid, request.headers.get('Eve-Alliancename', None)) and new_pilot(fleetid, request.form.get('Eve-Charid', None)):
			print request.form.get('Eve-Charname', None) 
			#add a pilot record for this fleet
			insert_db('insert into participants (fleetid, pilotname, pilotid, corpname, shiptypename, feedback, rating) values (?, ?, ?, ?, ?, ?, ?)',
					[request.form.get('fleetid', None), 
					request.form.get('Eve-Charname', None), 
					request.form.get('Eve-Charid', None), 
					request.form.get('Eve-Corpname', None), 
					request.form.get('Eve-Shiptypename', None),
					request.form.get('feedback', None), 
					request.form.get('rating', None)])
		else:
			return render_template('skynet-error.html')

	return render_template('skynet-success.html')	

def check_valid(fleetid, alliancename):
	fleet = query_db('select fleetid, created from fleets where fleetid = ?', [fleetid], one=True)

	if fleet is None or alliancename != "The WINGSPAN Logo Alliance":
		return False
	
	#only allow access to links created in the last 6 hours
	if datetime.strptime(fleet['created'],'%Y-%m-%d %H:%M:%S' ) < (datetime.utcnow() - timedelta(hours = 6)):
		return False

	return True

def new_pilot(fleetid, pilotid):
	participant = query_db('select fleetid, pilotid from participants where fleetid = ? and pilotid = ?', [fleetid, pilotid], one=True)

	if participant is None:
		print "no entries in participant", fleetid, ' ', pilotid
		return True

	return False


def get_fc_name(fleetid):
	fleet = query_db('select fleetid, fcname from fleets where fleetid = ?', [fleetid], one=True)

	return fleet['fcname']

def get_fleet_desc(fleetid):
	fleet = query_db('select fleetid, description from fleets where fleetid = ?', [fleetid], one=True)

	return fleet['description']

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_db()

    db.row_factory = sqlite3.Row

    return db

def connect_db():
    return sqlite3.connect(database)

def insert_db(query, args=()):
    # g.db is the database connection
    cur = get_db().execute(query, args)
    get_db().commit()
    cur.close()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
