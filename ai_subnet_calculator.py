#!/usr/bin/env python3
"""
AI-Powered IPv4 Subnet Calculator
Based on: Understanding the basics of IPv4 addressing
With Local LLM Integration (Ollama)
Answers all 7 subnetting questions automatically
"""

import ipaddress
import json
import re
import subprocess
from colorama import init, Fore, Style
import sys

# Initialize colorama for colored output
init(autoreset=True)

# Try to import ollama
try:
    import ollama
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
#     print(f"{Fore.YELLOW}⚠️  Ollama not installed. AI features disabled.{Style.RESET_ALL}")
#     print("Run: pip3 install ollama")

class AISubnetCalculator:
    """AI-Powered Subnet Calculator with Local LLM"""
    
    def __init__(self, ip_str, prefix=None):
        self.ip_str = ip_str
        self.prefix = prefix
        self.use_ai = False
        
        # Parse IP/prefix if provided in CIDR format
        if '/' in ip_str and prefix is None:
            parts = ip_str.split('/')
            self.ip_str = parts[0]
            self.prefix = int(parts[1])
        
        if self.prefix is None:
            # Auto-detect class if no prefix given
            self.prefix = self._detect_class_prefix()
        
        # Create network object
        try:
            self.network = ipaddress.ip_network(f"{self.ip_str}/{self.prefix}", strict=False)
        except Exception as e:
