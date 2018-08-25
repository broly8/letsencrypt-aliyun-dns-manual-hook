#!/usr/bin/env python

import sys
import time
import urllib
import base64
import hashlib
import hmac
import urllib
import urllib2


class AliyunDns:
    __endpoint = 'http://alidns.aliyuncs.com'
    __letsencryptSubDomain = '_acme-challenge'
    __appid = ''
    __appsecret = ''

    def __init__(self, appid, appsecret):
        self.__appid = appid
        self.__appsecret = appsecret

    def __getSignatureNonce(self):
        return int(round(time.time() * 1000))

    def __percentEncode(self, str):
        res = urllib.quote(str.decode(
            sys.stdin.encoding).encode('utf8'), '')
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
        h = hmac.new(self.__appsecret + "&", stringToSign, hashlib.sha1)
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

        # get final url
        url = '%s/?%s' % (self.__endpoint, urllib.urlencode(finalParams))
        # print(url)

        request = urllib2.Request(url)
        try:
            f = urllib2.urlopen(request)
            response = f.read()

            print(response)
        except urllib2.HTTPError as e:
            print(e.read().strip())
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
