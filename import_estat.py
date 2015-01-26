#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from estat_go_jp import * 
from estat_db import *
import sys


def main(argvs, argc):
    if argc != 5:
        print ("Usage #python %s api_key search_kind search_kind key_word mod_spatialite_path" % argvs[0])
        return 1
    api_key = argvs[1]
    search_kind = argvs[2]
    wd = argvs[3].decode('cp932')
    mod_spatialite_path = argvs[4]
    setup('estat.sqlite', mod_spatialite_path)
    stats_list = get_stats_list(api_key, search_kind, wd)
    stats_ids = []
    i = 0
    for stats in stats_list:
        print stats['title'], i, len(stats_list)
        import_stat(api_key, stats['id'])
        i = i + 1


if __name__ == '__main__':
    argvs = sys.argv
    argc = len(argvs)
    sys.exit(main(argvs, argc))
