#!/usr/bin/env python3
"""Print a PDF's page count without Spotlight or poppler.

mdls only answers for files Spotlight has indexed, so it returns "(null)" for
anything in /tmp or on a freshly written file. This reads the PDF directly:
first the /Count in the page tree, then a fallback that decompresses object
streams and counts /Type /Page.

Usage: pdf_pages.py FILE.pdf   ->  prints an integer, or "?" if undeterminable
"""
import re, sys, zlib


def page_count(path):
    data = open(path, "rb").read()

    # Fast path: /Type /Pages ... /Count N in the uncompressed trailer.
    for m in re.finditer(rb"/Type\s*/Pages\b(.{0,400}?)/Count\s+(\d+)", data, re.S):
        return int(m.group(2))
    for m in re.finditer(rb"/Count\s+(\d+)(.{0,400}?)/Type\s*/Pages\b", data, re.S):
        return int(m.group(1))

    # Fallback: decompress every stream and count page objects.
    blob = bytearray(data)
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", data, re.S):
        try:
            blob += zlib.decompress(m.group(1))
        except Exception:
            pass
    hits = re.findall(rb"/Type\s*/Page[^s]", bytes(blob))
    return len(hits) or None


if __name__ == "__main__":
    try:
        n = page_count(sys.argv[1])
        print(n if n else "?")
    except Exception:
        print("?")
