server_ip = None
server_port = 5000
config_name = "sobey-cube"
config_profile = "release"
config_server_id = "sobeyficus-config-server"
config_fail_fast = True
eureka_default_zone = "http://sobeyficus:JXTYp9icQaTzs4@sobeyficus-eureka:8765/eureka/"
application_name = None

def find_host_ip():
    """
    获取本机的IP地址
    :return:
    """
    global s
    try:
        # 创建一个临时的socket连接
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 向自己发送一个udp的请求
        s.connect(('8.8.8.8', 80))
        # 送结果中获取到真实的ip地址
        ip = s.getsockname()[0]
    finally:
        s.close()

    import config
    if config.server_ip is None:
        config.server_ip = ip
    return ip