import json
import re
from datetime import datetime, timezone
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

SOURCE = "https://cp.nowscore.com/buy/Jingcai.aspx?TypeID=105&OddsType=2"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; FootballAnalysisStudy/1.0)"}

def main():
    stamp = datetime.now(timezone.utc).isoformat()
    result = {
        "source": SOURCE,
        "fetched_at_utc": stamp,
        "status": "unknown",
        "message": "",
        "fixtures": [],
        "links": [],
        "raw_text_preview": ""
    }
    try:
        response = requests.get(SOURCE, headers=HEADERS, timeout=25)
        result["http_status"] = response.status_code
        response.raise_for_status()
        response.encoding = response.apparent_encoding or response.encoding
        soup = BeautifulSoup(response.text, "html.parser")
        result["page_title"] = soup.title.get_text(" ", strip=True) if soup.title else ""
        result["raw_text_preview"] = soup.get_text(" ", strip=True)[:6000]
        seen = set()
        for a in soup.find_all("a", href=True):
            label = a.get_text(" ", strip=True)
            href = urljoin(SOURCE, a["href"])
            if not label:
                continue
            if any(k in (label + " " + href).lower() for k in ["亚", "欧", "析", "jingcai", "matchdetail", "odds"]):
                key = (label, href)
                if key not in seen:
                    seen.add(key)
                    result["links"].append({"label": label[:120], "url": href})
        # Conservative extraction: only rows containing recognizable fixture markers.
        for tr in soup.find_all("tr"):
            text = tr.get_text(" ", strip=True)
            if not text or len(text) > 1200:
                continue
            anchors = [{"label": a.get_text(" ", strip=True), "url": urljoin(SOURCE, a.get("href", ""))}
                       for a in tr.find_all("a", href=True) if a.get_text(" ", strip=True)]
            if anchors and re.search(r"\b\d{3}\b", text):
                result["fixtures"].append({"row_text": text[:1000], "links": anchors[:20]})
        if response.status_code == 200:
            result["status"] = "fetched"
            result["message"] = "页面请求成功；赛事/盘口结构仍需验证，未识别的字段不会伪造。"
    except Exception as exc:
        result["status"] = "error"
        result["message"] = f"读取失败：{type(exc).__name__}: {exc}"
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"status={result['status']} fixtures={len(result['fixtures'])} links={len(result['links'])} message={result['message']}")

if __name__ == "__main__":
    main()
