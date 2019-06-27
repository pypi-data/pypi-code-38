# -*- coding: utf-8 -*-
import os
import json
import yaml
import ldap3
import click


USER_BASE_DN_TEMPLATE = u"cn=users,cn=accounts,{base_dn}"
USER_SEARCH_TEMPLATE = u"(uid={username})"

class IpaService(object):

    def __init__(self, host=u"127.0.0.1", port=389, base_dn=None, username=None, password=None, server_params=None, connection_params=None):
        self.host = host
        self.port = port
        self.base_dn = base_dn
        self.server_params = server_params or {}
        self.server_params.update({
            "get_info": ldap3.ALL,
        })
        self.connection_params = connection_params or {}
        if username:
            self.connection_params["user"] = username
        if password:
            self.connection_params["password"] = password
        if not base_dn:
            self.base_dn = self.auto_get_base_dn()
            if not self.base_dn:
                raise RuntimeError(u"异常：未提供BaseDN，且自动获取失败。")

    def auto_get_base_dn(self):
        connection = self.get_connection()
        base_dns = [x for x in connection.server.info.naming_contexts if "dc=" in x]
        if base_dns:
            return base_dns[0]
        else:
            return None

    @property
    def user_base_dn(self):
        return USER_BASE_DN_TEMPLATE.format(base_dn=self.base_dn)

    def get_connection(self):
        server = ldap3.Server(self.host, self.port, **self.server_params)
        connection = ldap3.Connection(server, **self.connection_params)
        connection.bind()
        return connection

    def get_user_detail(self, username, connection=None):
        connection = connection or self.get_connection()
        connection.search(
            search_base=self.base_dn,
            search_filter=USER_SEARCH_TEMPLATE.format(username=username),
            attributes=[ldap3.ALL_ATTRIBUTES, ldap3.ALL_OPERATIONAL_ATTRIBUTES],
            )
        data = {}
        for entry in json.loads(connection.response_to_json())["entries"]:
            data["dn"] = entry["dn"]
            data.update(entry["attributes"])
        for key in data.keys():
            value = data[key]
            if isinstance(value, list) and len(value) == 1:
                data[key] = value[0]
        return data


@click.group()
@click.option("-h", "--host", default="127.0.0.1", help=u"Ldap服务器地址，默认为127.0.0.1。")
@click.option("-p", "--port", default=389, type=int, help=u"Ldap服务端口，默认为389。")
@click.option("-u", "--username", help=u"Ldap帐号，不提供时使用匿名查询。不同权限的帐号，查询范围或字段可能不相同。")
@click.option("-p", "--password", help=u"Ldap帐号，不提供时使用匿名查询。不同权限的帐号，查询范围或字段可能不相同。")
@click.option("-b", "--base-dn", help=u"Ldap的BaseDN。如果为空则自动获取BaseDN，如果有多个，则自动选择第1个命名空间（排除了cn=changelog之类的管理类命名空间）。")
@click.pass_context
def ipa(ctx, host, port, username, password, base_dn):
    u"""Freeipa管理工具集。请指定子命令进行操作。
    """
    ctx.ensure_object(dict)
    ctx.obj["host"] = host
    ctx.obj["port"] = port
    ctx.obj["username"] = username
    ctx.obj["password"] = password
    ctx.obj["base_dn"] = base_dn


@ipa.command(name="get-user-detail")
@click.option("-o", "--output-format", default="yaml", type=click.Choice(['yaml', 'json']), help=u"信息输出格式，默认为yaml格式输出。")
@click.argument("username", nargs=1, required=True)
@click.pass_context
def get_user_detail(ctx, output_format, username):
    u"""查询用户信息，支持yaml/json等格式输出。
    """
    service = IpaService(ctx.obj["host"], ctx.obj["port"], ctx.obj["base_dn"], ctx.obj["username"], ctx.obj["password"])
    user = service.get_user_detail(username)
    if not user:
        click.echo(u"错误：没有找到用户名为 {username} 的帐号。".format(username=username))
        os.sys.exit(1)
    else:
        if output_format.lower() == u"json":
            click.echo(json.dumps(user, ensure_ascii=False))
        else:
            click.echo(yaml.safe_dump(user, allow_unicode=True))

    
if __name__ == "__main__":
    ipa()
