#!/usr/bin/env python

import sys
import time
import urllib
import base64
import hashlib
import hmac
import logging
import logging.handlers

if sys.version_info < (3,0):
    import urllib2
    import urllib
else:
    import urllib.request as urllib2
    import urllib.parse as urllib


class AliyunDns:
    __endpoint = 'http://alidns.aliyuncs.com'
    __letsencryptSubDomain = '_acme-challenge'
    __appid = ''
    __appsecret = ''
    __logger = logging.getLogger("logger")

    def __init__(self, appid, appsecret):
        self.__appid = appid
        self.__appsecret = appsecret

    def __getSignatureNonce(self):
        return int(round(time.time() * 1000))

    def __percentEncode(self, str):
        if sys.version_info <(3,0):
            res = urllib.quote(str.decode().encode('utf8'), '')
        else:
            res = urllib.quote(str.encode('utf8'))
        res = res.replace('+', '%20')
        res = res.replace('\'', '%27')
        res = res.replace('\"', '%22')
        res = res.replace('*', '%2A')
        res = res.replace('%7E', '~')

        return res

    def __signature(self, params):
        sortedParams = sorted(params.items(), key=lambda params: params[0])

        query = ''
        for (k, v) in sortedParams:
            query += '&' + \
                self.__percentEncode(k) + '=' + self.__percentEncode(str(v))

        stringToSign = 'GET&%2F&' + self.__percentEncode(query[1:])
        try:
            if (sys.version_info <(3,0)):
                h = hmac.new(self.__appsecret + "&", stringToSign, hashlib.sha1)
            else:
                h = hmac.new((self.__appsecret + "&").encode(encoding="utf-8"), stringToSign.encode(encoding="utf-8"), hashlib.sha1)
        except Exception as e:
            self.__logger.error(e)
        signature = base64.encodestring(h.digest()).strip()

        return signature

    def __request(self, params):
        commonParams = {
            'Format': 'JSON',
            'Version': '2015-01-09',
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureNonce': self.__getSignatureNonce(),
            'SignatureVersion': '1.0',
            'AccessKeyId': self.__appid,
            'Timestamp':  time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        # print(commonParams)

        # merge all params
        finalParams = commonParams.copy()
        finalParams.update(params)

        # signature
        finalParams['Signature'] = self.__signature(finalParams)
        self.__logger.info('Signature'+ str(finalParams['Signature']))
        # get final url
        url = '%s/?%s' % (self.__endpoint, urllib.urlencode(finalParams))
        # print(url)

        request = urllib2.Request(url)
        try:
            f = urllib2.urlopen(request)
            response = f.read()
            self.__logger.info(response.decode('utf-8'))
        except urllib2.HTTPError as e:
            self.__logger.info(e.read().strip().decode('utf-8'))
            raise SystemExit(e)

    def addDomainRecord(self, domain, rr, value):
        params = {
            'Action': 'AddDomainRecord',
            'DomainName': domain,
            'RR': rr,
            'Type': 'TXT',
            'Value': value
        }
        self.__request(params)

    def deleteSubDomainRecord(self, domain, rr):
        params = {
            'Action': 'DeleteSubDomainRecords',
            'DomainName': domain,
            'RR': rr,
            'Type': 'TXT'
        }
        self.__request(params)

    def addLetsencryptDomainRecord(self, domain, value):
        self.addDomainRecord(domain, self.__letsencryptSubDomain, value)

    def deleteLetsencryptDomainRecord(self, domain):
        self.deleteSubDomainRecord(domain, self.__letsencryptSubDomain)

    def toString(self):
        print('AliyunDns[appid='+self.__appid +
              ', appsecret='+self.__appsecret+']')
