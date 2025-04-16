import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import rich
from bs4 import BeautifulSoup
from rich import print
from rich.progress import track

from joom3y.components import COMPONENTS

REQUEST_TIMEOUT = 5
USER_AGENT = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0"
}


def check_url(url: str, path: str = "/"):
    fullurl = url + path
    try:
        conn = requests.get(
            fullurl, headers=USER_AGENT, timeout=REQUEST_TIMEOUT
        )
        return conn.status_code
    except Exception as e:
        print(f"[red]error {e}")
        return None


def get_content_length(url: str, path: str = "/"):
    fullurl = url + path
    try:
        conn = requests.head(
            fullurl, headers=USER_AGENT, timeout=REQUEST_TIMEOUT
        )
        return conn.headers["content-length"]
    except Exception:
        return -1


def check_and_print(url, paths, label):
    for path in paths:
        if check_url(url, path) == 200:
            print(
                f"\t [green]{label}[/green] file found \t > [blue]{url}{path}[blue]"
            )


def check_readme(url, component):
    paths = [
        "/components/" + component + "/README.txt",
        "/components/" + component + "/readme.txt",
        "/components/" + component + "/README.md",
        "/components/" + component + "/readme.md",
        "/administrator/components/" + component + "/README.txt",
        "/administrator/components/" + component + "/readme.txt",
        "/administrator/components/" + component + "/README.md",
        "/administrator/components/" + component + "/readme.md",
    ]
    check_and_print(url, paths, "README")


def check_license(url, component):
    paths = [
        "/components/" + component + "/LICENSE.txt",
        "/components/" + component + "/license.txt",
        "/administrator/components/" + component + "/LICENSE.txt",
        "/administrator/components/" + component + "/license.txt",
        "/components/" + component + "/" + component[4:] + ".xml",
        "/administrator/components/"
        + component
        + "/"
        + component[4:]
        + ".xml",
    ]
    check_and_print(url, paths, "LICENSE")


def check_changelog(url, component):
    paths = [
        "/components/" + component + "/CHANGELOG.txt",
        "/components/" + component + "/changelog.txt",
        "/administrator/components/" + component + "/CHANGELOG.txt",
        "/administrator/components/" + component + "/changelog.txt",
    ]
    check_and_print(url, paths, "CHANGELOG")


def check_mainfest(url, component):
    paths = [
        "/components/" + component + "/MANIFEST.xml",
        "/components/" + component + "/manifest.xml",
        "/administrator/components/" + component + "/MANIFEST.xml",
        "/administrator/components/" + component + "/manifest.xml",
    ]
    check_and_print(url, paths, "MANIFEST")


def check_index(url, component):
    paths = [
        "/components/" + component + "/index.htm",
        "/components/" + component + "/index.html",
        "/administrator/components/" + component + "/INDEX.htm",
        "/administrator/components/" + component + "/INDEX.html",
    ]
    for path in paths:
        if (
            check_url(url, path) == 200
            and get_content_length(url, path) > 1000
        ):
            print(f"\t INDEX file descriptive found \t > {url}{path}")


def index_of(url, path="/"):
    fullurl = url + path
    try:
        page = requests.get(
            fullurl, headers=USER_AGENT, timeout=REQUEST_TIMEOUT
        )
        soup = BeautifulSoup(page.text, "html.parser")
        if soup.title:
            titlepage = soup.title.string
            if titlepage and "Index of /" in titlepage:
                return True
            else:
                return False
        else:
            return False
    except Exception as _:
        return False


def scanner(url: str, component: str):
    if check_url(url, "/index.php?option=" + component) == 200:
        print(
            "Component found: "
            + component
            + "\t > "
            + url
            + "/index.php?option="
            + component
        )

        check_readme(url, component)
        check_license(url, component)
        check_changelog(url, component)
        check_mainfest(url, component)
        check_index(url, component)

        if index_of(url, "/components/" + component + "/"):
            print(
                "\t [green]Explorable Directory \t > "
                + url
                + "/components/"
                + component
                + "/"
            )

        if index_of(url, "/administrator/components/" + component + "/"):
            print(
                "\t [green]Explorable Directory \t > "
                + url
                + "/administrator/components/"
                + component
                + "/"
            )

    elif check_url(url, "/components/" + component + "/") == 200:
        print(
            "[green]Component found: "
            + component
            + "\t > "
            + url
            + "/index.php?option="
            + component
        )
        print("\t But possibly it is not active or protected")

        check_readme(url, component)
        check_license(url, component)
        check_changelog(url, component)
        check_mainfest(url, component)
        check_index(url, component)

        if index_of(url, "/components/" + component + "/"):
            print(
                "\t [green]Explorable Directory \t > "
                + url
                + "/components/"
                + component
                + "/"
            )

        if index_of(url, "/administrator/components/" + component + "/"):
            print(
                "\t [green]Explorable Directory \t > "
                + url
                + "/administrator/components/"
                + component
                + "/"
            )

    elif check_url(url, "/administrator/components/" + component + "/") == 200:
        print(
            "[green]Component found: "
            + component
            + "\t > "
            + url
            + "/index.php?option="
            + component
        )
        print("\t On the administrator components")

        check_readme(url, component)
        check_license(url, component)
        check_changelog(url, component)
        check_mainfest(url, component)
        check_index(url, component)

        if index_of(url, "/administrator/components/" + component + "/"):
            print(
                "\t [green]Explorable Directory \t > "
                + url
                + "/components/"
                + component
                + "/"
            )

        if index_of(url, "/administrator/components/" + component + "/"):
            print(
                "\t [green]Explorable Directory \t > "
                + url
                + "/administrator/components/"
                + component
                + "/"
            )


def scan(
    url: str, user_agent: str, timeout: int = 5, threads: int = os.cpu_count()
):
    global USER_AGENT, REQUEST_TIMEOUT
    USER_AGENT = {"User-Agent": user_agent}
    REQUEST_TIMEOUT = timeout

    if not url.startswith("http://") and not url.startswith("https://"):
        rich.print(f"[red] url {url} must have a scheme.")
        exit(1)

    # Remove the ending to the url
    if url.endswith("/"):
        url = url[:-1]

    if check_url(url):
        if check_url(url, "/robots.txt") == 200:
            print("[blue]Robots file found: \t \t > " + url + "/robots.txt")
        else:
            print("[red]No Robots file found")

        if check_url(url, "/error_log") == 200:
            print("[blue]Error log found: \t \t > " + url + "/error_log")
        else:
            print("[red]No Error Log found")

        # Check if the version is present
        version_paths = [
            "/administrator/manifests/files/joomla.xml",
            "/README.txt",
        ]

        # Go through the versions and check
        for version in version_paths:
            # If it resolves, check the version
            if check_url(url, version) == 200:
                print(
                    f"[green] Path {url + version} resolved, getting version string"
                )
                page_content = requests.get(url + version).text
                for line in page_content.split("\n"):
                    if "version" in line.lower():
                        print("\t", line)

        print("[green] Initiating component scans")
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [
                executor.submit(scanner, url, component)
                for component in COMPONENTS
            ]
            # Wrap as_completed with track to update the progress bar as tasks complete.
            for future in track(as_completed(futures), total=len(futures)):
                # Optionally, process result or catch exceptions here.
                future.result()
