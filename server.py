from flask import Flask, request, jsonify
import json
import main as gbauth

app = Flask(__name__)

config = json.load(open('config.json', encoding='utf-8'))
if config['debug']:
    config = json.load(open('dev-config.json', encoding='utf-8'))

gbauth.login()

@app.before_request
def before_request():
    if 'access_token' not in request.json:
        return jsonify({"status": False, "message": "No token provided."}), 403
    if request.json['access_token'] != config['access_token']:
        return jsonify({"status": False, "message": "Invalid token."}), 403

@app.after_request
def after_request(response):
    gbauth.clear_authkey()
    return response

@app.route('/generate_authkey', methods=['POST'])
def generate_authkey():
    return jsonify({"authkey": gbauth.generate_authkey()})


@app.route('/verify', methods=['POST'])
def verify():
    if 'authkey' not in request.json:
        return jsonify({"status": False, "message": "No authkey provided."}), 400
    return jsonify({"status": True, "info": gbauth.verify(request.json['authkey'])})




if __name__ == '__main__':
    app.run(host='127.0.0.1', port=4565, debug=False)
