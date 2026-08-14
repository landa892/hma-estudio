# -*- coding: utf-8 -*-
"""Avisa a IndexNow las URLs publicas del sitemap.

No forma parte del build: una falla externa nunca debe impedir un deploy. Se
ejecuta despues de publicar, cuando el archivo de validacion ya esta online.

    python docs/indexnow.py
"""
from __future__ import print_function

import io
import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = 'estudiohma.com'
KEY = 'c4fcc864706e47bab235d75dd0fcf3fd'
KEY_LOCATION = 'https://%s/%s.txt' % (HOST, KEY)


def urls_from_sitemap():
    with io.open(os.path.join(ROOT, 'sitemap.xml'), encoding='utf-8') as source:
        root = ET.fromstring(source.read())
    namespace = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    return [node.text for node in root.findall('s:url/s:loc', namespace)
            if node.text]


def main():
    urls = urls_from_sitemap()
    payload = json.dumps({
        'host': HOST,
        'key': KEY,
        'keyLocation': KEY_LOCATION,
        'urlList': urls,
    }).encode('utf-8')
    request = urllib.request.Request(
        'https://api.indexnow.org/indexnow',
        data=payload,
        headers={'Content-Type': 'application/json; charset=utf-8'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status = response.getcode()
    except Exception as error:
        print('IndexNow no pudo recibir las URLs: %s' % error)
        return 1
    if status not in (200, 202):
        print('IndexNow respondio HTTP %s' % status)
        return 1
    print('IndexNow recibio %d URLs (HTTP %s)' % (len(urls), status))
    return 0


if __name__ == '__main__':
    sys.exit(main())
