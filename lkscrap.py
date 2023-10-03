#!/usr/bin/python3

import sys
import requests
import json
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36.'
}


def make_request(url):
    data = requests.get(url, headers=HEADERS)

    if data.status_code == 200:
        return data
    else:
        return None


def duck_init_search(domain):
    url = f"https://duckduckgo.com/?va=n&t=ht&q=site%3Alinkedin.com%2Fin+{domain}&ia=web"
    return duck_parse_html(make_request(url))


def duck_parse_html(data):
    try:
        i = data.text.find('href="https://links.duckduckgo.com/d.js?q=')
        return data.text[i:i+400].split('"')[1]
        # return data.text[data.text.find('href="https://links.duckduckgo.com/d.js?q='):][:400].split('"')[1]
    except:
        return None


def duck_parse_json(data):
    begin_str = "if (DDG.pageLayout) DDG.pageLayout.load('d',["
    end_str = "DDG.duckbar.load('images');"

    ib = data.find(begin_str)
    ie = data.find(end_str)

    if ib == -1 or ie == -1:
        return None

    raw_data = "[" + data[ib + len(begin_str):ie][:-3] + "]"
    j = json.loads(raw_data)

    return j


def api_search_recurse(url, nb, out=[]):

    #print("[*] JSON recurse: %d (%s)" % (nb, url))
    if nb < 0:
        return out

    data = make_request(url)

    if data is None:
        print("[!] An error occurred while recursing API")
        return out

    j = duck_parse_json(data.text)
    if j is None:
        print("[!] No json found.. return results")
        return out

    nb = nb - 1

    out += j[:-1]
    url = "https://links.duckduckgo.com" + j[-1].get('n')

    time.sleep(2)

    return api_search_recurse(url, nb, out)



if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: %s <domain> [page_number, default 10]" % (sys.argv[0]))
        sys.exit()

    domain = sys.argv[1]
    page_nb = 10 if len(sys.argv) == 2 else int(sys.argv[2])

    print("[*] Targeting %s" % (domain))
    print("[*] Please wait...")

    url = duck_init_search(domain)

    if not url:
        print("[!] Unable to access ducky data! Blocked?")
        quit()

    #print("[*] JSON url: %s" % (url))

    out = api_search_recurse(url, page_nb)

    for d in out:
        print("%s (%s)" % (d.get('t'),d.get('u')))
