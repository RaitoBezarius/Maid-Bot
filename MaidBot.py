#!/usr/bin/python
# vim: set fileencoding=utf-8 :
from twitter import *
import ConfigParser, os

class ConfigurationSystem:
    def __init__(self):
        self.Config = ConfigParser.SafeConfigParser()

    def ReadConfig(self, filename):
        self.Config.read(filename)

    def WriteConfig(self, filename):
        self.Config.write(open(filename, 'w'))

class BotOperator(ConfigurationSystem):
    def __init__(self, API, Botname, ConfigFilename):
        ConfigurationSystem.__init__(self)
        self.API = API
        self.BotName = Botname

        self.ReadConfig(ConfigFilename)
        self.AnalyzeConfig()
    
    def AnalyzeConfig(self):
        print('Analyzing bot configuration data...')

    def Run(self):
        print('%s ran.' % self.BotName)


def main():
    print('Analyzing basic configuration data...')

    try:
        basicConfig = ConfigParser.SafeConfigParser({'BotName': 'Unknown'})
        basicConfig.read("BasicBot.conf")

        AppName = basicConfig.get('General', 'AppName')
        BotName = basicConfig.get('General', 'BotName')

        BotConfigFilename = basicConfig.get('Bot', 'ConfigFilename')

        ConsumerKey = basicConfig.get('OAuth', 'ConsumerKey')
        ConsumerSecret = basicConfig.get('OAuth', 'ConsumerSecret')

        if not basicConfig.has_option('OAuth', 'Token') or not basicConfig.has_option('OAuth', 'Secret'):
            oauth_token, oauth_secret = oauth_dance(AppName, ConsumerKey, ConsumerSecret)
            basicConfig.set('OAuth', 'Token', oauth_token)
            basicConfig.set('OAuth', 'Secret', oauth_secret)
        
        OAuthToken = basicConfig.get('OAuth', 'Token')
        OAuthSecret = basicConfig.get('OAuth', 'Secret')
        
        basicConfig.write(open('BasicBot.conf', 'w'))

        api = Twitter(auth = OAuth(OAuthToken, OAuthSecret, ConsumerKey, ConsumerSecret))

        bot = BotOperator(api, BotName, BotConfigFilename)
        bot.Run()
    except ConfigParser.NoSectionError as e:
        print('Failed to find section \'%s\' in a config file. Check your configuration files.' % e.section)

main()
