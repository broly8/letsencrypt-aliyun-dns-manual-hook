#!/usr/bin/env python

import sys
import os
import getopt
import time
import ConfigParser
import aliyun

CONFIG_FILENAME = 'config.ini'


def getAliyunDnsInstance():
    configFilepath = os.path.split(os.path.realpath(__file__))[0] + os.path.sep + CONFIG_FILENAME

    config = ConfigParser.ConfigParser()
    config.read(configFilepath)
    appid = config.get('aliyun', 'appid')
    appsecret = config.get('aliyun', 'appsecret')

    return aliyun.AliyunDns(appid, appsecret)


def auth():
    try:
        if not os.environ.has_key('CERTBOT_DOMAIN'):
            raise Exception('Environment variable CERTBOT_DOMAIN is empty.')
        if not os.environ.has_key('CERTBOT_VALIDATION'):
            raise Exception(
                'Environment variable CERTBOT_VALIDATION is empty.')

        domain = os.environ['CERTBOT_DOMAIN']
        value = os.environ['CERTBOT_VALIDATION']

        aliyunDns = getAliyunDnsInstance()
        # aliyunDns.toString()

        # add letsencrypt domain record
        aliyunDns.addLetsencryptDomainRecord(domain, value)

        # wait for completion
        time.sleep(10)

        print('Success.')

    except Exception as e:
        print('Error: ' + str(e.message) + '\n')
        sys.exit()


def cleanup():
    try:
        if not os.environ.has_key('CERTBOT_DOMAIN'):
            raise Exception('Environment variable CERTBOT_DOMAIN is empty.')

        domain = os.environ['CERTBOT_DOMAIN']

        aliyunDns = getAliyunDnsInstance()
        # aliyunDns.toString()

        # delete letsencrypt domain record
        aliyunDns.deleteLetsencryptDomainRecord(domain)

        # wait for completion
        time.sleep(10)

        print('Success.')

    except Exception as e:
        print('Error: ' + str(e.message) + '\n')
        sys.exit()


def usage():
    def printOpt(opt, desc):
        firstPartMaxLen = 30

        firstPart = '  ' + ', '.join(opt)
        secondPart = desc.replace('\n', '\n' + ' ' * firstPartMaxLen)

        delim = ''
        firstPartLen = len(firstPart)
        if firstPartLen >= firstPartMaxLen:
            spaceLen = firstPartMaxLen
            delim = '\n'
        else:
            spaceLen = firstPartMaxLen - firstPartLen

        delim = delim + ' ' * spaceLen
        print(firstPart + delim + secondPart)

    print('Usage: python %s [option] [arg] ...' % os.path.basename(__file__))
    print('Options:')
    printOpt(['-h', '--help'],
             'Display help information.')
    printOpt(['-v', '--version'],
             'Display version information.')
    printOpt(['--auth'],
             'auth hook.')
    printOpt(['--cleanup'],
             'auth hook.')


def version():
    print('dmlkdevtool.py ' + __version__)
    print(__copyright__)
    print('License ' + __license__ + '.')
    print('Written by ' + __author__ + '.')


def main(argc, argv):
    try:
        if(argc == 1):
            usage()
            raise Exception('')

        opts, args = getopt.getopt(
            argv[1:],
            'hv',
            [
                'help',
                'version',
                'auth',
                'cleanup',
            ]
        )

        for opt, arg in opts:
            if opt in ('-h', '--help'):
                usage()
            elif opt in ('-v', '--version'):
                version()
            elif opt in ('--auth'):
                auth()
            elif opt in ('--cleanup'):
                cleanup()
            else:
                print('Invalid option: ' + opt)

    except getopt.GetoptError as e:
        print('Error: ' + str(e) + '\n')
    except Exception as e:
        if e.message != '':
            print('Error: ' + str(e.message) + '\n')

        sys.exit()


if __name__ == '__main__':
    main(len(sys.argv), sys.argv)
