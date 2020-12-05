import pytest

from app.core.subtitle import SMISubtitle, SRTSubtitle, SubtitleMatcher, SubtitleList
from tests.data.core_reader import subtitle_matcher_data


def test_read_smi():
    text = """<BODY><SYNC Start=50774><P Class=KRCC>
누군가를 보며<br>궁금해한 적 있나요
<SYNC Start=52534><P Class=KRCC>
머릿속에서 무슨 일이<br>벌어지고 있을지?
<SYNC Start=55303><P Class=KRCC>
음, 전 알아요
<SYNC Start=56901><P Class=KRCC>
라일리의 머릿속은 잘 알죠
</BODY>"""

    subtitle = SMISubtitle(text)
    assert len(subtitle) == 4
    assert subtitle[0]["time"] == 50
    assert subtitle[0]["line"] == "누군가를 보며 궁금해한 적 있나요"
    assert subtitle[1]["time"] == 52
    assert subtitle[1]["line"] == "머릿속에서 무슨 일이 벌어지고 있을지?"
    assert subtitle[2]["time"] == 55
    assert subtitle[2]["line"] == "음, 전 알아요"
    assert subtitle[3]["time"] == 56
    assert subtitle[3]["line"] == "라일리의 머릿속은 잘 알죠"


def test_read_srt():
    text = """2
00:00:51,800 --> 00:00:53,290
<font color="#808080">JOY:</font> <i>Do you ever look
at someone and wonder...</i>

3
00:00:53,520 --> 00:00:55,648
<i>"What is going on
inside their head?"</i>

4
00:00:56,320 --> 00:00:59,403
<i>Well, I know.
Well, I know Riley's head.</i>

5
00:01:05,160 --> 00:01:07,162
<font color="#D900D9">(BABY COOING)</font>

6
00:01:35,640 --> 00:01:36,641
Hmm?
"""
    subtitle = SRTSubtitle(text)
    assert len(subtitle) == 4

    assert subtitle[0]["time"] == 51
    assert subtitle[0]["line"] == "JOY: Do you ever look at someone and wonder..."
    assert subtitle[1]["time"] == 53
    assert subtitle[1]["line"] == '"What is going on inside their head?"'
    assert subtitle[2]["time"] == 56
    assert subtitle[2]["line"] == "Well, I know. Well, I know Riley's head."
    assert subtitle[3]["time"] == 95
    assert subtitle[3]["line"] == "Hmm?"


@pytest.mark.parametrize("subtitle,translation,matched", subtitle_matcher_data)
def test_subtitle_matcher(subtitle, translation, matched):
    subtitle = SubtitleList(subtitle)
    translation = SubtitleList(translation)
    matcher = SubtitleMatcher(subtitle, translation)
    result = matcher.match()
    assert result == matched
