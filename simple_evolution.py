"""
🧬 簡化版自我進化系統 - 單一檔案版本
功能：連接 LLM，分析自己的代碼，自動改進並驗證
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path

# ============================================
# 配置區
# ============================================

# 在這裡設定您的 Gemini API 金鑰
GEMINI_API_KEY = "your_gemini_api_key_here"

# 或者從環境變數讀取
if os.getenv("GEMINI_API_KEY"):
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 進化設定
EVOLUTION_INTERVAL = 300  # 5分鐘自動進化一次（秒）
MAX_HISTORY = 10  # 保留最多 10 個歷史版本

# ============================================
# LLM 連接模組
# ============================================

class SimpleLLM:
    """簡化的 LLM 接口"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.model = None
        self._initialize()
    
    def _initialize(self):
        """初始化 Gemini"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            print("✅ Gemini LLM 已連接")
        except ImportError:
            print("❌ 請先安裝: pip install google-generativeai")
            sys.exit(1)
        except Exception as e:
            print(f"❌ LLM 初始化失敗: {e}")
            sys.exit(1)
    
    def generate(self, prompt):
        """生成回應"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"❌ 生成失敗: {e}")
            return None


# ============================================
# 自我進化引擎
# ============================================

class SelfEvolution:
    """自我進化核心"""
    
    def __init__(self, llm):
        self.llm = llm
        self.script_path = Path(__file__).resolve()
        self.history_dir = self.script_path.parent / "evolution_history"
        self.history_dir.mkdir(exist_ok=True)
        self.generation_file = self.history_dir / "generation.txt"
        self.current_generation = self._load_generation()
    
    def _load_generation(self):
        """讀取當前世代"""
        if self.generation_file.exists():
            return int(self.generation_file.read_text().strip())
        return 0
    
    def _save_generation(self, gen):
        """保存世代數"""
        self.generation_file.write_text(str(gen))
    
    def _backup_current(self):
        """備份當前版本"""
        timestamp = int(time.time())
        backup_name = f"gen_{self.current_generation:04d}_{timestamp}.py"
        backup_path = self.history_dir / backup_name
        backup_path.write_text(self.script_path.read_text(encoding='utf-8'), encoding='utf-8')
        print(f"💾 已備份當前版本: {backup_name}")
        
        # 清理舊備份
        backups = sorted(self.history_dir.glob("gen_*.py"))
        if len(backups) > MAX_HISTORY:
            for old_backup in backups[:-MAX_HISTORY]:
                old_backup.unlink()
                print(f"🗑️  已刪除舊備份: {old_backup.name}")
    
    def _read_source(self):
        """讀取自己的源碼"""
        return self.script_path.read_text(encoding='utf-8')
    
    def _analyze_code(self, source_code):
        """使用 LLM 分析代碼"""
        prompt = f"""
你是一個專業的 Python 代碼分析師。請分析以下代碼，找出問題和改進空間。

請以 JSON 格式回應（只回傳 JSON，不要其他文字）：
{{
    "issues": ["問題1", "問題2", ...],
    "suggestions": ["建議1", "建議2", ...],
    "priority": "high/medium/low"
}}

代碼：
```python
{source_code}
```
"""
        
        response = self.llm.generate(prompt)
        if not response:
            return None
        
        # 提取 JSON
        try:
            # 嘗試找到 JSON 區塊
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception as e:
            print(f"⚠️  解析分析結果失敗: {e}")
            return None
    
    def _generate_improvement(self, source_code, analysis):
        """生成改進版本"""
        prompt = f"""
基於以下分析結果，改進這段 Python 代碼。

分析結果：
{json.dumps(analysis, ensure_ascii=False, indent=2)}

原始代碼：
```python
{source_code}
```

請直接回傳完整的改進後代碼，不要包含任何解釋文字或 markdown 標記。
只回傳純 Python 代碼。
"""
        
        response = self.llm.generate(prompt)
        if not response:
            return None
        
        # 清理回應，移除可能的 markdown 標記
        code = response.strip()
        if code.startswith('```python'):
            code = code[9:]
        if code.startswith('```'):
            code = code[3:]
        if code.endswith('```'):
            code = code[:-3]
        
        return code.strip()
    
    def _test_code(self, code):
        """測試代碼是否可執行"""
        try:
            compile(code, '<string>', 'exec')
            return True
        except SyntaxError as e:
            print(f"❌ 語法錯誤: {e}")
            return False
    
    def evolve(self):
        """執行一次進化"""
        print("\n" + "="*60)
        print(f"🧬 開始進化 - 第 {self.current_generation} → {self.current_generation + 1} 代")
        print("="*60 + "\n")
        
        # 1. 讀取源碼
        print("📖 讀取源碼...")
        source_code = self._read_source()
        print(f"✅ 源碼大小: {len(source_code)} 字符\n")
        
        # 2. 分析代碼
        print("🔍 分析代碼...")
        analysis = self._analyze_code(source_code)
        if not analysis:
            print("❌ 分析失敗，跳過本次進化")
            return False
        
        print(f"✅ 發現 {len(analysis.get('issues', []))} 個問題")
        print(f"✅ 收到 {len(analysis.get('suggestions', []))} 個建議")
        print(f"✅ 優先級: {analysis.get('priority', 'unknown')}\n")
        
        # 3. 生成改進版本
        print("💡 生成改進版本...")
        improved_code = self._generate_improvement(source_code, analysis)
        if not improved_code:
            print("❌ 生成失敗，跳過本次進化")
            return False
        
        print(f"✅ 改進版本大小: {len(improved_code)} 字符\n")
        
        # 4. 測試新代碼
        print("🧪 測試新代碼...")
        if not self._test_code(improved_code):
            print("❌ 測試失敗，放棄本次進化")
            return False
        
        print("✅ 測試通過\n")
        
        # 5. 應用改進
        print("🚀 應用改進...")
        self._backup_current()
        self.script_path.write_text(improved_code, encoding='utf-8')
        self.current_generation += 1
        self._save_generation(self.current_generation)
        print(f"✅ 已進化到第 {self.current_generation} 代\n")
        
        print("🎉 進化成功！")
        print(f"📊 當前世代: {self.current_generation}\n")
        
        return True


