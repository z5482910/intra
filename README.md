# intra

1. ✅ Install Apache and mod_wsgi
On Ubuntu/Debian:

bash
Copy
Edit
sudo apt update
sudo apt install apache2 libapache2-mod-wsgi-py3 python3-pip
2. ✅ Install Flask
bash
Copy
Edit
pip3 install flask
3. ✅ Project Structure (example)
Assume your site lives at: /var/www/intranet

kotlin
Copy
Edit
/var/www/intranet/
├── app.wsgi
├── app.py
├── index.html
├── data.json
4. ✅ app.py (same as before)
Just remove the app.run() at the bottom.

python
Copy
Edit
from flask import Flask, request, send_from_directory, jsonify
import json

app = Flask(__name__)
DATA_FILE = "data.json"

@app.route("/")
def serve_html():
    return send_from_directory(".", "index.html")

@app.route("/load")
def load():
    try:
        with open(DATA_FILE) as f:
            return jsonify(json.load(f))
    except:
        return jsonify({"title": "Dashboard", "content": "Welcome!", "links": []})

@app.route("/save", methods=["POST"])
def save():
    with open(DATA_FILE, "w") as f:
        json.dump(request.json, f, indent=2)
    return "Saved", 200
5. ✅ app.wsgi (Glue Apache to Flask)
python
Copy
Edit
import sys
import logging

# Add your project directory to the sys.path
sys.path.insert(0, "/var/www/intranet")

from app import app as application
6. ✅ Apache VirtualHost Config
Create file: /etc/apache2/sites-available/intranet.conf

apache
Copy
Edit
<VirtualHost *:80>
    ServerName intranet.local

    WSGIDaemonProcess intranet threads=5
    WSGIScriptAlias / /var/www/intranet/app.wsgi

    <Directory /var/www/intranet>
        Require all granted
    </Directory>

    Alias /static/ /var/www/intranet/
</VirtualHost>
🔁 Replace intranet.local with your hostname or IP address (like 192.168.1.100).

7. ✅ Enable Site and Restart Apache
bash
Copy
Edit
sudo a2ensite intranet
sudo systemctl reload apache2
🧪 Test It
Visit http://localhost or your IP.

You should see your intranet page.

Changes you make will persist to data.json.

