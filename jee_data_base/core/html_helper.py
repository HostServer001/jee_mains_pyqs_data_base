import re
def convert_dollar_math_to_inline(text: str) -> str:
    """
    Convert TeX math delimiters:
      - $$...$$ -> \[ ... \]  (display)
      - $...$   -> \( ... \)  (inline)
    Preserves escaped dollars (i.e. \$).
    """
    if not isinstance(text, str):
        return text
    placeholder = "<<DOLLAR_ESCAPED>>"
    text = text.replace(r"\$", placeholder)
    text = re.sub(r'\$\$([\s\S]+?)\$\$', lambda m: f"\\[{m.group(1)}\\]", text, flags=re.S)
    text = re.sub(r'(?<!\\)\$([^\$].*?)\$', lambda m: f"\\({m.group(1)}\\)", text, flags=re.S)
    text = text.replace(placeholder, r"\$")

    return text

def make_inline(s: str) -> str:
        if not isinstance(s, str):
            s = str(s)
        s = convert_dollar_math_to_inline(s)
        s = s.replace(r"\[", r"\(").replace(r"\]", r"\)")
        return s

def q_block(idx,exam_html,q_text,options_html):
    q_block = f"""
      <div class="question-block">
        <div class="question-header">
          <span class="q-number">Q{idx}.</span>{exam_html}
        </div>
        <div class="q-text">{q_text}</div>
        <div class="q-options">{options_html}</div>
      </div>
    """
    return q_block

def cluter_html(label_title_html,size,q_blocks,answer_entries):
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
   return cluster_html

def explnation_html(explanation_entries):
    explnation_html = f"""
      <div class="cluster-explanations">
        <h4>Explanations</h4>
        <ol class="explanations">
{"".join(explanation_entries)}
        </ol>
      </div>
"""
    return explnation_html

def final_html_cluster(title,style,cluster_dict,total_questions,summary_html,clusters_html):
    final_html = rf"""<!DOCTYPE html>
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
    