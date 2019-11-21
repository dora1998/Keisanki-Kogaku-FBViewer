import urllib.request
import json
import re
import http.server
import webbrowser
import sys
import os
import hashlib
from enum import Enum

CONVERT_URL = 'id_python.cgi'
FBTOP_URL = 'feedback.html'
FB_URL = 'retr_score.cgi'
BASEURL_HASH = '015ad04b3009cade2ca7939966495b4adc0f6c6cfdb3e0b968d15a5c2b73a051'

SETTING_FILE = "settings.json"
DATA_FOLDER = "./data"


class Config:
    baseurl = ""

    student_num = ""
    password = ""
    password_each = {}
    server_port = 8081

    def load(self, fileName):
        """設定ファイルの読み込み"""
        try:
            with open(fileName) as f:
                df = json.load(f)
                self.student_num = df['student_num']
                self.password = df['password']
                if 'password_each' in df:
                    self.password_each = df['password_each']
                if 'server_port' in df:
                    self.server_port = df['server_port']

                self.baseurl = df['fburl']
                if self.baseurl.endswith("/") is False:
                    self.baseurl += "/"
                if hashlib.sha256(self.baseurl.encode("utf-8")).hexdigest() != BASEURL_HASH:
                    print("Error: フィードバックURLが不正です")
                    sys.exit()
        except FileNotFoundError:
            print(fileName + " not found!")
            sys.exit()
        except KeyError:
            print("Error: 設定ファイルが不正です")
            sys.exit()

    def save(self, fileName):
        """設定ファイルの書き込み"""
        df = {
            "student_num": self.student_num,
            "password": self.password,
            "password_each": self.password_each,
            "server_port": self.server_port,
            "fburl": self.baseurl
        }
        with open(fileName, 'w') as f:
            json.dump(df, f, indent=4)


def main():
    # 作業ディレクトリをスクリプトのある場所に
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # 設定ファイルがなければ初期設定
    config = Config()
    if not os.path.exists(SETTING_FILE):
        print('Error: 設定ファイルが見つかりません\n')
        print('-- 初期設定 --')
        print('※提出ごとにパスワードを変えている場合は、ドキュメントを参照の上、JSONファイルを手動で設定してください\n')

        print('学生番号(ハイフンなし): ', end='')
        config.student_num = input().replace('-', '')
        print('パスワード: ', end='')
        config.password = input()
        config.baseurl = 'http://easter.kuee.kyoto-u.ac.jp/X186eoI4htvDI/'

        config.save(SETTING_FILE)
        print('\n設定が完了しました。再度初期設定するには、settings.jsonを削除してください。\n')

    # 設定ファイルの読み込み
    config.load(SETTING_FILE)

    # dataフォルダがなければ作成
    os.makedirs(DATA_FOLDER, exist_ok=True)

    # フィードバックリストを取得して保存
    fbs = get_feedback_list(config.baseurl)
    save_json_file(f"{DATA_FOLDER}/fb.json", fbs)

    # 学生番号を変換
    ceid = get_ceid(config)
    if ceid is None:
        print("Error: 学生番号の変換に失敗しました")
        sys.exit()

    # 全フィードバックを取得
    get_all_feedback(ceid, config, ceid, fbs)

    # ビューワー用サーバーを開始
    start_server(config.server_port)


def get_ceid(conf):
    """学生番号を変換する関数"""
    print("学生番号変換中...")

    params = {
        'id0': conf.student_num,
    }
    req = urllib.request.Request(
        conf.baseurl + CONVERT_URL, urllib.parse.urlencode(params).encode('ascii'))

    ceid = None
    try:
        with urllib.request.urlopen(req) as res:
            ceid = res.read().decode('utf-8').replace("CE-ID: ", "").replace("\n", "")
    except urllib.error.URLError:
        print("Can't access the convert page!")
        sys.exit()

    print(f'ceid: {ceid}')
    return ceid


def get_feedback(id, password, date, baseurl):
    """フィードバック一つ分をサイトから取得"""
    params = {
        'id1': id,
        'passwd': password,
        'indate': date
    }

    body = ""
    req = urllib.request.Request(
        baseurl + FB_URL, urllib.parse.urlencode(params).encode('ascii'))
    try:
        with urllib.request.urlopen(req) as res:
            body = res.read().decode('utf-8')
    except urllib.error.URLError:
        print("Error: フィードバックにアクセスできません!")
        sys.exit()

    return body


