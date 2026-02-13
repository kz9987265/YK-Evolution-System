"""
YK Evolution System - Nebula 整合模組
通過 GitHub Issues 與 Nebula 協作（不需要 API）
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path


class NebulaIntegration:
    """通過 GitHub Issues 與 Nebula 協作"""
    
    def __init__(self, repo_owner="kz9987265", repo_name="YK-evolution-system"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.repo_full_name = f"{repo_owner}/{repo_name}"
        
    def create_evolution_request(self, code_content, version, context=""):
        """
        創建進化請求 Issue
        
        參數:
            code_content: 當前代碼內容
            version: 當前版本號
            context: 額外的上下文資訊
        
        返回:
            issue_data: Issue 資訊（包含 URL 和編號）
        """
        
        # 構建 Issue 標題
        title = f"🧬 YK Evolution Request v{version} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # 構建 Issue 內容
        body = self._build_issue_body(code_content, version, context)
        
        # Issue 資料
        issue_data = {
            "title": title,
            "body": body,
            "labels": ["evolution-request", "automated"],
            "assignees": ["Nebula"]  # 指派給 Nebula（如果可以的話）
        }
        
        print(f"📋 創建進化請求 Issue...")
        print(f"標題: {title}")
        print(f"倉庫: {self.repo_full_name}")
        
        return issue_data
    
    def _build_issue_body(self, code_content, version, context):
        """構建 Issue 內容（使用 Nebula 能理解的格式）"""
        
        body = f"""## 🤖 自動進化請求

@Nebula 請幫我分析以下代碼並提出改進建議。

---

### 📊 當前版本資訊
- **版本**: v{version}
- **時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **系統**: YK Evolution System

---

### 📝 當前代碼

```python
{code_content}
```

---

### 🎯 請求事項

請 @Nebula 執行以下分析：

1. **代碼審查**
   - 檢查語法和邏輯錯誤
   - 識別潛在的性能問題
   - 檢查安全性問題

2. **改進建議**
   - 提出具體的優化方案
   - 建議新功能或增強
   - 推薦最佳實踐

3. **測試驗證**
   - 執行基本功能測試
   - 驗證改進的可行性
   - 提供測試結果

4. **改進代碼**
   - 提供完整的改進後代碼
   - 標註主要變更點
   - 解釋改進理由

---

### 💡 額外上下文

{context if context else "無額外資訊"}

---

### ✅ 完成標準

請在回應中包含：
- [ ] 問題分析報告
- [ ] 具體改進建議
- [ ] 完整的改進後代碼
- [ ] 測試結果和驗證
- [ ] 版本更新建議

---

**此 Issue 由 YK Evolution System 自動創建**
"""
        
        return body
    
    def wait_for_nebula_response(self, issue_number, timeout=300, check_interval=10):
        """
        等待 Nebula 回應
        
        參數:
            issue_number: Issue 編號
            timeout: 超時時間（秒）
            check_interval: 檢查間隔（秒）
        
        返回:
            response: Nebula 的回應內容
        """
        
        print(f"⏳ 等待 Nebula 回應 (Issue #{issue_number})...")
        print(f"   最長等待 {timeout} 秒，每 {check_interval} 秒檢查一次")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            print(f"   檢查中... ({int(time.time() - start_time)}s)")
            
            # 這裡需要實際的 GitHub API 調用
            # 暫時返回模擬數據
            # TODO: 實作實際的 GitHub API 查詢
            
            time.sleep(check_interval)
        
        print("⚠️  等待超時，請手動檢查 Issue")
        return None
    
    def parse_nebula_response(self, response_text):
        """
        解析 Nebula 的回應
        
        參數:
            response_text: Nebula 的回應文本
        
        返回:
            parsed_data: 解析後的數據
        """
        
        parsed = {
            "analysis": "",
            "suggestions": [],
            "improved_code": "",
            "test_results": "",
            "should_apply": False
        }
        
        # 解析邏輯
        # TODO: 實作實際的解析邏輯
        
        return parsed
    
    def create_issue_via_github_cli(self, issue_data):
        """
        使用 GitHub CLI 創建 Issue
        
        需要安裝: gh cli (https://cli.github.com/)
        需要認證: gh auth login
        """
        
        import subprocess
        
        try:
            # 構建 gh 命令
            cmd = [
                "gh", "issue", "create",
                "--repo", self.repo_full_name,
                "--title", issue_data["title"],
                "--body", issue_data["body"],
            ]
            
            # 添加標籤
            if "labels" in issue_data:
                for label in issue_data["labels"]:
                    cmd.extend(["--label", label])
            
            # 執行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # 解析輸出（通常是 Issue URL）
            issue_url = result.stdout.strip()
            issue_number = issue_url.split('/')[-1]
            
            print(f"✅ Issue 創建成功！")
            print(f"   URL: {issue_url}")
            print(f"   編號: #{issue_number}")
            
            return {
                "success": True,
                "url": issue_url,
                "number": issue_number
            }
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 創建 Issue 失敗: {e}")
            print(f"   錯誤輸出: {e.stderr}")
            return {
                "success": False,
                "error": str(e)
            }
        except FileNotFoundError:
            print("❌ GitHub CLI (gh) 未安裝")
            print("   請安裝: https://cli.github.com/")
            print("   或使用手動模式")
            return {
                "success": False,
                "error": "gh cli not found"
            }
    
    def create_issue_manual_mode(self, issue_data):
        """
        手動模式：生成 Issue 內容，讓用戶手動創建
        """
        
        print("\n" + "="*60)
        print("📋 手動創建 Issue 模式")
        print("="*60)
        
        print(f"\n請前往: https://github.com/{self.repo_full_name}/issues/new")
        print("\n然後複製以下內容：")
        
        print("\n--- 標題 ---")
        print(issue_data["title"])
        
        print("\n--- 內容 ---")
        print(issue_data["body"])
        
        print("\n--- 標籤 ---")
        if "labels" in issue_data:
            print(", ".join(issue_data["labels"]))
        
        print("\n" + "="*60)
        
        # 將內容保存到檔案
        output_file = Path("nebula_issue_template.md")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {issue_data['title']}\n\n")
            f.write(issue_data['body'])
        
        print(f"\n✅ 內容已保存到: {output_file}")
        print("   您可以直接複製該檔案內容到 GitHub")
        
        return {
            "success": True,
            "mode": "manual",
            "file": str(output_file)
        }


# 使用範例
if __name__ == "__main__":
    
    # 初始化整合
    integration = NebulaIntegration(
        repo_owner="kz9987265",
        repo_name="YK-evolution-system"
    )
    
    # 讀取當前代碼
    code_file = Path(__file__).parent / "simple_evolution.py"
    if code_file.exists():
        with open(code_file, 'r', encoding='utf-8') as f:
            current_code = f.read()
    else:
        current_code = "# 代碼檔案不存在"
    
    # 創建進化請求
    issue_data = integration.create_evolution_request(
        code_content=current_code,
        version="1.0.0",
        context="首次測試 Nebula 整合"
    )
    
    # 方式 1：嘗試使用 GitHub CLI
    print("\n🔧 方式 1: 使用 GitHub CLI")
    result = integration.create_issue_via_github_cli(issue_data)
    
    if not result["success"]:
        # 方式 2：手動模式
        print("\n🔧 方式 2: 手動模式")
        integration.create_issue_manual_mode(issue_data)
    
    print("\n✅ 完成！")