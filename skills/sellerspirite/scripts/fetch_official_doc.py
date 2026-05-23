#!/usr/bin/env python3
"""Fetch SellerSprite official API docs and validate planned parameters."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

BASE = "https://open.sellersprite.com"

KNOWN_TOOLS = {
    "competitor_lookup": ("/api/1", "查竞品"),
    "product_research": ("/api/2", "选产品"),
    "product_node": ("/api/9", "查产品类目"),
    "asin_detail": ("/api/3", "ASIN 详情"),
    "asin_coupon_trend": ("/api/56", "ASIN优惠趋势"),
    "asin_detail_with_coupon_trend": ("/api/57", "ASIN详情及优惠趋势"),
    "asin_prediction": ("/api/27", "ASIN 销量预测"),
    "bsr_prediction": ("/api/26", "BSR销量预测"),
    "traffic_keyword": ("/api/14", "关键词反查(流量词列表)"),
    "keepa_info": ("/api/22", "商品趋势详情(keepa)"),
    "keyword_research": ("/api/10", "关键词选品"),
    "keyword_research_trends": ("/api/11", "关键词选品-趋势数据"),
    "keyword_miner": ("/api/6", "关键词挖掘"),
    "traffic_extend": ("/api/46", "拓展流量词"),
    "aba_research_weekly": ("/api/19", "ABA 数据选品-按周"),
    "aba_research_monthly": ("/api/20", "ABA 数据选品-按月"),
    "aba_research_trend": ("/api/60", "ABA 数据选品-关键词趋势"),
    "google_trend": ("/api/12", "谷歌趋势"),
    "keyword_order": ("/api/24", "出单词反查"),
    "traffic_listing": ("/api/16", "关联流量列表"),
    "traffic_keyword_stat": ("/api/13", "流量词统计"),
    "traffic_listing_stat": ("/api/15", "关联流量统计"),
    "traffic_source": ("/api/17", "查流量来源(关键词流向)"),
    "market_research": ("/api/29", "选市场列表"),
    "market_research_statistics": ("/api/30", "选市场-统计"),
    "market_product_concentration": ("/api/31", "选市场-商品集中度"),
    "market_brand_concentration": ("/api/32", "选市场-品牌集中度"),
    "market_seller_country_distribution": ("/api/35", "选市场-卖家所属地分布"),
    "market_seller_concentration": ("/api/33", "选市场-卖家集中度"),
    "market_seller_type_concentration": ("/api/34", "选市场-卖家类型分布"),
    "market_product_demand_trend": ("/api/36", "选市场-商品需求趋势"),
    "market_listing_date_distribution": ("/api/37", "选市场-上架时间分布"),
    "market_listing_trend_distribution": ("/api/38", "选市场-上架趋势分布"),
    "market_ratings_count_distribution": ("/api/39", "选市场-评分数分布"),
    "market_rating_distribution": ("/api/40", "选市场-评分值分布"),
    "market_price_distribution": ("/api/41", "选市场-价格分布"),
    "market_ebc_distribution": ("/api/42", "选市场-A+视频分布"),
    "review": ("/api/25", "查评论"),
}

KNOWN_TITLES = {title.lower(): path for path, title in KNOWN_TOOLS.values()}


@dataclass
class ToolDoc:
    path: str
    title: str
    method: str
    api_url: str
    mcp_code: str
    request_params: list[dict[str, str]]
    return_fields: list[dict[str, str]]
    supports_return_fields: bool


def fetch(path_or_url: str) -> str:
    url = path_or_url if path_or_url.startswith("http") else BASE + path_or_url
    req = urllib.request.Request(url, headers={"User-Agent": "codex-sellerspirite-skill/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        raise SystemExit(f"Failed to fetch official docs: {url}\n{exc}") from exc


def clean(value: str) -> str:
    value = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", value)
    value = re.sub(r"(?i)<br\\s*/?>", " ", value)
    value = re.sub(r"<[^>]+>", " ", value)
    return html.unescape(re.sub(r"\s+", " ", value)).strip()


def extract_cells(row_html: str) -> list[str]:
    cells = re.findall(r"(?is)<t[dh][^>]*>(.*?)</t[dh]>", row_html)
    return [clean(cell) for cell in cells]


def table_after(page: str, marker: str) -> list[list[str]]:
    pos = page.find(marker)
    if pos < 0:
        return []
    table_start = page.find("<table", pos)
    table_end = page.find("</table>", table_start)
    if table_start < 0 or table_end < 0:
        return []
    table = page[table_start : table_end + len("</table>")]
    rows = []
    for row in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", table):
        cells = extract_cells(row)
        if cells and cells[0] != "#":
            rows.append(cells)
    return rows


def parse_meta(page: str) -> tuple[str, str, str, str]:
    h1_matches = re.findall(r"(?is)<h1[^>]*>(.*?)</h1>", page)
    title = clean(h1_matches[-1]) if h1_matches else ""
    method = ""
    api_url = ""
    mcp_code = ""
    for row in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", page):
        cells = extract_cells(row)
        if len(cells) < 2:
            continue
        key = cells[0].lower().replace(" ", "")
        if key == "httpmethod":
            method = cells[1]
        elif key == "httprequesturl":
            api_url = cells[1]
        elif key == "mcpcode":
            mcp_code = cells[1]
    return title, method, api_url, mcp_code


def parse_doc(path: str) -> ToolDoc:
    page = fetch(path)
    title, method, api_url, mcp_code = parse_meta(page)
    req_rows = table_after(page, "-> 请求参数")
    ret_rows = table_after(page, "返回参数 <-")
    request_params = []
    for cells in req_rows:
        if len(cells) >= 6:
            request_params.append(
                {
                    "param": cells[1],
                    "type": cells[2],
                    "required": cells[3],
                    "name": cells[4],
                    "description": " ".join(cells[5:]),
                }
            )
    return_fields = []
    for cells in ret_rows:
        if len(cells) >= 5:
            return_fields.append(
                {
                    "field": cells[1],
                    "type": cells[2],
                    "name": cells[3],
                    "description": " ".join(cells[4:]),
                }
            )
    return ToolDoc(
        path=path,
        title=title,
        method=method,
        api_url=api_url,
        mcp_code=mcp_code,
        request_params=request_params,
        return_fields=return_fields,
        supports_return_fields="returnFields" in page and bool(mcp_code),
    )


def index_paths() -> list[tuple[str, str]]:
    page = fetch("/api")
    result = []
    for match in re.finditer(
        r'(?is)<a class="list-group-item[\s\S]*?href="(/api/\d+|/appendix)"[\s\S]*?<div>\s*([^<]+?)\s*</div>[\s\S]*?</a>',
        page,
    ):
        path, title = match.group(1), clean(match.group(2))
        if path != "/appendix":
            result.append((path, title))
    return result


def load_index() -> list[ToolDoc]:
    docs = []
    for path, _title in index_paths():
        doc = parse_doc(path)
        if doc.api_url:
            docs.append(doc)
    return docs


def resolve_tool(value: str) -> ToolDoc:
    normalized = value.strip().lower()
    if normalized.startswith("/api/"):
        return parse_doc(normalized)
    if normalized.startswith("api/"):
        return parse_doc("/" + normalized)
    if normalized in KNOWN_TOOLS:
        return parse_doc(KNOWN_TOOLS[normalized][0])
    if normalized in KNOWN_TITLES:
        return parse_doc(KNOWN_TITLES[normalized])
    for doc in load_index():
        candidates = {doc.mcp_code.lower(), doc.title.lower(), doc.path.lower()}
        if normalized in candidates:
            return doc
    raise SystemExit(f"Unknown official SellerSprite tool/page: {value}")


def normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def split_params(params: list[dict[str, str]]) -> tuple[dict[str, dict[str, str]], dict[str, set[str]], list[str]]:
    top_level: dict[str, dict[str, str]] = {}
    nested: dict[str, set[str]] = {}
    required: list[str] = []
    current_parent = ""
    for row in params:
        name = row["param"].strip()
        clean_name = name.lstrip("└").strip()
        if name.startswith("└") and current_parent:
            nested.setdefault(current_parent, set()).add(clean_name)
            continue
        current_parent = clean_name
        top_level[clean_name] = row
        if "✓" in row["required"]:
            required.append(clean_name)
    return top_level, nested, required


def validate(doc: ToolDoc, params: dict[str, Any]) -> int:
    top_level, nested, required = split_params(doc.request_params)
    allowed = set(top_level)
    if doc.supports_return_fields:
        allowed.add("returnFields")
    unknown = [key for key in params if key not in allowed]
    missing = [key for key in required if key not in params]
    nested_errors: list[str] = []
    for parent, children in nested.items():
        if parent in params and isinstance(params[parent], dict):
            for child in params[parent]:
                if child not in children:
                    nested_errors.append(f"{parent}.{child}")
    return_field_errors: list[str] = []
    if "returnFields" in params and doc.return_fields:
        official_fields = {row["field"].lstrip("└").strip() for row in doc.return_fields}
        fields = [part.strip() for part in str(params["returnFields"]).split(",") if part.strip()]
        return_field_errors = [field for field in fields if field not in official_fields]

    if not unknown and not missing and not nested_errors and not return_field_errors:
        print(f"OK: all parameters are documented for {doc.mcp_code or doc.path}.")
        return 0

    if missing:
        print("Missing required parameters:", ", ".join(missing))
    if unknown:
        print("Unknown top-level parameters:", ", ".join(unknown))
        for key in unknown:
            suggestion = next((known for known in allowed if normalize_key(known) == normalize_key(key)), "")
            if suggestion:
                print(f"  - Did you mean {suggestion!r} instead of {key!r}?")
    if nested_errors:
        print("Unknown nested parameters:", ", ".join(nested_errors))
    if return_field_errors:
        print("Unknown returnFields entries:", ", ".join(return_field_errors))
    return 2


def print_doc(doc: ToolDoc) -> None:
    print(f"# {doc.mcp_code or doc.path} - {doc.title}")
    print(f"Official page: {BASE}{doc.path}")
    print(f"Method: {doc.method}")
    print(f"API URL: {doc.api_url}")
    if doc.mcp_code:
        print(f"MCP Code: {doc.mcp_code}")
    if doc.supports_return_fields:
        print("MCP returnFields: supported")
    print("\n## Request Parameters")
    print("| Parameter | Type | Required | Name | Description |")
    print("|---|---|---:|---|---|")
    for row in doc.request_params:
        print(f"| `{row['param']}` | {row['type']} | {row['required']} | {row['name']} | {row['description']} |")
    print("\n## Return Fields")
    print("| Field | Type | Name | Description |")
    print("|---|---|---|---|")
    for row in doc.return_fields:
        print(f"| `{row['field']}` | {row['type']} | {row['name']} | {row['description']} |")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="List official API pages and MCP codes.")
    parser.add_argument("--tool", help="MCP code, official title, or /api/N path to inspect.")
    parser.add_argument("--validate", help="Path to a JSON file containing planned top-level request parameters.")
    parser.add_argument("--validate-json", help="Inline JSON object containing planned top-level request parameters.")
    args = parser.parse_args()

    if args.list:
        print("| MCP code | Name | Method | Official doc | API URL |")
        print("|---|---|---:|---|---|")
        for doc in load_index():
            code = f"`{doc.mcp_code}`" if doc.mcp_code else "-"
            print(f"| {code} | {doc.title} | {doc.method} | {BASE}{doc.path} | `{doc.api_url}` |")
        return 0

    if not args.tool:
        parser.error("--tool is required unless --list is used")

    doc = resolve_tool(args.tool)
    if args.validate and args.validate_json:
        parser.error("Use only one of --validate or --validate-json")

    if args.validate or args.validate_json:
        if args.validate:
            with open(args.validate, "r", encoding="utf-8") as fh:
                planned = json.load(fh)
        else:
            planned = json.loads(args.validate_json)
        if not isinstance(planned, dict):
            raise SystemExit("Validation input must be a JSON object.")
        return validate(doc, planned)

    print_doc(doc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
