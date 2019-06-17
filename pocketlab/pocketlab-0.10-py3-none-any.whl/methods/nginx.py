''' a package of methods to handle nginx configurations '''
__author__ = 'rcj1492'
__created__ = '2017.06'
__license__ = 'MIT'

def compile_nginx(server_list, http_port=80, ssl_port=None, ssl_gateway=''):
    
    '''
        a method to compile nginx configurations for forwarding to containers
        
    :param server_list: list of dictionaries with domain, port and default keys 
    :param http_port: integer with port of incoming http requests
    :param ssl_port: integer with port of incoming ssl requests
    :param ssl_gateway: string with name of ssl gateway connecting nginx to internet
    :return: string with nginx config text
    '''

    # http://nginx.org/en/docs/http/server_names.html
    # https://www.linode.com/docs/websites/nginx/how-to-configure-nginx/

# validate inputs
    if ssl_port:
        if not isinstance(ssl_port, int):
            raise ValueError('compile_nginx(ssl_port=%s) must be an integer.' % str(ssl_port))
        if not ssl_gateway:
            raise ValueError('compile_nginx(ssl_port=%s) requires an ssl_gateway argument.' % str(ssl_port))
    supported_gateways = ['elb', 'certbot']
    if ssl_gateway and not ssl_gateway in supported_gateways:
        from labpack.parsing.grammar import join_words
        gateway_text = join_words(supported_gateways, operator='disjunction')
        raise ValueError('compile_nginx(ssl_gateway=%s) must be either %s.' % (ssl_gateway, gateway_text))

# determine http port destinations
    import re
    domain_pattern = re.compile('^[^\.]*?\.[^\.]*?$')
    domain_list = []
    default_server = {}
    for server in server_list:
        if domain_pattern.match(server['domain']):
            domain_list.append(server)
        if 'default' in server.keys():
            default_server = server

# determine localhost port
    default_port = ''
    default_domain = ''
    if default_server:
        default_port = default_server['port']
        default_domain = default_server['domain']
    else:
        for server in domain_list:
            default_port = server['port']
            default_domain = server['domain']
            break

# construct default nginx insert
    nginx_insert = ''
    proxy_headers = ''
    ssl_map = {}
            
# determine proxy headers and health check localhost address for elb gateway
    if ssl_gateway == 'elb':
        proxy_headers = 'proxy_set_header X-Real-IP $remote_addr; proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; proxy_set_header Host $http_host; '
        if default_port:
            nginx_insert += 'server { listen %s; server_name localhost; location / { proxy_pass http://localhost:%s; } } ' % (http_port, default_port)

# determine ssl fields for certbot gateway
    elif ssl_gateway == 'certbot':
        for server in domain_list:
            ssl_insert = 'ssl_certificate "/etc/letsencrypt/live/%s/fullchain.pem";' % server['domain']
            ssl_insert += ' ssl_certificate_key "/etc/letsencrypt/live/%s/privkey.pem";' % server['domain']
            ssl_insert += ' ssl_session_cache shared:SSL:1m;'
            ssl_insert += ' ssl_session_timeout 10m;'
            ssl_insert += ' ssl_protocols TLSv1.2;'
            ssl_insert += ' ssl_ciphers "ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA:ECDHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA256:DHE-RSA-AES256-SHA:ECDHE-ECDSA-DES-CBC3-SHA:ECDHE-RSA-DES-CBC3-SHA:EDH-RSA-DES-CBC3-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:DES-CBC3-SHA:!DSS";'
            ssl_insert += ' ssl_prefer_server_ciphers on;'
            ssl_map[server['domain']] = ssl_insert

# construct ssl only properties
    if ssl_port and ssl_gateway:
        for server in domain_list:
            nginx_insert += 'server { listen %s; server_name .%s; rewrite ^ https://$server_name$request_uri? permanent; } ' % (http_port, server['domain'])
        if default_port:
            nginx_insert += 'server { listen %s default_server; location / { proxy_pass http://localhost:%s; %s} } ' % (http_port, default_port, proxy_headers)

    # add ssl for each server subdomain
        ssl_listener = ''
        for server in server_list:
            server_details = ''
            if ssl_gateway == 'elb':
                server_details = 'server { listen %s; server_name %s; location / { proxy_pass http://localhost:%s; %s} }' % (ssl_port, server['domain'], server['port'], proxy_headers)
            elif ssl_gateway == 'certbot':
                for key, value in ssl_map.items():
                    domain_index = server['domain'].rfind(key)
                    if domain_index > 0:
                        if server['domain'][:domain_index] + key == server['domain']:
                            server_details = 'server { listen %s ssl; server_name %s; %s location / { proxy_pass http://localhost:%s; } }' % (ssl_port, server['domain'], value, server['port'])
                    elif domain_index == 0:
                        server_details = 'server { listen %s ssl; server_name %s; %s location / { proxy_pass http://localhost:%s; } }' % (ssl_port, server['domain'], value, server['port'])
            if ssl_listener:
                ssl_listener += ' '
            ssl_listener += server_details
    
    # add redirection for all other subdomains
        for server in domain_list:
            if ssl_gateway == 'elb':
                ssl_listener += ' server { listen %s; server_name www.%s; return 301 https://%s; }' % (ssl_port, server['domain'], server['domain'])
        if default_domain and ssl_gateway == 'elb':
            ssl_listener += ' server { listen %s default_server; rewrite ^ https://%s permanent; }' % (ssl_port, default_domain)
        nginx_insert += ssl_listener

