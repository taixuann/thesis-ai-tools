#!/usr/bin/env python3
import os
import sys
import json
import re
import shutil
import sqlite3
import argparse
import subprocess
from datetime import datetime
from bs4 import BeautifulSoup, NavigableString

WORKSPACE = "/path/to/workspace"
WIKI_DIR = os.path.join(WORKSPACE, "wiki")
ZOTERO_TUI_DIR = os.path.join(WORKSPACE, "tools", "zotero-tui")
MYZOTERO_BIN = os.path.join(ZOTERO_TUI_DIR, "myzotero")
ZOTERO_STORAGE_DIR = os.path.expanduser("~/Zotero/storage")
ZOTERO_CACHE_DIR = os.path.expanduser("~/.cache/zotero-tui")
ZOTERO_SQLITE_PATH = os.path.expanduser("~/Zotero/zotero.sqlite")
TEMP_SQLITE_PATH = "/tmp/zotero_ingest_copy.sqlite"
LINTER_PATH = "/Users/tai/.gemini/skills/wiki-linter/scripts/wiki-linter.py"

# Valid Tag Taxonomy from SCHEMA.md / wiki-linter
VALID_PREFIXES = ["concept_type/", "domain/", "material_system/", "application/", "characterization_technique/", "maturity/", "local/"]
VALID_TAG_VALUES = {
    "concept_type": ["concept", "mechanism", "application", "entity", "method", "source", "methodology"],
    "domain": ["materials-science", "electrochemistry", "device-physics", "neuromorphic-computing", "organic-electronics"],
    "material_system": ["PDA", "ITO", "IGZO", "HfO2", "organic", "2d-materials", "graphene", "thin-films"],
    "application": ["memristor", "analog-memory", "synaptic-devices", "sensor"],
    "maturity": ["stable", "emerging", "speculative", "superseded"]
}

def run_cmd(args, cwd=None):
    res = subprocess.run(args, capture_output=True, text=True, cwd=cwd)
    if res.returncode != 0:
        print(f"Command failed: {' '.join(args)}")
        print(res.stderr)
        return None
    return res.stdout

def slugify(text):
    text = text.lower()
    text = re.sub(r'[:,\.\'\"\(\)\[\]—–]', '', text)
    return "-".join(text.split())

def get_citekey(paper):
    author = "unknown"
    if paper.get("authors"):
        first_author = paper["authors"][0]
        if "," in first_author:
            author = first_author.split(",")[0].strip().lower()
        else:
            author = first_author.split()[-1].strip().lower()
            
    year = paper.get("year", "unknown")
    
    title = paper.get("title", "")
    title_clean = re.sub(r'[^a-zA-Z0-9\s]', '', title.lower())
    title_words = title_clean.split()
    title_slug = "-".join(title_words[:4])
    
    return f"{author}-{year}-{title_slug}"

def parse_table(table_el):
    rows = []
    for tr in table_el.find_all('tr'):
        cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
        if cells:
            rows.append(cells)
    
    if not rows:
        return ""
        
    md_table = []
    header = rows[0]
    md_table.append("| " + " | ".join(header) + " |")
    md_table.append("| " + " | ".join(["---"] * len(header)) + " |")
    for row in rows[1:]:
        if len(row) < len(header):
            row += [""] * (len(header) - len(row))
        elif len(row) > len(header):
            row = row[:len(header)]
        md_table.append("| " + " | ".join(row) + " |")
        
    return "\n" + "\n".join(md_table) + "\n"

def convert_element(el):
    if isinstance(el, NavigableString):
        return str(el)
        
    tag = el.name
    
    if tag == 'table':
        return parse_table(el)
        
    child_text = "".join(convert_element(child) for child in el.children)
    
    if tag == 'h1':
        title = child_text.strip()
        if title.lower().startswith("summary:"):
            title = title[len("summary:"):].strip()
        return f"\n# {title}\n"
    elif tag == 'h2':
        return f"\n## {child_text.strip()}\n"
    elif tag == 'h3':
        return f"\n### {child_text.strip()}\n"
    elif tag == 'p':
        return f"\n{child_text.strip()}\n"
    elif tag == 'ul':
        return f"\n{child_text}\n"
    elif tag == 'ol':
        return f"\n{child_text}\n"
    elif tag == 'li':
        return f"- {child_text.strip()}\n"
    elif tag in ['strong', 'b']:
        return f"**{child_text}**"
    elif tag in ['em', 'i']:
        return f"*{child_text}*"
    elif tag == 'code':
        return f"`{child_text}`"
    elif tag == 'blockquote':
        return f"\n> {child_text.strip().replace(chr(10), chr(10) + '> ')}\n"
    elif tag == 'a':
        href = el.get('href', '')
        return f"[{child_text}]({href})"
    elif tag == 'span':
        return child_text
    elif tag in ['div', 'section']:
        return child_text
        
    return child_text

