from .ytcaptions import YTCaptionIndex

def index_class_factory( es_index_class=YTCaptionIndex, index='yt-captions', dtype='yt-video', doc_id_tmpl='yt-video-%(id)s' ):
    # We may want to index different Youtube channels using differnt
    # index and doc type names?
    class index_class(es_index_class):
        pass
    index_class.Meta.index_name = index
    index_class.Meta.doc_type = dtype
    index_class.Meta.doc_id_tmpl = doc_id_tmpl
    return index_class

def Index( index, dtype='yt-video', es_host='localhost:9200' ):
    # Create and instantiate a dynamic YTCaptionIndex
    return index_class_factory(index=index, dtype=dtype)(es_host)
