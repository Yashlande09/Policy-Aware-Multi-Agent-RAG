import re
from pypdf import PdfReader

HEADING_RE = re.compile(r"^\s*(?:[A-Z][A-Z0-9 /&'’(),.-]{4,}|(?:\d+(?:\.\d+)*[.)]?\s+).{3,80})\s*$")

def _clean(s):
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def extract_policy(path):
    reader=PdfReader(str(path))
    chunks=[]
    for page_no,page in enumerate(reader.pages,1):
        text=_clean(page.extract_text() or "")
        lines=text.splitlines()
        section="Unsectioned"
        buf=[]
        for line in lines:
            line=line.strip()
            if not line: continue
            is_heading=(len(line)<110 and (line.isupper() or re.match(r"^\d+(?:\.\d+)*\s",line)))
            if is_heading and buf:
                body=_clean("\n".join(buf))
                if len(body)>=80:
                    chunks.append({"chunk_id":f"P{page_no:02d}-C{len([x for x in chunks if x['page']==page_no])+1:03d}",
                                   "page":page_no,"section":section,"text":body})
                buf=[]
                section=line[:160]
            elif is_heading:
                section=line[:160]
            else:
                buf.append(line)
        if buf:
            body=_clean("\n".join(buf))
            if len(body)>=80:
                chunks.append({"chunk_id":f"P{page_no:02d}-C{len([x for x in chunks if x['page']==page_no])+1:03d}",
                               "page":page_no,"section":section,"text":body})
    # Merge very small fragments with the previous same-page chunk; preserve provenance.
    merged=[]
    for c in chunks:
        if merged and len(c["text"])<180 and merged[-1]["page"]==c["page"]:
            merged[-1]["text"] += "\n" + c["text"]
        else: merged.append(c)
    return merged
