import os
import sys
import ctypes
import json
import threading
import webbrowser
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# یہ فنکشن خود بخود چیک کرے گا اور نئے کمپیوٹر پر 'malikisp' سیٹ کر دے گا
def setup_local_domain():
    domain_name = "malikisp"
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    
    # چیک کریں کہ کیا نام پہلے سے موجود ہے یا نہیں
    try:
        with open(hosts_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if domain_name in content:
                return # اگر پہلے سے موجود ہے تو کچھ نہ کرو
    except:
        pass

    # اگر موجود نہیں ہے، تو خودکار طریقے سے ایڈمن پرمیشن مانگ کر ایڈ کر دو
    if not ctypes.windll.shell32.IsUserAnAdmin():
        # اگر ایڈمن نہیں ہے تو دوبارہ ایڈمن رائٹس کے ساتھ رن کرو
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    else:
        # hosts فائل میں نام شامل کرنا
        try:
            with open(hosts_path, 'a', encoding='utf-8') as f:
                f.write(f"\n127.0.0.1    {domain_name}\n")
        except Exception as e:
            print("Auto domain setup error:", e)

DATA_FILE = 'data.json'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f)

@app.route('/api/load', methods=['GET'])
def load_json_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                return jsonify(json.load(f))
            except:
                return jsonify({})
    return jsonify({})

@app.route('/api/save', methods=['POST'])
def save_json_data():
    data = request.json
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return jsonify({"status": "success"})

@app.route('/api/upload-photo', methods=['POST'])
def upload_photo():
    if 'image' in request.files:
        img = request.files['image']
        if img.filename != '':
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], img.filename)
            img.save(img_path)
            return jsonify({"status": "success", "filename": img.filename})
    return jsonify({"status": "error"})

@app.route('/')
def index():
    return render_template('index.html')

def open_browser():
    webbrowser.open_new('http://malikisp:8080/')

if __name__ == '__main__':
    # پروجیکٹ شروع ہوتے ہی ڈومین سیٹ کریں
    setup_local_domain()

    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.0, open_browser).start()
        
    app.run(debug=True, port=8080)