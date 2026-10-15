"""web/index.html を作る。footage_edited/complete の .lrc と web/audio の長さを読み、template.html に埋め込む。
使い方: python3 web/src/build.py  （13_seikatsusyosahyouhon で実行）"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "web"
SRC = ROOT / "footage_edited" / "complete"

ALBUMS = [
    dict(key="d", dir="生活所作標本 _ Specimens of Daily Actions", title="生活所作標本",
         en="Specimens of Daily Actions", cover="img/cover-daily.jpg",
         note="合理化される前の所作。ジャケットには音の波形をそのまま、横波としてエンボスした。",
         tools=["ほうき / Broom", "現金 / Cash", "やかん / Kettle", "ハンドドリップ / Hand Drip",
                "ペン / Pen", "マッチ / Match", "レコード / Vinyl"]),
    dict(key="o", dir="生活合理所作標本 _ Specimens of Optimized Daily Actions", title="生活合理所作標本",
         en="Specimens of Optimized Daily Actions", cover="img/cover-optimized.jpg",
         note="合理化された現在の所作。ジャケットには波形をバーコード状の縦波に置き換えてエンボスした。",
         tools=["掃除機 / Vacuum Cleaner", "キャッシュレス / Cashless", "電気ケトル / Electric Kettle",
                "インスタント / Instant", "キーボード / Keyboard", "ライター / Lighter",
                "ストリーミング / Streaming"]),
]

def duration(p):
    out = subprocess.run(["afinfo", str(p)], capture_output=True, text=True).stdout
    return round(float(re.search(r"estimated duration: ([\d.]+)", out).group(1)), 2)

def parse_lrc(p):
    lines = []
    for raw in p.read_text(encoding="utf-8-sig").splitlines():
        m = re.match(r"\[(\d+):(\d+(?:\.\d+)?)\](.*)", raw.strip())
        if not m:
            continue
        ja, _, en = m.group(3).partition(" / ")
        lines.append(dict(t=int(m.group(1)) * 60 + float(m.group(2)), ja=ja.strip(), en=en.strip()))
    return lines

data = []
for al in ALBUMS:
    lrcs = sorted((SRC / al["dir"]).glob("*.lrc"))
    tracks = []
    for i, lrc in enumerate(lrcs, 1):
        title = re.sub(r"^\d+\s+", "", lrc.stem).replace(" _ ", " / ")
        src = f"audio/{al['key']}0{i}.mp3"
        tracks.append(dict(id=f"{al['key']}0{i}", title=title, tool=al["tools"][i - 1], src=src,
                           dur=duration(WEB / src), lines=parse_lrc(lrc)))
    data.append(dict(title=al["title"], en=al["en"], cover=al["cover"], note=al["note"], tracks=tracks))

page = (WEB / "src" / "template.html").read_text(encoding="utf-8").replace(
    "__DATA__", json.dumps(data, ensure_ascii=False))

# GitHub Pages 用：完全な HTML 文書
(WEB / "index.html").write_text(
    '<!doctype html>\n<html lang="ja">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
    + page.replace("<svg width=\"0\"", "</head>\n<body>\n<svg width=\"0\"", 1)
    + "\n</body>\n</html>\n", encoding="utf-8")

# プレビュー用の断片（引数で出力先を指定したときだけ）
if len(sys.argv) > 1:
    Path(sys.argv[1]).write_text(page, encoding="utf-8")
print("ok", [len(a["tracks"]) for a in data])
