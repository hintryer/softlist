import requests
from datetime import datetime, timezone
from typing import Optional

def get_file_last_commit_date(owner: str, repo: str, path: str,
                              branch: str = "main",
                              token: Optional[str] = None,
                              timeout: int = 10) -> Optional[datetime]:
    """
    返回指定文件的最后一次提交时间（UTC datetime），找不到或出错返回 None。
    owner: 仓库所有者
    repo: 仓库名
    path: 文件路径（相对于仓库根）
    branch: 分支名或 commit sha（默认 main）
    token: 可选的 GitHub Token，用于提高限速
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    params = {"path": path, "sha": branch}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=timeout)
        r.raise_for_status()
    except requests.RequestException as e:
        # 可根据需要改为抛出异常
        return None

    items = r.json()
    if not items:
        return None

    latest = items[0]
    # 优先使用 committer.date，否则使用 author.date
    date_str = (latest.get("commit", {}).get("committer", {}) or {}).get("date") \
               or (latest.get("commit", {}).get("author", {}) or {}).get("date")
    if not date_str:
        return None

    # GitHub 返回格式通常为 '2026-09-06T12:34:56Z'
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        # 备用解析（某些 edge case）
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            return None
if __name__ == "__main__":
    dt = get_file_last_commit_date("hintryer", "softlist", "README.md", branch="main", token=None)
    if dt:
        print("Last modified (UTC):", dt.isoformat())
    else:
        print("No commit found or request failed.")