# *-* coding: utf-8 *-*

headers = {
    "Accept-Encoding":"gzip",
    "Cache-Control": "max-age=0",
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36',
    "Accept-Language":  "zh-CN,zh;q=0.8,en;q=0.6,en-US;q=0.4,zh-TW;q=0.2",
    "Connection" :  "keep-alive",
    "Accept-Encoding" :  "gzip, deflate",
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

class Dict(object):
    def __init__(self, mapping):
        if isinstance(mapping, dict):
            for key, value in dict(mapping).iteritems():
                if isinstance(value, dict):
                    setattr(self, key, Dict(value))
                elif isinstance(value, (tuple, list)):
                    setattr(self, key, [Dict(x) if isinstance(x, dict) else x for x in value])
                else:
                    setattr(self, key, value)
            super(Dict, self).__init__()
        else:
            raise TypeError('only support dict object')

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __setitem__(self, key, value):
        self.__setattr__(key, value)