# construct http properties
    else:
        open_listener = ''
        for server in server_list:
            server_details = 'server { listen %s; server_name %s; location / { proxy_pass http://localhost:%s; %s} }' % (http_port, server['domain'], server['port'], proxy_headers)
            if open_listener:
                open_listener += ' '
            open_listener += server_details
        for server in domain_list:
            open_listener += ' server { listen %s; server_name www.%s; return 301 http://%s; }' % (http_port, server['domain'], server['domain'])
            open_listener += ' server { listen %s; server_name *.%s; rewrite ^ http://%s permanent; }' % (http_port, server['domain'], server['domain'])
        if default_port:
            open_listener += ' server { listen %s default_server; location / { proxy_pass http://localhost:%s; %s} }' % (http_port, default_port, proxy_headers)
        nginx_insert += open_listener

# construct nginx properties
    nginx_text = 'user nginx; worker_processes auto; events { worker_connections 1024; } pid /var/run/nginx.pid; http { %s }' % nginx_insert
    
    return nginx_text

def extract_servers(nginx_text):
    
    server_list = []

# define regex
    import re
    server_regex = re.compile('server\s\{.*?(?=server\s\{|$)', re.S)
    domain_regex = re.compile('server_name\s(.*?);.*?\slocation\s/\s\{\sproxy_pass\shttp://localhost:(\d+);', re.S)
    default_open = re.compile('default_server;\slocation\s/\s\{\sproxy_pass\shttp://localhost:(\d+);', re.S)
    default_ssl = re.compile('default_server;\srewrite\s\^\shttps://(.*?)\spermanent;', re.S)

# search for matches
    server_search = server_regex.findall(nginx_text)
    default_port = 0
    default_domain = ''
    if server_search:
        for server_text in server_search:
            domain_search = domain_regex.findall(server_text)
            if domain_search:
                for match in domain_search:
                    name = match[0]
                    port = int(match[1])
                    if name != 'localhost':
                        server_list.append({'domain': name, 'port': port})
            open_search = default_open.findall(server_text)
            if open_search:
                default_port = int(open_search[0])
            ssl_search = default_ssl.findall(server_text)
            if ssl_search:
                default_domain = ssl_search[0]

    for server in server_list:
        if server['port'] == default_port:
            server['default'] = True
        elif server['domain'] == default_domain:
            server['default'] = True
            
    return server_list

if __name__ == '__main__':

# test open domains
    container_list = [ { 'domain': 'collectiveacuity.com', 'port': 5000 } ]
    nginx_text = compile_nginx(container_list)
    assert nginx_text.find('listen 80; server_name collectiveacuity.com;') > -1
    new_list = extract_servers(nginx_text)
    assert len(new_list) == len(container_list)
    assert new_list[0]['default']

# test ssl with elb
    nginx_text = compile_nginx(container_list, ssl_port=443, ssl_gateway='elb')
    assert nginx_text.find('rewrite ^ https://$server_name$request_uri?') > -1   

# test multiple domains on elb
    container_list.append({'domain': 'api.collectiveacuity.com', 'port': 5001})
    nginx_text = compile_nginx(container_list, ssl_port=443, ssl_gateway='elb')
    nginx_readable = nginx_text.replace(';', ';\n').replace('}', '}\n').replace('{', '{\n')
    print(nginx_readable)
    new_list = extract_servers(nginx_text)
    assert len(new_list) == len(container_list)
    assert new_list[0]['default']

# test multiple domains on certbot
    nginx_text = open('../../../cred/conf/nginx.conf').read()
    nginx_text = compile_nginx(container_list, ssl_port=443, ssl_gateway='certbot')
    nginx_readable = nginx_text.replace(';', ';\n').replace('}', '}\n').replace('{', '{\n')
    print(nginx_readable)
    new_list = extract_servers(nginx_text)
    assert len(new_list) == len(container_list)
    assert new_list[0]['default']
    print(nginx_text)
    print(new_list)