def parse_feedback(body, id):   # noqa: C901
    class ParseMode(Enum):
        TITLE = 0
        ANS = 1
        STATS = 2
        SCORECOUNT = 3

    json_data = {}
    json_data['raw_data'] = body
    json_data['ans'] = []
    json_data['stats'] = []
    json_data['score_count'] = {}

    mode = ParseMode.TITLE
    for line in body.splitlines():
        if mode == ParseMode.TITLE:
            if line.startswith('id='):
                json_data['submit_date'] = line.replace(f'id= {id} @ ', '')
                mode = ParseMode.ANS
            elif 'no match' in line:
                json_data['error'] = True
                mode = ParseMode.ANS
            elif line != '<pre>':
                json_data['title'] = line.replace(
                    '<br>', '').replace('<br />', '')
        if mode == ParseMode.ANS:
            pattern = r"(?P<qname>.+)\s:\s(?P<res>True|False)\s(?P<your_ans>.*)\s(?P<ans>\[.+\])"
            m = re.search(pattern, line)
            if m:
                json_data['ans'].append({
                    'qname': m.group('qname'),
                    'res': m.group('res'),
                    'your_ans': m.group('your_ans'),
                    'ans': m.group('ans')
                })
            elif line == "# stats":
                mode = ParseMode.STATS
        if mode == ParseMode.STATS:
            if line == "# score count":
                mode = ParseMode.SCORECOUNT
            elif line.startswith("#") is False:
                tbl = [i.strip() for i in line.split(' ') if len(i) > 0]
                if len(tbl) == 4:
                    json_data['stats'].append({
                        'qname': tbl[0],
                        'rate': float(tbl[1]),
                        'pos': int(tbl[2]),
                        'N': int(tbl[3])
                    })
        if mode == ParseMode.SCORECOUNT:
            if line.startswith("#") is False:
                tbl = line.split("    ")
                if len(tbl) == 2:
                    json_data['score_count'][int(tbl[0])] = int(tbl[1])

    return json_data


def get_feedback_list(baseurl):
    print("フィードバックリストを取得中...")

    regex_body = r'<option value="--------">.*?</option>(.+)<script>'
    regex_option = r'<option value="(.+)">.+</option>$'

    fblist = []

    req = urllib.request.Request(baseurl + FBTOP_URL)
    try:
        with urllib.request.urlopen(req) as res:
            body = res.read().decode('utf-8')
            match = re.search(regex_body, body, re.MULTILINE | re.DOTALL)
            if match:
                html_options = match.group(1)
                opt_matches = re.findall(
                    regex_option, html_options, re.MULTILINE)
                for opt_match in opt_matches:
                    fblist.append(opt_match)
    except urllib.error.URLError:
        print("Error: フィードバックリストにアクセスできませんでした!")
        sys.exit()

    return fblist


def get_all_feedback(id, conf, ceid, fbs):
    print("Get All feedback...")
    for fb in fbs:
        if os.path.exists(f"{DATA_FOLDER}/{fb}.json"):
            print(f"[Skipped] {fb}")
        else:
            print(f"[Get] {fb}")
            pwd = conf.password_each[fb] if fb in conf.password_each else conf.password
            body = get_feedback(id, pwd, fb, conf.baseurl)
            json_data = parse_feedback(body, id)
            save_json_file(f"{DATA_FOLDER}/{fb}.json", json_data)
            print(f"[Saved] {fb}")


def save_json_file(filename, json_data):
    if filename is None or json_data is None:
        return
    with open(filename, mode='w') as f:
        json.dump(json_data, f, indent=4)


def start_server(port):
    server_address = ("", port)
    handler_class = http.server.SimpleHTTPRequestHandler  # ハンドラを設定
    simple_server = http.server.HTTPServer(server_address, handler_class)

    print(' === サーバー開始 === ')
    print(f'http://localhost:{port} でフィードバック一覧にアクセスできます')
    print('終了するには、Ctrl+Cを押してください...')
    sys.stderr = open(os.devnull, 'w')

    webbrowser.open(f'http://localhost:{port}/')
    try:
        simple_server.serve_forever()
    except:  # noqa: E722
        sys.stderr.close()
        print(' === サーバー停止 === ')


if __name__ == "__main__":
    main()
