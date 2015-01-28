# -*- coding: utf-8 -*-
import os
from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
from estat_go_jp import *
import jpgrid


database_proxy = Proxy()  # Create a proxy for our db.

SRID = 4326


class PolygonField(Field):
    db_field = 'polygon'


class PointField(Field):
    db_field = 'point'


class LineStringField(Field):
    db_field = 'linestring'


class MultiPolygonField(Field):
    db_field = 'multipolygon'


class MultiPointField(Field):
    db_field = 'multipoint'


class MultiLineStringField(Field):
    db_field = 'multilinestring'


class Stat(Model):
    """
    統計情報を格納するモデル
    """
    stat_id = TextField(primary_key=True)
    stat_name = TextField()
    stat_name_code = TextField()
    gov_org = TextField()
    gov_org_code = TextField()
    #statistics_name = TextField()
    #cycle = TextField()
    survey_date = TextField()
    #open_date = TextField()
    #small_area = TextField()
    title = TextField()

    class Meta:
        database = database_proxy


class StatValue(Model):
    """
    統計の値を格納するモデル
    """
    id = PrimaryKeyField()
    stat_id = TextField(index=True, unique=False)
    value = TextField()

    class Meta:
        database = database_proxy


class StatValueAttr(Model):
    """
    統計の属性値を格納するモデル
    """
    id = PrimaryKeyField()
    stat_id = TextField()
    stat_value = ForeignKeyField(
        db_column='stat_value_id',
        rel_model=StatValue,
        to_field='id'
    )
    attr_name = TextField()
    attr_value = TextField()

    class Meta:
        database = database_proxy
        indexes = (
            (('stat_id', 'stat_value'), False),
            (('stat_id', 'stat_value', 'attr_name'), False),
        )


class MapArea(Model):
    """
    統計の属性値 areaにおけるPolygonを格納するモデル
    """
    id = PrimaryKeyField()
    stat_id = TextField()
    stat_val_attr = ForeignKeyField(
        db_column='stat_val_attr_id',
        rel_model=StatValueAttr,
        to_field='id'
    )
    geometry = PolygonField()

    class Meta:
        database = database_proxy
        indexes = (
            (('stat_id', 'stat_val_attr'), True),
        )


class idx_MapArea_Geometry(Model):
    pkid = PrimaryKeyField()
    xmin = FloatField()
    xmax = FloatField()
    ymin = FloatField()
    ymax = FloatField()

    class Meta:
        database = database_proxy


def connect(path, spatialite_path, evn_sep=';'):
    """
    データベースへの接続
    @param path sqliteのパス
    @param spatialite_path mod_spatialiteへのパス
    @param env_sep 環境変数PATHの接続文字 WINDOWSは; LINUXは:
    """
    os.environ["PATH"] = os.environ["PATH"] + evn_sep + os.path.dirname(spatialite_path)
    db = SqliteExtDatabase(path)
    database_proxy.initialize(db)
    db.field_overrides = {
        'polygon': 'POLYGON',
        'point': 'POINT',
        'linestring': 'LINESTRING',
        'multipolygon': 'MULTIPOLYGON',
        'multipoint': 'MULTIPOINT',
        'multilinestring': 'MULTILINESTRING',
    }
    db.load_extension(os.path.basename(spatialite_path))


