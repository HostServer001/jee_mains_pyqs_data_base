dark_style = """
<style>
  /* Excalidraw-style font */
  @font-face {
    font-family: "Excalifont";
    src: url("https://excalidraw.nyc3.cdn.digitaloceanspaces.com/fonts/Excalifont-Regular.woff2") format("woff2");
    font-weight: normal;
    font-style: normal;
    font-display: swap;
  }

  body {
    font-family: "Excalifont", "Segoe UI", Roboto, Arial, sans-serif;
    margin: 20px;
    background: #0f172a; /* deep navy background */
    color: #f1f5f9;       /* light text */
    line-height: 1.6;
  }

  .container {
    max-width: 1100px;
    margin: 0 auto;
    background: #1e293b; /* slate panel */
    padding: 24px 32px;
    border-radius: 12px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.6);
  }

  header {
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-bottom:16px;
  }

  h1 {
    margin:0;
    font-size:1.4rem;
    color:#e2e8f0; /* light heading */
  }

  .meta {
    color:#94a3b8;
    font-size:0.95rem;
  }

  .cluster-summary {
    margin:12px 0 22px 0;
    padding-left:1.1em;
    color:#cbd5e1;
  }

  section.cluster {
    padding: 16px 20px;
    border-radius: 10px;
    border: 1px solid #334155;
    margin-bottom: 20px;
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
  }

  .cluster h3 {
    margin: 0 0 8px 0;
    color:#f8fafc;
  }

  .cluster-size {
    color:#38bdf8; /* cyan accent */
    font-weight:600;
    font-size:0.95rem;
    margin-left:8px;
  }

  .question-block {
    margin-bottom: 14px;
    padding:12px;
    background:#0f172a;
    border-radius:8px;
    border:1px solid #334155;
  }

  .q-number {
    font-weight:600;
    margin-right:8px;
    color:#38bdf8; /* cyan accent */
  }

  .q-text {
    margin:6px 0;
    line-height:1.5;
    font-size:1.05em;
    color:#f1f5f9;
  }

  .options {
    padding-left:1.1em;
    margin:6px 0;
  }

  .answer-key, .explanations {
    padding-left:1.1em;
    color:#cbd5e1;
  }

  .cluster-answers, .cluster-explanations {
    margin-top:12px;
    padding-top:10px;
    border-top:1px dashed #475569;
  }

  /* 📱 Mobile responsiveness */
  @media (max-width: 600px) {
    body { margin: 10px; font-size: 0.95em; }
    .container { padding: 16px; }
    h1 { font-size: 1.2rem; }
    .q-text { font-size: 1em; }
  }
</style>
"""


white_style = """
<style>
  /* Load Excalifont (Virgil-style hand‑drawn font) */
  @font-face {
    font-family: "Excalifont";
    src: url("https://excalidraw.nyc3.cdn.digitaloceanspaces.com/fonts/Excalifont-Regular.woff2") format("woff2");
    font-weight: normal;
    font-style: normal;
    font-display: swap;
  }

  /* Apply globally */
  body {
    font-family: "Excalifont", "Segoe UI", Roboto, Arial, sans-serif;
    margin: 20px;
    background: #f4f6fb; /* keep your light background */
    color: #111827;       /* keep your text color */
    line-height: 1.6;
  }

  .container {
    max-width: 1100px;
    margin: 0 auto;
    background: #fff;
    padding: 24px 32px;
    border-radius: 12px;
    box-shadow: 0 8px 30px rgba(2,6,23,0.08);
  }

  header {
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-bottom:16px;
  }

  h1 {
    margin:0;
    font-size:1.4rem;
    color:#0f172a; /* keep headings dark */
  }

  .meta {
    color:#6b7280;
    font-size:0.95rem;
  }

  section.cluster {
    padding: 16px 20px;
    border-radius: 10px;
    border: 1px solid #e6eef8;
    margin-bottom: 20px;
    background: linear-gradient(180deg, #ffffff 0%, #f9fafb 100%);
  }

  .cluster h3 {
    margin: 0 0 8px 0;
    color:#0f172a;
  }

  .question-block {
    margin-bottom: 14px;
    padding:12px;
    background:#fff;
    border-radius:8px;
    border:1px solid #f1f5f9;
  }

  .q-number {
    font-weight:600;
    margin-right:8px;
    color:#2563eb; /* accent color */
  }

  .q-text {
    margin:6px 0;
    line-height:1.5;
    font-size:1.05em;
  }

  .options {
    padding-left:1.1em;
    margin:6px 0;
  }

  .answer-key, .explanations {
    padding-left:1.1em;
  }

  .cluster-answers, .cluster-explanations {
    margin-top:12px;
    padding-top:10px;
    border-top:1px dashed #e6eef8;
  }

  /* 📱 Mobile responsiveness */
  @media (max-width: 600px) {
    body { margin: 10px; font-size: 0.95em; }
    .container { padding: 16px; }
    h1 { font-size: 1.2rem; }
    .q-text { font-size: 1em; }
  }
</style>
"""	