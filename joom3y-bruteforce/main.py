import os

from rich import print
from typer import Option, Typer
from typing_extensions import Annotated

from joomla_brute import joomla_brute

app = Typer()

@app.command()
def main(
    url: Annotated[str, Option("--url", "-u", help="The Joomla URL to scan.")],
    wordlist: Annotated[
        str, Option("--wordlist", "-w", help="Path to wordlist file.")
    ],
    username: Annotated[
        str, Option("--username", "-usr", help="Username to bruteforce.")
    ] = "admin",
    threads: Annotated[
        int, Option("--threads", "-t", help="Number of threads to use for bruteforce.")
    ] = 8,
    verbose: Annotated[
        bool, Option("--verbose", "-v", help="Show verbose output.")
    ] = False,
):
    """Joomla login bruteforce tool."""
    print("[bold blue]Starting bruteforce attack...[/bold blue]")
    # add userlist
    joomla_brute(url=url, wordlist=wordlist, username=username, threads=threads, verbose=verbose)

if __name__ == "__main__":
    app()
