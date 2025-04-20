import os

from rich import print
from typer import Option, Typer
from typing_extensions import Annotated

from joom3y.brute import joomla_brute
from joom3y.joom3y import scan

app = Typer()


@app.command()
def enumerate(
    url: Annotated[str, Option("--url", "-u", help="The Joomla URL to scan.")],
    threads: Annotated[
        int, Option("--threads", "-t", help="Number of threads to use.")
    ] = os.cpu_count(),
    agent: Annotated[
        str | None, Option("--user-agent", "-a", help="The user agent to use.")
    ] = None,
    timeout: Annotated[
        int,
        Option(
            "--timeout",
            "-T",
            help="The timeout before moving on with an http request to joomla.",
        ),
    ] = 5,
):
    if agent is None:
        from faker import Faker
        from faker.providers import user_agent

        fake = Faker()
        fake.add_provider(user_agent)
        agent = fake.user_agent()
        print("[blue]No user agent found, generated user agent is:", agent)

    scan(url, agent, timeout, threads)


@app.command()
def brute(
    url: Annotated[str, Option("--url", "-u", help="The Joomla URL to scan.")],
    wordlist: Annotated[
        str, Option("--wordlist", "-w", help="Path to wordlist file.")
    ],
    username: Annotated[
        str, Option("--username", "-usr", help="Username to bruteforce.")
    ] = "admin",
    threads: Annotated[
        int,
        Option(
            "--threads", "-t", help="Number of threads to use for bruteforce."
        ),
    ] = 8,
    verbose: Annotated[
        bool, Option("--verbose", "-v", help="Show verbose output.")
    ] = False,
):
    """Joomla login bruteforce tool."""
    print("[bold blue]Starting bruteforce attack[/bold blue]")

    joomla_brute(
        url=url,
        wordlist=wordlist,
        username=username,
        threads=threads,
        verbose=verbose,
    )


if __name__ == "__main__":
    app()