def html_to_markdown(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    md_div = soup.find(class_='markdown')
    if md_div:
        soup = md_div
    
    md = convert_element(soup)
    md = re.sub(r'\n{3,}', '\n\n', md)
    return md.strip()

def map_tag(tag_str):
    t_clean = re.sub(r'[^\w\s\-\/\+#]', '', tag_str).strip()
    if not t_clean.startswith('#'):
        if any(t_clean.startswith(p) for p in VALID_PREFIXES):
            return t_clean
        return f"local/{slugify(t_clean)}"
    
    parts = t_clean[1:].split('/', 1)
    if len(parts) < 2:
        return f"local/{slugify(t_clean[1:])}"
    
    prefix, val = parts[0], parts[1]
    val_slug = slugify(val)
    
    prefix_map = {
        "type": "concept_type",
        "concept_type": "concept_type",
        "domain": "domain",
        "mat": "material_system",
        "charact": "characterization_technique",
        "mechanism": "local",
        "process": "local",
        "application": "application",
        "maturity": "maturity",
        "custom": "local"
    }
    
    mapped_prefix = prefix_map.get(prefix, "local")
    
    # Force concept_type/source for source pages
    if mapped_prefix == "concept_type":
        return "concept_type/source"
        
    if prefix == "mechanism":
        return f"local/mech-{val_slug}"
    if prefix == "process":
        return f"local/proc-{val_slug}"
        
    valid_vals = VALID_TAG_VALUES.get(mapped_prefix)
    if valid_vals:
        matched_val = None
        for v in valid_vals:
            if v.lower() == val.lower() or slugify(v) == val_slug:
                matched_val = v
                break
        if matched_val:
            return f"{mapped_prefix}/{matched_val}"
        else:
            return f"local/{prefix}-{val_slug}"
    else:
        if mapped_prefix == "local":
            return f"local/{val_slug}"
        return f"{mapped_prefix}/{val_slug}"

def process_zotero_tags(zotero_tags):
    # Default tags for every source page
    tags = ["concept_type/source", "domain/materials-science", "local/active-research"]
    raw_tags = []
    
    for t in zotero_tags:
        t_str = str(t).strip()
        raw_tags.append(t_str)
        mapped = map_tag(t_str)
        if mapped:
            tags.append(mapped)
            
    # Ensure source concept_type tag is strictly source
    if "concept_type/source" not in tags:
        tags.append("concept_type/source")
        
    return sorted(list(set(tags))), sorted(list(set(raw_tags)))

def main():
    parser = argparse.ArgumentParser(description="Direct Local Zotero Note Ingester")
    parser.add_argument("--key", "-k", required=True, help="Zotero Item Key (e.g. K33D65Q2)")
    parser.add_argument("--cluster", "-c", help="Cluster slug to symlink source to")
    args = parser.parse_args()

    # Load cache for base metadata
    papers_path = os.path.join(ZOTERO_CACHE_DIR, "papers.json")
    if not os.path.exists(papers_path):
        print("Zotero cache not found. Refreshing...")
        run_cmd([MYZOTERO_BIN, "refresh"])

    with open(papers_path, "r") as f:
        cache_data = json.load(f)
    
    papers = cache_data.get("papers", [])
    target_paper = None
    for p in papers:
        if p["key"] == args.key:
            target_paper = p
            break
            
    if not target_paper:
        print(f"Error: Paper with key '{args.key}' not found in Zotero cache. Try running 'myzotero refresh' first.")
        sys.exit(1)

    citekey = get_citekey(target_paper)
    print(f"\nIngesting Beaver Note for: {target_paper['title'][:70]}...")
    print(f"Citekey  : {citekey}")
    print(f"Item Key : {args.key}")

    # Copy Zotero SQLite to bypass locks
    if not os.path.exists(ZOTERO_SQLITE_PATH):
        print(f"Error: Zotero database not found at {ZOTERO_SQLITE_PATH}")
        sys.exit(1)
        
    try:
        shutil.copyfile(ZOTERO_SQLITE_PATH, TEMP_SQLITE_PATH)
    except Exception as e:
        print(f"Error: Failed to copy Zotero database: {e}")
        sys.exit(1)

    # Query SQLite database for itemID, note, and tags
    conn = sqlite3.connect(TEMP_SQLITE_PATH)
    
    # 1. Get itemID
    res = conn.execute("SELECT itemID FROM items WHERE key = ?", (args.key,)).fetchone()
    if not res:
        print(f"Error: Item key '{args.key}' not found in Zotero SQLite database.")
        sys.exit(1)
    item_id = res[0]
    
    # 2. Get tags
    tag_rows = conn.execute("""
        SELECT t.name 
        FROM tags t 
        JOIN itemTags it ON t.tagID = it.tagID 
        WHERE it.itemID = ?
    """, (item_id,)).fetchall()
    db_tags = [r[0] for r in tag_rows]
    print(f"Found {len(db_tags)} tags in database.")

    # 3. Get Beaver note
    note_rows = conn.execute("SELECT note, title FROM itemNotes WHERE parentItemID = ?", (item_id,)).fetchall()
    beaver_note_html = None
    for note_content, note_title in note_rows:
        if "beaver" in note_content.lower() or "markdown" in note_content.lower():
            beaver_note_html = note_content
            break
            
    if not beaver_note_html and note_rows:
        beaver_note_html = note_rows[0][0] # Fallback to first note

    if not beaver_note_html:
        print(f"Error: No note found attached to item '{args.key}' in Zotero database.")
        sys.exit(1)
    print("✓ Located Beaver note.")

    # Convert Note HTML to Markdown
    note_markdown = html_to_markdown(beaver_note_html)
    print("✓ Converted HTML note to Markdown.")

    # Ensure directories exist
    os.makedirs(os.path.join(WIKI_DIR, "sources", "raw", "pdfs"), exist_ok=True)
    os.makedirs(os.path.join(WIKI_DIR, "sources", "raw", "markdown"), exist_ok=True)
    os.makedirs(os.path.join(WIKI_DIR, "candidates", "sources"), exist_ok=True)

    # Locate PDF in Zotero storage
    pdf_dir = os.path.join(ZOTERO_STORAGE_DIR, args.key)
    pdf_path = None
    if os.path.exists(pdf_dir):
        for f in os.listdir(pdf_dir):
            if f.lower().endswith(".pdf"):
                pdf_path = os.path.join(pdf_dir, f)
                break

    if not pdf_path:
        print(f"Warning: No PDF found in Zotero storage ({pdf_dir}). Ingestion will continue without copying PDF.")
    else:
        # Copy PDF to wiki/sources/raw/pdfs/
        dest_pdf = os.path.join(WIKI_DIR, "sources", "raw", "pdfs", f"{citekey}.pdf")
        shutil.copy(pdf_path, dest_pdf)
        print("✓ Copied raw PDF.")

        # Convert PDF to Markdown using docling
        print("Converting PDF using Docling...")
        run_cmd(["docling", dest_pdf, "--output", os.path.join(WIKI_DIR, "sources", "raw", "markdown"), "--from", "pdf", "--to", "markdown"])
        print("✓ Converted PDF to Markdown source text.")

    # Map tags to taxonomy
    ontology_tags, raw_tags = process_zotero_tags(db_tags)

    # Generate Candidate Source Page Content
    source_content = "---\n"
    source_content += f'title: "{target_paper["title"]}"\n'
    source_content += "tags:\n"
    for t in ontology_tags:
        source_content += f"  - {t}\n"
    source_content += "sources:\n"
    source_content += f"  - {citekey}.md\n"
    source_content += "last_updated: " + datetime.today().strftime('%Y-%m-%d') + "\n"
    if raw_tags:
        source_content += "zotero_tags:\n"
        for rt in raw_tags:
            source_content += f'  - "{rt}"\n'
    source_content += "---\n\n"
    
    # Append the parsed note content
    source_content += note_markdown + "\n"

    # Add quick links block to the bottom or top of the body
    quick_links = f"""

## 🔗 Quick Source Links
*   **AI Read**: [[sources/raw/markdown/{citekey}.md|Markdown Source Text]]
*   **Human Read**: [[sources/raw/pdfs/{citekey}.pdf|PDF Original Document]]
*   **Zotero select**: [Open in Desktop Zotero](zotero://select/items/0_{args.key})
"""
    source_content += quick_links

    # Write Candidate Source Page
    candidate_source_path = os.path.join(WIKI_DIR, "candidates", "sources", f"{citekey}.md")
    with open(candidate_source_path, "w", encoding="utf-8") as f:
        f.write(source_content)
    print("✓ Created staged Candidate Source Page.")

    # Create Symlink to cluster
    if args.cluster:
        cluster_sources_dir = os.path.join(WIKI_DIR, "sources", "references", f"cluster_{args.cluster}", "sources")
        os.makedirs(cluster_sources_dir, exist_ok=True)
        dst = os.path.join(cluster_sources_dir, f"{citekey}.md")
        
        # Link points to wiki/sources/{citekey}.md when promoted
        # From sources/references/cluster_{cluster_slug}/sources/ to sources/ is: ../../../{citekey}.md
        src_rel_path = f"../../../{citekey}.md"
        if os.path.exists(dst):
            os.remove(dst)
        try:
            os.symlink(src_rel_path, dst)
            print(f"✓ Symlinked source to cluster '{args.cluster}'.")
        except Exception as e:
            print(f"✕ Failed to create symlink: {e}")

    # Set status
    print("Updating Zotero pipeline status...")
    run_cmd([MYZOTERO_BIN, "status", "--set-docling", "wiki-ingested", args.key])
    run_cmd([MYZOTERO_BIN, "tag", "sync", args.key])
    print("✓ Pipeline status updated in Zotero.")

    # Clean up temp file
    if os.path.exists(TEMP_SQLITE_PATH):
        os.remove(TEMP_SQLITE_PATH)

    # Run linter
    if os.path.exists(LINTER_PATH):
        print("\nRunning compliance linter check...")
        linter_out = run_cmd(["python3", LINTER_PATH])
        if linter_out:
            print(linter_out)

if __name__ == "__main__":
    main()
