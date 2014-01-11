#!/usr/bin/python
# vim: set fileencoding=utf-8 :
from twython import Twython, exceptions
import pickle, time, os, random

class Settings:
		def __init__(self):
				self.data = dict()

		def Set(self, key, value):
				self.data[key] = value

		def Get(self, key, defaultValue = None):
				if key in self.data:
						return self.data[key]
				else:
						return defaultValue
		
		def Write(self, fileName = 'Settings.data'):
				f = open(fileName, 'wb')
				pickle.dump(self.data, f)
		
		def Read(self, fileName = 'Settings.data'):
				try:
					f = open(fileName, 'rb')
					self.data = pickle.load(f)
				except IOError:
						self.data = dict()

class BotOperator:
		def __init__(self):
				self.Data = Settings()
				self.Data.Read()

				self.ScreenName = 'BotRaito'

				self.Initialization = self.Data.Get('Initialization', True)

				if not self.Initialization:
						self.APP_KEY = self.Data.Get('AppKey')
						self.APP_SECRET = self.Data.Get('AppSecret')
						self.OAUTH_TOKEN_KEY = self.Data.Get('OAuthTokenKey')
						self.OAUTH_TOKEN_SECRET = self.Data.Get('OAuthTokenSecret')

						self.lastSinceId = self.Data.Get('LastSinceId', dict())
				else:
						print('Consumer key ?')
						self.APP_KEY = str(raw_input())
						print('Consumer secret ?')
						self.APP_SECRET = str(raw_input())
						print('OAuth Token Key ?')
						self.OAUTH_TOKEN_KEY = str(raw_input())
						print('OAuth Token Secret ?')
						self.OAUTH_TOKEN_SECRET = str(raw_input())

						self.Data.Set('AppKey', self.APP_KEY)
						self.Data.Set('AppSecret', self.APP_SECRET)
						self.Data.Set('OAuthTokenKey', self.OAUTH_TOKEN_KEY)
						self.Data.Set('OAuthTokenSecret', self.OAUTH_TOKEN_SECRET)
						self.Data.Set('Initialization', False)

				self.Running = True
				self.TweetsProcessed = self.Data.Get('TweetsProcessed', dict())
				self.Users = []

				self.lastSinceId = dict()
				for user in self.Users:
						self.lastSinceId[user] = self.Data.Get('LastSinceId/' + user, 1)

				self.API = Twython(self.APP_KEY, self.APP_SECRET, self.OAUTH_TOKEN_KEY, self.OAUTH_TOKEN_SECRET)

				try:
					self.API.update_status(status = 'Kidô... Kidô.. Kidô. Nishiki. #Activation')
				except exceptions.TwythonError:
					print('Activation already tweeted.')

		def __del__(self):
				self.Data.Write()

		def Log(self, error):
				with open('log.txt', 'w') as f:
						f.write(error.msg + '\n')
				print(error.msg)

		def DumpTweet(self, data):
				tweet = dict()
				tweet['id'] = data['id']
				tweet['id_str'] = data['id_str']
				tweet['text'] = data['text']
				tweet['username'] = data['user']['screen_name']

				return tweet

		def StripUserFromTweet(self, tweet):
				to_strip = '@' + tweet['username'] + ' '
				t = tweet['text'].strip(to_strip)
				to_strip = '@' + self.ScreenName + ' '
				return t.strip(to_strip)
	
		def Reply(self, tweet, replyId):
				self.API.update_status(status = tweet, in_reply_to_status_id = replyId)

		def Ping(self, target):
				return os.system("ping -c 1 " + target) != 0

	
		def ProcessSystemCommand(self, tweet):
				text = tweet['text']
				if text.startswith('Shutdown bot process') or text.startswith('SLR command') or text.startswith("It's time to sleep, Maid.") or text.startswith("Override command number 1"):
						self.Running = False
				elif text.startswith("Ping"):
						params = text.split(' ')
						target = params[1]
						self.API.update_status(status = 'Trying to ping %s' % target)
						if self.Ping(target):
								self.API.update_status(status = 'Target alive.')
						else:
								self.API.update_status(status = 'Target seems to be down.')
				elif text.startswith("Kill"):
						params = text.split(' ')
						target = params[1]
						try:
								self.API.update_status(status = 'Activating combat mode.')
								time.sleep(5)
								self.API.update_status(status = 'Overriding all systems.')
								time.sleep(3)
								self.API.update_status(status = 'Target acquired @%s. Launching procedure number 001.' % target)
						except:
								pass
				elif text.startswith("Give power to"):
						params = text.split(' ')
						target = params[3]
						self.API.update_status(status = 'Temporary power given to @%s. #level1' % target)
						self.lastSinceId[target] = 1
						self.AddUser(target)
				elif text.startswith('Randomize'):
						params = text.split(' ')
						minn = params[1]
						maxn = params[2]
						self.API.update_status(status = ('Randomized number %i.' % random.randint(minn, maxn)))

		def AddUser(self, user):
				self.Users.append(user)

		def MarkTweet(self, tweet):
				self.TweetsProcessed[tweet['id']] = tweet
				self.Data.Set('TweetsProcessed', self.TweetsProcessed)

		def ProcessTweets(self, res, User):
				for tweet in res:
						if tweet['id'] not in self.TweetsProcessed:
								self.lastSinceId[User] = max(tweet['id'], int(self.lastSinceId[User]))
								self.Data.Set('LastSinceId/' + User, self.lastSinceId[User])

								tweetDumped = self.DumpTweet(tweet)

								self.MarkTweet(tweetDumped)

								if '#SystemOverride' in tweetDumped['text']:
										self.ProcessSystemCommand(tweetDumped)
								else:
										print('Unknown tweet logged. (%s)' % (tweetDumped['text']))


		def Run(self):
				while self.Running:
						try:
								for User in self.Users:
										res = self.API.get_user_timeline(screen_name = User, since_id = self.lastSinceId[User], exclude_replies=True, includes_retweets=False, )
										self.ProcessTweets(res, User)
						except exceptions.TwythonError as e:
								self.Log(e)
								print('Sleeping for 30 seconds.')
								time.sleep(30)
						except exceptions.TwythonRateLimitError as e:
								self.Log(e)
								print('Sleeping for 30 minutes.')
								time.sleep(30 * 60)
						time.sleep(5)
				try:
						self.API.update_status(status = 'Bot is now disabled. #off')
				except exceptions.TwythonError as e:
						self.Log(e)
						print('Failed to tweet the state of the bot.')
		def Tweet(self, message):
				self.API.update_status(status = message)

def main():
		print('Starting bot.')
		bot = BotOperator()
		bot.Run()

main()
