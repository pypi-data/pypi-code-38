from .initializer_model import InitializerModel
from .media import Media
import textwrap

class Account(InitializerModel):

    def __init__(self, props = None):
        super(Account, self).__init__(props)

    def get_profile_picture_url(self):
        try:
            if (self.profile_pic_url_hd != ''):
                return self.profile_pic_url_hd
        except AttributeError:
            try:
                return self.profile_pic_url
            except AttributeError:
                return ''

    def __str__(self):
        string = f'''
        Account info:
        Id: {self.identifier}
        Username: {self.username if hasattr(self, 'username') else '-'}
        Full Name: {self.full_name if hasattr(self, 'full_name') else '-'}
        Bio: {self.biography if hasattr(self, 'biography') else '-'}
        Profile Pic Url: {self.get_profile_picture_url}
        External url: {self.external_url if hasattr(self, 'external_url') else '-'}
        Number of published posts: {self.media_count if hasattr(self, 'mediaCount') else '-'}
        Number of followers: {self.followed_by_count if hasattr(self, 'followed_by_count') else '-'}
        Number of follows: {self.follows_count if hasattr(self, 'follows_count') else '-'}
        Is private: {self.is_private if hasattr(self, 'is_private') else '-'}
        Is verified: {self.is_verified if hasattr(self, 'is_verified') else '-'}
        '''
        return textwrap.dedent(string)

    '''
     * @param Media $media
     * @return Account
     '''
    def add_media(self, media):
        try:
            self.medias.append(media)
        except AttributeError:
            raise AttributeError



    def _init_properties_custom(self, value, prop, array):
        
        if prop == 'id':
            self.identifier = value

        standart_properties = [
            'username',
            'full_name',
            'profile_pic_url',
            'profile_pic_url_hd',
            'biography',
            'external_url',
            'is_private',
            'is_verified',
            'blocked_by_viewer',
            'country_block',
            'followed_by_viewer',
            'follows_viewer',
            'has_channel',
            'has_blocked_viewer', 
            'highlight_reel_count',
            'has_requested_viewer',
            'is_business_account',
            'is_joined_recently',
            'business_category_name',
            'business_email',
            'business_phone_number',
            'business_address_json',
            'requested_by_viewer',
            'connected_fb_page'
        ]
        if prop in standart_properties: 
            self.__setattr__(prop, value)   
        
        if prop == 'edge_follow':
            self.follows_count = array[prop]['count'] if array[prop]['count'] != None  else 0

        if prop == 'edge_followed_by':
            self.followed_by_count = array[prop]['count'] if array[prop]['count'] != None  else 0

        if prop == 'edge_owner_to_timeline_media':
            self._init_media(array[prop])


    def _init_media(self, array):
        self.media_count = array['count'] if 'count' in array.keys() else 0 

        try:
            nodes = array['edges']
        except:
            return

        if not self.media_count or isinstance(nodes, list):
            return

        for media_array in nodes:
            media = Media(media_array['node'])
            if isinstance(media, Media):
                self.add_media(media)
