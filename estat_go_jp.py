# -*- coding: utf-8 -*-
import urllib
import urllib2
from lxml import etree
import csv
from collections import defaultdict


def trim_data(d):
    if d:
        return d.strip()
    return d


def export_statical_data(writer, api_key, stats_data_id, class_object, start_position):
    """
    統計情報のエクスポート
    """
    url = ('http://api.e-stat.go.jp/rest/1.0/app/getStatsData?limit=10000&appId=%s&lang=J&statsDataId=%s&metaGetFlg=N&cntGetFlg=N' % (api_key, stats_data_id))
    if start_position > 0:
        url = url + ('&startPosition=%d' % start_position)

    req = urllib2.Request(url)
    opener = urllib2.build_opener()
    conn = opener.open(req)
    cont = conn.read()
    parser = etree.XMLParser(recover=True)
    root = etree.fromstring(cont, parser)

    row = []
    datas = {}
    value_tags = root.xpath('//STATISTICAL_DATA/DATA_INF/VALUE')
    for value_tag in value_tags:
        row = []
        for key in class_object:
            val = value_tag.get(key)
            if val in class_object[key]['objects']:
                level = ''
                if 'level' in class_object[key]['objects'][val]:
                    if class_object[key]['objects'][val]['level'].isdigit():
                        level = ' ' * (int(class_object[key]['objects'][val]['level']) - 1)
                text = ("%s%s" % (level, class_object[key]['objects'][val]['name']))
                row.append(text.encode('utf-8'))
            else:
                row.append(val.encode('utf-8'))
        row.append(value_tag.text)
        writer.writerow(row)

    next_tags = root.xpath('//STATISTICAL_DATA/TABLE_INF/NEXT_KEY')
    if next_tags:
        if next_tags[0].text:
            export_statical_data(writer, api_key, stats_data_id, class_object, int(next_tags[0].text))


def get_table_inf(api_key, stats_data_id):
    """
    メタ情報取得
    """
    url = ('http://api.e-stat.go.jp/rest/1.0/app/getMetaInfo?appId=%s&lang=J&statsDataId=%s' % (api_key, stats_data_id))
    req = urllib2.Request(url)
    opener = urllib2.build_opener()
    conn = opener.open(req)
    cont = conn.read()
    parser = etree.XMLParser(recover=True)
    root = etree.fromstring(cont, parser)

    # TABLE_INF取得
    table_inf = root.xpath('//METADATA_INF/TABLE_INF')[0]
    item = {
        'id': trim_data(table_inf.get('id'))
    }
    stat_name = table_inf.find('STAT_NAME')
    if stat_name is not None:
        item['stat_name'] = trim_data(stat_name.text)
        item['stat_name_code'] = trim_data(stat_name.get('code'))

    gov_org = table_inf.find('GOV_ORG')
    if gov_org is not None:
        item['gov_org'] = trim_data(gov_org.text)
        item['gov_org_code'] = trim_data(gov_org.get('code'))

    statistics_name = table_inf.find('STATISTICS_NAME')
    if statistics_name is not None:
        item['statistics_name'] = trim_data(statistics_name.text)

    title = table_inf.find('TITLE')
    if title is not None:
        item['title'] = trim_data(title.text)

    cycle = table_inf.find('CYCLE')
    if cycle is not None:
        item['cycle'] = trim_data(cycle.text)

    survey_date = table_inf.find('SURVEY_DATE')
    if survey_date is not None:
        item['survey_date'] = trim_data(survey_date.text)

    open_date = table_inf.find('OPEN_DATE')
    if open_date is not None:
        item['open_date'] = trim_data(open_date.text)

    small_area = table_inf.find('SMALL_AREA')
    if small_area is not None:
        item['small_area'] = trim_data(small_area.text)

    return item


def get_meta_data(api_key, stats_data_id):
    """
    メタ情報取得
    """
    url = ('http://api.e-stat.go.jp/rest/1.0/app/getMetaInfo?appId=%s&lang=J&statsDataId=%s' % (api_key, stats_data_id))
    req = urllib2.Request(url)
    opener = urllib2.build_opener()
    conn = opener.open(req)
    cont = conn.read()
    parser = etree.XMLParser(recover=True)
    root = etree.fromstring(cont, parser)
    class_object_tags = root.xpath('//METADATA_INF/CLASS_INF/CLASS_OBJ')
    class_object = {}

    for class_object_tag in class_object_tags:
        class_object_id = class_object_tag.get('id')
        class_object_name = class_object_tag.get('name')
        class_object_item = {
            'id': trim_data(class_object_id),
            'name': trim_data(class_object_name),
            'objects': {}
        }
        class_tags = class_object_tag.xpath('.//CLASS')
        for class_tag in class_tags:
            class_item = {
                'code': trim_data(class_tag.get('code')),
                'name': trim_data(class_tag.get('name')),
                'level': trim_data(class_tag.get('level')),
                'unit': trim_data(class_tag.get('unit'))
            }
            class_object_item['objects'][class_item['code']] = class_item
        class_object[class_object_id] = class_object_item
    return class_object


