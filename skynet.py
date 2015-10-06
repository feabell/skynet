from flask import Flask
from flask import request
from flask import render_template

app = Flask(__name__)

@app.route('/')
def main():
	print request.headers	

	return render_template('skynet.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
