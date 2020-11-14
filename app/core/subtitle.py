import abc
import re


class BaseReader(abc.ABC):
    @abc.abstractmethod
    def read(self, file):
        pass


class SRTReader(BaseReader):
    def _trim(self, text):
        text = text.replace("\r", "")
        # Remove html
        text = re.sub(r"<[^>]*>", "", text)
        # Remove numeric-only line
        text = re.sub(r"^\d+$", "", text, flags=re.MULTILINE)
        # Remove parentheses-only line
        text = re.sub(r"^\(.*\)$", "", text, flags=re.MULTILINE)
        # Remove starting - or . more than one
        text = re.sub(r"^(- |\.+)", "", text, flags=re.MULTILINE)
        # Adjust new line
        text = re.sub(r"&nbsp;", "", text)
        text = re.sub(r"\n+", "\n", text)
        # I forgot this...
        text = re.sub(r"([^\d])\n([^\d])", r"\g<1> \g<2>", text)
        # Trim space taking larger space
        text = re.sub(r" +", " ", text)
        return text

    def _process_time(self, time):
        h, m, s = tuple(time.split(":"))
        seconds = int(h) * 3600 + int(m) * 60 + int(s)
        return seconds

    def read(self, text):
        text = self._trim(text)
        lines = []
        re_sync = r"(\d\d:\d\d:\d\d),\d+\s*-->\s*\d\d:\d\d:\d\d,\d+\s*"
        iterator = re.finditer(re_sync, text, flags=re.IGNORECASE)
        prev_start = 0
        prev_seconds = 0

        for each in iterator:
            line = text[prev_start : each.start()]  # noqa
            line = re.sub(re_sync, "", line).strip()  # Trim line
            prev_start = each.start()

            if not line.strip():
                prev_seconds = self._process_time(each.group(1))
                continue

            lines.append((prev_seconds, line))
            prev_seconds = self._process_time(each.group(1))

        return lines


class SMIReader(BaseReader):
    def _trim(self, text):
        text = text.replace("\r", "")
        extracted_text = re.search(
            r"<BODY>.*</BODY>", text, flags=re.IGNORECASE | re.DOTALL
        )
        text = extracted_text.group() if extracted_text else ""
        # Remove comments
        text = re.sub(r"<!--.*-->", "", text, flags=re.DOTALL)
        # Remove starting - or . more than one
        text = re.sub(r"^(- |\.+)", "", text, flags=re.MULTILINE)
        # Adjust new line
        text = re.sub(r"&nbsp;", "", text)
        text = re.sub(r"\n+", "\n", text)
        # Trim space taking larger space
        text = re.sub(r" +", " ", text)
        # Replace <br>
        text = re.sub(r"<br>\n*", " ", text, flags=re.IGNORECASE)
        return text

    def _process_time(self, time: int):
        seconds = int(int(time) / 1000)
        return seconds

    def read(self, text):
        text = self._trim(text)
        lines = []
        re_sync = r"<SYNC Start[\s]*=[\s]*([0-9]+)[\s]*>"
        iterator = re.finditer(re_sync, text, flags=re.IGNORECASE)
        prev_start = 0
        prev_seconds = 0

        for each in iterator:
            line = text[prev_start : each.start()]  # noqa
            line = re.sub(r"(<.*?>|^[\s]*-|\(.*\))", "", line).strip()  # Trim line
            prev_start = each.start()

            if not line.strip():
                prev_seconds = self._process_time(each.group(1))
                continue

            lines.append((prev_seconds, line))
            prev_seconds = self._process_time(each.group(1))

        return lines
