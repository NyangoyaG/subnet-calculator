#!/usr/bin/env python3
"""AI-Powered IPv4 Subnet Calculator"""

import ipaddress

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLOR = True
except ImportError:
    COLOR = False
    class Fore:
        RED = GREEN = YELLOW = CYAN = WHITE = ''
    class Style:
        RESET_ALL = ''


class AISubnetCalculator:
    def __init__(self, ip_str, prefix=None):
        self.ip_str = ip_str
        self.prefix = prefix
        if '/' in ip_str and prefix is None:
            parts = ip_str.split('/')
            self.ip_str = parts[0]
            self.prefix = int(parts[1])
        if self.prefix is None:
            self.prefix = self._detect_class_prefix()
        self.network = ipaddress.ip_network(f"{self.ip_str}/{self.prefix}", strict=False)

    def _detect_class_prefix(self):
        first = int(self.ip_str.split('.')[0])
        if 1 <= first <= 126: return 8
        elif 128 <= first <= 191: return 16
        elif 192 <= first <= 223: return 24
        return 24

    def get_class_info(self):
        first = int(self.ip_str.split('.')[0])
        if 1 <= first <= 126: return 'A', 8
        elif 128 <= first <= 191: return 'B', 16
        elif 192 <= first <= 223: return 'C', 24
        return 'Special', None

    def get_next_boundary(self):
        if self.prefix <= 8: return 8
        elif self.prefix <= 16: return 16
        elif self.prefix <= 24: return 24
        return 32

    def get_block_size(self):
        return 2 ** (self.get_next_boundary() - self.prefix)

    def get_number_of_subnets(self):
        _, cb = self.get_class_info()
        if cb is None: return 0
        return 2 ** (self.prefix - cb)

    def get_usable_hosts(self):
        return max((2 ** (32 - self.prefix)) - 2, 0)

    def get_network_address(self): return str(self.network.network_address)
    def get_broadcast_address(self): return str(self.network.broadcast_address)

    def get_first_usable(self):
        hosts = list(self.network.hosts())
        return str(hosts[0]) if hosts else 'N/A'

    def get_last_usable(self):
        hosts = list(self.network.hosts())
        return str(hosts[-1]) if hosts else 'N/A'

    def get_subnet_mask(self): return str(self.network.netmask)

    def get_wildcard_mask(self):
        return '.'.join(str(255 - int(o)) for o in str(self.network.netmask).split('.'))

    def get_all_answers(self):
        return [
            {'question': 'Number of subnets', 'answer': str(self.get_number_of_subnets())},
            {'question': 'Number of usable IPs', 'answer': str(self.get_usable_hosts())},
            {'question': 'First usable IP', 'answer': self.get_first_usable()},
            {'question': 'Last usable IP', 'answer': self.get_last_usable()},
            {'question': 'Broadcast IP', 'answer': self.get_broadcast_address()},
            {'question': 'Network IP', 'answer': self.get_network_address()},
            {'question': 'Wildcard mask', 'answer': self.get_wildcard_mask()}
        ]


if __name__ == '__main__':
    calc = AISubnetCalculator('192.168.34.221/27')
    print(f"Network: {calc.get_network_address()}")
    print("OK")
