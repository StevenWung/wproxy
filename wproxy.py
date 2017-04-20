import os
import re
import sys
import json
import thread
import socket


class WProxy:
    name = 'WProxy'
    config_file = 'wproxy.json'
    config = None
    #
    host = '0.0.0.0'
    port = 80
    proxy = []

    def __init__(self):
        self.__parse_argues()
        self.__read_config()

    def run(self):
        self.echo("Running %s" % self.name)
        #
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            self.sock.bind((self.host, self.port))
            self.sock.listen(100)
            while 1:
                conn, address = self.sock.accept()
                thread.start_new_thread(self.__accept, (conn, address))

        except Exception, e:
            self.echo("Sock Error : %s" % str(e))
        if self.sock is not None:
            self.sock.close()

    def close(self):
        if self.sock is not None:
            self.sock.close()

    def __accept(self, connection, address):
        request = connection.recv(10240)
        protocol_line = request.split('\r')[0]
        try:
            request_url = protocol_line.split(' ')[1]
        except Exception, e:
            self.echo("Exception : %s [%s]" % (str(e), protocol_line))
        #
        proxy_host = ''
        proxy_port = ''
        for proxy in self.proxy:
            proxy_host = proxy['host']
            proxy_port = proxy['port']
            if re.match(proxy['regex'], request_url):
                break
        #
        proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy_sock.connect((proxy_host, proxy_port))
        proxy_sock.send(request)
        while 1:
            data = proxy_sock.recv(10240)
            if (len(data) > 0):
                connection.send(data)
            else:
                break
        proxy_sock.close()
        connection.close()

    def echo(self, msg):
        print msg

    def __parse_argues(self):
        if len(sys.argv) > 1:
            self.config_file = sys.argv[1]
            if not os._exists(self.config_file):
                self.echo("config file doesnot exist")
                exit(1)

    def __read_config(self):
        fd = open(self.config_file, 'r')
        self.config = json.load(fd)
        fd.close()

        #
        if 'name' in self.config:
            self.name = self.config['name']
        if 'host' in self.config:
            self.listen = self.config['host']
        if 'port' in self.config:
            self.port = self.config['port']
        if 'proxy' in self.config:
            self.proxy = self.config['proxy']
        #
        # validate
        if len(self.proxy) == 0:
            self.echo("Error proxy route should be set")
            exit(1)


if __name__ == "__main__":
    wproxy = WProxy()
    try:
        wproxy.run()
    except KeyboardInterrupt, e:
        wproxy.close()
