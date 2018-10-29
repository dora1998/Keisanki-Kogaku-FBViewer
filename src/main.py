import urllib.request
import json
import re
import http.server
import webbrowser
import sys
import os
import hashlib

CONVERT_URL = 'id_python.cgi'
FBTOP_URL = 'feedback.html'
FB_URL = 'retr_score.cgi'
BASEURL_HASH = '015ad04b3009cade2ca7939966495b4adc0f6c6cfdb3e0b968d15a5c2b73a051'

SETTING_FILE = "settings.json"
DATA_FOLDER = "./data"

student_num = ""
password = ""
password_each = {}
server_port = 8081
baseurl = ""

os.chdir(os.path.dirname(os.path.abspath(__file__)))

try:
    with open(SETTING_FILE) as f:
        df = json.load(f)
        student_num = df['student_num']
        password = df['password']
        password_each = df['password_each']
        server_port = df['server_port'] if 'server_port' in df else server_port

        baseurl = df['fburl']
        if baseurl.endswith("/") == False:
            baseurl += "/"
        if hashlib.sha256(baseurl.encode("utf-8")).hexdigest() != BASEURL_HASH:
            print("Error: フィードバックURLが不正です")
            sys.exit()
except FileNotFoundError:
    print(SETTING_FILE +  " not found!")
    sys.exit()
except KeyError:
    print("Error: 設定ファイルが不正です")

def convertStuNum(stunum):
    print("Convert your Student ID...")

    params = {
        'id0': stunum,
    }
    req = urllib.request.Request(baseurl + CONVERT_URL, urllib.parse.urlencode(params).encode('ascii'))

    convstu_num = None
    try:
        with urllib.request.urlopen(req) as res:
            convstu_num = res.read().decode('utf-8').replace("CE-ID: ", "").replace("\n", "")
    except urllib.error.URLError:
        print("Can't acces the convert page!")
        sys.exit()

    return convstu_num

def getFeedback(id, password, date):
    params = {
        'id1': id,
        'passwd': password,
        'indate': date
    }

    body = ""
    req = urllib.request.Request(baseurl + FB_URL, urllib.parse.urlencode(params).encode('ascii'))
    try:
        with urllib.request.urlopen(req) as res:
            body = res.read().decode('utf-8')
    except urllib.error.URLError:
        print("Error: Can't acces the feedback!")
        sys.exit()

    return body

def parseFeedback(body):
    MODE_TITLE = 0
    MODE_ANS = 1
    MODE_STATS = 2
    MODE_SCORECOUNT = 3

    json_data = {}
    json_data['raw_data'] = body
    json_data['ans'] = []
    json_data['stats'] = []
    json_data['score_count'] = {}

    mode = MODE_TITLE
    for line in body.splitlines():
        if mode == MODE_TITLE:
            if line.startswith('id='):
                json_data['submit_date'] = line.replace(f'id= {convstu_num} @ ', '')
                mode = MODE_ANS
            elif line != '<pre>':
                json_data['title'] = line.replace('<br>', '')
        if mode == MODE_ANS:
            pattern = r"(?P<qname>.+)\s:\s(?P<res>True|False)\s(?P<your_ans>.+)\s(?P<ans>\[.+\])"
            m = re.search(pattern, line)
            if m:
                json_data['ans'].append({
                    'qname': m.group('qname'),
                    'res': m.group('res'),
                    'your_ans': m.group('your_ans'),
                    'ans': m.group('ans')
                })
            elif line == "# stats":
                mode = MODE_STATS
        if mode == MODE_STATS:
            if line == "# score count":
                mode = MODE_SCORECOUNT
            elif line.startswith("#") == False:
                tbl = [i for i in line.split(' ') if len(i) > 0]
                if len(tbl) == 4:
                    json_data['stats'].append({
                        'qname': tbl[0],
                        'rate': tbl[1],
                        'pos': tbl[2],
                        'N': tbl[3]
                    })
        if mode == MODE_SCORECOUNT:
            if line.startswith("#") == False:
                tbl = line.split("    ")
                if len(tbl) == 2:
                    json_data['score_count'][int(tbl[0])] = tbl[1]

    return json_data

def getFeedbackList():
    print("Get feedback list...")

    regex_body = r'<option value="--------"> --------</option>(.+)<script>'
    regex_option = r'^<option value="(.+)">.+<\/option>$'

    fblist = []

    req = urllib.request.Request(baseurl + FBTOP_URL)
    try:
        with urllib.request.urlopen(req) as res:
            body = res.read().decode('utf-8')
            match = re.search(regex_body, body, re.MULTILINE | re.DOTALL)
            if match:
                html_options = match.group(1)
                opt_matches = re.findall(regex_option, html_options, re.MULTILINE)
                for opt_match in opt_matches:
                    fblist.append(opt_match)
    except urllib.error.URLError:
        print("Can't acces the feedback list!")
        sys.exit()

    return fblist

def getAllFeedback(id, passwd, passwd_each, fbs):
    print("Get All feedback...")
    for fb in fbs:
        if os.path.exists(f"{DATA_FOLDER}/{fb}.json"):
            print(f"[Skipped] {fb}")
        else:
            print(f"[Get] {fb}")
            pwd = passwd_each[fb] if fb in passwd_each else passwd
            body = getFeedback(id, pwd, fb)
            json_data = parseFeedback(body)
            saveJsonFile(f"{DATA_FOLDER}/{fb}.json", json_data)
            print(f"[Saved] {fb}")
            

def saveJsonFile(filename, json_data):
    if filename == None or json_data == None:
        return
    with open(filename, mode='w') as f:
        json.dump(json_data, f, indent=4)

def startServer():
    server_address = ("", server_port)
    handler_class = http.server.SimpleHTTPRequestHandler #ハンドラを設定
    simple_server = http.server.HTTPServer(server_address, handler_class)

    print(' === サーバー開始 === ')
    print(f'http://localhost:{server_port} でフィードバック一覧にアクセスできます')
    print('終了するには、Ctrl+Cを押してください...')
    sys.stderr = open(os.devnull, 'w')

    webbrowser.open(f'http://localhost:{server_port}/')
    try:
        simple_server.serve_forever()
    except:
        sys.stderr.close()
        print(' === サーバー停止 === ')

os.makedirs(DATA_FOLDER, exist_ok=True)

fbs = getFeedbackList()
saveJsonFile(f"{DATA_FOLDER}/fb.json", fbs)

convstu_num = convertStuNum(student_num)
if convstu_num == None:
    print("Error: Can't convert your Student ID")
    sys.exit()

getAllFeedback(convstu_num, password, password_each, fbs)

startServer()