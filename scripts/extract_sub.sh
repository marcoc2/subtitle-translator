#!/usr/bin/env bash
set -e

if [ -z "$1" ]; then
    echo "Uso: $0 arquivo.mkv"
    exit 1
fi

INPUT="$1"

if ! command -v ffprobe >/dev/null 2>&1 || ! command -v ffmpeg >/dev/null 2>&1; then
    echo "Precisa ter ffmpeg e ffprobe instalados."
    exit 1
fi

mapfile -t SUBS < <(ffprobe -v error -select_streams s \
    -show_entries stream=index:stream_tags=language,title \
    -of csv=p=0 "$INPUT")

if [ "${#SUBS[@]}" -eq 0 ]; then
    echo "Nenhuma legenda encontrada em: $INPUT"
    exit 1
fi

CHOSEN_LINE=""
for line in "${SUBS[@]}"; do
    IFS=',' read -r IDX TYPE LANG TITLE <<<"$line"
    if [ "$LANG" = "eng" ]; then
        CHOSEN_LINE="$line"
        break
    fi
done

if [ -z "$CHOSEN_LINE" ]; then
    CHOSEN_LINE="${SUBS[0]}"
fi

IFS=',' read -r IDX TYPE LANG TITLE <<<"$CHOSEN_LINE"

BASENAME="${INPUT%.*}"
TAG="${LANG:-sub}"
OUTFILE="${BASENAME}.${TAG}.srt"

echo "Extraindo legenda (idx=$IDX, lang=${LANG:-desconhecido}) para: $OUTFILE"

ffmpeg -y -i "$INPUT" -map "0:$IDX" -c:s srt "$OUTFILE"

echo "Pronto."
