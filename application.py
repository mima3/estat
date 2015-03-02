# coding=utf-8
from bottle import get, post, template, request, Bottle, response, redirect, abort
from json import dumps
import os
import json
from collections import defaultdict
import time
import cgi
import urllib
import estat_db
import peewee
import math


app = Bottle()


def setup(conf):
    global app
    estat_db.connect(conf.get('database', 'path'), conf.get('database', 'mod_path'), conf.get('database', 'sep'))


@app.get('/')
def Home():
    return 'Estat page...'


@app.get('/population')
def populationPage():
    return template('population').replace('\n', '')


def str_isfloat(str):
    try:
        float(str)
        return True
    except ValueError:
        return False


@app.get('/json/get_population')
def getPopulation():
    stat_id = request.query.stat_id
    swlat = request.query.swlat
    swlng = request.query.swlng
    nelat = request.query.nelat
    nelng = request.query.nelng
    attrval = request.query.attr_value

    if (not str_isfloat(swlat) or
        not str_isfloat(swlng) or
        not str_isfloat(nelat) or
        not str_isfloat(nelng)):
        response.content_type = 'application/json;charset=utf-8'
        response.set_header('Access-Control-Allow-Origin', '*')
        response.status = 400
        return json.dumps({'message':'wrong parameter type'})

    maxrange = 1
    if ((math.fabs(float(swlat) - float(nelat)) + math.fabs(float(swlng) - float(nelng))) > maxrange):
        response.content_type = 'application/json;charset=utf-8'
        response.set_header('Access-Control-Allow-Origin', '*')
        response.status = 400
        return json.dumps({'message':'wrong parameter range'})

    ret = estat_db.get_mesh_stat(stat_id, attrval, swlng, swlat, nelng, nelat)
    res = {'type': 'FeatureCollection', 'features': []}
    for r in ret:
        item = {
            'type': 'Feature',
            'geometry': json.loads(r['geometory']),
            'properties': {'value': r['value']}
        }
        res['features'].append(item)
    response.content_type = 'application/json;charset=utf-8'
    response.set_header('Access-Control-Allow-Origin', '*')
    return json.dumps(res)


@app.get('/json/get_mesh_stat_group_by_mesh')
def getPopulationGroupByMesh():
    stat_id = request.query.stat_id
    swlat = request.query.swlat
    swlng = request.query.swlng
    nelat = request.query.nelat
    nelng = request.query.nelng
    if (not str_isfloat(swlat) or
        not str_isfloat(swlng) or
        not str_isfloat(nelat) or
        not str_isfloat(nelng)):
        response.content_type = 'application/json;charset=utf-8'
        response.set_header('Access-Control-Allow-Origin', '*')
        response.status = 400
        return json.dumps({'message':'wrong parameter type'})

    maxrange = 0.7
    if ((math.fabs(float(swlat) - float(nelat)) + math.fabs(float(swlng) - float(nelng))) > maxrange):
        response.content_type = 'application/json;charset=utf-8'
        response.set_header('Access-Control-Allow-Origin', '*')
        response.status = 400
        return json.dumps({'message':'wrong parameter range'})

    ret = estat_db.get_mesh_stat_group_by_mesh(stat_id, swlng, swlat, nelng, nelat)
    res = {'type': 'FeatureCollection', 'features': []}
    for r in ret:
        item = {
            'type': 'Feature',
            'geometry': json.loads(r['geometory']),
            'properties': {}
        }
        for k , i in r.items():
            if k == 'geometory':
                continue
            item['properties'][k] = i
        res['features'].append(item)
    response.content_type = 'application/json;charset=utf-8'
    response.set_header('Access-Control-Allow-Origin', '*')
    return json.dumps(res)
