import abc
import csv
import re
import io


class SubtitleList(list):
    def to_csv(self):
        csvfile = io.StringIO()
        fields = list(self[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        for each in self:
            writer.writerow(each)
        return csvfile

    def __repr__(self):
        return super().__repr__()


class BaseSubtitle(abc.ABC):
    def __init__(self, text: str):
        self._subtitles = self.read(text)

    def __getitem__(self, idx: int):
        return self._subtitles[idx]

    def __len__(self):
        return len(self._subtitles)

    def __repr__(self):
        return repr(self._subtitles)

    def __getattr__(self, key):
        return self._subtitles.__getattribute__(key)

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

            lines.append({"time": prev_seconds, "subtitle": line})
            prev_seconds = self._process_time(each.group(1))

        # process last group
        line = text[each.start() :]  # noqa:E203
        line = re.sub(re_sync, "", line).strip()
        time = self._process_time(each.group(1))
        lines.append({"time": time, "subtitle": line})

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

            lines.append({"time": prev_seconds, "subtitle": line})
            prev_seconds = self._process_time(each.group(1))
        # process last group
        line = text[each.start() :]  # noqa:E203
        time = self._process_time(each.group(1))
        line = re.sub(r"(<.*?>|^[\s]*-|\(.*\))", "", line).strip()
        lines.append({"time": time, "subtitle": line})

        return lines


class SubtitleMatcher:
    def __init__(self, subtitles: SubtitleList, translations: SubtitleList):
        self._subtitles = subtitles
        self._translations = translations

    def _find_lte_idx(
        self,
        translations: SubtitleList,
        current_sub: SubtitleList,
        next_sub: SubtitleList,
    ):
        for idx, current_trans in enumerate(translations):
            try:
                next_trans = translations[idx + 1]
            except IndexError:
                next_trans = current_trans

            if current_trans["time"] >= next_sub["time"]:
                return translations[:idx]

            if (
                next_trans["time"] >= current_sub["time"]
                and next_trans["time"] < next_sub["time"]
            ):
                continue

            if current_trans["time"] >= current_sub["time"]:
                break

        return translations[: idx + 1]

    def _concat_translations(self, partition: SubtitleList):
        translation = ""
        for i, each in enumerate(partition):
            if i != 0:
                translation += " "
            translation += each["subtitle"]
        return translation

    def match(self):
        """Match subtitle and translation"""

        matched = SubtitleList()
        prev_idx = 0

        for i, current_subtitle in enumerate(self._subtitles):
            try:
                next_subtitle = self._subtitles[i + 1]
                trans_chunk = self._find_lte_idx(
                    self._translations[prev_idx:], current_subtitle, next_subtitle
                )
            except IndexError:
                # Last subtitle
                trans_chunk = self._translations[prev_idx:]

            new_translation = self._concat_translations(trans_chunk)
            matched.append(
                {
                    "time": current_subtitle.pop("time"),
                    "subtitle": current_subtitle.pop("subtitle"),
                    "translation": new_translation,
                    **current_subtitle,
                }
            )
            prev_idx += len(trans_chunk)
        return matched
