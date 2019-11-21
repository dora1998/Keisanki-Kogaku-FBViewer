# 計算機工学 フィードバックビューワー

京大の月 4「計算機工学」で提供されるフィードバックデータを簡単に閲覧できるようにしたプログラムです。
![Main Image](./img/main1.png)

正答率や人数分布、元データについても確認可能です。
![Main Image 2](./img/main2.png)

## ダウンロード

右上の **「Clone or Download」** を押し、 **「Download ZIP」** をクリック

## 初期設定

初回起動時にログイン情報の入力を行います。もし、毎回個別にパスワードを設定している場合は、下記の「JSON ファイルの手動設定方法」を参照してください。
![Init Image 2](./img/init_settings.png)

<details>
<summary>JSON ファイルの手動設定方法</summary>

- `settings.sample.json` を `settings.json` にリネーム
- `student_num`と `password` を記入(変換の必要はありません)
- もし個別でパスワードを設定している場合は、以下のような形式で挿入

```
    "password_each": {
        "日付(ex.20181001)": "個別のパスワード"
    },
```

</details>

## 実行方法

### Python 3.x をインストールしている場合

```
python main.py
```

### インストールしていない場合 (Windows のみ)

`main.exe` をダブルクリック

実行後、自動で全フィードバックを取得し、ブラウザが開きます。  
終了するには、 `Ctrl+C`　を押してください。  
もし、パスワード不備などで取得に失敗したファイルが残った場合、data フォルダ内を削除すれば再取得されます。

<details>
<summary>開発向けコマンド</summary>

### テスト

`main.py` があるディレクトリにて、

```
python -m tests.test_main
```

</details>

## 不具合報告・質問

もし不具合報告や質問などがありましたら、Issue もしくは[Twitter](https://twitter.com/d0ra1998)までご連絡願います。修正 PR も大歓迎です。
