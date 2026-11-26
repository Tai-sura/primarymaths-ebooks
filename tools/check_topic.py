"""Check a book (or a proposed code/name) against the topic registry.

Only the registries actually present in `docs/topics/` are loaded, so each repository
checks its own subject and nothing else: the physics repository carries `physics.json`,
the maths one carries `maths.json`, and the other subject is never consulted here.

Usage:
  python tools/check_topic.py jpfm08
  python tools/check_topic.py --code JPWM01
  python tools/check_topic.py --code SPEM05 --title "Magnetic force on current-carrying wires"

Exit code 0 = the code exists and (when a title is given) the title matches the list exactly.
"""
import argparse, glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOPICS = os.path.join(ROOT, "docs", "topics")


def load():
    reg = {}
    paths = sorted(glob.glob(os.path.join(TOPICS, "*.json")))
    if not paths:
        sys.exit(f"no topic registry in {TOPICS}")
    for path in paths:
        subject = os.path.splitext(os.path.basename(path))[0]
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        for t in data["topics"]:
            reg[t["code"]] = dict(t, subject=subject)
    return reg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("book", nargs="?")
    ap.add_argument("--code")
    ap.add_argument("--title")
    a = ap.parse_args()

    reg = load()

    code, title, where = a.code, a.title, "arguments"
    if a.book:
        bj = os.path.join(ROOT, "books", a.book, "book.json")
        if not os.path.isfile(bj):
            sys.exit(f"no book.json at {bj}")
        with open(bj, encoding="utf-8") as fh:
            book = json.load(fh)
        code = book.get("code", "")
        title = book.get("title", "")
        where = f"books/{a.book}/book.json"

    if not code:
        sys.exit(f"no code to check ({where})")

    hit = reg.get(code.strip())
    if not hit:
        near = [c for c in reg if c.upper().startswith(code.strip().upper()[:4])][:8]
        print(f"FAIL  code {code!r} is not in the topic list. Closest codes: {near}")
        return 1

    print(f"code  {code}  ->  {hit['name_en']} / {hit['name_zh']}  ({hit['subject']})")
    if title is not None and title != "":
        if title.strip().lower() == hit["name_en"].strip().lower():
            print("title matches the list exactly  -> ok")
            return 0
        print(f"FAIL  title {title!r} != list {hit['name_en']!r}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
