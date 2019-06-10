def show_urls( urllist, depth=0 ):
    for entry in urllist:
        if ( hasattr( entry, 'namespace' ) ):
            print( "\t" * depth, entry.pattern.regex.pattern,
                   "[%s]" % entry.namespace )
        else:
            print( "\t" * depth, entry.pattern.regex.pattern,
                   "[%s]" % entry.name )
        if hasattr( entry, 'url_patterns' ):
            show_urls( entry.url_patterns, depth + 1 )
