from typing import Self


class Url:
    """A compliant, but non-exhaustive URL contianer. It does not handle
    fragments, for example."""

    def __init__(self, url_string: str):
        self._raw = url_string

        # Components of a URL
        self.scheme_end: int = -1
        self.host_start: int = -1
        self.host_end: int = -1
        self.port: int | None = None
        self.path_start: int | None = None
        self.query_start: int | None = None

    def __repr__(self) -> str:
        return self._raw

    def __add__(self, path: str) -> Self:
        if path.startswith("/"):
            path = path[1:]

        if self._raw.endswith("/"):
            self._raw = self._raw[:-1]

        return Url.parse(self._raw + "/", path)

    @property
    def scheme(self) -> str:
        return self._raw[: self.scheme_end]

    @property
    def host(self) -> str:
        return self._raw[self.host_start : self.host_end]

    @property
    def path(self) -> str | None:
        if self.path_start is not None:
            if self.query_start is not None:
                return self._raw[self.path_start : self.query_start]
            return self._raw[self.path_start :]
        return None

    @property
    def query(self) -> str | None:
        if self.query_start:
            return self._raw[self.query_start :]
        return None

    @classmethod
    def parse(cls, url_string: str) -> Self:
        """Parses a URL into its components.

        This method assumes the URL starts with http:// or https://.
        It determines the scheme, host (with optional port), path, and query.

        Args:
            url_string (str): e.g. "http://foo.bar/baz?qux=hex"

        Returns:
            Self: An instance of Url with parsed parts.
        """
        # Ensure the scheme is present.
        if not (
            url_string.startswith("http://")
            or url_string.startswith("https://")
        ):
            raise ValueError(f"url string {url_string} is missing a scheme.")

        # Create a new instance and record the scheme end.
        instance = cls(url_string)
        instance.scheme_end = (
            url_string.index("//") + 2
        )  # the position after "http://" or "https://"

        # Find the first occurrence of "/" and "?" after the scheme.
        # These mark the beginnings of the path and query respectively.
        first_slash = url_string.find("/", instance.scheme_end)
        first_qmark = url_string.find("?", instance.scheme_end)

        # The host ends where the first "/" or "?" appears.
        if first_slash == -1 and first_qmark == -1:
            host_end = len(url_string)
        elif first_slash == -1:
            host_end = first_qmark
        elif first_qmark == -1:
            host_end = first_slash
        else:
            host_end = min(first_slash, first_qmark)

        instance.host_start = instance.scheme_end
        instance.host_end = host_end

        # Extract the host section from the URL.
        host_str = url_string[instance.host_start : instance.host_end]

        # If a port is specified (after a colon) in the host, separate it.
        if ":" in host_str:
            host_only, port_str = host_str.split(":", 1)
            # Adjust the host_end to end at the port separator.
            instance.host_end = instance.host_start + len(host_only)
            instance.port = int(port_str)
        else:
            instance.port = None

        # Process the path (if any)
        if first_slash != -1:
            instance.path_start = first_slash
            # If there's a query following the path, record its start.
            if first_qmark != -1 and first_qmark > first_slash:
                instance.query_start = first_qmark
            else:
                instance.query_start = None
        else:
            instance.path_start = None
            instance.query_start = first_qmark if first_qmark != -1 else None

        return instance


