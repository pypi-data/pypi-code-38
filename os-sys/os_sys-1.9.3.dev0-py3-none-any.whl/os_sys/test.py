from devserver import build
import devserver
def index(request):
    return build.HTTPResponse('''post: %s <br> get: %s<br>python: <?py
print("hello")
print(''.join(str(request.GET)))
py?>
<?php echo('<br>php test');?>''' % (str(request.POST), str(request.GET)))
#for public with lan
#devserver.build.config(('index', index), host='', port=63001)
#dev
devserver.build.config(('index', index))
