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

# telegraf

# JSON to Telegraf

## Config

```toml
# Test configuration using JSON
[agent]
  interval = "10s"
  debug = true

[[outputs.file]]
  files = ["stdout"]
  data_format = "influx"

[[outputs.influxdb_v2]]
  urls = ["http://localhost:8086"]
  token = "EMEeAlG4P2PsBy-tryZkgHGbUPmzGHlmcwiZJB0cbfEy9_AwY2ogFi30aVceLPAg_vRmhG52jT6Z_nf4sr3xwA=="
  organization = "south"
  bucket = "lab"

[[inputs.http_listener_v2]]
  service_address = ":8094"
  paths = ["/telegraf"]
  methods = ["POST"]
  data_format = "json"
  name_override = "super_server"
  tag_keys = [
    "message_messageId",
    "message_version",
    "message_priority",
    "message_sender"
  ]
  # Parse all string fields explicitly
  json_string_fields = [
    "message_payload_field1",
    "message_payload_field3"
  ]

[[processors.starlark]]
  source = '''
def apply(metric):
    # Debug: print all incoming fields and tags
    print("Incoming fields:", metric.fields)
    print("Incoming tags:", metric.tags)

    new_fields = {}
    timestamp = None

    # Process all fields
    for key, value in metric.fields.items():
        if key.startswith("message_"):
            # Remove the "message_" prefix
            clean_key = key[8:]  # Remove "message_"

            if clean_key == "timestamp":
                # Convert Unix timestamp to nanoseconds
                timestamp = int(value) * 1000000000
            elif clean_key.startswith("payload_"):
                # Keep payload fields as is
                new_fields[clean_key] = value

    # Clear existing fields and add new ones
    metric.fields.clear()
    for key, value in new_fields.items():
        metric.fields[key] = value

    # Process tags
    new_tags = {}
    for key, value in metric.tags.items():
        if key.startswith("message_"):
            clean_key = key[8:]  # Remove "message_"
            new_tags[clean_key] = str(value)
        elif key == "host":
            new_tags["host"] = value

    # Clear existing tags and add new ones
    metric.tags.clear()
    for key, value in new_tags.items():
        metric.tags[key] = value

    # Set timestamp if available
    if timestamp:
        metric.time = timestamp

    # Ensure measurement name is super_server
    metric.name = "super_server4"

    print("Output fields:", metric.fields)
    print("Output tags:", metric.tags)

    return metric
'''
```

## Curl

```bash
curl -X POST http://localhost:8094/telegraf -H "Content-Type: application/json" -d '{ "message": { "messageId": "MSG-12345", "version": "1.0", "priority": "high", "sender": "system", "payload": { "field1": "Hello World", "field2": 42, "field3": "active", "field4": 45.4 }, "timestamp": 1753498220 } }'
```

## Output (1 line)

```
0       super_server4   payload_field1  Hello World     2025-07-26T01:17:48.000Z        ovirt-engine.local      MSG-12345       high    system  1.0
```

---

# XML to Telegraf

## Config

```toml
# Test configuration using XML
[agent]
  interval = "10s"
  debug = true

[[outputs.file]]
  files = ["stdout"]
  data_format = "influx"

[[outputs.influxdb_v2]]
  urls = ["http://localhost:8086"]
  token = "EMEeAlG4P2PsBy-tryZkgHGbUPmzGHlmcwiZJB0cbfEy9_AwY2ogFi30aVceLPAg_vRmhG52jT6Z_nf4sr3xwA=="
  organization = "south"
  bucket = "lab"

[[inputs.http_listener_v2]]
  service_address = ":8094"
  paths = ["/telegraf"]
  methods = ["POST"]
  data_format = "xml"
  name_override = "super_server5"
  
  [[inputs.http_listener_v2.xml]]
    # Metric selection
    metric_name = "'super_server5'"
    metric_selection = "/message"
    
    # Timestamp
    timestamp = "timestamp"
    timestamp_format = "unix"
    
    # Field selections - get all payload fields
    field_selection = "payload/*"
    field_name_expansion = true
    
    # Tag selections
    tag_selection = "messageId|version|priority|sender"

[[processors.starlark]]
  source = '''
def apply(metric):
    # Debug logging
    print("Incoming fields:", metric.fields)
    print("Incoming tags:", metric.tags)
    
    # Rename fields to add payload_ prefix
    new_fields = {}
    for key, value in metric.fields.items():
        if not key.startswith("payload_"):
            new_fields["payload_" + key] = value
        else:
            new_fields[key] = value
    
    # Clear and update fields
    metric.fields.clear()
    for key, value in new_fields.items():
        metric.fields[key] = value
    
    # Ensure measurement name
    metric.name = "super_server5"
    
    print("Output fields:", metric.fields)
    print("Output tags:", metric.tags)
    
    return metric
'''
```

## Curl

```bash
curl -X POST http://localhost:8094/telegraf -H "Content-Type: application/xml" -d '<message> <messageId>MSG-12345</messageId> <version>1.0</version> <priority>high</priority> <sender>system</sender> <payload> <field1>Hello World</field1> <field2>42</field2> <field3>active</field3> <field4>55.2</field4> </payload> <timestamp>1753501652</timestamp> </message>'
```

## Output (1 line)

```
1	super_server5	payload_field2	42	2025-07-26T01:17:48.000Z	ovirt-engine.local	MSG-12345	high	system	1.0
```