def export_csv(api_key, stats_data_id, output_path):
    """
    指定の統計情報をCSVにエクスポートする.
    """
    writer = csv.writer(open(output_path, 'wb'), quoting=csv.QUOTE_ALL)

    class_object = get_meta_data(api_key, stats_data_id)
    row = []
    for key in class_object:
        title = class_object[key]['name']
        row.append(title.encode('utf-8'))
    row.append('VALUE')
    writer.writerow(row)

    export_statical_data(writer, api_key, stats_data_id, class_object, 1)


def get_stats_list(api_key, search_kind, key_word):
    """
    統計情報の検索
    @param api_key APIキー
    @param search_kind 統計の種類
    @param key_word 検索キー
    """
    key_word = urllib.quote(key_word.encode('utf-8'))
    url = ('http://api.e-stat.go.jp/rest/1.0/app/getStatsList?appId=%s&lang=J&searchKind=%s&searchWord=%s' % (api_key, search_kind, key_word))
    req = urllib2.Request(url)
    opener = urllib2.build_opener()
    conn = opener.open(req)
    cont = conn.read()
    parser = etree.XMLParser(recover=True)
    root = etree.fromstring(cont, parser)
    ret = []
    data_list = root.find('DATALIST_INF')
    list_infs = data_list.xpath('.//LIST_INF')
    for list_inf in list_infs:
        item = {
            'id': trim_data(list_inf.get('id'))
        }
        stat_name = list_inf.find('STAT_NAME')
        if stat_name is not None:
            item['stat_name'] = trim_data(stat_name.text)
            item['stat_name_code'] = trim_data(stat_name.get('code'))

        gov_org = list_inf.find('GOV_ORG')
        if gov_org is not None:
            item['gov_org'] = trim_data(gov_org.text)
            item['gov_org_code'] = trim_data(gov_org.get('code'))

        statistics_name = list_inf.find('STATISTICS_NAME')
        if statistics_name is not None:
            item['statistics_name'] = trim_data(statistics_name.text)

        title = list_inf.find('TITLE')
        if title is not None:
            item['title'] = trim_data(title.text)

        cycle = list_inf.find('CYCLE')
        if cycle is not None:
            item['cycle'] = cycle.text

        survey_date = list_inf.find('SURVEY_DATE')
        if survey_date is not None:
            item['survey_date'] = trim_data(survey_date.text)

        open_date = list_inf.find('OPEN_DATE')
        if open_date is not None:
            item['open_date'] = trim_data(open_date.text)

        small_area = list_inf.find('SMALL_AREA')
        if small_area is not None:
            item['small_area'] = trim_data(small_area.text)

        ret.append(item)
    return ret


def _get_stats_id_value(api_key, stats_data_id, class_object, start_position, filter_str):
    """
    統計情報の取得
    """
    url = ('http://api.e-stat.go.jp/rest/1.0/app/getStatsData?limit=10000&appId=%s&lang=J&statsDataId=%s&metaGetFlg=N&cntGetFlg=N%s' % (api_key, stats_data_id, filter_str))
    if start_position > 0:
        url = url + ('&startPosition=%d' % start_position)
    req = urllib2.Request(url)
    opener = urllib2.build_opener()
    conn = opener.open(req)
    cont = conn.read()
    parser = etree.XMLParser(recover=True)
    root = etree.fromstring(cont, parser)
    ret = []
    row = {}
    datas = {}
    value_tags = root.xpath('//STATISTICAL_DATA/DATA_INF/VALUE')
    for value_tag in value_tags:
        row = {}
        for key in class_object:
            val = value_tag.get(key)
            if val in class_object[key]['objects']:
                text = class_object[key]['objects'][val]['name']
                row[key] = trim_data(text.encode('utf-8'))
            else:
                row[key] = val.encode('utf-8')
        row['value'] = trim_data(value_tag.text)
        ret.append(row)
    return ret


def get_stats_id_value(api_key, stats_data_id, filter):
    """
    統計取得
    @param api_key APIキー
    @param stats_data_id 統計表ID
    @param filter_str フィルター文字
    """
    filter_str = ''
    for key in filter:
        filter_str += ('&%s=%s' % (key, urllib.quote(filter[key].encode('utf-8'))))
    class_object = get_meta_data(api_key, stats_data_id)
    return _get_stats_id_value(api_key, stats_data_id, class_object, 1, filter_str), class_object


def get_stats_id_list_value(api_key, stats_data_ids, filter):
    """
    統計取得
    @param api_key APIキー
    @param stats_data_id 統計表IDの一覧
    @param filter_str フィルター文字
    """
    filter_str = ''
    for key in filter:
        filter_str += ('&%s=%s' % (key, urllib.quote(filter[key].encode('utf-8'))))
    ret = []
    i = 0
    for stats_data_id in stats_data_ids:
        list, class_object = get_stats_id_value(api_key, stats_data_id, filter_str)
        ret.extend(list)
        i = i + 1
    return ret
