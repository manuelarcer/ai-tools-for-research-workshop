from bot.memory import AnsweredQ, RecentQA

def q(i):
    return AnsweredQ(question=f"pregunta {i}", answer_summary=f"resumen {i}",
                     message_id=1000 + i, timestamp=float(i))

def test_rolling_cap_keeps_newest():
    m = RecentQA(maxlen=3)
    for i in range(5):
        m.add(q(i))
    ids = [a.message_id for a in m.recent()]
    assert ids == [1002, 1003, 1004]          # oldest dropped, order preserved

def test_render_empty_is_blank():
    assert RecentQA().render_for_prompt() == ""

def test_render_includes_question_and_message_id():
    m = RecentQA()
    m.add(q(1))
    out = m.render_for_prompt()
    assert "pregunta 1" in out
    assert "1001" in out                      # message_id referenced
    assert "reply" in out.lower() or "responder" in out.lower()  # dedup guidance present
