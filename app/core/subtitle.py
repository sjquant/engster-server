import abc
import re

import pandas as pd


class SubtitleList(list):
    def to_df(self):
        return pd.DataFrame(self).set_index("time")

    def to_csv(self, path: str, encoding="utf-8"):
        self.to_df().to_csv(path, encoding=encoding)


class BaseSubtitle(abc.ABC):
    def __init__(self, text: str):
        self._subtitles = self.read(text)

    def __getitem__(self, idx: int):
        return self._subtitles[idx]

    def __len__(self):
        return len(self._subtitles)

    @abc.abstractmethod
    def read(self, text: str):
        pass


class SRTSubtitle(BaseSubtitle):
    def _trim(self, text: str):
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

    def read(self, text: str):
        text = self._trim(text)
        lines = SubtitleList()
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

            lines.append({"time": prev_seconds, "line": line})
            prev_seconds = self._process_time(each.group(1))
        return lines


class SMISubtitle(BaseSubtitle):
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
        lines = SubtitleList()
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

            lines.append({"time": prev_seconds, "line": line})
            prev_seconds = self._process_time(each.group(1))
        return lines


class SubtitleMatcher:
    def __init__(self, subtitles: SubtitleList, translations: SubtitleList):
        self._subtitles = subtitles
        self._translations = translations

    def _find_lte_idx(self, partition: SubtitleList, *, lte_time: int):
        for idx, each in enumerate(partition):
            if each["time"] > lte_time:
                break
        return idx

    def _concat_translations(self, partition: SubtitleList):
        translation = ""
        for i, each in enumerate(partition):
            if i != 0:
                translation += " "
            translation += each["line"]
        return translation

    def match(self):
        prev_idx = 0
        matched = SubtitleList()
        for each in self._subtitles:
            lte_idx = self._find_lte_idx(
                self._translations[prev_idx:], lte_time=each["time"]
            )
            new_translation = self._concat_translations(
                self._translations[prev_idx : prev_idx + lte_idx]  # noqa
            )
            matched.append(
                {
                    "time": each.pop("time"),
                    "subtitle": each.pop("line"),
                    "trnaslation": new_translation,
                    **each,
                }
            )
            prev_idx += lte_idx
        return matched
