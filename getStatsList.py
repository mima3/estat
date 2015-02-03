#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import codecs
sys.stdout = codecs.getwriter('cp932')(sys.stdout)
from estat_go_jp import * 

def main(argvs, argc):
    if argc != 4:
        print ("Usage #python %s api_key search_kind key_word" % argvs[0])
        return 1
    api_key = argvs[1]
    search_kind = argvs[2]
    key_word = argvs[3].decode('cp932')
    ret = get_stats_list(api_key, search_kind, key_word)
    print ret

if __name__ == '__main__':
    argvs = sys.argv
    argc = len(argvs)
    sys.exit(main(argvs, argc))
