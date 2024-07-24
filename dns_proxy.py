from dnslib.server import DNSServer, DNSHandler, DNSLogger
from dnslib.proxy import ProxyResolver
from configparser import ConfigParser

def main(local_server_address=('0.0.0.0', 53), dns_server_address=('1.1.1.1', 53), timeout=5, log='', log_prefix=False):
    resolver = ProxyResolver(*dns_server_address, timeout=timeout)
    logger = DNSLogger(log, log_prefix)
    server_ = DNSServer(resolver, *local_server_address, logger=logger, handler=DNSHandler)
    try:
        server_.start()
    except KeyboardInterrupt:
        print('Keyboard Interrupt detected. Closing...')
        exit(0)

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-b', '-a', '--bind', '--address', default='0.0.0.0', metavar='ADDRESS', dest='address',
                        help='bind to this address '
                             '(default: all interfaces)')
    parser.add_argument('port', default=53, type=int, nargs='?',
                        help='bind to this port '
                             '(default: %(default)s)')
    parser.add_argument('-u', '--upstream', default='1.1.1.1:53', metavar='<dns server:port>', dest='upstream',
                        help='upstream DNS server:port '
                             '(default: %(default)s)')
    parser.add_argument('-t', '--timeout', default=5, dest='timeout', type=int,
                        help='timeout for the server to resolve queries '
                             '(default: %(default)s)')
    parser.add_argument('--log', default='request,reply,truncated,error', dest='log',
                        help='log hooks to enable (default: +request,+reply,+truncated,+error,-recv,-send,-data)')
    parser.add_argument('--log-prefix', action='store_true', default=False, dest='log_prefix',
                        help='log prefix (timestamp/handler/resolver) (default: False)')
    parser.add_argument('--save-config', nargs='?', default=False, const='dns_proxy_settings.ini', type=str, dest='save_config',
                        help='whether to save specified arguments to a config file for load on next start'
                             '(default: %(default)s)')
    parser.add_argument('--use-args', action='store_true', default=False, dest='use_args',
                        help='whether to use by default the arguments passedto the script or \'dns_proxy_settings.ini\' file'
                             '(default: config file)')
    args = parser.parse_args()

    defaults = {'address':'0.0.0.0',
                'port':53,
                'upstream':'1.1.1.1:53',
                'timeout':5,
                'log':'request,reply,truncated,error',
                'log_prefix':False,
                }

    c_parser = ConfigParser(defaults=defaults)
    c_parser.add_section('SAVED')
    config_file_route = args.save_config if args.save_config else 'dns_proxy_settings.ini'
    if args.save_config:
        for arg, xdefect_value in defaults.items():
            dict_args = dict(args._get_kwargs())
            if dict_args[arg] != xdefect_value:
                c_parser.set('SAVED', arg, str(dict_args[arg]))
        with open(config_file_route, 'w') as file:
            c_parser.write(file)

    if not args.use_args:
        found_ = c_parser.read(config_file_route)
        if found_:
            address = c_parser.get('SAVED', 'address')
            port = c_parser.getint('SAVED', 'port')
            upstream = c_parser.get('SAVED', 'upstream')
            timeout = c_parser.getint('SAVED', 'timeout')
            log = c_parser.get('SAVED', 'log')
            log_prefix = c_parser.get('SAVED', 'log_prefix')
        else:
            args.use_args = True
    if args.use_args:
        address, port, upstream, timeout, log, log_prefix = args.address, args.port, args.upstream, args.timeout, args.log, args.log_prefix

    upstream_address, _, upstream_port = args.upstream.partition(':')
    upstream_port = int(upstream_port or 53)
    print('Server started at %s:%d'%(address, port))
    main((address, port), (upstream_address, upstream_port), timeout, log, log_prefix)