def setup(path, spatialite_path, evn_sep=';'):
    """
    データベースの作成
    @param path sqliteのパス
    @param spatialite_path mod_spatialiteへのパス
    @param env_sep 環境変数PATHの接続文字 WINDOWSは; LINUXは:
    """
    connect(path, spatialite_path, evn_sep)

    database_proxy.create_tables([Stat, StatValue, StatValueAttr], True)
    database_proxy.get_conn().execute('SELECT InitSpatialMetaData()')

    # Geometryのテーブルは直接実装する必要がある.
    database_proxy.get_conn().execute("""
        CREATE TABLE IF NOT EXISTS "MapArea" (
          "id" INTEGER PRIMARY KEY AUTOINCREMENT,
          "stat_id" TEXT,
          "stat_val_attr_id" INTEGER ,
          FOREIGN KEY(stat_val_attr_id) REFERENCES StatValueAttr(id));
    """)

    database_proxy.get_conn().execute("""
        CREATE INDEX IF NOT EXISTS "ix_MapArea_stat_id" ON MapArea(stat_id);
    """)

    database_proxy.get_conn().execute("""
        CREATE INDEX IF NOT EXISTS "ix_MapArea_stat_id_stat_val_attr_id" ON MapArea(stat_id, stat_val_attr_id);
    """)

    database_proxy.get_conn().execute("""
        Select AddGeometryColumn ("MapArea", "Geometry", ?, "POLYGON", 2);
    """, (SRID,))

    database_proxy.get_conn().execute("""
        SELECT CreateSpatialIndex("MapArea", "geometry")
    """)


def import_stat(api_key, stat_id):
    """
    統計情報のインポート
    @param api_key e-statのAPIKEY
    @param stat_id 統計ID
    """
    with database_proxy.transaction():
        MapArea.delete().filter(MapArea.stat_id == stat_id).execute()
        StatValueAttr.delete().filter(StatValueAttr.stat_id == stat_id).execute()
        StatValue.delete().filter(StatValue.stat_id == stat_id).execute()
        Stat.delete().filter(Stat.stat_id == stat_id).execute()

        tableinf = get_table_inf(api_key, stat_id)
        stat_row = Stat.create(
            stat_id=stat_id,
            stat_name=tableinf['stat_name'],
            stat_name_code=tableinf['stat_name_code'],
            title=tableinf['title'],
            gov_org=tableinf['gov_org'],
            gov_org_code=tableinf['gov_org_code'],
            survey_date=tableinf['survey_date']
        )
        values, class_object = get_stats_id_value(api_key, stat_id, {})
        for vdata in values:
            if not 'value' in vdata:
                continue
            value_row = StatValue.create(
                stat_id=stat_id,
                value=vdata['value']
            )
            for k, v in vdata.items():
                stat_val_attr = StatValueAttr.create(
                    stat_id=stat_id,
                    stat_value=value_row,
                    attr_name=k,
                    attr_value=v
                )
                if k == 'area':
                    # メッシュコード
                    meshbox = jpgrid.bbox(v)
                    database_proxy.get_conn().execute(
                        'INSERT INTO MapArea(stat_id, stat_val_attr_id, geometry) VALUES(?,?,BuildMBR(?,?,?,?,?))',
                        (stat_id, stat_val_attr.id, meshbox['s'], meshbox['e'], meshbox['n'], meshbox['w'], SRID)
                    )
        database_proxy.commit()


def get_mesh_stat(stat_id_start_str, attr_value, xmin, ymin, xmax, ymax):
    """
    地域メッシュの統計情報を取得する
    @param stat_id_start_str 統計IDの開始文字 この文字から始まるIDをすべて取得する.
    @param attr_value cat01において絞り込む値
    @param xmin 取得範囲
    @param ymin 取得範囲
    @param xmax 取得範囲
    @param ymax 取得範囲
    """
    rows = database_proxy.get_conn().execute("""
        SELECT
          statValue.value,
          AsGeoJson(MapArea.Geometry)
        FROM
          MapArea
          inner join idx_MapArea_Geometry ON pkid = MapArea.id AND xmin > ? AND ymin > ? AND xmax < ? AND ymax < ?
          inner join statValueAttr ON MapArea.stat_val_attr_id = statValueAttr.id
          inner join statValueAttr AS b ON b.stat_value_id = statValueAttr.stat_value_id AND b.attr_value = ?
          inner join statValue ON statValue.id = b.stat_value_id
        WHERE
          MapArea.stat_id like ?;
    """, (xmin, ymin, xmax, ymax, attr_value, stat_id_start_str + '%'))
    ret = []
    for r in rows:
        ret.append({
            'value': r[0],
            'geometory': r[1]
        })
    return ret
