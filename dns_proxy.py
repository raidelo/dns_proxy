from time import strftime
from dnslib.server import DNSServer, DNSHandler, DNSLogger, RR, RCODE, QTYPE
from dnslib.proxy import ProxyResolver
from configparser import ConfigParser

def get_mapping(args:list) -> dict:
    map = {}
    if len(args) == 0:
        return map
    if ',' in args[0]:
        args = args[0].split(',')
    for i in args:
        domain, _, ip = i.partition(':')
        if ip:
            map[domain] = ip
    return map

def get_section_without_defaults(parser:ConfigParser, section:str) -> dict:
    if parser.has_section(section):
        data = {item[0]:item[1] for item in parser.items(section) if item not in parser.items(parser.default_section) and not item[0].startswith('$')}
        return data
    return {}

def parse_logfile(logs_file:str, default_value:str):
    if isinstance(logs_file, str):
        if logs_file.strip().lower() in ['true', '1', 'activate', 'on']:
            return default_value
        elif logs_file.strip().lower() in ['false', '0', 'deactivate', 'off']:
            return False
        else:
            return logs_file
    else:
        return default_value if logs_file else logs_file

class MainResolver(ProxyResolver):
    def __init__(self, address, port, timeout=0, strip_aaaa=False, map={}, exceptions={}):
        self.map = map
        self.exceptions = exceptions
        super().__init__(address, port, timeout, strip_aaaa)
    
    def resolve(self, request, handler):
        domain = domain = self.get_domain(request.q.qname)
        if domain in self.map.keys() and not (domain in self.exceptions.keys() and self.exceptions[domain] == handler.client_address[0]):
            reply = request.reply()
            ip = self.map[domain]
            reply.add_answer(*RR.fromZone('{domain} A {ip}'.format(domain=domain, ip=ip)))
            return reply
        return super().resolve(request, handler)

    def get_domain(self, qname):
        return b'.'.join(qname.label).decode('utf-8')

class MainLogger(DNSLogger):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.logfile = None

    def log_prefix(self, handler):
        if self.prefix:
            return "%s " % (strftime("%Y-%m-%d %X"))
        else:
            return ""

    def log_request(self, handler, request):
        self.logf("%sRequest: [%s:%d] (%s) / '%s' (%s)" % (
                    self.log_prefix(handler),
                    handler.client_address[0],
                    handler.client_address[1],
                    handler.protocol,
                    request.q.qname,
                    QTYPE[request.q.qtype]))
        self.log_data(request)
    
    def log_reply(self, handler, reply):
        if reply.header.rcode == RCODE.NOERROR:
            self.logf("%sReply:   [%s:%d] (%s) / '%s' (%s) / RRs: %s" % (
                    self.log_prefix(handler),
                    handler.client_address[0],
                    handler.client_address[1],
                    handler.protocol,
                    reply.q.qname,
                    QTYPE[reply.q.qtype],
                    ",".join([QTYPE[a.rtype] for a in reply.rr])))
        else:
            self.logf("%sReply:   [%s:%d] (%s) / '%s' (%s) / %s" % (
                    self.log_prefix(handler),
                    handler.client_address[0],
                    handler.client_address[1],
                    handler.protocol,
                    reply.q.qname,
                    QTYPE[reply.q.qtype],
                    RCODE[reply.header.rcode]))
        self.log_data(reply)

    def log_dumper(self, data):
        print(data)
        self.logfile.write(data.encode() + b'\n')
        self.logfile.flush()

    def set_logfile(self, logfile:str):
        try:
            self.logfile = open(logfile, "wb")
            self.logf = self.log_dumper
        except:
            print("error: failed to open the log file")

    def __del__(self):
        if self.logfile:
            self.logfile.close()

def main(local_server_address=('0.0.0.0', 53), dns_server_address=('1.1.1.1', 53), timeout=5, log_format='', log_prefix=False, logs_file:str=False, map={}, exceptions={}):
    resolver = MainResolver(*dns_server_address, timeout=timeout, map=map, exceptions=exceptions)
    logger = MainLogger(log_format, log_prefix)
    if logs_file:
        logger.set_logfile(logs_file)
    server_ = DNSServer(resolver, *local_server_address, logger=logger, handler=DNSHandler)
    try:
        server_.start()
    except KeyboardInterrupt:
        print('Keyboard Interrupt detected. Closing...')
        exit(0)

