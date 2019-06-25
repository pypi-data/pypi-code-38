from .esindex import ESIndex
from .golden_q import GOLDENQ

class YTCaptionIndex(ESIndex):
    # YTCaptionIndex defines an ESIndex specific
    # to indexing and searching Youtube video captions
    class Meta:
        index_name = 'yt-captions'
        doc_type = 'yt-video'
        doc_id_tmpl = 'yt-video-%(id)s'
        mapping = {
          'properties': {
            'id': { 'type': 'text', 'index': 'false' },
            'upload_date': { 'type': 'date', 'index': 'false'  },
            'title': { 'type': 'text' },
            'description': { 'type': 'text', 'analyzer':'english' },
            'thumbnail': { 'type': 'text', 'index': 'false'  },
            'url': { 'type': 'text', 'index': 'false' },
            'captions': {
              'type': 'nested',
              'properties': {
                'start': {'type':'long', 'index': 'false' },
                'end': {'type':'long', 'index': 'false' },
                'content': {'type':'text', 'analyzer':'english'}
              }
            }
          }
        }

    def search(self, query, query_type='match_phrase', size=20, from_=0, q_func=GOLDENQ):
        q = q_func(query)
        return self._es.search(index=self.Meta.index_name, body=q, size=size, from_=from_)

    def get(self, id):
        return self._es.get(id=self.Meta.doc_id_tmpl%{'id':id}, index=self.Meta.index_name)