# ============================================
# 主程式
# ============================================

def main():
    """主函數"""
    print("="*60)
    print("🧬 簡化版自我進化系統")
    print("="*60 + "\n")
    
    # 檢查 API 金鑰
    if GEMINI_API_KEY == "your_gemini_api_key_here":
        print("❌ 請先設定 GEMINI_API_KEY")
        print("\n方式 1: 直接修改代碼第 17 行")
        print("方式 2: 設定環境變數 GEMINI_API_KEY\n")
        sys.exit(1)
    
    # 初始化
    print("🔌 連接 LLM...")
    llm = SimpleLLM(GEMINI_API_KEY)
    
    print("\n🧬 初始化進化引擎...")
    evolution = SelfEvolution(llm)
    print(f"✅ 當前世代: {evolution.current_generation}")
    
    print(f"\n⏰ 自動進化間隔: {EVOLUTION_INTERVAL} 秒")
    print("🎯 按 Ctrl+C 停止\n")
    
    # 自動進化循環
    try:
        while True:
            success = evolution.evolve()
            
            if success:
                print("⚠️  重啟系統以應用更新...")
                print(f"⏰ {EVOLUTION_INTERVAL} 秒後重啟\n")
                time.sleep(EVOLUTION_INTERVAL)
                
                # 重啟自己
                print("🔄 重啟中...\n")
                os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                print(f"⏰ 等待 {EVOLUTION_INTERVAL} 秒後重試...\n")
                time.sleep(EVOLUTION_INTERVAL)
    
    except KeyboardInterrupt:
        print("\n\n👋 已停止進化系統")
        print(f"📊 最終世代: {evolution.current_generation}")
        sys.exit(0)


if __name__ == "__main__":
    main()