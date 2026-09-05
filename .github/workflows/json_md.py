import os
import json

def json_md(input_folder="./bucket", md_out="./README.md"):
    md_lines = ["# 软件清单", "", "| 名称 | 版本 | 主页 | 下载 |", "| ---- | ---- | ---- | ---- |"]
    count = 0
    # 获取文件列表 + 字母排序（不区分大小写）
    filenames = os.listdir(input_folder)
    filenames = sorted(filenames, key=str.lower)

    for filename in filenames:
        if filename.lower().endswith(".json"):
            file_path = os.path.join(input_folder, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                print(f"[跳过] {filename} 读取失败: {e}")
                continue

            name = filename.split(".")[0]
            homepage_val = data.get("homepage", "")
            version_val = data.get("version", "")
            # 优先64bit地址
            url_val = data.get("architecture", {}).get("64bit", {}).get("url", "")
            if not url_val:
                url_val = data.get("url", "")
            # url数组取第一条
            if isinstance(url_val, list) and len(url_val) > 0:
                url_val = url_val[0]

            if homepage_val:
                homepage_val = f"[主页]({homepage_val})"
            if url_val:
                url_val = f"[下载]({url_val})"

            row = f"| {name} | {version_val} | {homepage_val} | {url_val} |"
            md_lines.append(row)
            count += 1
            print(f"✅已处理: {filename}")

    with open(md_out, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"\n✅完成，共 {count} 条记录")

if __name__ == "__main__":
    json_md()
