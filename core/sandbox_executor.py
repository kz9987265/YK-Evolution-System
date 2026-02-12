"""
沙盒執行和測試引擎
安全地執行、測試和評估新生成的代碼
"""

import os
import sys
import subprocess
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json
import tempfile
import shutil
import ast
import time


class CodeValidator:
    """代碼安全驗證器"""
    
    # 危險操作黑名單
    DANGEROUS_IMPORTS = {
        'os.system', 'subprocess.call', 'subprocess.Popen',
        'eval', 'exec', 'compile', '__import__',
        'shutil.rmtree', 'os.remove', 'os.rmdir',
        'pickle', 'shelve',  # 可能的代碼注入
    }
    
    DANGEROUS_BUILTINS = {
        'eval', 'exec', 'compile', '__import__',
        'open',  # 限制文件操作
    }
    
    @staticmethod
    def is_safe(code: str) -> Tuple[bool, str]:
        """
        檢查代碼是否安全
        
        Returns:
            (is_safe, reason)
        """
        try:
            # 1. 嘗試解析代碼
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"語法錯誤: {e}"
        
        # 2. 檢查危險操作
        for node in ast.walk(tree):
            # 檢查危險的導入
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(danger in alias.name for danger in ['os', 'subprocess', 'sys']):
                        return False, f"禁止導入危險模組: {alias.name}"
            
            if isinstance(node, ast.ImportFrom):
                if node.module and any(danger in node.module for danger in ['os', 'subprocess', 'sys']):
                    return False, f"禁止從危險模組導入: {node.module}"
            
            # 檢查危險的函數調用
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in CodeValidator.DANGEROUS_BUILTINS:
                        return False, f"禁止使用危險內建函數: {node.func.id}"
        
        return True, "代碼安全"
    
    @staticmethod
    def estimate_complexity(code: str) -> int:
        """估算代碼複雜度（行數 + 函數數量 + 類數量）"""
        try:
            tree = ast.parse(code)
            lines = len(code.split('\n'))
            functions = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
            classes = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
            
            return lines + functions * 10 + classes * 20
        except:
            return len(code.split('\n'))