#             print(f"{Fore.RED}❌ Invalid IP/prefix combination: {e}{Style.RESET_ALL}")
            sys.exit(1)
        
        self.ip_obj = ipaddress.ip_address(self.ip_str)
        
    def _detect_class_prefix(self):
        """Auto-detect class-based prefix if not specified"""
        first_octet = int(self.ip_str.split('.')[0])
        if 1 <= first_octet <= 126:
            return 8
        elif 128 <= first_octet <= 191:
            return 16
        elif 192 <= first_octet <= 223:
            return 24
        else:
            return 24  # Default
    
    def get_class_info(self):
        """Determine Class and Class Boundary (CB)"""
        first_octet = int(self.ip_str.split('.')[0])
        if 1 <= first_octet <= 126:
            return 'A', 8, f"1-126 (Default: /8)"
        elif 128 <= first_octet <= 191:
            return 'B', 16, f"128-191 (Default: /16)"
        elif 192 <= first_octet <= 223:
            return 'C', 24, f"192-223 (Default: /24)"
        else:
            return 'Special', None, "Reserved"
    
    def get_next_boundary(self):
        """Determine Next Boundary (NB)"""
        if self.prefix <= 8:
            return 8
        elif self.prefix <= 16:
            return 16
        elif self.prefix <= 24:
            return 24
        else:
            return 32
    
    def get_block_size(self):
        """Block Size = 2^(NB-NM)"""
        nb = self.get_next_boundary()
        return 2 ** (nb - self.prefix)
    
    def get_number_of_subnets(self):
        """Number of subnets = 2^(NM-CB)"""
        ip_class, cb, _ = self.get_class_info()
        if cb is None:
            return 0
        return 2 ** (self.prefix - cb)
    
    def get_usable_hosts(self):
        """Usable hosts = 2^(32-NM) - 2"""
        hosts = (2 ** (32 - self.prefix)) - 2
        return max(hosts, 0)
    
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
    
    def get_wildcard_mask(self):
        """Wildcard mask = Inverse of subnet mask"""
        wildcard = []
        for octet in str(self.network.netmask).split('.'):
            wildcard.append(str(255 - int(octet)))
        return '.'.join(wildcard)
    
    def get_subnet_mask(self):
        return str(self.network.netmask)
    
    def get_binary_network(self):
        return self._ip_to_binary(str(self.network.network_address))
    
    def get_binary_mask(self):
        return self._ip_to_binary(str(self.network.netmask))
    
    def _ip_to_binary(self, ip_str):
        """Convert IP to binary with dots"""
        octets = ip_str.split('.')
        binary = ''
        for octet in octets:
            binary += format(int(octet), '08b') + '.'
        return binary[:-1]
    
    # ============================================
    # ALL 7 QUESTIONS ANSWERED AUTOMATICALLY
    # ============================================
    
    def answer_question_1(self):
        """1. What is the number of subnets?"""
        count = self.get_number_of_subnets()
        ip_class, cb, _ = self.get_class_info()
        return {
            'question': 'Number of subnets',
            'answer': f'{count}',
            'formula': f'2^({self.prefix} - {cb}) = 2^{self.prefix - cb} = {count}',
            'explanation': f'Network is Class {ip_class} with Class Boundary {cb}. Using /{self.prefix} mask creates {count} subnets.'
        }
    
    def answer_question_2(self):
        """2. What is the number of usable IP addresses?"""
        count = self.get_usable_hosts()
        return {
            'question': 'Number of usable IP addresses',
            'answer': f'{count}',
            'formula': f'2^(32-{self.prefix}) - 2 = 2^{32-self.prefix} - 2 = {count}',
            'explanation': f'Total addresses in subnet = {2**(32-self.prefix)}. Subtract network and broadcast addresses = {count} usable.'
        }
    
    def answer_question_3(self):
        """3. What is the first IP address?"""
        first = self.get_first_usable()
        return {
            'question': 'First usable IP address',
            'answer': first,
            'formula': f'Network address + 1',
            'explanation': f'First usable address is {first} (network address {self.get_network_address()} + 1).'
        }
    
    def answer_question_4(self):
        """4. What is the last usable IP address?"""
        last = self.get_last_usable()
        return {
            'question': 'Last usable IP address',
            'answer': last,
            'formula': f'Broadcast address - 1',
            'explanation': f'Last usable address is {last} (broadcast address {self.get_broadcast_address()} - 1).'
        }
    
    def answer_question_5(self):
        """5. What is the broadcast IP address?"""
        broadcast = self.get_broadcast_address()
        return {
            'question': 'Broadcast IP address',
            'answer': broadcast,
            'formula': f'All host bits set to 1',
            'explanation': f'Broadcast address is {broadcast}. All bits in the host portion are 1.'
        }
    
    def answer_question_6(self):
        """6. What is the network IP address?"""
        network = self.get_network_address()
        return {
            'question': 'Network IP address',
            'answer': network,
            'formula': f'All host bits set to 0',
            'explanation': f'Network address is {network}. All bits in the host portion are 0.'
        }
    
    def answer_question_7(self):
        """7. What is the wildcard mask?"""
        wildcard = self.get_wildcard_mask()
        return {
            'question': 'Wildcard mask',
            'answer': wildcard,
            'formula': f'Inverse of subnet mask',
            'explanation': f'Wildcard mask is {wildcard} (subnet mask {self.get_subnet_mask()} inverted). Used in ACLs.'
        }
    
    def get_all_answers(self):
        """Get answers to all 7 questions"""
        return [
            self.answer_question_1(),
            self.answer_question_2(),
            self.answer_question_3(),
            self.answer_question_4(),
            self.answer_question_5(),
            self.answer_question_6(),
            self.answer_question_7()
        ]
    
    # ============================================
    # AI-POWERED EXPLANATIONS
    # ============================================
    
    def get_ai_explanation(self, question_data):
        """Generate AI-powered explanation using local LLM"""
        if not AI_AVAILABLE:
            return question_data['explanation']
        
        try:
            prompt = f"""
            You are a networking expert. Explain this IPv4 subnetting concept clearly:
            
            IP: {self.ip_str}/{self.prefix}
            Class: {self.get_class_info()[0]}
            Question: {question_data['question']}
            Answer: {question_data['answer']}
            
            Provide a concise, beginner-friendly explanation (max 2 sentences) about WHY this is the answer.
            Focus on the subnetting logic.
            """
            
            response = ollama.chat(
                model='llama3.2:3b',
                messages=[{'role': 'user', 'content': prompt}]
            )
            
            ai_explanation = response['message']['content'].strip()
            return ai_explanation
        
        except Exception as e:
            return question_data['explanation']  # Fallback to standard explanation
    
    def display_all_answers(self, use_ai=True):
        """Display all 7 answers with nice formatting"""
#         print(f"\n{'='*80}")
#         print(f"{Fore.CYAN}📡 SUBNET CALCULATOR RESULTS{Style.RESET_ALL}")
#         print(f"{'='*80}")
#         print(f"{Fore.YELLOW}IP Address:{Style.RESET_ALL} {self.ip_str}")
#         print(f"{Fore.YELLOW}NetMask:{Style.RESET_ALL} /{self.prefix} ({self.get_subnet_mask()})")
        ip_class, cb, range_info = self.get_class_info()
#         print(f"{Fore.YELLOW}Class:{Style.RESET_ALL} {ip_class} ({range_info})")
#         print(f"{Fore.YELLOW}Next Boundary:{Style.RESET_ALL} {self.get_next_boundary()}")
#         print(f"{Fore.YELLOW}Block Size:{Style.RESET_ALL} {self.get_block_size()}")
#         print(f"{'-'*80}")
        
        # Get all 7 answers
        all_answers = self.get_all_answers()
        
        # Display each question and answer
        for idx, ans in enumerate(all_answers, 1):
