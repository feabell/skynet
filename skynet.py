from flask import Flask
from flask import request
from flask import render_template
from flask import g
from datetime import datetime, timedelta

app = Flask(__name__)

database = 'skynet.db'

@app.route('/fleet/<fleetid>', methods=['GET', 'POST'])
def main(fleetid):
	if request.method == 'GET':
		if check_valid(fleetid):
			name = get_fc_name(fleetid)
			return render_template('skynet.html', name=name, fleetid=fleetid)
		else:
			return render_template('skynet-error.html')
	else if request.method == 'POST':
		if check_valid(fleetid):
			#add a pilot record for this fleet
		else
			return render_template('skynet-error.html')


def check_valid(fleetid):
	fleet = query_db('select fleetid, created from fleets where fleetid = ?', [fleetid], one=True)

	if fleet is None:
		return false

	if fleet['created'] > (datetime.utcnow() - datetime.timedelta(hours = 6)):
		return false

	return true

def get_fc_name(fleetid):
	fleet = query_db('select fleetid, fcname from fleets where fleetid = ?', [fleetid], one=True)

	return fleet['fcname']

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def get_db():
	db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
