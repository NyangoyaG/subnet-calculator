#!/usr/bin/env python3
"""
AI-Powered Subnet Calculator - Web Interface
Accessible from any browser
"""

from flask import Flask, request, render_template, jsonify, send_from_directory
from flask_cors import CORS
import ipaddress
import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import the AI calculator
try:
    from ai_subnet_calculator import AISubnetCalculator
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("⚠️ AI Subnet Calculator not found. Using basic calculator.")

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

class SimpleSubnetCalculator:
    """Fallback calculator if AI version is not available"""
    
    def __init__(self, ip_str, prefix):
        self.ip_str = ip_str
        self.prefix = prefix
        self.network = ipaddress.ip_network(f"{ip_str}/{prefix}", strict=False)
    
    def get_network_address(self):
        return str(self.network.network_address)
    
    def get_broadcast_address(self):
        return str(self.network.broadcast_address)
    
    def get_first_usable(self):
        hosts = list(self.network.hosts())
        return str(hosts[0]) if hosts else 'N/A'
    
    def get_last_usable(self):
        hosts = list(self.network.hosts())
        return str(hosts[-1]) if hosts else 'N/A'
    
    def get_subnet_mask(self):
        return str(self.network.netmask)
    
    def get_wildcard_mask(self):
        wildcard = []
        for octet in str(self.network.netmask).split('.'):
            wildcard.append(str(255 - int(octet)))
        return '.'.join(wildcard)
    
    def get_number_of_subnets(self):
        first_octet = int(self.ip_str.split('.')[0])
        if 1 <= first_octet <= 126:
            cb = 8
        elif 128 <= first_octet <= 191:
            cb = 16
        elif 192 <= first_octet <= 223:
            cb = 24
        else:
            cb = 24
        return 2 ** (self.prefix - cb) if self.prefix > cb else 1
    
    def get_usable_hosts(self):
        hosts = (2 ** (32 - self.prefix)) - 2
        return max(hosts, 0)
    
    def get_class_info(self):
        first_octet = int(self.ip_str.split('.')[0])
        if 1 <= first_octet <= 126:
            return 'A', 8
        elif 128 <= first_octet <= 191:
            return 'B', 16
        elif 192 <= first_octet <= 223:
            return 'C', 24
        else:
            return 'Special', None

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """API endpoint for subnet calculation"""
    data = request.get_json()
    
    if not data or 'ip' not in data:
        return jsonify({'error': 'Missing IP address'}), 400
    
    ip_input = data['ip']
    prefix = data.get('prefix')
    
    # Handle CIDR format
    if '/' in ip_input and not prefix:
        parts = ip_input.split('/')
        ip_input = parts[0]
        prefix = int(parts[1])
    
    try:
        if AI_AVAILABLE:
            calc = AISubnetCalculator(ip_input, prefix)
        else:
            calc = SimpleSubnetCalculator(ip_input, prefix)
        
        # Get all answers
        result = {
            'ip': ip_input,
            'prefix': prefix or calc.prefix if hasattr(calc, 'prefix') else 24,
            'subnet_mask': calc.get_subnet_mask(),
            'network_address': calc.get_network_address(),
            'broadcast_address': calc.get_broadcast_address(),
            'wildcard_mask': calc.get_wildcard_mask(),
            'first_usable': calc.get_first_usable(),
            'last_usable': calc.get_last_usable(),
            'number_of_subnets': calc.get_number_of_subnets(),
            'usable_hosts': calc.get_usable_hosts(),
            'class_info': calc.get_class_info()[0] if hasattr(calc, 'get_class_info') else 'Unknown'
        }
        
        # Get AI explanation if available
        if AI_AVAILABLE:
            try:
                all_answers = calc.get_all_answers()
                result['ai_explanations'] = [ans['question'] for ans in all_answers]
            except:
                pass
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/batch', methods=['POST'])
def batch_calculate():
    """API endpoint for batch calculation"""
    data = request.get_json()
    
    if not data or 'ips' not in data:
        return jsonify({'error': 'Missing IP list'}), 400
    
    results = []
    for ip_input in data['ips']:
        try:
            if '/' in ip_input:
                parts = ip_input.split('/')
                ip = parts[0]
                prefix = int(parts[1])
            else:
                ip = ip_input
                prefix = 24
            
            if AI_AVAILABLE:
                calc = AISubnetCalculator(ip, prefix)
            else:
                calc = SimpleSubnetCalculator(ip, prefix)
            
            results.append({
                'ip': ip_input,
                'network': calc.get_network_address(),
                'broadcast': calc.get_broadcast_address(),
                'usable_hosts': calc.get_usable_hosts(),
                'first_usable': calc.get_first_usable(),
                'last_usable': calc.get_last_usable()
            })
        except Exception as e:
            results.append({
                'ip': ip_input,
                'error': str(e)
            })
    
    return jsonify({'results': results})

if __name__ == '__main__':
    # Get local IP for display
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print("\n" + "="*60)
    print("🌐 AI-Powered Subnet Calculator Web Server")
    print("="*60)
    print(f"\n📍 Access from any browser:")
    print(f"   Local:    http://localhost:5000")
    print(f"   Network:  http://{local_ip}:5000")
    print("\n📱 To access from other devices, use the Network URL")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
