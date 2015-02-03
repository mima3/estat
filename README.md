政府統計情報のテストプログラム
==========
このプログラムは政府統計総合窓口の提供する地域メッシュをDBに格納してHTTP経由で結果を返すプログラムです。  

<<<<<<< HEAD
政府統計総合窓口:http://www.e-stat.go.jp/api/  
demo:http://needtec.sakura.ne.jp/estat/population  
=======
政府統計総合窓口:http://www.e-stat.go.jp/api/
demo:http://needtec.sakura.ne.jp/estat/population
>>>>>>> d654b494a44d33f714fdfbc3cc065150eca2a5ff

依存ファイル
-------------
easy_install python-geohash  
easy_install peewee  

インストール方法
-----------------
1.application.ini.originをコピーしてappication.iniを作成する。  
下記を修正すること。  

    [database]
    path = ./estat.sqlite # データべースのパス
    mod_path = C:\tool\spatialite\mod_spatialite.dll # mod_spatialite.dllへのパス
    sep = ;  # 環境変数PATHの区切り文字　WINDOWSは; LINUXは:とする

2.index.cgiの構築  
/home/username/estat/ にapplication.ini,databaseファイルがあるものとする.  
/home/username/www/estat/ が公開さきのディレクトリとする  
以下のコマンドを実行

    git clone git://github.com/mima3/estat.git 
    rm -rf estat/.git

    cp -rf estat /home/username/www/
    python /home/username/www/estat/create_index_cgi.py "/usr/local/bin/python" "/home/username/estat/application.ini" > /home/username/www/estat/index.cgi
    chmod +x  /home/username/www/estat/index.cgi

3.統計情報のインポート  
以下のようなコマンドを実行します。  

    python import_estat.py API_KEY 2 平成２２年国勢調査－世界測地系(1KMメッシュ)20101001  C:\tool\spatialite\mod_spatialite-4.2.0-win-x86\mod_spatialite.dll estat.sqlite
    python import_estat.py API_KEY 2 平成２１年経済センサス(1KMメッシュ)20090701  C:\tool\spatialite\mod_spatialite-4.2.0-win-x86\mod_spatialite.dll estat.sqlite

cp932で処理しているのでWindows以外の場合あhimport_estat.pyを適切に修正する必要があります。  


地域メッシュの取得方法
--------------------
以下のようなURLを実行します。

    http://needtec.sakura.ne.jp/estat/json/get_population?stat_id=T000608&attr_value=%E4%BA%BA%E5%8F%A3%E7%B7%8F%E6%95%B0&swlat=35.503426100823496&swlng=139.53192492382811&nelat=35.83811583873688&nelng=140.08124133007811

stat_id: 統計IDの接頭語  
attr_value: cat01の属性値  
swlat: 取得範囲の南西の経度  
swlng: 取得範囲の南西の緯度  
nelat: 取得範囲の北東の経度  
nelng: 取得範囲の北東の緯度  

ライセンス
-------------
当方が作成したコードに関してはMITとします。  
その他、jqueryなどに関しては、それぞれにライセンスを参照してください。

    The MIT License (MIT)

    Copyright (c) 2015 m.ita

    Permission is hereby granted, free of charge, to any person obtaining a copy of
    this software and associated documentation files (the "Software"), to deal in
    the Software without restriction, including without limitation the rights to
    use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
    the Software, and to permit persons to whom the Software is furnished to do so,
    subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
    FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
    COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
    IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
    CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

