import os
import json
from urllib.parse import urlparse

def merge_json(input_folder="./bucket", output_file="./bin/result.json"):
    """
    合并文件夹下所有 JSON 只保留指定字段
    :param input_folder: 输入文件夹，默认 ./bucket
    :param output_file: 输出文件路径，默认 ./result.json
    """
    # ====================== 字段已移入函数内 ======================
    REQUIRED_FIELDS = [
        "name",
        "version",
        "homepage",
        "url"
    ]
    # ============================================================
    
    merged_list = []

    # 遍历文件夹所有文件
    for filename in os.listdir(input_folder):
        # 只处理 .json 文件
        if filename.lower().endswith(".json"):
            file_path = os.path.join(input_folder, filename)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # 如果是列表，遍历；如果是单对象，直接处理
                items = data if isinstance(data, list) else [data]

                for item in items:
                    # 优先从 architecture -> 64bit 提取下载地址，否则使用顶层 url
                    url = ""
                    arch = item.get("architecture", {}) or {}
                    if isinstance(arch, dict):
                        url = arch.get("64bit", {}).get("url", "") or arch.get("x64", {}).get("url", "")
                    if not url:
                        url = item.get("url", "")

                    # 从 url 的 path 部分取最后一段作为 name（若存在），否则使用原 name 或空字符串
                    name_from_url = ""
                    if url:
                        try:
                            path = urlparse(url).path
                            name_from_url = os.path.basename(path) or ""
                        except Exception:
                            name_from_url = ""

                    # 构造最终保留字段
                    filtered = {
                        "name": name_from_url or item.get("name", ""),
                        "version": item.get("version", ""),
                        "homepage": item.get("homepage", ""),
                        "url": url
                    }

                    merged_list.append(filtered)

                print(f"✅ 已处理：{filename}")

            except Exception as e:
                print(f"❌ 处理失败 {filename}：{str(e)}")

    # 写入最终文件
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(merged_list, f, ensure_ascii=False, indent=4)

    print(f"\n🎉 合并完成！共 {len(merged_list)} 条数据")
    #print(f"📁 输出文件：{output_file}")
    return merged_list

def json_to_markdown(json_file="./bin/result.json", md_file="./bin/result.md"):
    """
    JSON转MD表格 + 按分类排序 + 主页、下载统一为链接格式
    """
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 按分类排序
    data = sorted(data, key=lambda x: x.get("category", "").lower())

    md_content = """# 软件清单

| 名称 | 版本 |  主页 | 下载 |
| ---- |---- | ---- | ---- |
"""

    for item in data:
        name = item.get("name", "")
        version = item.get("version", "")
        homepage = item.get("homepage", "")
        url = item.get("url", "")

        # 主页：有地址就 [主页](链接)，否则空
        home_str = f"[主页]({homepage})" if homepage.strip() else ""
        # 下载：有地址就 [下载](链接)，否则空
        down_str = f"[下载]({url})" if url and url.strip() else ""

        md_content += f"| {name} | {version} | {home_str} | {down_str} |\n"

    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"✅ 转换完成！Markdown 文件已保存：{md_file}")

if __name__ == "__main__":
    merge_json()
    json_to_markdown()