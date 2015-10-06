from flask import Flask
from flask import request
from flask import render_template

app = Flask(__name__)

@app.route('/fleet/<fleetid>')
def main(fleetid):
	name = "Dakodai"
	return render_template('skynet.html', name=name, fleetid=fleetid)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
