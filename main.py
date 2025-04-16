import os

from rich import print
from typer import Option, Typer
from typing_extensions import Annotated

from joom3y.joom3y import scan

app = Typer()


@app.command()
def main(
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


if __name__ == "__main__":
    app()
