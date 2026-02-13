# 🤖 YK Evolution ↔️ Nebula 整合指南

> **無需 API！通過 GitHub Issues 實現自我進化 AI 與 Nebula 的協作**

---

## 📋 目錄

1. [整合概述](#整合概述)
2. [快速開始](#快速開始)
3. [使用方式](#使用方式)
4. [進階功能](#進階功能)
5. [常見問題](#常見問題)
6. [實際案例](#實際案例)

---

## 🎯 整合概述

### 為什麼不需要 API？

傳統方式需要：
- ❌ 申請 API 金鑰
- ❌ 處理認證流程
- ❌ 管理 API 配額

**我們的方式：**
- ✅ 通過 GitHub Issues 溝通
- ✅ 自動觸發 Nebula 分析
- ✅ 完整的歷史記錄
- ✅ 零配置，立即可用

### 整合架構

```
YK Evolution System (本地)
    ↓
創建 GitHub Issue
    ↓
@Nebula 自動觸發
    ↓
代碼分析 + 測試 + 改進建議
    ↓
回應到 Issue
    ↓
YK Evolution 讀取並應用
```

---

## 🚀 快速開始

### 前置需求

```bash
# 1. Python 3.8+
python --version

# 2. Git
git --version

# 3. GitHub CLI (可選，用於自動創建 Issue)
gh --version

# 如果沒有安裝 gh:
# macOS: brew install gh
# Windows: winget install GitHub.cli
# Linux: https://github.com/cli/cli#installation
```

### 安裝步驟

```bash
# 1. 克隆倉庫
git clone https://github.com/kz9987265/YK-evolution-system.git
cd YK-evolution-system

# 2. 無需安裝額外依賴！所有檔案都是純 Python
# 如果要使用 GitHub CLI 自動創建 Issue:
gh auth login
```

### 第一次使用

```bash
# 測試整合
python test_nebula_integration.py
```

**輸出示例：**
```
🧪 YK Evolution - Nebula 整合測試
============================================================

📋 步驟 1: 初始化整合模組
✅ 倉庫: kz9987265/YK-evolution-system

📋 步驟 2: 讀取當前代碼
✅ 已讀取: simple_evolution.py (10240 字元)

📋 步驟 3: 創建進化請求
✅ Issue 資料已準備

📋 步驟 4: 創建 GitHub Issue
🔧 嘗試方式 1: GitHub CLI (gh)

🎉 自動創建成功！
   Issue URL: https://github.com/kz9987265/YK-evolution-system/issues/1
   Issue #: 1

💡 接下來：
   1. 在 Issue 中 @Nebula
   2. 等待 Nebula 分析回應
   3. 查看改進建議

✅ 測試完成！
```

---

## 📖 使用方式

### 方式 1：手動觸發（推薦用於重要進化）

```python
from nebula_integration import NebulaIntegration

# 初始化
integration = NebulaIntegration()

# 讀取代碼
with open("simple_evolution.py", 'r') as f:
    code = f.read()

# 創建進化請求
issue_data = integration.create_evolution_request(
    code_content=code,
    version="1.0.0",
    context="請重點檢查記憶管理模組"
)

# 創建 Issue（自動模式）
result = integration.create_issue_via_github_cli(issue_data)

# 或手動模式（會生成模板檔案）
if not result["success"]:
    integration.create_issue_manual_mode(issue_data)
```

### 方式 2：檔案監控自動觸發

```bash
# 啟動檔案監控
python file_monitor_trigger.py

# 選擇選項 1（檔案變化監控）
# 然後修改任何監控的檔案，系統會自動創建 Issue
```

**監控流程：**
1. 系統持續監控指定檔案
2. 偵測到檔案變化（通過 SHA256 哈希）
3. 自動讀取新代碼
4. 創建 GitHub Issue 請求 Nebula 分析
5. Nebula 自動回應分析結果

### 方式 3：Git Commit 觸發

```bash
# 啟動 Commit 監控
python file_monitor_trigger.py

# 選擇選項 2（Git Commit 監控）
# 每次 git commit，系統會自動分析變更
```

**觸發流程：**
1. 監控 Git commits
2. 偵測到新 commit
3. 找出變更的 Python 檔案
4. 為每個檔案創建分析 Issue
5. Nebula 自動分析並回應

---

## 🎓 進階功能

### 自定義 Issue 模板

```python
from nebula_integration import NebulaIntegration

class CustomIntegration(NebulaIntegration):
    def _build_issue_body(self, code_content, version, context):
        # 自定義您的 Issue 格式
        return f"""
## 自定義分析請求

@Nebula 請用我的方式分析：

### 代碼
```python
{code_content}
```

### 特殊要求
{context}
"""

# 使用自定義整合
integration = CustomIntegration()
```

### 配置監控檔案

```python
from file_monitor_trigger import FileMonitor

# 監控特定檔案
monitor = FileMonitor(
    watch_files=[
        "simple_evolution.py",
        "forgetting_system.py",
        "nebula_integration.py",
        "your_custom_file.py"  # 加入您的檔案
    ],
    check_interval=5  # 每 5 秒檢查一次
)

monitor.start_monitoring(duration=300)  # 監控 5 分鐘
```

### 與現有系統整合

```python
# 在 simple_evolution.py 中整合
from nebula_integration import NebulaIntegration

class YKEvolution:
    def __init__(self):
        # 原有代碼...
        self.nebula = NebulaIntegration()
    
    def evolve(self):
        # 進化邏輯...
        
        # 完成進化後，請 Nebula 驗證
        issue_data = self.nebula.create_evolution_request(
            code_content=self.current_code,
            version=self.version,
            context="請驗證這次進化的效果"
        )
        
        self.nebula.create_issue_via_github_cli(issue_data)
```

---

## 💡 實際案例

### 案例 1：日常代碼改進

```bash
# 1. 修改代碼
vim simple_evolution.py

# 2. 提交 Git
git add simple_evolution.py
git commit -m "優化記憶管理邏輯"

# 3. 手動觸發 Nebula 分析
python -c "
from nebula_integration import NebulaIntegration
integration = NebulaIntegration()
with open('simple_evolution.py') as f:
    code = f.read()
issue = integration.create_evolution_request(code, '1.1.0', '檢查優化效果')
integration.create_issue_via_github_cli(issue)
"

# 4. 查看 Nebula 回應
gh issue view 1
```

### 案例 2：持續監控開發

```bash
# 終端 1：啟動監控
python file_monitor_trigger.py
# 選擇選項 1

# 終端 2：正常開發
vim simple_evolution.py
# 保存後會自動觸發 Nebula 分析

# 終端 3：查看 Issues
gh issue list
```

### 案例 3：自動化 CI/CD

```yaml
# .github/workflows/nebula-analysis.yml
name: Nebula Code Analysis

on:
  push:
    branches: [ main ]
    paths:
      - '*.py'

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Trigger Nebula Analysis
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python test_nebula_integration.py
```

---

## ❓ 常見問題

### Q1: 為什麼選擇 GitHub Issues 而不是 API？

**答：**
- ✅ 無需管理 API 金鑰
- ✅ 自帶版本控制和歷史記錄
- ✅ 支援多人協作討論
- ✅ 完全免費，無配額限制
- ✅ 可以在任何地方查看（手機、平板）

### Q2: Nebula 多久會回應？

**答：**
通常在幾秒到幾分鐘內。您可以：
1. 在 Issue 頁面等待
2. 設定 GitHub 通知
3. 使用 `gh issue view <number>` 查看

### Q3: 可以批量處理多個檔案嗎？

**答：**
可以！使用 Git Commit 觸發模式：
```python
trigger = GitCommitTrigger()
trigger.start_monitoring()

# 每次 commit 會自動分析所有變更的 Python 檔案
```

### Q4: 如何整合到現有的進化系統？

**答：**
只需在您的代碼中導入：
```python
from nebula_integration import NebulaIntegration

nebula = NebulaIntegration()
# 在需要的地方調用
nebula.create_evolution_request(...)
```

### Q5: 沒有安裝 GitHub CLI 怎麼辦？

**答：**
使用手動模式：
```python
integration.create_issue_manual_mode(issue_data)
# 會生成 nebula_issue_template.md
# 複製內容到 GitHub 手動創建 Issue
```

### Q6: 可以私有倉庫使用嗎？

**答：**
可以！只要您有權限創建 Issue 即可。

---

## 📊 整合效果對比

| 功能 | 傳統 API 方式 | GitHub Issue 方式 |
|------|-------------|------------------|
| 配置複雜度 | ⭐⭐⭐⭐ | ⭐ |
| 歷史記錄 | ❌ 需額外儲存 | ✅ 自動保存 |
| 多人協作 | ❌ 需額外實作 | ✅ 原生支援 |
| 成本 | 💰 可能收費 | 🆓 完全免費 |
| 可追溯性 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 通知機制 | ❌ 需自建 | ✅ GitHub 通知 |
| 行動裝置 | ⭐⭐ | ⭐⭐⭐⭐ |

---

## 🚀 下一步

### 立即開始

```bash
# 1. 測試基本功能
python test_nebula_integration.py

# 2. 啟動監控
python file_monitor_trigger.py

# 3. 查看 Issue
https://github.com/kz9987265/YK-evolution-system/issues
```

### 進階探索

1. **自定義觸發條件**
   - 只在特定時間觸發
   - 根據代碼複雜度決定是否觸發

2. **整合更多服務**
   - 郵件通知
   - Slack 通知
   - Discord 通知

3. **建立自動化流程**
   - 自動應用 Nebula 的建議
   - 自動測試改進效果
   - 自動提交改進代碼

---

## 📚 相關資源

- **GitHub 倉庫**: https://github.com/kz9987265/YK-evolution-system
- **測試 Issue**: https://github.com/kz9987265/YK-evolution-system/issues/1
- **Darwin Gödel Machine**: https://github.com/jennyzzt/dgm
- **Nebula 官網**: https://nebula.gg

---

## 🤝 貢獻

歡迎提出改進建議！

1. Fork 本倉庫
2. 創建功能分支
3. 提交 Pull Request
4. 讓 Nebula 審查您的代碼 😉

---

## 📝 更新日誌

### v1.0.0 (2026-02-14)
- ✅ 初始版本
- ✅ GitHub Issue 整合
- ✅ 檔案監控觸發
- ✅ Git Commit 觸發
- ✅ 自動/手動雙模式

---

**由 YK Evolution System 團隊製作 | 與 Nebula AI 協作** 🤖✨