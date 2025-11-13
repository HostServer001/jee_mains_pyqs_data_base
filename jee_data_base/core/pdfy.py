import re
from .styles import dark_style,white_style
from .html_helper import *

def convert_dollar_math_to_inline(text: str) -> str:
    """
    Convert TeX math delimiters:
      - $$...$$ -> \[ ... \]  (display)
      - $...$   -> \( ... \)  (inline)
    Preserves escaped dollars (i.e. \$).
    """
    if not isinstance(text, str):
        return text

    # Temporarily protect escaped dollars
    placeholder = "<<DOLLAR_ESCAPED>>"
    text = text.replace(r"\$", placeholder)

    # Convert $$...$$ -> \[...\]
    text = re.sub(r'\$\$([\s\S]+?)\$\$', lambda m: f"\\[{m.group(1)}\\]", text, flags=re.S)

    # Convert single $...$ -> \(...\) (avoid $$ which already handled)
    text = re.sub(r'(?<!\\)\$([^\$].*?)\$', lambda m: f"\\({m.group(1)}\\)", text, flags=re.S)

    # Restore escaped dollars
    text = text.replace(placeholder, r"\$")

    return text

def conv_to_html_mathjax(text: str, filename: str = "mathjax_render.html"):
    """
    Converts LaTeX math in $$...$$ to inline MathJax format and writes it into an HTML file.
    """
    converted_text = convert_dollar_math_to_inline(text)

    html = rf"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Inline MathJax</title>
  <script id="MathJax-script" async
    src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
  </script>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 50px;
      font-size: 18px;
    }}
  </style>
</head>
<body>
  <p>{converted_text}</p>
</body>
</html>
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)



