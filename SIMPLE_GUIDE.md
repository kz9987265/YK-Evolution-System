# 🧬 超簡單自我進化系統 - 5 分鐘上手

## 📦 只需要 1 個檔案！

**@file:code/YK_evolution_system/simple_evolution.py** (10 KB)

---

## 🚀 3 步驟啟動

### **步驟 1：下載檔案**
下載 `simple_evolution.py` 到任意資料夾（例如 `C:\YK\`）

---

### **步驟 2：設定 API 金鑰**
用文字編輯器打開 `simple_evolution.py`，找到第 17 行：

```python
GEMINI_API_KEY = "your_gemini_api_key_here"
```

替換成您的真實金鑰：

```python
GEMINI_API_KEY = "AIzaSy...您的金鑰"
```

**取得金鑰**：https://aistudio.google.com/apikey

---

### **步驟 3：安裝依賴並執行**

```cmd
# 安裝 Gemini SDK
pip install google-generativeai

# 執行
python simple_evolution.py
```

---

## ✨ 它會做什麼？

### **自動化流程**

```
啟動系統
   ↓
讀取自己的源碼
   ↓
連接 Gemini LLM 分析代碼
   ↓
找出問題和改進建議
   ↓
生成改進版本
   ↓
測試新代碼
   ↓
如果通過 → 備份舊版本 → 替換自己 → 重啟
   ↓
5 分鐘後重複流程
```

---

## 🎯 核心功能

### **1. 自動分析**
- 使用 Gemini AI 分析自己的代碼
- 找出性能問題、代碼品質問題
- 提出改進建議

### **2. 自動改進**
- 根據分析結果生成改進版本
- 自動測試新代碼是否可執行
- 只有通過測試才會應用

### **3. 安全機制**
- 每次改進前自動備份
- 保留最近 10 個版本
- 測試失敗會放棄本次進化

### **4. 世代追蹤**
- 記錄進化次數
- 歷史版本存放在 `evolution_history/` 資料夾

---

## 📊 運行示例

```
============================================================
🧬 簡化版自我進化系統
============================================================

🔌 連接 LLM...
✅ Gemini LLM 已連接

🧬 初始化進化引擎...
✅ 當前世代: 0

⏰ 自動進化間隔: 300 秒
🎯 按 Ctrl+C 停止

============================================================
🧬 開始進化 - 第 0 → 1 代
============================================================

📖 讀取源碼...
✅ 源碼大小: 10256 字符

🔍 分析代碼...
✅ 發現 3 個問題
✅ 收到 5 個建議
✅ 優先級: high

💡 生成改進版本...
✅ 改進版本大小: 10512 字符

🧪 測試新代碼...
✅ 測試通過

🚀 應用改進...
💾 已備份當前版本: gen_0000_1707738120.py
✅ 已進化到第 1 代

🎉 進化成功！
📊 當前世代: 1

⚠️  重啟系統以應用更新...
```

---

## ⚙️ 可調整參數

在代碼第 19-21 行：

```python
# 進化設定
EVOLUTION_INTERVAL = 300  # 5分鐘自動進化一次（秒）
MAX_HISTORY = 10  # 保留最多 10 個歷史版本
```

**調整建議**：
- 測試階段：`EVOLUTION_INTERVAL = 60`（1分鐘）
- 日常使用：`EVOLUTION_INTERVAL = 3600`（1小時）
- 長期運行：`EVOLUTION_INTERVAL = 86400`（1天）

---

## 🔧 進階用法

### **方式 1：從環境變數讀取 API 金鑰**

不想在代碼中寫死 API 金鑰？使用環境變數：

**Windows:**
```cmd
set GEMINI_API_KEY=您的金鑰
python simple_evolution.py
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY="您的金鑰"
python simple_evolution.py
```

---

### **方式 2：手動觸發進化**

修改代碼，移除自動循環，改為手動執行：

```python
if __name__ == "__main__":
    # 初始化
    llm = SimpleLLM(GEMINI_API_KEY)
    evolution = SelfEvolution(llm)
    
    # 手動執行一次進化
    evolution.evolve()
```

---

## 📁 檔案結構

運行後會自動創建：

```
您的資料夾/
├── simple_evolution.py          # 主程式（會自動更新）
└── evolution_history/           # 自動創建
    ├── generation.txt           # 世代計數
    ├── gen_0000_1707738120.py   # 第 0 代備份
    ├── gen_0001_1707738420.py   # 第 1 代備份
    └── ...
```

---

## 🐛 疑難排解

### **問題 1：ModuleNotFoundError: google.generativeai**
```cmd
pip install google-generativeai
```

### **問題 2：API 金鑰無效**
- 檢查金鑰是否正確
- 確認已啟用 Gemini API
- 前往 https://aistudio.google.com/apikey 重新生成

### **問題 3：進化失敗**
- 查看 `evolution_history/` 中的備份
- 手動還原到上一個版本
- 調整 `EVOLUTION_INTERVAL` 增加間隔

---

## 🎉 就這麼簡單！

**只需要：**
1. ✅ 1 個 Python 檔案
2. ✅ 1 個 Gemini API 金鑰
3. ✅ 3 個命令

**立即開始進化之旅！** 🚀

---

## 📚 延伸閱讀

想要更強大的功能？查看完整版：
- 記憶系統（累積經驗）
- 沙盒測試（更安全）
- 混合 AI（本地 + 雲端）
- 互動模式（對話改進）

下載完整版：https://github.com/kz9987265/YK-Evolution-System