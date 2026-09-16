import re
from urllib.parse import urlparse


def extract_features(url):
    parsed = urlparse(url)

    hostname = parsed.netloc
    path = parsed.path

    features = [
        len(url),                                      # 1. URL length
        len(hostname),                                 # 2. Domain length
        len(path),                                     # 3. Path length
        url.count("."),                                # 4. Dots
        url.count("-"),                                # 5. Hyphens
        url.count("@"),                                # 6. @ symbol
        url.count("?"),                                # 7. ?
        url.count("&"),                                # 8. &
        url.count("="),                                # 9. =
        url.count("_"),                                # 10. _
        url.count("~"),                                # 11. ~
        url.count("%"),                                # 12. %
        url.count("/"),                                # 13. /
        url.count(":"),                                # 14. :
        url.count("*"),                                # 15. *
        url.count("|"),                                # 16. |
        url.count("!"),                                # 17. !
        url.count("$"),                                # 18. $
        url.count("'"),                                # 19. '
        url.count(","),                                # 20. ,
        int("http://" in url.lower()),                 # 21. HTTP
        int("https://" in url.lower()),                # 22. HTTPS
        int(re.search(r"\d", hostname) is not None),   # 23. Number in domain
        sum(c.isdigit() for c in url),                 # 24. Number of digits
        sum(c.isalpha() for c in url),                 # 25. Number of letters
        int("@" in url),                                # 26. @ present
        int(re.match(r"^\d{1,3}(\.\d{1,3}){3}$", hostname) is not None),  # 27. IP address
        int(len(url) > 75),                            # 28. Long URL
        int(len(url) > 100),                           # 29. Very long URL
        int(any(word in url.lower() for word in [
            "login", "verify", "update", "secure",
            "account", "bank", "signin", "confirm"
        ]))                                            # 30. Suspicious keyword
    ]

    return features