"""
自我進化引擎
AI 驅動的代碼生成、評估和自我改進系統
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import difflib


class EvolutionEngine:
    """自我進化引擎 - 核心進化邏輯"""
    
    def __init__(self, hybrid_ai, memory_manager, sandbox_executor, core_path: Path):
        """
        Args:
            hybrid_ai: HybridAI 實例
            memory_manager: MemoryManager 實例
            sandbox_executor: SandboxExecutor 實例
            core_path: core 資料夾路徑
        """
        self.ai = hybrid_ai
        self.memory = memory_manager
        self.sandbox = sandbox_executor
        self.core_path = core_path
        
        # 進化統計
        self.evolution_stats = {
            "total_attempts": 0,
            "successful_evolutions": 0,
            "failed_evolutions": 0,
            "code_improvements": 0,
            "performance_improvements": 0,
        }
        
        print("✅ 進化引擎初始化完成")
    
    def analyze_code(self, code: str, context: str = "") -> Dict[str, Any]:
        """
        分析代碼並識別改進機會
        
        Args:
            code: 要分析的代碼
            context: 代碼上下文說明
            
        Returns:
            {
                "issues": List[str],  # 發現的問題
                "suggestions": List[str],  # 改進建議
                "complexity": int,  # 複雜度評分
                "quality_score": float  # 質量評分 0-1
            }
        """
        print(f"🔍 分析代碼... ({len(code)} 字符)")
        
        # 使用 AI 分析代碼
        analysis_prompt = f"""
分析以下 Python 代碼，識別潛在問題和改進機會：

上下文: {context}

代碼:
```python
{code}
```

請提供：
1. 發現的問題（性能、可讀性、安全性等）
2. 具體的改進建議
3. 代碼質量評分（0-10）

以 JSON 格式回答：
{{
    "issues": ["問題1", "問題2"],
    "suggestions": ["建議1", "建議2"],
    "quality_score": 7.5
}}
"""
        
        result = self.ai.generate(
            analysis_prompt,
            task_complexity="medium",
            max_tokens=1024,
            temperature=0.3
        )
        
        # 解析 AI 回應
        try:
            # 嘗試提取 JSON
            response_text = result["text"]
            
            # 尋找 JSON 區塊
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                analysis_data = json.loads(json_match.group())
            else:
                # 如果沒有 JSON，使用預設值
                analysis_data = {
                    "issues": ["無法自動分析"],
                    "suggestions": ["手動審查代碼"],
                    "quality_score": 5.0
                }
            
            # 標準化
            return {
                "issues": analysis_data.get("issues", []),
                "suggestions": analysis_data.get("suggestions", []),
                "complexity": self.sandbox.validator.estimate_complexity(code),
                "quality_score": analysis_data.get("quality_score", 5.0) / 10.0  # 轉換為 0-1
            }
            
        except Exception as e:
            print(f"⚠️  代碼分析失敗: {e}")
            return {
                "issues": [f"分析錯誤: {str(e)}"],
                "suggestions": [],
                "complexity": self.sandbox.validator.estimate_complexity(code),
                "quality_score": 0.5
            }
    
    def generate_improved_code(
        self,
        original_code: str,
        analysis: Dict[str, Any],
        context: str = ""
    ) -> Optional[str]:
        """
        基於分析結果生成改進的代碼
        
        Args:
            original_code: 原始代碼
            analysis: 代碼分析結果
            context: 上下文說明
            
        Returns:
            改進後的代碼，如果生成失敗則返回 None
        """
        print("🔧 生成改進代碼...")
        
        # 構建改進提示
        improvement_prompt = f"""
你是一個專業的 Python 代碼優化專家。請改進以下代碼。

上下文: {context}

原始代碼:
```python
{original_code}
```

發現的問題:
{chr(10).join(f"- {issue}" for issue in analysis["issues"])}

改進建議:
{chr(10).join(f"- {suggestion}" for suggestion in analysis["suggestions"])}

要求：
1. 保持原有功能完全一致
2. 提升代碼性能和可讀性
3. 遵循 Python 最佳實踐
4. 添加必要的註釋
5. 只返回改進後的代碼，不要其他解釋