#             print(f"\n{Fore.GREEN}Q{idx}. {ans['question']}:{Style.RESET_ALL}")
#             print(f"   {Fore.WHITE}Answer:{Style.RESET_ALL} {Fore.CYAN}{ans['answer']}{Style.RESET_ALL}")
#             print(f"   {Fore.WHITE}Formula:{Style.RESET_ALL} {ans['formula']}")
            
            # Get AI explanation if available and enabled
            if use_ai and AI_AVAILABLE:
                ai_exp = self.get_ai_explanation(ans)
#                 print(f"   {Fore.WHITE}🤖 AI Explanation:{Style.RESET_ALL} {ai_exp}")
            else:
#                 print(f"   {Fore.WHITE}Explanation:{Style.RESET_ALL} {ans['explanation']}")
        
#         print(f"\n{'='*80}")
#         print(f"{Fore.YELLOW}📊 SUMMARY{Style.RESET_ALL}")
#         print(f"{'='*80}")
#         print(f"Network Address:     {self.get_network_address()}")
#         print(f"Broadcast Address:   {self.get_broadcast_address()}")
#         print(f"Subnet Mask:         {self.get_subnet_mask()}")
#         print(f"Wildcard Mask:       {self.get_wildcard_mask()}")
#         print(f"Usable IPs:          {self.get_first_usable()} - {self.get_last_usable()}")
#         print(f"Total Subnets:       {self.get_number_of_subnets()}")
#         print(f"Usable Hosts/Subnet: {self.get_usable_hosts()}")
#         print(f"{'='*80}\n")
    
    def get_json_output(self):
        """Get all answers as JSON (for API or file output)"""
        all_answers = self.get_all_answers()
        result = {
            'ip': self.ip_str,
            'prefix': self.prefix,
            'subnet_mask': self.get_subnet_mask(),
            'network_address': self.get_network_address(),
            'broadcast_address': self.get_broadcast_address(),
            'wildcard_mask': self.get_wildcard_mask(),
            'class': self.get_class_info()[0],
            'class_boundary': self.get_class_info()[1],
            'next_boundary': self.get_next_boundary(),
            'block_size': self.get_block_size(),
            'answers': all_answers
        }
        return result


# ============================================
# INTERACTIVE MENU
# ============================================

