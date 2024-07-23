from dnslib.server import DNSServer, DNSHandler, DNSLogger
from dnslib.proxy import ProxyResolver

def main(local_server_address=('0.0.0.0', 53), dns_server_address=('1.1.1.1', 53), timeout=5, log='', log_prefix=False):
    resolver = ProxyResolver(*dns_server_address, timeout=timeout)
    logger = DNSLogger(log, log_prefix)
    server_ = DNSServer(resolver, *local_server_address, logger=logger, handler=DNSHandler)
    server_.start()

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
    args = parser.parse_args()
    upstream_address, _, upstream_port = args.upstream.partition(':')
    upstream_port = int(upstream_port or 53)
         
    main((args.address, args.port), (upstream_address, upstream_port), args.timeout, args.log, args.log_prefix)