if __name__ == '__main__':
    from argparse import ArgumentParser
    defaults = {'address':'0.0.0.0',
                'port':53,
                'upstream':'1.1.1.1:53',
                'timeout':5,
                'log_format':'request,reply,truncated,error',
                'log_prefix':False,
                'logs_file':False,
                }
    default_logs_file = 'dns_logs.log'
    parser = ArgumentParser()
    parser.add_argument('-b', '-a', '--bind', '--address', default=defaults['address'], metavar='ADDRESS', dest='address',
                        help='bind to this address '
                        '(default: all interfaces)')
    parser.add_argument('port', default=defaults['port'], type=int, nargs='?',
                        help='bind to this port '
                        '(default: %(default)s)')
    parser.add_argument('-u', '--upstream', default=defaults['upstream'], metavar='<dns server:port>', dest='upstream',
                        help='upstream DNS server:port '
                        '(default: %(default)s)')
    parser.add_argument('-t', '--timeout', default=defaults['timeout'], type=int, dest='timeout',
                        help='timeout for the server to resolve queries '
                        '(default: %(default)s)')
    parser.add_argument('--log-format', default=defaults['log_format'], dest='log_format',
                        help='log hooks to enable '
                        '(default: +request,+reply,+truncated,+error,-recv,-send,-data)')
    parser.add_argument('--log-prefix', action='store_true', default=defaults['log_prefix'], dest='log_prefix',
                        help='log prefix (timestamp/handler/resolver) '
                        '(default: %(default)s)')
    parser.add_argument('--save-config', nargs='?', default=False, const='dns_proxy_settings.ini', type=str, dest='save_config',
                        help='whether to save specified arguments to a config file for load on next start '
                        '(default: %(default)s)')
    parser.add_argument('--use-args', action='store_true', default=False, dest='use_args',
                        help='whether to use by default the arguments passedto the script or \'dns_proxy_settings.ini\' file '
                        '(default: config file)')
    parser.add_argument('-m', '--map', nargs='+', default={}, metavar='<domain:ip domain:ip ...>', dest='map',
                        help='a map like: domain:ip,domain:ip or separated by spaces like: domain:ip domain:ip. It will answer the query for the domain with the given IP address '
                        '(default: %(default)s)')
    parser.add_argument('-x', '--exceptions', nargs='+', default={}, metavar='<domain:ip domain:ip ...>', dest='exceptions',
                        help='similar to parameter --map. If the client\'s IP address matches the given ip and the client is asking for the given domain, the local server will be forced to ask the upstream DNS server for that domain, even if that domain is manually mapped to the specified IP in the MAP section '
                        '(default: %(default)s)')
    parser.add_argument('--logs-file', default=default_logs_file, dest='logs_file',
                        help='whether to dump logs to a file, its name is optional '
                        '(default: %(default)s)')
    args = parser.parse_args()

    map_ = get_mapping(args.map)
    exceptions_ = get_mapping(args.exceptions)

    if args.save_config or not args.use_args:
        c_parser = ConfigParser(defaults=defaults)
        for section in ('SAVED', 'MAP', 'EXCEPTIONS'):
            c_parser.add_section(section)
        config_file_route = args.save_config if args.save_config else 'dns_proxy_settings.ini'
        if args.save_config:
            for arg, xdefect_value in defaults.items():
                dict_args = dict(args._get_kwargs())
                if dict_args[arg] != xdefect_value:
                    c_parser.set('SAVED', arg, str(dict_args[arg]))
            if map_:
                c_parser['MAP'] = map_
            if exceptions_:
                c_parser['EXCEPTIONS'] = exceptions_
            with open(config_file_route, 'w') as file:
                c_parser.write(file)

        if not args.use_args:
            found_ = c_parser.read(config_file_route)
            if found_:
                address = c_parser.get('SAVED', 'address')
                port = c_parser.getint('SAVED', 'port')
                upstream = c_parser.get('SAVED', 'upstream')
                timeout = c_parser.getint('SAVED', 'timeout')
                log_format = c_parser.get('SAVED', 'log_format')
                log_prefix = c_parser.getboolean('SAVED', 'log_prefix')
                logs_file = c_parser.get('SAVED', 'logs_file')
                map_ = get_section_without_defaults(c_parser, 'MAP')
                exceptions_ = get_section_without_defaults(c_parser, 'EXCEPTIONS')
            else:
                args.use_args = True
    if args.use_args:
        address, port, upstream, timeout, log_format, log_prefix, logs_file = args.address, args.port, args.upstream, args.timeout, args.log_format, args.log_prefix, args.logs_file

    upstream_address, _, upstream_port = upstream.partition(':')
    upstream_port = int(upstream_port or 53)
    print('Server started at %s:%d || Remote server at %s:%d'%(address, port, upstream_address, upstream_port))
    main((address, port), (upstream_address, upstream_port), timeout, log_format, log_prefix, parse_logfile(logs_file, default_value=default_logs_file), map_, exceptions_)