def render_to_html(question_list: list, filename: str = "questions_render.html"):
    """
    Renders a list of Question objects into a styled HTML file with MathJax support.
    Each question and its options are added. An answer key section is produced at the end.
    Exam date (examDate) is shown beside a question if present.

    Updates:
    - Use Question.answer for numerical/integer type questions as fallback.
    - Robust handling of correct_options (ints, digit-strings, letters).
    - Add Explanation Answer Key section after the answer key containing per-question explanations.
    """
    def format_correct_options(correct_options):
        if not correct_options:
            return ""
        labels = []
        for opt in correct_options:
            if isinstance(opt, int):
                labels.append(chr(ord("A") + opt))
            elif isinstance(opt, str) and opt.isdigit():
                labels.append(chr(ord("A") + int(opt)))
            else:
                labels.append(str(opt))
        return ", ".join(labels)

    def get_answer_label(q):
        # 1) If question has explicit 'answer' (numerical types), use it
        qtype = getattr(q, "type", "") or ""
        if qtype.lower() in ("integer", "numerical", "numeric", "number"):
            ans = getattr(q, "answer", None)
            if ans is not None and ans != "":
                return convert_dollar_math_to_inline(str(ans))

        # 2) Use correct_options if available
        corr = getattr(q, "correct_options", None)
        if corr:
            if not isinstance(corr, (list, tuple)):
                corr = [corr]
            return format_correct_options(corr)

        # 3) Common fallback fields
        for attr in ("answer", "correct_answer", "solution", "correct"):
            val = getattr(q, attr, None)
            if val:
                if isinstance(val, (list, tuple)):
                    return format_correct_options(val)
                return convert_dollar_math_to_inline(str(val))

        # 4) Try explanation numeric extraction (best-effort)
        exp = getattr(q, "explanation", "") or ""
        m = re.search(r'([-+]?\d+(\.\d+)?)', exp)
        if m:
            return m.group(1)

        return ""

    # Build questions HTML
    q_blocks = []
    answer_entries = []
    explanation_entries = []
    for idx, q in enumerate(question_list, start=1):
        q_text = convert_dollar_math_to_inline(getattr(q, "question", ""))
        exam_date = getattr(q, "examDate", None)
        exam_html = f" <span class='exam-date'>[{exam_date}]</span>" if exam_date else ""

        # Options: expect list of dicts with "content"
        options_html_items = []
        options = getattr(q, "options", []) or []
        for opt_i, opt in enumerate(options):
            content = opt.get("content") if isinstance(opt, dict) else str(opt)
            content_conv = convert_dollar_math_to_inline(content)
            options_html_items.append(f"<li class='option'>{content_conv}</li>")

        options_html = ""
        if options_html_items:
            options_html = "<ol class='options' type='A'>\n" + "\n".join(options_html_items) + "\n</ol>"

        q_block = f"""
  <div class="question-block">
    <div class="question-header">
      <span class="q-number">Q{idx}.</span>{exam_html}
    </div>
    <div class="q-text">{q_text}</div>
    <div class="q-options">{options_html}</div>
  </div>
"""
        q_blocks.append(q_block)

        # Prepare answer key entry (robust)
        answer_label = get_answer_label(q)
        answer_entries.append(f"<li>Q{idx}: <strong>{answer_label}</strong></li>")

        # Prepare explanation entry (if exists)
        explanation = getattr(q, "explanation", "") or ""
        if explanation and explanation.strip():
            explanation_html = convert_dollar_math_to_inline(explanation)
            explanation_entries.append(f"<li><strong>Q{idx}:</strong> {explanation_html}</li>")

    questions_html = "\n".join(q_blocks)
    answer_key_html = "<ol class='answer-key'>\n" + "\n".join(answer_entries) + "\n</ol>"

    explanation_key_html = ""
    if explanation_entries:
        explanation_key_html = "<div class='explanation-section'>\n  <h3>Explanation Answer Key</h3>\n  <ol class='explanations'>\n" + "\n".join(explanation_entries) + "\n  </ol>\n</div>"
    
    html = rf"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Questions</title>
  <script id="MathJax-script" async
    src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
  </script>
  <style>
    body {{
      font-family: "Segoe UI", Roboto, Arial, sans-serif;
      margin: 30px;
      background: #f7f8fb;
      color: #222;
    }}
    .container {{
      max-width: 900px;
      margin: 0 auto;
      background: #fff;
      padding: 24px 32px;
      border-radius: 8px;
      box-shadow: 0 6px 18px rgba(15,23,42,0.08);
    }}
    .question-block {{
      padding: 14px 18px;
      border-radius: 6px;
      border: 1px solid #eef1f6;
      margin-bottom: 16px;
      background: linear-gradient(180deg, #ffffff 0%, #fbfcfe 100%);
    }}
    .question-header {{
      margin-bottom: 8px;
      color: #334155;
    }}
    .q-number {{
      font-weight: 600;
      margin-right: 8px;
    }}
    .exam-date {{
      color: #64748b;
      font-size: 0.95em;
      margin-left: 8px;
    }}
    .q-text {{
      margin-bottom: 10px;
      line-height: 1.5;
      font-size: 1.03em;
    }}
    .options {{
      margin: 0;
      padding-left: 1.1em;
    }}
    .option {{
      margin: 6px 0;
    }}
    .answer-section {{
      margin-top: 28px;
      padding-top: 18px;
      border-top: 1px dashed #e6eef8;
    }}
    .answer-key {{
      padding-left: 1.1em;
      list-style-type:None;
    }}
    .explanation-section {{
      margin-top: 18px;
      padding-top: 12px;
      border-top: 1px dashed #e6eef8;
    }}
    .explanations {{
      padding-left: 1.1em;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h2>Questions</h2>
{questions_html}
    <div class="answer-section">
      <h3>Answer Key</h3>
{answer_key_html}
    </div>
{explanation_key_html}
  </div>
</body>
</html>
"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

# ...existing code...
def render_cluster_to_html(cluster_dict: dict, filename: str = "clusters_render.html", title: str = "Clustered Questions",mode:str="dark"):
    """
    Render clustered questions into an HTML file.

    - Uses convert_dollar_math_to_inline for all visible text (questions, options,
      explanations, answer labels and cluster/summary titles).
    - Forces any LaTeX display delimiters (\[...\]) to inline delimiters \(...\)
      so MathJax renders everything inline.
    - Accepts cluster keys that may be numpy integer types (e.g. np.int64).
    """
    def make_inline(s: str) -> str:
        if not isinstance(s, str):
            s = str(s)
        # First convert $...$ / $$...$$ using existing helper
        s = convert_dollar_math_to_inline(s)
        # Then force any \[ ... \] to inline \( ... \) to avoid display math blocks
        s = s.replace(r"\[", r"\(").replace(r"\]", r"\)")
        return s

    def format_correct_options(correct_options):
        if not correct_options:
            return ""
        labels = []
        for opt in correct_options:
            if isinstance(opt, int):
                labels.append(chr(ord("A") + opt))
            elif isinstance(opt, str) and opt.isdigit():
                labels.append(chr(ord("A") + int(opt)))
            else:
                labels.append(str(opt))
        return ", ".join(labels)

    def get_answer_label(q):
        qtype = getattr(q, "type", "") or ""
        if isinstance(qtype, str) and qtype.lower() in ("integer", "numerical", "numeric", "number"):
            ans = getattr(q, "answer", None)
            if ans is not None and ans != "":
                return make_inline(str(ans))

        corr = getattr(q, "correct_options", None)
        if corr:
            if not isinstance(corr, (list, tuple)):
                corr = [corr]
            return format_correct_options(corr)

        for attr in ("answer", "correct_answer", "solution", "correct"):
            val = getattr(q, attr, None)
            if val:
                if isinstance(val, (list, tuple)):
                    return format_correct_options(val)
                return make_inline(str(val))

        exp = getattr(q, "explanation", "") or ""
        m = re.search(r'([-+]?\d+(\.\d+)?)', exp)
        if m:
            return m.group(1)

        return ""

    # Normalize and sort cluster labels; put noise (-1) last
    labels = list(cluster_dict.keys())
    try:
        labels_sorted = sorted(labels, key=lambda x: (int(x) == -1, int(x)))
    except Exception:
        labels_sorted = sorted(labels, key=lambda x: (str(x) == "-1", str(x)))

    cluster_blocks = []
    summary_entries = []
    total_questions = sum(len(v) for v in cluster_dict.values())

    for clabel in labels_sorted:
        q_list = cluster_dict.get(clabel) or []
        try:
            clabel_int = int(clabel)
        except Exception:
            clabel_int = clabel

        label_title = "Noise" if clabel_int == -1 else f"Cluster {clabel_int}"
        label_title_html = make_inline(label_title)
        size = len(q_list)
        summary_entries.append(f"<li><strong>{label_title_html}:</strong> {size} question(s)</li>")

        q_blocks = []
        answer_entries = []
        explanation_entries = []

        for idx, q in enumerate(q_list, start=1):
            q_text = make_inline(getattr(q, "question", ""))
            exam_date = getattr(q, "examDate", None)
            exam_html = f" <span class='exam-date'>[{make_inline(exam_date)}]</span>" if exam_date else ""

            options_html_items = []
            options = getattr(q, "options", []) or []
            for opt_i, opt in enumerate(options):
                content = opt.get("content") if isinstance(opt, dict) else str(opt)
                content_conv = make_inline(content)
                options_html_items.append(f"<li class='option'>{content_conv}</li>")

            options_html = ""
            if options_html_items:
                options_html = "<ol class='options' type='A'>\n" + "\n".join(options_html_items) + "\n</ol>"

            q_block_var = q_block(idx,exam_html,q_text,options_html)
            q_blocks.append(q_block_var)

            answer_label = make_inline(get_answer_label(q))
            # if answer label empty, show placeholder
            answer_entries.append(f"<li>Q{idx}: <strong>{answer_label or ''}</strong></li>")

            explanation = getattr(q, "explanation", "") or ""
            if explanation and explanation.strip():
                explanation_html = make_inline(explanation)
                explanation_entries.append(f"<li><strong>Q{idx}:</strong> {explanation_html}</li>")

        cluster_html = f"""
    <section class="cluster">
      <h3>{label_title_html} <span class="cluster-size">({size})</span></h3>
      <div class="cluster-questions">
{"".join(q_blocks)}
      </div>
      <div class="cluster-answers">
        <h4>Answer Key</h4>
        <ol class="answer-key" style="list-style-type: none;">
{"".join(answer_entries)}
        </ol>
      </div>
"""
        if explanation_entries:
            cluster_html += f"""
      <div class="cluster-explanations">
        <h4>Explanations</h4>
        <ol class="explanations">
{"".join(explanation_entries)}
        </ol>
      </div>
"""
        cluster_html += "\n    </section>\n"
        cluster_blocks.append(cluster_html)

    clusters_html = "\n".join(cluster_blocks)
    summary_html = "<ul class='cluster-summary'>\n" + "\n".join(summary_entries) + "\n</ul>"
   
    if mode == "dark":
        style = dark_style
    else:
        style = white_style
    html = rf"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <title>{make_inline(title)}</title>
  <script id="MathJax-script" async
    src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
  </script>
  {style}
</head>
<body>
  <div class="container">
    <header>
      <h1>{make_inline(title)}</h1>
      <div class="meta">Total clusters: {len(cluster_dict)}, Total questions: {total_questions}</div>
    </header>
    <div class="summary">
      <h4>Cluster Summary</h4>
{summary_html}
    </div>
{clusters_html}
  </div>
</body>
</html>
"""
    with open(filename, "w", encoding="utf-8") as f:
    	f.write(html)


def render_cluster_to_html_skim(cluster_dict: dict, filename: str = "clusters_render.html", title: str = "Clustered Questions",mode:str="dark"):
    """
    Render clustered questions into an HTML file.

    - Uses convert_dollar_math_to_inline for all visible text (questions, options,
      explanations, answer labels and cluster/summary titles).
    - Forces any LaTeX display delimiters (\[...\]) to inline delimiters \(...\)
      so MathJax renders everything inline.
    - Accepts cluster keys that may be numpy integer types (e.g. np.int64).
    """
    def make_inline(s: str) -> str:
        if not isinstance(s, str):
            s = str(s)
        # First convert $...$ / $$...$$ using existing helper
        s = convert_dollar_math_to_inline(s)
        # Then force any \[ ... \] to inline \( ... \) to avoid display math blocks
        s = s.replace(r"\[", r"\(").replace(r"\]", r"\)")
        return s

    def format_correct_options(correct_options):
        if not correct_options:
            return ""
        labels = []
        for opt in correct_options:
            if isinstance(opt, int):
                labels.append(chr(ord("A") + opt))
            elif isinstance(opt, str) and opt.isdigit():
                labels.append(chr(ord("A") + int(opt)))
            else:
                labels.append(str(opt))
        return ", ".join(labels)

    def get_answer_label(q):
        qtype = getattr(q, "type", "") or ""
        if isinstance(qtype, str) and qtype.lower() in ("integer", "numerical", "numeric", "number"):
            ans = getattr(q, "answer", None)
            if ans is not None and ans != "":
                return make_inline(str(ans))

        corr = getattr(q, "correct_options", None)
        if corr:
            if not isinstance(corr, (list, tuple)):
                corr = [corr]
            return format_correct_options(corr)

        for attr in ("answer", "correct_answer", "solution", "correct"):
            val = getattr(q, attr, None)
            if val:
                if isinstance(val, (list, tuple)):
                    return format_correct_options(val)
                return make_inline(str(val))

        exp = getattr(q, "explanation", "") or ""
        m = re.search(r'([-+]?\d+(\.\d+)?)', exp)
        if m:
            return m.group(1)

        return ""

    # Normalize and sort cluster labels; put noise (-1) last
    labels = list(cluster_dict.keys())
    try:
        labels_sorted = sorted(labels, key=lambda x: (int(x) == -1, int(x)))
    except Exception:
        labels_sorted = sorted(labels, key=lambda x: (str(x) == "-1", str(x)))

    cluster_blocks = []
    summary_entries = []
    total_questions = sum(len(v) for v in cluster_dict.values())

    for clabel in labels_sorted:
        q_list = cluster_dict.get(clabel) or []
        try:
            clabel_int = int(clabel)
        except Exception:
            clabel_int = clabel

        label_title = "Noise" if clabel_int == -1 else f"Cluster {clabel_int}"
        label_title_html = make_inline(label_title)
        size = len(q_list)
        summary_entries.append(f"<li><strong>{label_title_html}:</strong> {size} question(s)</li>")

        q_blocks = []
        answer_entries = []
        explanation_entries = []

        for idx, q in enumerate(q_list, start=1):
            q_text = make_inline(getattr(q, "question", ""))
            exam_date = getattr(q, "examDate", None)
            exam_html = f" <span class='exam-date'>[{make_inline(exam_date)}]</span>" if exam_date else ""

            options_html_items = []
            options = getattr(q, "options", []) or []
            for opt_i, opt in enumerate(options):
                content = opt.get("content") if isinstance(opt, dict) else str(opt)
                content_conv = make_inline(content)
                options_html_items.append(f"<li class='option'>{content_conv}</li>")

            options_html = ""
            if options_html_items:
                options_html = "<ol class='options' type='A'>\n" + "\n".join(options_html_items) + "\n</ol>"

            q_block = f"""
      <div class="question-block">
        <div class="question-header">
          <span class="q-number">Q{idx}.</span>{exam_html}
        </div>
        <div class="q-text">{q_text}</div>
        <div class="q-options">{options_html}</div>
        <div class="cluster-explanation"> {make_inline(getattr(q,'explanation',''))}</div>
        </div>
    """
            q_blocks.append(q_block)

            answer_label = make_inline(get_answer_label(q))
            # if answer label empty, show placeholder
            answer_entries.append(f"<li>Q{idx}: <strong>{answer_label or ''}</strong></li>")

            explanation = getattr(q, "explanation", "") or ""
            if explanation and explanation.strip():
                explanation_html = make_inline(explanation)
                explanation_entries.append(f"<li><strong>Q{idx}:</strong> {explanation_html}</li>")

        cluster_html = f"""
    <section class="cluster">
      <h3>{label_title_html} <span class="cluster-size">({size})</span></h3>
      <div class="cluster-questions">
{"".join(q_blocks)}
      </div>
      <div class="cluster-answers">
        <h4>Answer Key</h4>
        <ol class="answer-key">
{"".join(answer_entries)}
        </ol>
      </div>
"""
        if explanation_entries:
            cluster_html += f"""
      <div class="cluster-explanations">
        <h4>Explanations</h4>
        <ol class="explanations">
{"".join(explanation_entries)}
        </ol>
      </div>
"""
        cluster_html += "\n    </section>\n"
        cluster_blocks.append(cluster_html)

    clusters_html = "\n".join(cluster_blocks)
    summary_html = "<ul class='cluster-summary'>\n" + "\n".join(summary_entries) + "\n</ul>"
   
    if mode == "dark":
        style = dark_style
    else:
        style = white_style
    html = rf"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <title>{make_inline(title)}</title>
  <script id="MathJax-script" async
    src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
  </script>
  {style}
</head>
<body>
  <div class="container">
    <header>
      <h1>{make_inline(title)}</h1>
      <div class="meta">Total clusters: {len(cluster_dict)}, Total questions: {total_questions}</div>
    </header>
    <div class="summary">
      <h4>Cluster Summary</h4>
{summary_html}
    </div>
{clusters_html}
  </div>
</body>
</html>
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

# ...existing code...