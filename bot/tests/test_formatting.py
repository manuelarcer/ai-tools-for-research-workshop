from bot.formatting import render_html


def test_bold_double_star():
    assert render_html("mira **esto** bien") == "mira <b>esto</b> bien"


def test_italic_single_star():
    assert render_html("es *importante* aquí") == "es <i>importante</i> aquí"


def test_inline_code():
    assert render_html("usa `pip install` ahora") == "usa <code>pip install</code> ahora"


def test_fenced_code_with_language():
    out = render_html("Ejemplo:\n```python\nprint('hola')\n```")
    assert '<pre><code class="language-python">print(\'hola\')</code></pre>' in out
    assert "```" not in out


def test_fenced_code_without_language():
    out = render_html("```\nx = 1\n```")
    assert out == "<pre>x = 1</pre>"


def test_html_special_chars_are_escaped():
    assert render_html("si a < b & c > d") == "si a &lt; b &amp; c &gt; d"


def test_code_content_is_escaped():
    assert render_html("`<div>`") == "<code>&lt;div&gt;</code>"


def test_bold_markers_inside_code_block_are_literal():
    # ** inside a code block must NOT become <b>, and must be escaped-safe
    out = render_html("```python\ny = a**2\n```")
    assert 'a**2' in out
    assert "<b>" not in out


def test_link_conversion():
    out = render_html("ver [docs](https://claude.com/x)")
    assert out == 'ver <a href="https://claude.com/x">docs</a>'


def test_plain_text_passthrough():
    assert render_html("solo texto normal, sin formato.") == "solo texto normal, sin formato."


def test_multiple_features_together():
    src = "Hola **Ana**, corre `ls` o:\n```bash\ncd bot\n```\ny listo."
    out = render_html(src)
    assert "<b>Ana</b>" in out
    assert "<code>ls</code>" in out
    assert '<pre><code class="language-bash">cd bot</code></pre>' in out
