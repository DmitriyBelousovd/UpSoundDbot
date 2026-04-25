import re
from typing import Optional


URL_RE = re.compile(r"(https?://[^\s]+)")


def extract_first_url(text: str) -> Optional[str]:
    if not text:
        return None
    match = URL_RE.search(text)
    if not match:
        return None
    return match.group(1).strip(").,!?\"'")
