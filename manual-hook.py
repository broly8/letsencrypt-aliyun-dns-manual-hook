#!/usr/bin/env python

import sys
import os
import getopt
import time
if sys.version_info < (3,0):
    import ConfigParser
else:
    import configparser as ConfigParser
import aliyun
import logging
import logging.handlers

# Set the global configuration
CONFIG_FILENAME = 'config.ini'
configFilepath = os.path.split(os.path.realpath(__file__))[0] + os.path.sep + CONFIG_FILENAME
config = ConfigParser.ConfigParser()
config.read(configFilepath)

logger = logging.getLogger("logger")
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
consoleHandler = logging.StreamHandler()
logger.setLevel(logging.DEBUG)
consoleHandler.setLevel(logging.DEBUG)
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

fileLogFlag = True if config.get('log','enable').lower() == 'true' else False
if fileLogFlag:
    logfile = config.get('log','logfile')
    fileHandler = logging.FileHandler(filename=logfile)
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)


def getAliyunDnsInstance():
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

        logger.info('Start setting DNS')
        logger.info('Domain:' + domain)
        logger.info('Value:' + value)

        aliyunDns = getAliyunDnsInstance()
        # aliyunDns.toString()

        # add letsencrypt domain record
        aliyunDns.addLetsencryptDomainRecord(domain, value)

        # wait for completion
        logger.info('sleep 10 secs')
        time.sleep(10)

        logger.info('Success.')
        logger.info('DNS setting end!')

    except Exception as e:
        logger.error('Error: ' + str(e.message) + '\n')
        sys.exit()


def cleanup():
    try:
        if not os.environ.has_key('CERTBOT_DOMAIN'):
            raise Exception('Environment variable CERTBOT_DOMAIN is empty.')

        domain = os.environ['CERTBOT_DOMAIN']
        logger.info('Start to clean up')
        logger.info('Domain:' + domain)
        aliyunDns = getAliyunDnsInstance()
        # aliyunDns.toString()

        # delete letsencrypt domain record
        aliyunDns.deleteLetsencryptDomainRecord(domain)

        # wait for completion
        time.sleep(10)

        logger.info('Success.')
        logger.info('Clean up end!')

    except Exception as e:
        logger.error('Error: ' + str(e.message) + '\n')
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
                logger.error('Invalid option: ' + opt)

    except getopt.GetoptError as e:
        logger.error('Error: ' + str(e) + '\n')
    except AttributeError as e:
        logger.error(e.args)
    except Exception as e:
        if e.message != '':
            logger.error('Error: ' + str(e.message) + '\n')

        sys.exit()


if __name__ == '__main__':
    main(len(sys.argv), sys.argv)
