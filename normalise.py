_AVAILABILITY_KEYWORDS = [
    # English
    "open to work", "looking for", "seeking", "available", "job search",
    # French
    "disponible", "en recherche", "à l'écoute", "cherche poste", "cherche emploi",
    # Spanish
    "buscando trabajo", "en búsqueda", "busco empleo",
    # Portuguese
    "disponível", "procurando emprego", "à procura de",
]


def _has_signal(text: str) -> bool:
    t = text.lower()
    return any(kw in t for kw in _AVAILABILITY_KEYWORDS)


def _join(*parts) -> str:
    return " ".join(p for p in parts if p)


def _linkedin(r: dict) -> dict | None:
    url = r.get("profileUrl") or r.get("linkedinProfile", "")
    if not url:
        return None
    bio = _join(r.get("headline", ""), r.get("summary", ""), r.get("description", ""))
    if not _has_signal(bio):
        return None
    return {
        "profile_url": url,
        "platform":    "linkedin",
        "full_name":   _join(r.get("firstName", ""), r.get("lastName", "")),
        "headline":    r.get("headline", ""),
        "location":    r.get("location", ""),
        "bio_text":    bio[:2000],
    }


def _twitter(r: dict) -> dict | None:
    url = r.get("profileUrl") or r.get("twitterUrl", "")
    if not url:
        return None
    bio = _join(r.get("name", ""), r.get("biography", ""), r.get("bio", ""))
    if not _has_signal(bio):
        return None
    return {
        "profile_url": url,
        "platform":    "twitter",
        "full_name":   r.get("name", ""),
        "headline":    r.get("biography") or r.get("bio", ""),
        "location":    r.get("location", ""),
        "bio_text":    bio[:2000],
    }


def _github(r: dict) -> dict | None:
    url = r.get("profileUrl") or r.get("githubUrl", "")
    if not url and r.get("login"):
        url = f"https://github.com/{r['login']}"
    if not url:
        return None
    bio = _join(r.get("bio", ""), r.get("name", ""), r.get("company", ""))
    if not _has_signal(bio):
        return None
    return {
        "profile_url": url,
        "platform":    "github",
        "full_name":   r.get("name", "") or r.get("login", ""),
        "headline":    r.get("bio", ""),
        "location":    r.get("location", ""),
        "bio_text":    bio[:2000],
    }


def _reddit(r: dict) -> dict | None:
    url = r.get("profileUrl", "")
    if not url and r.get("username"):
        url = f"https://reddit.com/user/{r['username']}"
    if not url:
        return None
    bio = _join(
        r.get("commentBody") or r.get("body", ""),
        r.get("postTitle", ""),
        r.get("bio", ""),
    )
    if not _has_signal(bio):
        return None
    return {
        "profile_url": url,
        "platform":    "reddit",
        "full_name":   r.get("username", ""),
        "headline":    r.get("postTitle", ""),
        "location":    r.get("location", ""),
        "bio_text":    bio[:2000],
    }


_NORMALISERS = {
    "linkedin": _linkedin,
    "twitter":  _twitter,
    "github":   _github,
    "reddit":   _reddit,
}


def normalise_all(raw_results: dict) -> list:
    out = []
    for platform, records in raw_results.items():
        fn = _NORMALISERS.get(platform)
        if not fn:
            continue
        for record in records:
            try:
                p = fn(record)
                if p:
                    out.append(p)
            except Exception as e:
                print(f"[normalise] skip {platform} record: {e}")
    return out
