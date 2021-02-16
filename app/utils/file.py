def get_file_url(path: str, *, file_host: str = "127.0.0.1"):
    if not path or path.startswith("http"):
        return path
    else:
        return f"{file_host}/{path}"
