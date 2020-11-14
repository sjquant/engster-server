def validate_file_size(file_body, file_size=1e7):
    if len(file_body) < 1e7:
        return True
    return False


def get_photo_url(path: str, *, media_url: str = "127.0.0.1"):
    if not path or path.startswith("http"):
        return path
    else:
        return f"{media_url}/{path}"
