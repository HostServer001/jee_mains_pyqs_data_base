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

