# YK 自我進化系統 🧬

完全自主的 AI 進化系統，結合本地 Qwen3 模型和 Gemini API，實現代碼自我改進和持續學習。

## ✨ 核心功能

### 🤖 混合 AI 推理
- **本地模型**: Qwen3-4B-Instruct (快速、私密)
- **雲端增強**: Gemini 2.0 Flash (強大、創新)
- **智能路由**: 自動選擇最佳推理引擎

### 🧠 三層記憶系統
- **即時記憶**: 當前對話上下文 (RAM)
- **短期記憶**: 近期經驗學習 (30天保留)
- **長期記憶**: 永久知識庫 (分類存儲)

### 🧪 沙盒測試引擎
- **安全執行**: 代碼安全驗證，防止危險操作
- **功能測試**: 自動化測試用例執行
- **性能基準**: 多輪性能測試和比較

### 🧬 自我進化引擎
- **代碼分析**: AI 驅動的代碼質量評估
- **智能改進**: 自動生成優化代碼
- **版本比較**: 功能和性能全面對比
- **自動整合**: 通過測試後自動應用改進
- **💤 閒置進化**: 系統閒置 3 分鐘自動觸發進化（可配置）

---

## 📦 安裝部署

### 1. 環境準備

```bash
# 進入 YK 目錄
cd C:/Users/YourUser/YK

# 激活虛擬環境
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安裝依賴
cd core
pip install -r requirements.txt
```

### 2. 配置 Gemini API

編輯 `YK/.env.local`：

```bash
GEMINI_API_KEY=your_api_key_here
```

獲取 API Key: https://aistudio.google.com/app/apikey

### 3. 準備 LLM 模型

將 `Qwen3-4B-Instruct-2507-Q8_0.gguf` 放入 `YK/LLM/` 目錄

---

## 🚀 使用方式

### 模式 1: 互動模式（推薦初次使用）

```bash
python main.py
```

**💤 閒置進化**: 互動模式下，系統閒置 3 分鐘會自動觸發進化，任何命令輸入會重置計時器。

可用命令：
- `evolve [module_name]` - 進化指定模塊（或全部）
- `status` - 顯示系統狀態
- `stats` - 顯示進化統計
- `memory <query>` - 搜索記憶
- `config <key> <value>` - 修改配置
- `auto` - 啟動自主進化
- `exit` - 退出

### 模式 2: 單次進化

```bash
# 進化所有模塊
python main.py --evolve

# 進化特定模塊
python main.py --evolve hybrid_ai.py
```

### 模式 3: 完全自主模式

```bash
python main.py --auto
```

系統將：
- 每 24 小時自動進化一次
- **💤 閒置 3 分鐘後自動進化**
- 自動整合記憶
- 自動應用通過測試的改進
- 持續運行直到手動停止 (Ctrl+C)

---

## ⚙️ 配置選項

在互動模式中使用 `config` 命令修改：

```bash
YK> config auto_evolution_interval_hours 12  # 改為每 12 小時
YK> config auto_apply_improvements false      # 關閉自動應用
YK> config evolution_on_startup true          # 啟動時立即進化
YK> config idle_evolution_minutes 5           # 改為閒置 5 分鐘進化
YK> config enable_idle_evolution false        # 關閉閒置進化
```

**可配置項目**：
- `auto_evolution_interval_hours` - 定時進化間隔（小時）
- `auto_apply_improvements` - 自動應用改進（true/false）
- `min_quality_threshold` - 最低質量閾值（0.0-1.0）
- `evolution_on_startup` - 啟動時立即進化（true/false）
- `idle_evolution_minutes` - 閒置多久觸發進化（分鐘）
- `enable_idle_evolution` - 啟用閒置進化（true/false）

或直接編輯 `main.py` 中的 `self.config` 字典。

---

## 📂 目錄結構

```
YK/
├── core/                       # 核心代碼（會被自動進化）
│   ├── hybrid_ai.py           # 混合 AI 系統
│   ├── memory_manager.py      # 記憶管理
│   ├── sandbox_executor.py    # 沙盒執行
│   ├── evolution_engine.py    # 進化引擎
│   ├── main.py                # 主控制器
│   └── requirements.txt       # 依賴列表
│
├── memory/                     # 記憶存儲
│   ├── instant_memory/        # （運行時）
│   ├── short_term_memory/     # 短期記憶 JSON
│   └── long_term_memory/      # 長期記憶 JSON
│
├── Sandbox/                    # 進化沙盒
│   ├── test_modules/          # 測試模塊
│   ├── benchmarks/            # 性能基準
│   └── evolution_logs/        # 進化日誌
│
├── LLM/                        # 本地模型
│   └── Qwen3-4B-Instruct-2507-Q8_0.gguf
│
├── venv/                       # 虛擬環境
└── .env.local                  # API 配置
```

