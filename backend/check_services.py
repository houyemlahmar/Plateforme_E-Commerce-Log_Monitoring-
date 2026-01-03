"""
Check if required services are running before starting Flask app
"""

import socket
import sys
from colorama import init, Fore, Style

# Initialize colorama for Windows
init(autoreset=True)


def check_service(host, port, service_name):
    """Check if a service is accessible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"{Fore.GREEN}✓ {service_name} is running on {host}:{port}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}✗ {service_name} is NOT running on {host}:{port}{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}✗ {service_name} check failed: {str(e)}{Style.RESET_ALL}")
        return False


def main():
    """Check all required services"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print("Checking Required Services")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    services = [
        ('localhost', 27017, 'MongoDB', True),
        ('localhost', 9200, 'Elasticsearch', False),
        ('localhost', 6379, 'Redis', False),
    ]
    
    all_running = True
    required_missing = []
    optional_missing = []
    
    for host, port, name, required in services:
        is_running = check_service(host, port, name)
        
        if not is_running:
            all_running = False
            if required:
                required_missing.append(name)
            else:
                optional_missing.append(name)
    
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    if required_missing:
        print(f"\n{Fore.RED}ERROR: Required services are not running:{Style.RESET_ALL}")
        for service in required_missing:
            print(f"  - {service}")
        
        print(f"\n{Fore.YELLOW}To start services with Docker Compose:{Style.RESET_ALL}")
        print(f"  cd C:\\projet_bigdata")
        print(f"  docker-compose up -d mongodb")
        
        print(f"\n{Fore.YELLOW}Or install MongoDB locally:{Style.RESET_ALL}")
        print(f"  Download from: https://www.mongodb.com/try/download/community")
        
        return False
    
    if optional_missing:
        print(f"\n{Fore.YELLOW}WARNING: Optional services are not running:{Style.RESET_ALL}")
        for service in optional_missing:
            print(f"  - {service}")
        print(f"\n{Fore.YELLOW}Some features may not work without these services.{Style.RESET_ALL}")
    
    if all_running:
        print(f"\n{Fore.GREEN}✓ All services are running!{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}✓ Required services are running. You can start the Flask app.{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}To start Flask app:{Style.RESET_ALL}")
    print(f"  python main.py")
    print()
    
    return not bool(required_missing)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
