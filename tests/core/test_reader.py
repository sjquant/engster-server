import pytest

from app.core.subtitle import SMISubtitle, SRTSubtitle, SubtitleMatcher


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
    subtitle = SMISubtitle(sample_smi)

    data = subtitle[5]
    assert data["time"] == 50
    assert data["line"] == "누군가를 보며 궁금해한 적 있나요"

    data = subtitle[11]
    assert data["time"] == 110
    assert data["line"] == "라일리... - 너 좀 보렴"


def test_read_srt(sample_srt):
    subtitle = SRTSubtitle(sample_srt)

    data = subtitle[3]
    assert data["time"] == 56
    assert data["line"] == "Well, I know. Well, I know Riley's head."

    data = subtitle[8]
    assert data["time"] == 114
    assert data["line"] == "Aren't you a little bundle of joy?"


def test_subtitle_matcher(sample_smi, sample_srt):
    eng_subtitle = SRTSubtitle(sample_srt)
    ko_subtitle = SMISubtitle(sample_smi)
    matcher = SubtitleMatcher(eng_subtitle, ko_subtitle)
    matched = matcher.match()
    return matched
