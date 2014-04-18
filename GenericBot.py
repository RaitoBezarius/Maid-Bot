#!/usr/bin/python
# vim: set fileencoding=utf-8 :
from twitter import *
import ConfigParser, os, argparse, random

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
  
    
    def _Tweet(self, t):
        try:
            self.API.statuses.update(status = t)
        except:
            return False

        return True

    def _RetryRandomTweet(self, list_tweets):
        selected_tweet = random.choice(list_tweets)
        tweeted = False
        while not tweeted and len(list_tweets) > 0:
            selected_tweet = random.choice(list_tweets)
            tweeted = self._Tweet(selected_tweet)
            if not tweeted:
                list_tweets.remove(selected_tweet)

        return tweeted


    def Run(self, statuses, randomize):
        print('%s ran.' % self.BotName)
        if not randomize:
            for tweet in statuses:
                if not self._Tweet(tweet):
                    print('Failed to tweet %s.' % tweet)
        else:
            if not self._RetryRandomTweet(statuses):
                print('Failed to tweet only one tweet from the list.')


def main():
    print('Analyzing basic configuration data and command line options...')

    try:
        parser = argparse.ArgumentParser(description='Generic bot.')
        
        parser.add_argument('-s', '--status', action="append", help="tweet what you've wrote !", required=True)
        parser.add_argument('-r', '--randomize', action="store_true", help="choose one tweet from list and randomize it")
        parser.add_argument('-bot', '--botname', help='set bot name (eyecandy)', required=True)
        parser.add_argument('-config', '--basic_config_file', help='path where basic config file is (default: BasicBot.conf)', default="BasicBot.conf")
        parser.add_argument('-bot_config', '--bot_config_file', help='path where bot config file is (default: BotConfig.conf)', default="BotConfig.conf")

        Args = parser.parse_args()

        basicConfig = ConfigParser.SafeConfigParser({'TwitterCredentialsPath': '~/.default_creds', 'BotName': 'Unknown'})
        basicConfig.read(Args.basic_config_file)

        TwitterCredsPath = os.path.expanduser(basicConfig.get('General', 'TwitterCredentialsPath'))

        AppName = basicConfig.get('General', 'AppName')

        ConsumerKey = basicConfig.get('OAuth', 'ConsumerKey')
        ConsumerSecret = basicConfig.get('OAuth', 'ConsumerSecret')

        if not os.path.exists(TwitterCredsPath):
            oauth_dance(AppName, ConsumerKey, ConsumerSecret, TwitterCredsPath)

        oauth_token, oauth_secret = read_token_file(TwitterCredsPath)

        api = Twitter(auth = OAuth(oauth_token, oauth_secret, ConsumerKey, ConsumerSecret))

        bot = BotOperator(api, Args.botname, Args.bot_config_file)
        bot.Run(Args.status, Args.randomize)
    except ConfigParser.NoSectionError as e:
        print('Failed to find section \'%s\' in a config file. Check your configuration files.' % e.section)

main()