class SandboxExecutor:
    """沙盒代碼執行器"""
    
    def __init__(self, sandbox_root: Path):
        self.sandbox_root = sandbox_root
        self.test_modules_dir = sandbox_root / "test_modules"
        self.benchmarks_dir = sandbox_root / "benchmarks"
        self.evolution_logs_dir = sandbox_root / "evolution_logs"
        
        # 創建目錄
        for directory in [self.test_modules_dir, self.benchmarks_dir, self.evolution_logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.validator = CodeValidator()
        
        print("✅ 沙盒環境初始化完成")
    
    def execute_safe(
        self,
        code: str,
        timeout: int = 10,
        globals_dict: Optional[Dict] = None,
        locals_dict: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        安全執行代碼
        
        Args:
            code: 要執行的代碼
            timeout: 超時時間（秒）
            globals_dict: 全局變量
            locals_dict: 局部變量
            
        Returns:
            {
                "success": bool,
                "output": str,
                "error": str,
                "execution_time": float,
                "result": Any
            }
        """
        # 1. 安全檢查
        is_safe, reason = self.validator.is_safe(code)
        if not is_safe:
            return {
                "success": False,
                "output": "",
                "error": f"安全檢查失敗: {reason}",
                "execution_time": 0,
                "result": None
            }
        
        # 2. 準備執行環境
        if globals_dict is None:
            globals_dict = {
                "__builtins__": {
                    # 只提供安全的內建函數
                    "print": print,
                    "len": len,
                    "range": range,
                    "str": str,
                    "int": int,
                    "float": float,
                    "bool": bool,
                    "list": list,
                    "dict": dict,
                    "tuple": tuple,
                    "set": set,
                    "sum": sum,
                    "max": max,
                    "min": min,
                    "abs": abs,
                    "round": round,
                    "sorted": sorted,
                    "enumerate": enumerate,
                    "zip": zip,
                    "map": map,
                    "filter": filter,
                }
            }
        
        if locals_dict is None:
            locals_dict = {}
        
        # 3. 捕獲輸出
        from io import StringIO
        import sys
        
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        stdout_capture = StringIO()
        stderr_capture = StringIO()
        
        result = {
            "success": False,
            "output": "",
            "error": "",
            "execution_time": 0,
            "result": None
        }
        
        try:
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture
            
            start_time = time.time()
            
            # 執行代碼
            exec(code, globals_dict, locals_dict)
            
            end_time = time.time()
            
            result["success"] = True
            result["output"] = stdout_capture.getvalue()
            result["execution_time"] = end_time - start_time
            result["result"] = locals_dict.get('result', None)
            
        except Exception as e:
            result["error"] = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        
        return result
    
    def test_module(
        self,
        module_code: str,
        test_cases: List[Dict[str, Any]],
        module_name: str = "test_module"
    ) -> Dict[str, Any]:
        """
        測試模塊代碼
        
        Args:
            module_code: 模塊代碼
            test_cases: 測試用例列表 [{"input": ..., "expected": ...}, ...]
            module_name: 模塊名稱
            
        Returns:
            {
                "success": bool,
                "passed": int,
                "failed": int,
                "total": int,
                "results": List[Dict],
                "score": float  # 0-1
            }
        """
        # 1. 保存模塊到沙盒
        module_path = self.test_modules_dir / f"{module_name}.py"
        with open(module_path, 'w', encoding='utf-8') as f:
            f.write(module_code)
        
        # 2. 運行測試用例
        passed = 0
        failed = 0
        test_results = []
        
        for i, test_case in enumerate(test_cases):
            test_input = test_case.get("input", {})
            expected = test_case.get("expected")
            
            # 構建測試代碼
            test_code = f"""
{module_code}

# 測試用例 {i+1}
test_input = {repr(test_input)}
result = main(**test_input) if callable(main) else None
"""
            
            # 執行測試
            exec_result = self.execute_safe(test_code, timeout=5)
            
            if exec_result["success"]:
                actual = exec_result["result"]
                
                # 比較結果
                if actual == expected:
                    passed += 1
                    test_results.append({
                        "test_id": i + 1,
                        "passed": True,
                        "input": test_input,
                        "expected": expected,
                        "actual": actual
                    })
                else:
                    failed += 1
                    test_results.append({
                        "test_id": i + 1,
                        "passed": False,
                        "input": test_input,
                        "expected": expected,
                        "actual": actual,
                        "error": "輸出不符合預期"
                    })
            else:
                failed += 1
                test_results.append({
                    "test_id": i + 1,
                    "passed": False,
                    "input": test_input,
                    "error": exec_result["error"]
                })
        
        total = len(test_cases)
        score = passed / total if total > 0 else 0
        
        return {
            "success": score > 0,
            "passed": passed,
            "failed": failed,
            "total": total,
            "results": test_results,
            "score": score
        }
    
    def benchmark(
        self,
        code: str,
        iterations: int = 100,
        warmup: int = 10
    ) -> Dict[str, Any]:
        """
        性能基準測試
        
        Args:
            code: 要測試的代碼
            iterations: 迭代次數
            warmup: 預熱次數
            
        Returns:
            {
                "avg_time": float,
                "min_time": float,
                "max_time": float,
                "total_time": float
            }
        """
        times = []
        
        # 預熱
        for _ in range(warmup):
            self.execute_safe(code, timeout=5)
        
        # 正式測試
        for _ in range(iterations):
            result = self.execute_safe(code, timeout=5)
            if result["success"]:
                times.append(result["execution_time"])
        
        if not times:
            return {
                "avg_time": 0,
                "min_time": 0,
                "max_time": 0,
                "total_time": 0,
                "error": "所有迭代都失敗了"
            }
        
        return {
            "avg_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "total_time": sum(times),
            "iterations": len(times)
        }
    
    def compare_versions(
        self,
        old_code: str,
        new_code: str,
        test_cases: List[Dict[str, Any]],
        benchmark_iterations: int = 50
    ) -> Dict[str, Any]:
        """
        比較兩個版本的代碼
        
        Returns:
            {
                "old_score": float,
                "new_score": float,
                "improvement": float,
                "old_performance": Dict,
                "new_performance": Dict,
                "recommendation": str
            }
        """
        # 1. 功能測試
        old_test = self.test_module(old_code, test_cases, "old_version")
        new_test = self.test_module(new_code, test_cases, "new_version")
        
        # 2. 性能測試
        old_perf = self.benchmark(old_code, benchmark_iterations)
        new_perf = self.benchmark(new_code, benchmark_iterations)
        
        # 3. 計算改進
        score_improvement = new_test["score"] - old_test["score"]
        
        if old_perf.get("avg_time", 0) > 0:
            perf_improvement = (old_perf["avg_time"] - new_perf.get("avg_time", 0)) / old_perf["avg_time"]
        else:
            perf_improvement = 0
        
        # 4. 綜合評估
        total_improvement = score_improvement * 0.7 + perf_improvement * 0.3
        
        # 5. 推薦
        if total_improvement > 0.1:
            recommendation = "✅ 新版本明顯更好，建議採用"
        elif total_improvement > 0:
            recommendation = "⚠️  新版本略有改進，可以考慮採用"
        elif total_improvement > -0.05:
            recommendation = "⚖️  新舊版本差不多，保留舊版本"
        else:
            recommendation = "❌ 新版本更差，拒絕採用"
        
        return {
            "old_score": old_test["score"],
            "new_score": new_test["score"],
            "score_improvement": score_improvement,
            "old_performance": old_perf,
            "new_performance": new_perf,
            "performance_improvement": perf_improvement,
            "total_improvement": total_improvement,
            "recommendation": recommendation,
            "old_test_results": old_test,
            "new_test_results": new_test
        }
    
    def log_evolution(
        self,
        module_name: str,
        old_code: str,
        new_code: str,
        comparison: Dict[str, Any],
        accepted: bool
    ):
        """記錄進化日誌"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "module_name": module_name,
            "old_complexity": self.validator.estimate_complexity(old_code),
            "new_complexity": self.validator.estimate_complexity(new_code),
            "score_improvement": comparison["score_improvement"],
            "performance_improvement": comparison["performance_improvement"],
            "total_improvement": comparison["total_improvement"],
            "recommendation": comparison["recommendation"],
            "accepted": accepted,
            "old_code_hash": hash(old_code),
            "new_code_hash": hash(new_code)
        }
        
        # 保存日誌
        log_file = self.evolution_logs_dir / f"evolution_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        return log_entry
    
    def cleanup(self):
        """清理臨時文件"""
        for file in self.test_modules_dir.glob("*.py"):
            if file.name.startswith("test_") or file.name.startswith("old_") or file.name.startswith("new_"):
                file.unlink()


# 測試代碼
if __name__ == "__main__":
    print("🧪 測試沙盒執行引擎\n")
    
    sandbox_root = Path("C:/Users/YourUser/YK/Sandbox")  # 請修改路徑
    executor = SandboxExecutor(sandbox_root)
    
    # 測試 1: 安全執行
    print("📝 測試 1: 安全執行代碼")
    safe_code = """
result = sum([1, 2, 3, 4, 5])
print(f"總和: {result}")
"""
    result = executor.execute_safe(safe_code)
    print(f"  成功: {result['success']}")
    print(f"  輸出: {result['output']}")
    print(f"  結果: {result['result']}")
    print(f"  時間: {result['execution_time']:.4f}s\n")
    
    # 測試 2: 危險代碼檢測
    print("📝 測試 2: 危險代碼檢測")
    dangerous_code = "import os\nos.system('rm -rf /')"
    result = executor.execute_safe(dangerous_code)
    print(f"  成功: {result['success']}")
    print(f"  錯誤: {result['error']}\n")
    
    # 測試 3: 模塊測試
    print("📝 測試 3: 模塊功能測試")
    module_code = """
def main(a, b):
    return a + b
"""
    test_cases = [
        {"input": {"a": 1, "b": 2}, "expected": 3},
        {"input": {"a": 10, "b": 20}, "expected": 30},
        {"input": {"a": -5, "b": 5}, "expected": 0},
    ]
    
    test_result = executor.test_module(module_code, test_cases)
    print(f"  通過: {test_result['passed']}/{test_result['total']}")
    print(f"  分數: {test_result['score']:.2%}\n")
    
    # 測試 4: 性能基準
    print("📝 測試 4: 性能基準測試")
    perf_result = executor.benchmark("result = sum(range(1000))", iterations=100)
    print(f"  平均時間: {perf_result['avg_time']*1000:.3f}ms")
    print(f"  最小時間: {perf_result['min_time']*1000:.3f}ms")
    print(f"  最大時間: {perf_result['max_time']*1000:.3f}ms\n")
    
    # 測試 5: 版本比較
    print("📝 測試 5: 版本比較")
    old_code = """
def main(n):
    result = 0
    for i in range(n):
        result += i
    return result
"""
    new_code = """
def main(n):
    return sum(range(n))
"""
    
    comparison = executor.compare_versions(
        old_code, new_code,
        test_cases=[
            {"input": {"n": 10}, "expected": 45},
            {"input": {"n": 100}, "expected": 4950},
        ]
    )
    
    print(f"  舊版本分數: {comparison['old_score']:.2%}")
    print(f"  新版本分數: {comparison['new_score']:.2%}")
    print(f"  性能改進: {comparison['performance_improvement']:.2%}")
    print(f"  推薦: {comparison['recommendation']}\n")
    
    print("✅ 測試完成！")
