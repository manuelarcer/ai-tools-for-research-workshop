from bot.user_state import UserState, UserStates, MAX_HISTORY


def test_get_creates_and_refreshes_activity():
    states = UserStates(window_seconds=100)
    st = states.get(7, now=10.0)
    assert st.last_activity == 10.0
    st.opus_calls = 1
    # within window -> same object, state preserved, activity refreshed
    st2 = states.get(7, now=50.0)
    assert st2 is st
    assert st2.opus_calls == 1
    assert st2.last_activity == 50.0


def test_get_resets_after_window():
    states = UserStates(window_seconds=100)
    st = states.get(7, now=10.0)
    st.opus_calls = 2
    st.handed_off = True
    st.messages.append("hola")
    # idle longer than window -> fresh record
    st2 = states.get(7, now=200.0)
    assert st2 is not st
    assert st2.opus_calls == 0
    assert st2.handed_off is False
    assert list(st2.messages) == []


def test_users_are_independent():
    states = UserStates(window_seconds=100)
    a = states.get(1, now=10.0)
    a.opus_calls = 2
    b = states.get(2, now=10.0)
    assert b.opus_calls == 0


def test_render_history_empty():
    assert UserState().render_history() == ""


def test_render_history_lists_messages():
    st = UserState()
    st.messages.append("no funciona")
    st.messages.append("sigue igual")
    out = st.render_history()
    assert "no funciona" in out and "sigue igual" in out
    assert "1." in out and "2." in out


def test_messages_capped_at_max_history():
    st = UserState()
    for i in range(MAX_HISTORY + 3):
        st.messages.append(f"m{i}")
    assert len(st.messages) == MAX_HISTORY
    assert list(st.messages)[0] == f"m{3}"   # oldest dropped
