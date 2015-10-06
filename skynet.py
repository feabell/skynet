from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/')
def main():
	print request.headers	

	if check_igb():
		return "using the ingame browser!"
	else:
		return "this won't work"

def check_igb():
	return True	

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
