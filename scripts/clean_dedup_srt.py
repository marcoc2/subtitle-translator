#!/usr/bin/env python3
import re
import sys
from pathlib import Path

TAG_HTML = re.compile(r"<[^>]*>")
TAG_ASS  = re.compile(r"\{\\[^}]*\}")

def clean_line(line: str) -> str:
    line = TAG_HTML.sub("", line)
    line = TAG_ASS.sub("", line)
    line = re.sub(r"\s+", " ", line)
    return line.strip()

def parse_blocks(text: str):
    raw_blocks = text.strip("\n").split("\n\n")
    blocks = []
    for b in raw_blocks:
        lines = b.splitlines()
        if len(lines) < 2:
            continue
        index = lines[0].strip()
        time = lines[1].strip()
        content = lines[2:]
        blocks.append((index, time, content))
    return blocks

def main():
    if len(sys.argv) < 2:
        print("Uso: clean_dedup_srt.py entrada.srt [saida.srt]")
        sys.exit(1)

    in_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else in_path.with_suffix(".clean.srt")

    text = in_path.read_text(encoding="utf-8", errors="ignore")
    blocks = parse_blocks(text)

    out_blocks = []
    last_key = None

    for _, time, content in blocks:
        # limpa cada linha de texto
        cleaned_lines = [clean_line(l) for l in content]
        # remove linhas vazias após limpeza
        cleaned_lines = [l for l in cleaned_lines if l]

        if not cleaned_lines:
            continue

        key = (time, "\n".join(cleaned_lines))

        # se for igual ao bloco anterior (mesmo tempo + mesmo texto limpo), pula
        if key == last_key:
            continue

        last_key = key
        out_blocks.append((time, cleaned_lines))

    # grava de volta com índices reordenados
    with out_path.open("w", encoding="utf-8") as f:
        for i, (time, lines) in enumerate(out_blocks, start=1):
            f.write(f"{i}\n")
            f.write(f"{time}\n")
            for l in lines:
                f.write(l + "\n")
            f.write("\n")

    print(f"Gerado: {out_path}")

if __name__ == "__main__":
    main()
