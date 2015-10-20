# convenience wrapper for urllib2 & friends

try:
    import cookielib as cookiejar
except ImportError:
    import http.cookiejar as cookiejar
import json
import urllib
try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

try:
    from urllib import quote, quote_plus as _quote_plus
except ImportError:
    from urllib.parse import quote, quote_plus as _quote_plus

try:
    from urllib2 import HTTPError, URLError
except ImportError:
    from urllib.error import HTTPError, URLError

from lxml import etree, html


ua_skybot = 'Skybot/1.0 http://github.com/rmmh/skybot'

ua_firefox = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.6) ' \
    'Gecko/20070725 Firefox/2.0.0.6'
ua_internetexplorer = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'

jar = cookiejar.CookieJar()


def get(*args, **kwargs):
    return open(*args, **kwargs).read()


def get_html(*args, **kwargs):
    return html.fromstring(get(*args, **kwargs))


def get_xml(*args, **kwargs):
    return etree.fromstring(get(*args, **kwargs))


def get_json(*args, **kwargs):
    return json.loads(get(*args, **kwargs))


def open(url, query_params=None, user_agent=None, post_data=None,
         get_method=None, cookies=False, **kwargs):

    if query_params is None:
        query_params = {}

    if user_agent is None:
        user_agent = ua_skybot

    query_params.update(kwargs)

    url = prepare_url(url, query_params)

    request = urllib2.Request(url, post_data)

    if get_method is not None:
        request.get_method = lambda: get_method

    request.add_header('User-Agent', user_agent)

    if cookies:
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
    else:
        opener = urllib2.build_opener()

    return opener.open(request)


def prepare_url(url, queries):
    if queries:
        scheme, netloc, path, query, fragment = urlparse.urlsplit(url)

        query = dict(urlparse.parse_qsl(query))
        query.update(queries)
        query = urllib.urlencode(dict((to_utf8(key), to_utf8(value))
                                  for key, value in query.items()))

        url = urlparse.urlunsplit((scheme, netloc, path, query, fragment))

    return url


def to_utf8(s):
    if isinstance(s, unicode):
        return s.encode('utf8', 'ignore')
    else:
        return str(s)


def quote_plus(s):
    return _quote_plus(to_utf8(s))


def unescape(s):
    if not s.strip():
        return s
    return html.fromstring(s).text_content()