if __name__ == "__main__":
    print("starting test")
    test_urls = [
        "http://foo.bar/baz?qux=hex",
        "https://www.example.com",
        "https://example.com:8080/abc?param=value",
        "http://localhost:3000/api/v1/users",
        "http://192.168.1.1/path/to/page",
        "https://sub.domain.example.com/some/path/",
        "http://example.com?foo=bar",
        "https://example.com/path?foo=bar&baz=qux",
        "http://example.com:80/",
        "http://example.com/path.with.dots/in/it",
        "https://example.co.uk",
        "http://user@domain.com/path",
        "http://[::1]:8080/ipv6",
        "https://example.com:443",
        "http://example.com:1234?arg=val",
        "ftp://example.com/path",
        "https://example.com/path/subpath/?key=value&another=thing",
        "http://example.com/complex/path/with.numbers123?data=456&more=789",
        "https://www.subdomain.example.org/some/deep/path/here",
        "http://example.com:8080/special_chars-_.~",
    ]

    url = Url.parse(test_urls[0])
    assert url.scheme == "http://"
    assert url.host == "foo.bar"
    assert url.port is None
    assert url.path == "/baz"
    assert url.query == "?qux=hex"

    url = Url.parse(test_urls[1])
    assert url.scheme == "https://"
    assert url.host == "www.example.com"
    assert url.port is None
    assert url.path is None
    assert url.query is None

    url = Url.parse(test_urls[2])
    assert url.scheme == "https://"
    assert url.host == "example.com"
    assert url.port == 8080
    assert url.path == "/abc"
    assert url.query == "?param=value"

    url = Url.parse(test_urls[3])
    assert url.scheme == "http://"
    assert url.host == "localhost"
    assert url.port == 3000
    assert url.path == "/api/v1/users"
    assert url.query is None

    url = Url.parse(test_urls[4])
    assert url.scheme == "http://"
    assert url.host == "192.168.1.1"
    assert url.port is None
    assert url.path == "/path/to/page"
    assert url.query is None

    url = Url.parse(test_urls[5])
    assert url.scheme == "https://"
    assert url.host == "sub.domain.example.com"
    assert url.port is None
    assert url.path == "/some/path/"
    assert url.query is None

    url = Url.parse(test_urls[6])
    assert url.scheme == "http://"
    assert url.host == "example.com"
    assert url.port is None
    assert url.path is None
    assert url.query == "?foo=bar"

    url = Url.parse(test_urls[7])
    assert url.scheme == "https://"
    assert url.host == "example.com"
    assert url.port is None
    assert url.path == "/path"
    assert url.query == "?foo=bar&baz=qux"

    url = Url.parse(test_urls[8])
    assert url.scheme == "http://"
    assert url.host == "example.com"
    assert url.port == 80
    assert url.path == "/"
    assert url.query is None

    url = Url.parse(test_urls[9])
    assert url.scheme == "http://"
    assert url.host == "example.com"
    assert url.port is None
    assert url.path == "/path.with.dots/in/it"
    assert url.query is None

    url = Url.parse(test_urls[10])
    assert url.scheme == "https://"
    assert url.host == "example.co.uk"
    assert url.port is None
    assert url.path is None
    assert url.query is None

    url = Url.parse(test_urls[11])
    assert url.scheme == "http://"
    assert url.host == "user@domain.com"
    assert url.port is None
    assert url.path == "/path"
    assert url.query is None

    try:
        url = Url.parse(test_urls[12])
        assert False, "IPv6 test should raise ValueError"
    except ValueError:
        pass

    url = Url.parse(test_urls[13])
    assert url.scheme == "https://"
    assert url.host == "example.com"
    assert url.port == 443
    assert url.path is None
    assert url.query is None

    url = Url.parse(test_urls[14])
    assert url.scheme == "http://"
    assert url.host == "example.com"
    assert url.port == 1234
    assert url.path is None
    assert url.query == "?arg=val"

    try:
        url = Url.parse(test_urls[15])
        assert False, "ftp URL should raise ValueError"
    except ValueError:
        pass

    url = Url.parse(test_urls[16])
    assert url.scheme == "https://"
    assert url.host == "example.com"
    assert url.port is None
    assert url.path == "/path/subpath/"
    assert url.query == "?key=value&another=thing"

    url = Url.parse(test_urls[17])
    assert url.scheme == "http://"
    assert url.host == "example.com"
    assert url.port is None
    assert url.path == "/complex/path/with.numbers123"
    assert url.query == "?data=456&more=789"

    url = Url.parse(test_urls[18])
    assert url.scheme == "https://"
    assert url.host == "www.subdomain.example.org"
    assert url.port is None
    assert url.path == "/some/deep/path/here"
    assert url.query is None

    url = Url.parse(test_urls[19])
    assert url.scheme == "http://"
    assert url.host == "example.com"
    assert url.port == 8080
    assert url.path == "/special_chars-_.~"
    assert url.query is None

    print("cases passed")
