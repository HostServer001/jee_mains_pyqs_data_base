import re
from .types import *

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

def make_inline(text: str) -> str:
    """
    Wrapper fucntion around convert_dollar_math_to_inline function.
    Is used in get_answer_label clustering mainly and in clustering funstions of pdfy.py
    """
    if not isinstance(text, str):
        text = str(text)
    # First convert $...$ / $$...$$ using existing helper
    text = convert_dollar_math_to_inline(text)
    # Then force any \[ ... \] to inline \( ... \) to avoid display math blocks
    text = text.replace(r"\[", r"\(").replace(r"\]", r"\)")
    return text

def get_answer_label_clustering(question:QuestionLike)->CorrectOptions:
    qtype = getattr(question, "type", "") or ""
    if isinstance(qtype, str) and qtype.lower() in ("integer", "numerical", "numeric", "number"):
        ans = getattr(question, "answer", None)
        if ans is not None and ans != "":
            return make_inline(str(ans))

    corr = getattr(question, "correct_options", None)
    if corr:
        if not isinstance(corr, (list, tuple)):
            corr = [corr]
        return format_correct_options(corr)

    for attr in ("answer", "correct_answer", "solution", "correct"):
        val = getattr(question, attr, None)
        if val:
            if isinstance(val, (list, tuple)):
                return format_correct_options(val)
            return make_inline(str(val))

    explanation = getattr(question, "explanation", "") or ""
    match = re.search(r'([-+]?\d+(\.\d+)?)', explanation)
    if match:
        return match.group(1)

    return ""

def get_answer_label_normal(question:QuestionLike)->CorrectOptions:
    qtype = getattr(question, "type", "") or ""
    if qtype.lower() in ("integer", "numerical", "numeric", "number"):
        ans = getattr(question, "answer", None)
        if ans is not None and ans != "":
            return convert_dollar_math_to_inline(str(ans))

    corr = getattr(question, "correct_options", None)
    if corr:
        if not isinstance(corr, (list, tuple)):
            corr = [corr]
        return format_correct_options(corr)

    for attr in ("answer", "correct_answer", "solution", "correct"):
        val = getattr(question, attr, None)
        if val:
            if isinstance(val, (list, tuple)):
                return format_correct_options(val)
            return convert_dollar_math_to_inline(str(val))

    explanation = getattr(question, "explanation", "") or ""
    match = re.search(r'([-+]?\d+(\.\d+)?)', explanation)
    if match:
        return match.group(1)

    return ""

def format_correct_options(correct_options)->FormatedCorrectOptions:
    if not correct_options:
        return ""
    labels = []
    for option in correct_options:
        if isinstance(option, int):
            labels.append(chr(ord("A") + option))
        elif isinstance(option, str) and option.isdigit():
            labels.append(chr(ord("A") + int(option)))
        else:
            labels.append(str(option))
    return ", ".join(labels)

def get_exam_html(question:QuestionLike)->HtmlLike:
    exam_date = getattr(question, "examDate", None)
    exam_html = f" <span class='exam-date'>[{exam_date}]</span>" if exam_date else ""
    return exam_html

def get_options_html(question:QuestionLike):
    options_html_items = []
    options = getattr(question, "options", []) or []
    for opt_i, opt in enumerate(options):
        content = opt.get("content") if isinstance(opt, dict) else str(opt)
        content_conv = convert_dollar_math_to_inline(content)
        options_html_items.append(f"<li class='option'>{content_conv}</li>")

    options_html = ""
    if options_html_items:
        options_html = "<ol class='options' type='A'>\n" + "\n".join(options_html_items) + "\n</ol>"
    return options_html

def get_labels_sorted(labels)->list:
    """
    Sort cluster labels from a clustering dictionary, ensuring that all valid
    cluster IDs (e.g., 0, 1, 2, ...) appear in ascending order while the special
    noise label -1 is placed at the end. Works for both integer and string labels.
    """
    try:
        labels_sorted = sorted(labels, key=lambda x: (int(x) == -1, int(x)))
    except Exception:
        labels_sorted = sorted(labels, key=lambda x: (str(x) == "-1", str(x)))
    return labels_sorted