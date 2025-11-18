from .styles import dark_style,white_style
from .html_helper import *
from .types import *
from .pdfy_support import (
    get_exam_html,
    get_answer_label_normal,
    get_answer_label_clustering,
    get_labels_sorted,
    get_options_html,
    convert_dollar_math_to_inline,
    make_inline,
    )

def get_html(question_list: list,style:str="dark")->HtmlLike:
    q_blocks = []
    answer_entries = []
    explanation_entries = []
    for index, question in enumerate(question_list, start=1):
        q_text = convert_dollar_math_to_inline(getattr(question, "question", ""))
        exam_html = get_exam_html(question)
        options_html = get_options_html(question)

        q_block = q_block_fx(index,exam_html,q_text,options_html)
        q_blocks.append(q_block)

        answer_label = get_answer_label_normal(question)
        answer_entries.append(f"<li>Q{index}: <strong>{answer_label}</strong></li>")


        explanation = getattr(question, "explanation", "") or ""
        if explanation and explanation.strip():
            explanation_html = convert_dollar_math_to_inline(explanation)
            explanation_entries.append(f"<li><strong>Q{index}:</strong> {explanation_html}</li>")

    questions_html = "\n".join(q_blocks)
    answer_key_html = "<ol class='answer-key' list-style-type=none;>\n" + "\n".join(answer_entries) + "\n</ol>"

    explanation_key_html = ""
    if explanation_entries:
        explanation_key_html = "<div class='explanation-section'>\n  <h3>Explanation Answer Key</h3>\n  <ol class='explanations'>\n" + "\n".join(explanation_entries) + "\n  </ol>\n</div>"
    
    if style == "dark":
        style_theme = dark_style
    if style == "white":
        style_theme == white_style
    
    html = final_html_fx(style_theme,questions_html,answer_key_html,explanation_key_html)
    return html

def get_cluster_html(cluster_dict: dict,title: str = "Clustered Questions",mode:str="dark")->HtmlLike:
    """
    Render clustered questions into an HTML file.

    - Uses convert_dollar_math_to_inline for all visible text (questions, options,
      explanations, answer labels and cluster/summary titles).
    - Forces any LaTeX display delimiters (\[...\]) to inline delimiters \(...\)
      so MathJax renders everything inline.
    - Accepts cluster keys that may be numpy integer types (e.g. np.int64).
    """

    labels = list(cluster_dict.keys())
    labels_sorted = get_labels_sorted(labels)

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

        for index, question in enumerate(q_list, start=1):
            q_text = make_inline(getattr(question, "question", ""))
            exam_html = get_exam_html(question)

            options_html = get_options_html(question)

            q_block_var = q_block_fx(index,exam_html,q_text,options_html)
            q_blocks.append(q_block_var)

            answer_label = make_inline(get_answer_label_clustering(question))
            # if answer label empty, show placeholder
            answer_entries.append(f"<li>Q{index}: <strong>{answer_label or ''}</strong></li>")

            explanation = getattr(question, "explanation", "") or ""
            if explanation and explanation.strip():
                explanation_html = make_inline(explanation)
                explanation_entries.append(f"<li><strong>Q{index}:</strong> {explanation_html}</li>")

        cluster_html = cluster_html_fx(label_title_html,size,q_blocks,answer_entries)
        if explanation_entries:
            cluster_html += explnation_html_fx(explanation_entries)
        cluster_html += "\n    </section>\n"
        cluster_blocks.append(cluster_html)

    clusters_html = "\n".join(cluster_blocks)
    summary_html = "<ul class='cluster-summary'>\n" + "\n".join(summary_entries) + "\n</ul>"
   
    if mode == "dark":
        style = dark_style
    else:
        style = white_style
    html = final_html_cluster_fx(title,style,cluster_dict,total_questions,summary_html,clusters_html)
    return html

def get_cluster_skim_html(cluster_dict: dict, title: str = "Clustered Questions",mode:str="dark")->HtmlLike:
    """
    Render clustered questions into an HTML file.

    - Uses convert_dollar_math_to_inline for all visible text (questions, options,
      explanations, answer labels and cluster/summary titles).
    - Forces any LaTeX display delimiters (\[...\]) to inline delimiters \(...\)
      so MathJax renders everything inline.
    - Accepts cluster keys that may be numpy integer types (e.g. np.int64).
    """
    # Normalize and sort cluster labels; put noise (-1) last
    labels = list(cluster_dict.keys())
    labels_sorted = get_labels_sorted(labels)

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

        for index, question in enumerate(q_list, start=1):
            q_text = make_inline(getattr(question, "question", ""))
            exam_html = get_exam_html(question)

            options_html = get_options_html(question)

            q_block = q_block_skim_fx(index,exam_html,q_text,options_html,question)
            q_blocks.append(q_block)

            answer_label = make_inline(get_answer_label_clustering(question))
            # if answer label empty, show placeholder
            answer_entries.append(f"<li>Q{index}: <strong>{answer_label or ''}</strong></li>")

            explanation = getattr(question, "explanation", "") or ""
            if explanation and explanation.strip():
                explanation_html = make_inline(explanation)
                explanation_entries.append(f"<li><strong>Q{index}:</strong> {explanation_html}</li>")

        cluster_html = cluster_html_skim_fx(label_title_html,size,q_blocks)
        
        cluster_blocks.append(cluster_html)

    clusters_html = "\n".join(cluster_blocks)
    summary_html = "<ul class='cluster-summary'>\n" + "\n".join(summary_entries) + "\n</ul>"
   
    if mode == "dark":
        style = dark_style
    else:
        style = white_style
    html = final_html_cluster_fx(title,style,cluster_dict,total_questions,summary_html,clusters_html)
    return html