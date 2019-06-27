import requests

class Profile:

	def __init__(self, username):
		self.username = username
		self.url = 'https://www.instagram.com/%s?__a=1' % self.username
		self.data = requests.get(self.url).json()['graphql']['user']
		self.name = self.data['full_name']
		self.is_private = self.data['is_private']
		self.is_verified = self.data['is_verified']
		self.following = self.data['edge_follow']['count']
		self.follower = self.data['edge_followed_by']['count']
		self.biography = self.data['biography']
		self.external_url = self.data['external_url']
		self.id = self.data['id']
		self.is_business_account = self.data['is_business_account']
		self.is_joined_recently = self.data['is_joined_recently']
	def __len__(self):
		posts = self.data['edge_owner_to_timeline_media']['count']
		return posts
	def __str__(self):
		text = str("Name: {}\n".format(self.name)+
				   "Followers: {:,}\n".format(self.follower)+
				   "Following: {:,}\n".format(self.following)+
				   "Posts: {:,}\n".format(self.__len__())+
				   "Biography: {}\n".format(self.biography)+
				   "Url: {}".format(self.url))
		return text

	def get_avatar(self):
		return self.data['profile_pic_url_hd']
	def get_posts(self):
		data = self.data['edge_owner_to_timeline_media']['edges']
		result = []
		for node in data:
			result.append('https://www.instagram.com/p/%s?__a=1' % node['node']['shortcode'])
		return result
	def get_igtv(self):
		data = self.data['edge_felix_video_timeline']['edges']
		result = []
		for node in data:
			result.append('https://www.instagram.com/tv/%s?__a=1' % node['node']['shortcode'])
		return result





