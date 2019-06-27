import requests

class Content:
	
	def __init__(self, url):
		self.url = url
		self.data = requests.get(url).json()['graphql']['shortcode_media']
		self.type = self.data['__typename']
		self.id = self.data['id']
		self.caption = self.data['edge_media_to_caption']['edges']
		self.caption_is_edited = self.data['caption_is_edited']
		self.tagged_user = self.data['edge_media_to_tagged_user']['edges']
		self.is_video = self.data['is_video']
		self.dimensions = self.data['dimensions']
		self.location = self.data['location']
		self.timestamp = self.data['taken_at_timestamp']
		self.likes = self.data['edge_media_preview_like']['count']
		self.comments_disabled = self.data['comments_disabled']
		self.viewer_can_reshare = self.data['viewer_can_reshare']
		self.has_ranked_comments = self.data['has_ranked_comments']
		
		try:
			self.title = self.data['title']
		except:
			self.title = None

	def get_content(self):
		if self.type == 'GraphSidecar':
			data = self.data['edge_sidecar_to_children']['edges']
		else:
			data = [{'node':self.data}]

		result = []
		for node in data:
			item = {}
			if node['node']['is_video']:
				item['content'] = node['node']['video_url']
			else:
				item['content'] = node['node']['display_url']
			item['display_url'] = node['node']['display_url']
			result.append(item)
		return result




