#!/usr/bin/env python3

#########################
#                       #
#   SUBDOMAINator       #
#                       #
#########################

import sys
import requests
import argparse
import random
from pyfiglet import figlet_format
from termcolor import cprint
from colorama import Fore , Style

#to be filled
parser = argparse.ArgumentParser(description = "A bruteforce based subdomain digger")
parser.add_argument("--url" , "-u" , help = "Specify the URL. Example: 'google.com' , 'example.com'")
parser.add_argument("--domain" , "-d" , help="Specify domain/website name instead of URL. Example: 'google' , 'example'")
parser.add_argument("--wordlist" , "-w" , help="Specify the wordlist to use for bruteforce")
parser.add_argument("--debug" , "-v" , help="Show verbose output or turn debug mode on" , action="store_true")
parser.add_argument("--domain-list" , "-l" , help="Specify custom domain list")
arguments = parser.parse_args()

def print_banner():
    cprint(figlet_format("SUBDOMAINator" , font = "slant") , "white")

def pre_checks():
    #check whether the wordlist is right
    if arguments.wordlist:
        wordlist_status = check_wordlist(arguments.wordlist)
        if wordlist_status is False:
            sys.exit()
    else:
        if arguments.debug:
            print(Fore.YELLOW + "[+]No wordlist specified! Default wordlist will be used!" + Style.RESET_ALL)
        arguments.wordlist = "default_subdomains.txt"

    #check validity of domain wordlist
    if arguments.domain and arguments.domain_list:  
        domain_wordlist_status = check_wordlist(arguments.domain_list)
        if domain_wordlist_status is False:
            sys.exit()
    elif arguments.domain and not arguments.domain_list:    #if domain name is specified but not the wordlist, defaut one will be used
        if arguments.debug:
            print(Fore.YELLOW + "[+]No domain wordlist specified! Default wordlist will be used!" + Style.RESET_ALL)
        arguments.domain_list = "default_end.txt"

    #URL checks
    if arguments.url and not arguments.domain:
        TYPE = "URL"
        data = arguments.url
        #check protocol
        protocol_validity = check_protocol(arguments.url)
        if protocol_validity is False:
            print(Fore.RED + "[!]No protocol specified in the URL" + Style.RESET_ALL)
            sys.exit()

        #check if the URL seems valid(look for '.' character in the URL)
        if data.find(".") < 0:
            print(Fore.RED + "[!]URL seems invalid" + Style.RESET_ALL)
            sys.exit()

    #domain checks
    elif arguments.domain and not arguments.url:
        TYPE = "DOMAIN"
        data = arguments.domain

    #Check if both flags are specified(they shouldn't)
    if arguments.url and arguments.domain:
        if arguments.debug:
            print(Fore.YELLOW + "[+]Please specify either a URL or a domain/website name! Example: 'google' , 'facebook'" + Style.RESET_ALL)
        sys.exit()

    #Check if atleas one among URL or domain is specified
    if not (arguments.url or arguments.domain):
        if arguments.debug:
            print(Fore.YELLOW + "[+]Please specify a URL or a domain to test" + Style.RESET_ALL)
        sys.exit()    
    
    return (data , TYPE)     #all validity checks has been passed

def check_protocol(data):
    if len(data.split(":")[0]) == len(data):       #split returns a list of splitted items, we just want the first one(protocol)
        return False                               #but when the character isn't present, it doesn't create a list and keep the original data
    else:
        return True

def check_wordlist(wordlist):
    try:
        wordlist = open(arguments.wordlist , 'r')
    except FileNotFoundError:
        print(Fore.RED + "[!]No such wordlist exist in the specified path" + Style.RESET_ALL)
        return False
    except:
        print(Fore.RED + "[!]A problem occurred while opening the wordlist!" + Style.RESET_ALL)
        return False
    else:
        wordlist.close()
        return True


def subdomain_digger(data, TYPE):
    if arguments.debug:
        print(Fore.YELLOW + "[+]Opening subdomain wordlist" + Style.RESET_ALL)
    subdomains_list = open(arguments.wordlist , "r").read().splitlines()
    if TYPE == "DOMAIN":
        if arguments.debug:
            print(Fore.YELLOW + "[+]Opening default protocol wordlist" + Style.RESET_ALL)
        protocols_list = open("default_protocols.txt" , "r").read().splitlines()
        if arguments.debug:
            print(Fore.YELLOW + "[+]Opening default domain end wordlist\n" + Style.RESET_ALL)
        domains_list = open(arguments.domain_list , "r").read().splitlines()
        for protocol in protocols_list:
            for domain in domains_list:
                for subdomain in subdomains_list:
                    url = protocol + subdomain + "." + data + domain
                    request_url(url)
    elif TYPE == "URL":
        subdomain_injection_index = data.find("//")
        for subdomain in subdomains_list:
            url = data[:subdomain_injection_index + 2] + subdomain + "." + data[subdomain_injection_index + 2:]
            request_url(url)

def request_url(url):
    user_agent_list = open("default_user_agents.txt" ,"r").read().splitlines()
    user_agent = user_agent_list[random.randint(0 , 10)]
    #for space indentation of response code
    space_strip = " " * (40-len(url))
    try:
        response = requests.get(url , headers = {"User-Agent": user_agent} , timeout=5)
        if response.status_code >= 200 and response.status_code < 400:
            print(Fore.GREEN + "[*]" + url + space_strip + f"RESPONSE = {response.status_code}" + Style.RESET_ALL)
        else:
            print(Fore.RED + "[-]" + url + space_strip + f"RESPONSE = {response.status_code}" + Style.RESET_ALL)
    except:
        pass
        
if __name__ == "__main__":
    print_banner()
    data , TYPE = pre_checks()
    subdomain_digger(data , TYPE)
