

def html(soup, title='_None'):
    print(f"\n{'*'*60}\n Debug html : {title}\n")
    #print(f"\n soup original :\n\n{soup.prettify()}\n\n")
    for script in soup.find_all('script'):
        soup.script.decompose()
    print(f"\n soup removing JavaScript :\n\n{soup.prettify()}\n\n")
