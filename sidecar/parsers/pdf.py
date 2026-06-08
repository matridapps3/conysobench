from __future__ import annotations
import pdfplumber


def parse(stream) -> dict:
    pages = []
    with pdfplumber.open(stream) as pdf:
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables() or []
            pages.append({
                "page": i + 1,
                "text": page.extract_text() or "",
                "tables": [
                    {"header": t[0] if t else [], "rows": t[1:] if len(t) > 1 else []}
                    for t in tables
                ],
            })
    # Flatten the first table that has data rows into a top-level list[dict] so
    # the uploader (which looks for a top-level `rows`) can ingest a PDF table.
    # Without this the rows stay nested under pages[].tables[] and never import.
    rows = []
    for pg in pages:
        for t in pg["tables"]:
            if t["rows"]:
                header = [str(h) if h not in (None, "") else f"col_{j}"
                          for j, h in enumerate(t["header"])]
                for r in t["rows"]:
                    rows.append({(header[j] if j < len(header) else f"col_{j}"): cell
                                 for j, cell in enumerate(r)})
                break
        if rows:
            break
    return {"kind": "pdf", "n_pages": len(pages), "rows": rows, "pages": pages}