改進後的代碼:
```python
"""
        
        result = self.ai.generate(
            improvement_prompt,
            task_complexity="complex",  # 使用 Gemini
            max_tokens=2048,
            temperature=0.4
        )
        
        # 提取代碼
        try:
            response_text = result["text"]
            
            # 提取 Python 代碼塊
            import re
            code_match = re.search(r'```python\n(.*?)\n```', response_text, re.DOTALL)
            if code_match:
                improved_code = code_match.group(1).strip()
            else:
                # 如果沒有代碼塊標記，嘗試直接使用回應
                improved_code = response_text.strip()
            
            # 驗證代碼語法
            is_safe, reason = self.sandbox.validator.is_safe(improved_code)
            if not is_safe:
                print(f"⚠️  生成的代碼不安全: {reason}")
                return None
            
            return improved_code
            
        except Exception as e:
            print(f"❌ 代碼生成失敗: {e}")
            return None
    
    def evolve_module(
        self,
        module_path: Path,
        test_cases: Optional[List[Dict[str, Any]]] = None,
        auto_apply: bool = True
    ) -> Dict[str, Any]:
        """
        進化一個模塊
        
        Args:
            module_path: 模塊文件路徑
            test_cases: 測試用例（如果有）
            auto_apply: 是否自動應用改進（如果測試通過）
            
        Returns:
            進化結果字典
        """
        self.evolution_stats["total_attempts"] += 1
        
        print(f"\n{'='*60}")
        print(f"🧬 開始進化模塊: {module_path.name}")
        print(f"{'='*60}\n")
        
        # 1. 讀取原始代碼
        if not module_path.exists():
            return {
                "success": False,
                "error": f"模塊不存在: {module_path}"
            }
        
        with open(module_path, 'r', encoding='utf-8') as f:
            original_code = f.read()
        
        print(f"📄 原始代碼: {len(original_code)} 字符\n")
        
        # 2. 分析代碼
        analysis = self.analyze_code(original_code, context=f"模塊: {module_path.name}")
        
        print(f"📊 分析結果:")
        print(f"  質量評分: {analysis['quality_score']:.2%}")
        print(f"  複雜度: {analysis['complexity']}")
        print(f"  發現問題: {len(analysis['issues'])} 個")
        print(f"  改進建議: {len(analysis['suggestions'])} 個\n")
        
        # 如果質量已經很高，跳過
        if analysis['quality_score'] > 0.9:
            print("✅ 代碼質量已經很高，無需改進\n")
            return {
                "success": True,
                "improved": False,
                "reason": "代碼質量已達標",
                "analysis": analysis
            }
        
        # 3. 生成改進代碼
        improved_code = self.generate_improved_code(original_code, analysis, f"模塊: {module_path.name}")
        
        if not improved_code:
            self.evolution_stats["failed_evolutions"] += 1
            return {
                "success": False,
                "error": "代碼生成失敗"
            }
        
        print(f"✨ 改進代碼: {len(improved_code)} 字符\n")
        
        # 4. 測試比較
        if test_cases:
            print("🧪 運行測試...")
            comparison = self.sandbox.compare_versions(
                original_code,
                improved_code,
                test_cases
            )
            
            print(f"\n📊 測試結果:")
            print(f"  功能測試: {comparison['new_score']:.2%} (原: {comparison['old_score']:.2%})")
            print(f"  性能改進: {comparison['performance_improvement']:.2%}")
            print(f"  總體改進: {comparison['total_improvement']:.2%}")
            print(f"  {comparison['recommendation']}\n")
            
            # 判斷是否接受
            accept = comparison['total_improvement'] > 0
            
        else:
            print("⚠️  無測試用例，跳過測試\n")
            comparison = None
            accept = True  # 無測試時默認接受
        
        # 5. 決定是否應用
        if accept and auto_apply:
            # 備份原始文件
            backup_path = module_path.with_suffix('.py.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_code)
            
            # 應用改進
            with open(module_path, 'w', encoding='utf-8') as f:
                f.write(improved_code)
            
            print(f"✅ 改進已應用到 {module_path.name}")
            print(f"💾 原始代碼備份到 {backup_path.name}\n")
            
            self.evolution_stats["successful_evolutions"] += 1
            
            if comparison and comparison['total_improvement'] > 0:
                self.evolution_stats["code_improvements"] += 1
                if comparison['performance_improvement'] > 0:
                    self.evolution_stats["performance_improvements"] += 1
            
            # 記憶學習
            self.memory.remember(
                f"成功優化 {module_path.name}，改進度: {comparison['total_improvement']:.2%}" if comparison else f"優化了 {module_path.name}",
                importance=0.9,
                metadata={
                    "category": "optimizations",
                    "module": module_path.name,
                    "improvement": comparison['total_improvement'] if comparison else 0
                }
            )
            
            # 記錄日誌
            if comparison:
                self.sandbox.log_evolution(
                    module_path.name,
                    original_code,
                    improved_code,
                    comparison,
                    accepted=True
                )
            
            return {
                "success": True,
                "improved": True,
                "analysis": analysis,
                "comparison": comparison,
                "backup_path": str(backup_path)
            }
        
        else:
            print(f"❌ 改進未通過，保留原始代碼\n")
            self.evolution_stats["failed_evolutions"] += 1
            
            # 記錄失敗經驗
            self.memory.remember(
                f"嘗試優化 {module_path.name} 失敗",
                importance=0.6,
                metadata={
                    "category": "failures",
                    "module": module_path.name
                }
            )
            
            if comparison:
                self.sandbox.log_evolution(
                    module_path.name,
                    original_code,
                    improved_code,
                    comparison,
                    accepted=False
                )
            
            return {
                "success": False,
                "improved": False,
                "reason": "改進未達標",
                "analysis": analysis,
                "comparison": comparison
            }
    
    def evolve_all_modules(
        self,
        auto_apply: bool = True,
        skip_patterns: List[str] = None
    ) -> Dict[str, Any]:
        """
        進化 core 資料夾中的所有模塊
        
        Args:
            auto_apply: 是否自動應用改進
            skip_patterns: 要跳過的文件名模式
            
        Returns:
            總體進化報告
        """
        if skip_patterns is None:
            skip_patterns = ["__init__.py", "test_", "backup"]
        
        print(f"\n{'='*60}")
        print(f"🌟 開始全局進化")
        print(f"{'='*60}\n")
        
        results = []
        
        # 遍歷所有 Python 文件
        for py_file in self.core_path.glob("*.py"):
            # 跳過特定文件
            if any(pattern in py_file.name for pattern in skip_patterns):
                print(f"⏭️  跳過 {py_file.name}")
                continue
            
            # 進化模塊
            result = self.evolve_module(py_file, auto_apply=auto_apply)
            results.append({
                "module": py_file.name,
                "result": result
            })
        
        # 統計
        total = len(results)
        improved = sum(1 for r in results if r["result"].get("improved", False))
        failed = sum(1 for r in results if not r["result"].get("success", False))
        
        print(f"\n{'='*60}")
        print(f"📊 進化完成")
        print(f"{'='*60}")
        print(f"  總模塊數: {total}")
        print(f"  成功改進: {improved}")
        print(f"  失敗/跳過: {failed}")
        print(f"  改進率: {improved/total:.2%}" if total > 0 else "  改進率: N/A")
        print(f"{'='*60}\n")
        
        return {
            "total": total,
            "improved": improved,
            "failed": failed,
            "results": results,
            "stats": self.evolution_stats.copy()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取進化統計"""
        return self.evolution_stats.copy()
    
    def learn_from_feedback(self, feedback: str, context: str = ""):
        """從用戶反饋中學習"""
        self.memory.remember(
            f"用戶反饋: {feedback}",
            importance=0.85,
            metadata={
                "category": "experiences",
                "type": "user_feedback",
                "context": context
            }
        )
        
        print(f"📝 已記錄用戶反饋並學習")


# 測試代碼
if __name__ == "__main__":
    from hybrid_ai import HybridAI
    from memory_manager import MemoryManager
    from sandbox_executor import SandboxExecutor
    
    print("🧬 測試進化引擎\n")
    
    # 初始化組件
    project_root = Path("C:/Users/YourUser/YK")  # 請修改路徑
    
    ai = HybridAI(project_root)
    memory = MemoryManager(project_root / "memory")
    sandbox = SandboxExecutor(project_root / "Sandbox")
    
    # 初始化進化引擎
    engine = EvolutionEngine(ai, memory, sandbox, project_root / "core")
    
    # 測試：分析代碼
    print("📝 測試 1: 代碼分析")
    test_code = """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total = total + num
    return total
"""
    
    analysis = engine.analyze_code(test_code, "求和函數")
    print(f"  質量評分: {analysis['quality_score']:.2%}")
    print(f"  發現問題: {len(analysis['issues'])} 個")
    
    # 測試：生成改進代碼
    print("\n📝 測試 2: 生成改進代碼")
    improved = engine.generate_improved_code(test_code, analysis, "求和函數")
    if improved:
        print(f"  改進代碼長度: {len(improved)} 字符")
        print(f"  預覽:\n{improved[:200]}...")
    
    print("\n✅ 測試完成！")
