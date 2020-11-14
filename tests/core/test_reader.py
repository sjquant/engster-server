import pytest

from app.core.subtitle import SMIReader, SRTReader


@pytest.fixture(scope="module")
def sample_smi():
    with open("data/subtitles/InsideOut.smi", encoding="euc-kr", errors="ignore") as f:
        text = f.read()
    return text


@pytest.fixture(scope="module")
def sample_srt():
    with open("data/subtitles/InsideOut.srt", encoding="euc-kr", errors="ignore") as f:
        text = f.read()
    return text


def test_read_smi(sample_smi):
    reader = SMIReader()
    data = reader.read(sample_smi)

    time, line = data[5]
    assert time == 50
    assert line == "누군가를 보며 궁금해한 적 있나요"

    time, line = data[11]
    assert time == 110
    assert line == "라일리... - 너 좀 보렴"


def test_read_srt(sample_srt):
    reader = SRTReader()
    data = reader.read(sample_srt)

    time, line = data[3]
    assert time == 56
    assert line == "Well, I know. Well, I know Riley's head."

    time, line = data[8]
    assert time == 114
    assert line == "Aren't you a little bundle of joy?"
