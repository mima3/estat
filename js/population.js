$(function() {
  var stat_dict = {
    'T000608' : {id:'T000608', attrval: '人口総数'},
    'T000616_people' : {id:'T000616', attrval: '全産業従業者数'},
    'T000616_business' : {id:'T000616', attrval: '全産業事業所数'}
  };
  $(document).ready(function() {
    // 参考
    // http://shimz.me/blog/google-map-api/3445
    var latlng = new google.maps.LatLng(35.709984,139.810703);
    var opts = {
      zoom: 11,
      center: latlng,
      scrollwheel: false,
      disableDoubleClickZoom: true,
      scaleControl: false,
      zoomControl : false,
      streetViewControl : false,
      mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    var map = new google.maps.Map(document.getElementById("map_canvas"), opts);
    var features = [];
    map.data.addListener('click', function(e) {
      alert(e.feature.getProperty('value'));
      console.log(e.feature.getProperty('value'));
    });

    google.maps.event.addListener(map, 'dragend', function() {
      var statid = $("input[name='estatid']:checked").val();

      for (var i = 0; i < features.length; i++) {
        map.data.remove(features[i]);
      }

      var latlngBounds = map.getBounds();
      var swLatlng = latlngBounds.getSouthWest();
      var swlat = swLatlng.lat();
      var swlng = swLatlng.lng();
      var neLatlng = latlngBounds.getNorthEast();
      var nelat = neLatlng.lat();
      var nelng = neLatlng.lng();
      var styleFeature = function(max) {
        var colorScale = d3.scale.linear().domain([0, max]).range(["#CCFFCC", "red"]);
        return function(feature) {
          return {
            strokeWeight : 1,
            fillColor: colorScale(+feature.getProperty('value')),
            fillOpacity: 0.5
          };
        };
      }

      util.getJson(
        '/estat/json/get_population',
        {
          stat_id : stat_dict[statid].id,
          attr_value : stat_dict[statid].attrval,
          swlat : swlat,
          swlng : swlng,
          nelat : nelat,
          nelng : nelng
        },
        function (errCode, result) {
          if (errCode) {
            return;
          }
          features  = map.data.addGeoJson(result);
          var max = 0;
          for (var i = 0; i < features.length; i++) {
            if (max < features[i].getProperty('value')) {
              max = features[i].getProperty('value');
            }
          }
          map.data.setStyle(styleFeature(max));
        },
        function() {
          $.blockUI({ message: '<img src="/estat/img/loading.gif" />' });
        },
        function() {
          $.unblockUI();
        }
      );
    });
    google.maps.event.addListener(map, 'bounds_changed', function() {
      console.log('bounds_changed');
    });
  });
});
