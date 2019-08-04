from typing import List, Tuple, Optional
import re
from datetime import timedelta

import pandas as pd

from app.utils.exceptions import (
    UnsupportedExtensionError,
    InvalidDataFrameError
)


def trim_smi_text(text: str) -> str:
    text = text.replace('\r', '')
    extracted_text = re.search(r"<BODY>.*</BODY>", text,
                               flags=re.IGNORECASE | re.DOTALL)
    text = extracted_text.group() if extracted_text else ''
    # remove comments
    text = re.sub(r"<!--.*-->", "", text,
                  flags=re.DOTALL)

    # remove starting - or . more than one
    text = re.sub(r"^(- |\.+)", "", text, flags=re.MULTILINE)

    # adjust new line
    text = re.sub(r"\n+", "\n", text)

    # trim space taking larger space
    text = re.sub(r" +", " ", text)

    # replace <br>
    text = re.sub(r"<br>\n*", " ", text,
                  flags=re.IGNORECASE)

    return text


def trim_srt_text(text: str) -> str:
    text = text.replace('\r', '')
    text = re.sub(r"<[^>]*>", "", text)
    # adjust new line
    text = re.sub(r"\n+", "\n", text)
    return text


def _get_smi_line_info(time: str,
                       line: str,
                       lang: str) -> Optional[Tuple[str, str, str]]:
    """
    get info from a line

    Returns
    ----------
    line_info: (time, line, lang)
    """
    try:
        if line == '':
            return None
        time = str(timedelta(seconds=int(float(time)/1000)))
        time = f"{time}".zfill(8)
        line_info = (time, line, lang)
        return line_info

    # No time_list
    except IndexError:
        return None


def _convert_lang(lang: str) -> str:
    if lang in ['KRCC']:
        lang = 'KR'
    elif lang in ['ENCC']:
        lang = 'ENG'
    return lang


def get_smi_lines(text: str) -> List[Tuple[str, str, str]]:
    """
    get list of lines from smi file
    """
    text = trim_smi_text(text)
    lines = []
    re_sync = re.compile(
        r"<SYNC Start[\s]*=[\s]*([0-9]+)[\s]*><P[\s]*Class[\s]*=[\s]*(\w*)[\s]*",
        flags=re.IGNORECASE
    )
    time = ''
    lang = ''
    for line in text.split('\n'):
        if line == "":
            continue
        m = re.search(re_sync, line)
        if m:
            time = m.group(1)
            lang = _convert_lang(m.group(2))
        else:
            # html 제거
            line = re.sub(r'(<.*?>|^[\s]*-|\(.*\))', '', line).strip()
            line_info = _get_smi_line_info(time, line, lang)
            if line_info:
                lines.append(line_info)
    return lines


def get_srt_lines(text: str) -> list:
    """
    get list of lines from srt file
    """
    text = trim_srt_text(text)
    # 숫자 제거
    text = re.sub(r"^\d+$", "", text, flags=re.MULTILINE)
    # -, ...로 시작하는 말제거
    text = re.sub(r"^(- |\.+)", "", text, flags=re.MULTILINE)
    # adjust new line
    text = re.sub(r"\n+", "\n", text)

    # 시간 뒤에 여러문장이 있으면 한문장으로
    text = re.sub(r"([^\d])\n([^\d])", r"\g<1> \g<2>", text)

    # trim space taking larger space
    text = re.sub(r" +", " ", text)
    lines = []

    re_sync = re.compile(
        r"(\d\d:\d\d:\d\d),\d+\s*-->\s*\d\d:\d\d:\d\d,\d+\s*"
    )

    time = ''
    for line in text.split('\n'):
        if line == "":
            continue
        m = re.search(re_sync, line)

        if m:
            time = m.group(1)
            continue
        else:
            if time != '':
                lines.append((time, line, 'ENG'))
    return lines


def read_lines(text: str, ext: str):
    """
    read lines of subtitle file (.srt / .smi)
    """
    if ext == 'smi':
        lines = get_smi_lines(text)
    elif ext == 'srt':
        lines = get_srt_lines(text)
    else:
        raise UnsupportedExtensionError
    return lines


def lines_to_df(lines: List[Tuple[str, str, str]]) -> pd.DataFrame:
    """
    Create pandas Dataframe using lines for dealing with lines more easily.
    """
    df = pd.DataFrame(lines, columns=['time', 'line', 'lang'])
    df.set_index('time', inplace=True)
    return df


def combine_eng_kor(df_a: pd.DataFrame, df_b: pd.DataFrame) -> pd.DataFrame:

    lang_a = pd.unique(df_a['lang']).tolist()
    lang_b = pd.unique(df_b['lang']).tolist()

    langs = set(lang_a + lang_b)
    # Check it has two languages ENG / KR
    if len(langs) < 2 or not ('ENG' in langs and 'KR' in langs):
        raise InvalidDataFrameError
    eng_df = df_a if lang_a[0] == 'ENG' else df_b
    kor_df = df_a if lang_a[0] == 'KR' else df_b

    df = pd.merge(eng_df, kor_df, how='outer', left_index=True,
                  right_index=True, suffixes=('_eng', '_kr'))
    df = df.rename(columns={
        'line_eng': 'line',
        'line_kr': 'translation'
    })[['line', 'translation']]
    return df


def df_to_csv(df: pd.DataFrame, path: str):
    if df.columns.tolist() == ['line', 'translation']:
        df.to_csv(path, encoding='cp949')
        return df
    elif 'lang' in df.columns:
        langs = pd.unique(df['lang'])
        if len(langs) > 1:
            eng_df = df[df['lang'] == 'ENG']
            kor_df = df[df['lang'] == 'KR']
            df = combine_eng_kor(eng_df, kor_df)
        else:
            df.drop(['lang'], axis=1, inplace=True)
        df.to_csv(path, encoding='cp949')
        return df
    else:
        raise InvalidDataFrameError