def check_ollama_status():
    """Check if Ollama is running and ready"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if 'llama3.2' in result.stdout:
            return True
        else:
#             print(f"{Fore.YELLOW}⚠️  Llama model not found. Pulling llama3.2:3b...{Style.RESET_ALL}")
            subprocess.run(['ollama', 'pull', 'llama3.2:3b'])
            return True
    except:
        return False

def main():
#     print(f"\n{Fore.CYAN}{'='*80}")
#     print(f"🤖 AI-POWERED IPv4 SUBNET CALCULATOR")
#     print(f"Based on: Understanding the basics of IPv4 addressing")
#     print(f"{'='*80}{Style.RESET_ALL}\n")
    
    # Check AI availability
    use_ai = False
    if AI_AVAILABLE:
        if check_ollama_status():
            use_ai = True
#             print(f"{Fore.GREEN}✅ AI Enabled (Ollama + Llama 3.2){Style.RESET_ALL}")
        else:
#             print(f"{Fore.YELLOW}⚠️  AI disabled (Ollama not running). Using standard explanations.{Style.RESET_ALL}")
#             print(f"   Run: sudo systemctl start ollama")
    else:
#         print(f"{Fore.YELLOW}⚠️  AI disabled (Ollama not installed). Using standard explanations.{Style.RESET_ALL}")
#         print(f"   Install: curl -fsSL https://ollama.ai/install.sh | sh")
    
    while True:
#         print(f"\n{Fore.CYAN}OPTIONS:{Style.RESET_ALL}")
#         print("  1. Enter IP address (auto-detect class)")
#         print("  2. Enter IP in CIDR format (e.g., 192.168.34.221/27)")
#         print("  3. Batch process multiple IPs")
#         print("  4. Export results to JSON")
#         print("  5. Troubleshooting gateway example")
#         print("  6. Test with article examples")
#         print("  7. Exit")
        
        choice = input(f"\n{Fore.YELLOW}Enter your choice (1-7): {Style.RESET_ALL}").strip()
        
        if choice == '1':
            ip_input = input("Enter IP address (e.g., 192.168.50.10): ").strip()
            prefix_input = input("Enter NetMask in CIDR (optional, press Enter for auto-detect): ").strip()
            
            if prefix_input:
                prefix = int(prefix_input)
            else:
                prefix = None
            
            try:
                calc = AISubnetCalculator(ip_input, prefix)
                calc.display_all_answers(use_ai=use_ai)
            except Exception as e:
#                 print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        
        elif choice == '2':
            cidr_input = input("Enter IP/prefix (e.g., 192.168.34.221/27): ").strip()
            try:
                calc = AISubnetCalculator(cidr_input)
                calc.display_all_answers(use_ai=use_ai)
            except Exception as e:
#                 print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        
        elif choice == '3':
#             print(f"\n{Fore.CYAN}Enter IPs one per line (format: IP/prefix){Style.RESET_ALL}")
#             print("Example: 192.168.34.221/27")
#             print("Type 'done' when finished.")
            
            entries = []
            while True:
                line = input("> ").strip()
                if line.lower() == 'done':
                    break
                if line:
                    entries.append(line)
            
#             print(f"\n{Fore.GREEN}BATCH RESULTS:{Style.RESET_ALL}\n")
            for entry in entries:
                try:
                    calc = AISubnetCalculator(entry)
#                     print(f"{Fore.CYAN}▶ {entry}{Style.RESET_ALL}")
#                     print(f"   Network: {calc.get_network_address()}")
#                     print(f"   Broadcast: {calc.get_broadcast_address()}")
#                     print(f"   Usable: {calc.get_first_usable()} - {calc.get_last_usable()}")
#                     print(f"   Hosts: {calc.get_usable_hosts()}")
#                     print(f"   Subnets: {calc.get_number_of_subnets()}")
#                     print()
                except Exception as e:
#                     print(f"{Fore.RED}❌ Error with {entry}: {e}{Style.RESET_ALL}")
        
        elif choice == '4':
            ip_input = input("Enter IP/prefix (e.g., 192.168.34.221/27): ").strip()
            try:
                calc = AISubnetCalculator(ip_input)
                result = calc.get_json_output()
                json_output = json.dumps(result, indent=2)
#                 print(f"\n{Fore.GREEN}JSON Output:{Style.RESET_ALL}")
#                 print(json_output)
                
                # Save to file
                filename = f"subnet_result_{ip_input.replace('/', '_')}.json"
                with open(filename, 'w') as f:
                    f.write(json_output)
#                 print(f"\n{Fore.GREEN}✅ Saved to: {filename}{Style.RESET_ALL}")
            except Exception as e:
#                 print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        
        elif choice == '5':
#             print(f"\n{Fore.CYAN}TROUBLESHOOTING: Default Gateway Misconfiguration{Style.RESET_ALL}")
#             print("Scenario: PC with IP 192.168.50.10/24, Gateway 192.168.60.1\n")
            
            pc_calc = AISubnetCalculator("192.168.50.10/24")
            gw_calc = AISubnetCalculator("192.168.60.1/24")
            
#             print(f"PC Network:     {pc_calc.get_network_address()}")
#             print(f"Gateway Network: {gw_calc.get_network_address()}")
            
            if pc_calc.get_network_address() == gw_calc.get_network_address():
#                 print(f"\n{Fore.GREEN}✅ Both on same subnet. Gateway is correct.{Style.RESET_ALL}")
            else:
#                 print(f"\n{Fore.RED}❌ They are on DIFFERENT subnets!{Style.RESET_ALL}")
#                 print(f"   PC is on:     {pc_calc.get_network_address()}")
#                 print(f"   Gateway is on: {gw_calc.get_network_address()}")
#                 print(f"\n{Fore.YELLOW}→ Default gateway MUST be on the same local subnet.{Style.RESET_ALL}")
#                 print(f"{Fore.CYAN}✅ Correct Answer: C. Default gateway{Style.RESET_ALL}")
        
        elif choice == '6':
#             print(f"\n{Fore.CYAN}TESTING WITH ARTICLE EXAMPLES{Style.RESET_ALL}\n")
            
            examples = [
                ("192.168.34.221/27", "Should be subnet 192.168.34.192"),
                ("172.16.113.1/18", "Should be subnet 172.16.64.0"),
                ("10.20.60.234/11", "Should be subnet 10.0.0.0"),
                ("172.20.0.0/28", "Should have 4096 subnets, 14 usable hosts")
            ]
            
            for ip, expected in examples:
                try:
                    calc = AISubnetCalculator(ip)
#                     print(f"{Fore.GREEN}▶ {ip}{Style.RESET_ALL}")
#                     print(f"   Network: {calc.get_network_address()}")
#                     print(f"   Subnets: {calc.get_number_of_subnets()}")
#                     print(f"   Usable hosts: {calc.get_usable_hosts()}")
#                     print(f"   Expected: {expected}\n")
                except Exception as e:
#                     print(f"{Fore.RED}❌ Error with {ip}: {e}{Style.RESET_ALL}")
        
        elif choice == '7':
#             print(f"\n{Fore.GREEN}Thank you for using AI-Powered Subnet Calculator! 👋{Style.RESET_ALL}")
            break
        
        else:
#             print(f"{Fore.RED}Invalid choice. Please select 1-7.{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
#         print(f"\n\n{Fore.YELLOW}Exiting... Goodbye!{Style.RESET_ALL}")
        sys.exit(0)