---

## 🔍 進化流程

```
1. 代碼分析
   ↓
   - AI 識別問題和改進機會
   - 計算代碼質量評分
   
2. 生成改進
   ↓
   - 基於分析結果生成優化代碼
   - 保持功能完全一致
   
3. 沙盒測試
   ↓
   - 運行功能測試用例
   - 執行性能基準測試
   - 版本對比評估
   
4. 決策整合
   ↓
   - 改進 > 0: 自動應用 ✅
   - 改進 ≤ 0: 保留原版本 ❌
   - 備份原始文件
   
5. 記憶學習
   ↓
   - 記錄成功/失敗經驗
   - 整合到長期記憶
```

---

## 📊 監控和日誌

### 系統狀態

```bash
YK> status
```

顯示：
- 運行狀態
- 進化次數
- 記憶統計
- AI 使用情況

### 進化日誌

位置: `YK/Sandbox/evolution_logs/evolution_YYYYMMDD.jsonl`

每次進化都會記錄：
- 時間戳
- 模塊名稱
- 改進度
- 是否接受

### 備份文件

每次成功進化都會創建 `.py.backup` 備份文件，如需回滾：

```bash
cp hybrid_ai.py.backup hybrid_ai.py
```

---

## 🛡️ 安全機制

### 代碼安全驗證
- 禁止危險導入 (os, subprocess, sys)
- 禁止危險函數 (eval, exec, compile)
- 語法檢查和 AST 分析

### 沙盒隔離
- 所有新代碼先在沙盒中測試
- 限制執行時間（防止無限循環）
- 受限的內建函數集

### 自動備份
- 應用改進前自動備份
- 保留進化歷史記錄
- 支持手動回滾

---

## 🔧 故障排除

### 問題 1: llama-cpp-python 安裝失敗

**解決方案**:
```bash
# Windows (需要 Visual Studio Build Tools)
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

# 或使用預編譯 wheel
pip install llama-cpp-python --prefer-binary
```

### 問題 2: 找不到 GGUF 模型

**檢查**:
- 確認模型文件在 `YK/LLM/` 目錄
- 文件名包含 `.gguf` 擴展名
- 文件名包含 `qwen3`（優先選擇）

### 問題 3: Gemini API 錯誤

**檢查**:
- `.env.local` 中 API Key 格式正確
- API Key 有效且未過期
- 網絡連接正常

### 問題 4: 進化失敗率高

**調整配置**:
```bash
YK> config auto_apply_improvements false  # 先手動審查
YK> config min_quality_threshold 0.5      # 降低質量要求
```

---

## 📈 性能優化建議

### GPU 加速（如果有 NVIDIA 顯卡）

安裝 CUDA 版本的 llama-cpp-python:
```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

在 `hybrid_ai.py` 中已配置 `n_gpu_layers=-1`（使用所有 GPU 層）

### 記憶管理

定期清理過期記憶：
```bash
YK> memory cleanup  # （可在未來版本添加此命令）
```

### 日誌清理

定期清理舊日誌：
```bash
# 刪除 30 天前的日誌
cd YK/Sandbox/evolution_logs
del evolution_202401*.jsonl  # Windows
```

---

## 🎯 最佳實踐

### 1. 漸進式進化
- 初次使用先手動測試幾個模塊
- 觀察改進質量後再啟用自動模式

### 2. 定期審查
- 每週檢查進化日誌
- 審查重要模塊的改進

### 3. 備份管理
- 定期備份整個 YK 目錄
- 保留關鍵版本的快照

### 4. 記憶整合
- 定期運行 `memory consolidate`
- 保持知識庫乾淨有序

---

## 🤝 貢獻和擴展

### 添加新模塊

將新的 `.py` 文件放入 `core/` 目錄，系統會自動納入進化範圍。

### 自定義進化策略

修改 `evolution_engine.py` 中的：
- `analyze_code()` - 代碼分析邏輯
- `generate_improved_code()` - 改進生成提示
- `evolve_module()` - 進化流程

### 擴展記憶系統

在 `memory_manager.py` 中添加新的記憶分類或檢索方法。

---

## 📄 授權

本項目為個人學習項目，僅供參考。

---

## 🙏 致謝

- **Qwen Team** - 開源 Qwen3 模型
- **Google** - Gemini API
- **llama.cpp** - 高效 LLM 推理框架

---

**享受 AI 自我進化的樂趣！** 🚀✨
