from __future__ import annotations

from pathlib import Path

import streamlit.components.v1 as components

_CSS_DIR = Path(__file__).resolve().parent
_STYLE_ID = "mychance-theme-style"


def _read_css(*filenames: str) -> str:
    return "\n".join((_CSS_DIR / name).read_text(encoding="utf-8") for name in filenames)


def inject_theme(*, auth_page: bool = False) -> None:
    css_files = ["theme.css"]
    if auth_page:
        css_files.append("theme_auth.css")
    else:
        css_files.append("theme_app.css")

    css = _read_css(*css_files).replace("`", "\\`").replace("</style>", "<\\/style>")

    components.html(
        f"""
        <script>
        (function() {{
            const doc = window.parent.document;
            let style = doc.getElementById("{_STYLE_ID}");
            if (!style) {{
                style = doc.createElement("style");
                style.id = "{_STYLE_ID}";
                doc.head.appendChild(style);
            }}
            style.textContent = `{css}`;
        }})();
        </script>
        """,
        height=0,
    )
