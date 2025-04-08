
import re
from bs4 import BeautifulSoup

RECYCLABLE_KEYWORDS = ["塑膠", "玻璃", "鋁", "銅", "橡膠", "不銹鋼", "木材", "ASR-DF", "SRF", "廢橡膠", "廢銅", "廢木材"]

def extract_num(text):
    try:
        return float(text.replace(',', '').strip())
    except:
        return 0.0

def is_recyclable(name):
    return any(keyword in name for keyword in RECYCLABLE_KEYWORDS)

def parse_html(content):
    soup = BeautifulSoup(content, 'html.parser')
    data = {}

    def get_by_id(soup, ids):
        for id_ in ids:
            tag = soup.find(id=id_)
            if tag and tag.text:
                return extract_num(tag.text)
        return 0.0

    # 公司名稱抓取
    # 加入容錯邏輯抓公司名稱
    com_tag = soup.find(id="ContentPlaceHolder1_MCheckI_lblComName")
    if not com_tag:
        # 嘗試以文字關鍵字模糊搜尋（含「股份有限公司」等字樣）
        com_tag = next((s for s in soup.find_all("span") if s and "公司" in s.text and "股份有限公司" in s.text), None)
    data["公司名稱"] = com_tag.text.strip() if com_tag else ""

    data["處理量"] = get_by_id(soup, ["ContentPlaceHolder1_MCheckI_lCarShell_WeightB", "ctl00_ContentPlaceHolder1_MCheckI_lCarShell_WeightB"])
    data["鋼鐵"] = get_by_id(soup, ["ContentPlaceHolder1_MCheckI_lRecycle_WeightB0", "ctl00_ContentPlaceHolder1_MCheckI_lRecycle_WeightB0"])

    recycle_total = 0
    recycle_items = []
    delay_required = False
    material_ratios = {}

    # 再生料：建立 index:name 對應表
    item_index = {}
    for span in soup.find_all("span"):
        sid = span.get("id", "")
        if sid.startswith("ContentPlaceHolder1_MCheckI_lRecycle_ItemName"):
            idx = sid.replace("ContentPlaceHolder1_MCheckI_lRecycle_ItemName", "")
            name = span.text.strip()
            item_index[idx] = name

    # 處理再生料
    for idx, name in item_index.items():
        gen_span = soup.find(id=f"ContentPlaceHolder1_MCheckI_lRecycle_WeightA{idx}")
        stock_span = soup.find(id=f"ContentPlaceHolder1_MCheckI_lRecycle_TodayWeight{idx}")
        gen = extract_num(gen_span.text) if gen_span else 0
        stock = extract_num(stock_span.text) if stock_span else 0
        if is_recyclable(name) and gen > 0:
            recycle_total += gen
            recycle_items.append(f"{name}:{gen}")
            if stock >= gen * 0.5:
                delay_required = True
        if name in ["廢塑膠", "廢玻璃", "廢玻璃砂土", "廢橡膠"]:
            ratio = round(stock / gen * 100, 2) if gen else 0
            material_ratios[name] = {
                "產生量": gen,
                "庫存量": stock,
                "比率(%)": ratio
            }

    # ASR 與 SRF 類的比率處理（依 Drop_ItemName 對應）
    for span in soup.find_all("span"):
        sid = span.get("id", "")
        if sid.startswith("ContentPlaceHolder1_MCheckI_lDrop_ItemName"):
            idx = sid.replace("ContentPlaceHolder1_MCheckI_lDrop_ItemName", "")
            name = span.text.strip()
            if "ASR" in name or "SRF" in name:
                gen_span = soup.find(id=f"ContentPlaceHolder1_MCheckI_lDrop_WeightA{idx}")
                stock_span = soup.find(id=f"ContentPlaceHolder1_MCheckI_lDrop_TodayWeight{idx}")
                gen = extract_num(gen_span.text) if gen_span else 0
                stock = extract_num(stock_span.text) if stock_span else 0
                ratio = round(stock / gen * 100, 2) if gen else 0
                material_ratios[name] = {
                    "產生量": gen,
                    "庫存量": stock,
                    "比率(%)": ratio
                }
                if gen > 0 and stock >= gen * 0.1:
                    delay_required = True

    threshold = data["處理量"] * 0.7
    raw_cert = min(data["鋼鐵"], threshold)
    delay_amount = raw_cert * 0.3 if delay_required else 0
    actual_cert = raw_cert - delay_amount
    recycle_ratio = round((raw_cert + recycle_total) / data["處理量"] * 100, 2) if data["處理量"] else 0
    subsidy_rate = round(min((4200 + 800 * ((recycle_ratio - 82) / 17)) / 1000, 5), 3)
    subsidy = round(actual_cert * subsidy_rate, 2)

    data.update({
        "原始認證量": round(raw_cert, 2),
        "緩發量": round(delay_amount, 2),
        "實際認證量": round(actual_cert, 2),
        "資再比(%)": recycle_ratio,
        "補貼費率": subsidy_rate,
        "補貼費": subsidy,
        "再生料明細": ", ".join(recycle_items),
        "緩發條件": "⚠️ 觸發緩發條件，將核發70%" if delay_required else "無"
    })

    data["比率明細"] = material_ratios

    return data
