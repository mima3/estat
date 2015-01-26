<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html lang="ja">
<head>
  <title>メッシュ情報</title>
  <link rel="stylesheet" href="/estat/js/select2/select2.css" type="text/css" />
  <link rel="stylesheet" href="/estat/js/jquery/jquery-ui.min.css" type="text/css" />
  <link rel="stylesheet" href="/estat/base.css" type="text/css" />
  <script type="text/javascript" src="/estat/js/jquery/jquery-1.11.1.min.js"></script>
  <script type="text/javascript" src="/estat/js/jquery/jquery-ui-1.10.4.min.js"></script>
  <script type="text/javascript" src="/estat/js/select2/select2.min.js"></script>
  <script type="text/javascript" src="/estat/js/blockui/jquery.blockUI.js"></script>
  <script type="text/javascript" src="/estat/js/d3/d3.min.js"></script>
  <script src="https://maps.googleapis.com/maps/api/js?v=3.exp"></script>
  <script type="text/javascript" src="/estat/js/util.js"></script>
  <script type="text/javascript" src="/estat/js/population.js"></script>
</head>
<body>
  <div id="contents">
    <p>取得したいデータを選択して、ドラッグしてください</p>
    <p><input type="radio" name="estatid" value="T000608" checked="checked">平成２２年国勢調査－世界測地系(1KMメッシュ)20101001 人口総数</p>
    <p><input type="radio" name="estatid" value="T000616_people">平成２１年経済センサス(1KMメッシュ)20090701 全産業従業者数</p>
    <p><input type="radio" name="estatid" value="T000616_business">平成２１年経済センサス(1KMメッシュ)20090701 全産業事業所数</p>
    <div id="map_canvas" style="width: 800px; height: 600px"></div>
  </div>
</body>
</html>
