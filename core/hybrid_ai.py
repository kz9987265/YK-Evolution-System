"""
混合 AI 系統 - Qwen3 本地模型 + Gemini API
智能路由：根據任務複雜度選擇最佳推理引擎
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, List
import json
from datetime import datetime

try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    print("⚠️  llama-cpp-python not installed. Install with: pip install llama-cpp-python")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  google-generativeai not installed. Install with: pip install google-generativeai")


class HybridAI:
    """混合 AI 推理系統"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.llm_path = project_root / "LLM"
        
        # 初始化本地模型
        self.local_model: Optional[Llama] = None
        self.gemini_model = None
        
        # 性能統計
        self.stats = {
            "local_calls": 0,
            "gemini_calls": 0,
            "local_tokens": 0,
            "gemini_tokens": 0,
            "avg_local_time": 0,
            "avg_gemini_time": 0
        }
        
        self._initialize_models()
    
    def _initialize_models(self):
        """初始化所有可用的模型"""
        # 1. 初始化本地 Qwen3 模型
        if LLAMA_AVAILABLE:
            model_file = self._find_gguf_model()
            if model_file:
                try:
                    print(f"🔄 加載本地模型: {model_file.name}")
                    self.local_model = Llama(
                        model_path=str(model_file),
                        n_ctx=8192,  # 上下文窗口
                        n_gpu_layers=-1,  # 使用 GPU（如果可用）
                        n_threads=8,  # CPU 線程數
                        verbose=False
                    )
                    print("✅ 本地模型加載成功！")
                except Exception as e:
                    print(f"❌ 本地模型加載失敗: {e}")
        
        # 2. 初始化 Gemini API
        if GEMINI_AVAILABLE:
            api_key = self._load_gemini_key()
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
                    print("✅ Gemini API 連接成功！")
                except Exception as e:
                    print(f"❌ Gemini API 初始化失敗: {e}")
    
    def _find_gguf_model(self) -> Optional[Path]:
        """在 LLM 資料夾中尋找 GGUF 模型"""
        if not self.llm_path.exists():
            print(f"❌ LLM 資料夾不存在: {self.llm_path}")
            return None
        
        gguf_files = list(self.llm_path.glob("*.gguf"))
        if not gguf_files:
            print(f"❌ 在 {self.llm_path} 中找不到 .gguf 檔案")
            return None
        
        # 優先選擇 Qwen3 模型
        for file in gguf_files:
            if "qwen3" in file.name.lower():
                return file
        
        return gguf_files[0]  # 返回第一個找到的模型
    
    def _load_gemini_key(self) -> Optional[str]:
        """從 .env.local 加載 Gemini API Key"""
        env_file = self.project_root / ".env.local"
        if not env_file.exists():
            print(f"❌ 配置文件不存在: {env_file}")
            return None
        
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('GEMINI_API_KEY'):
                        key = line.split('=', 1)[1].strip().strip('"').strip("'")
                        return key
        except Exception as e:
            print(f"❌ 讀取 API Key 失敗: {e}")
        
        return None
    
    def _should_use_local(self, task_complexity: str, prompt: str) -> bool:
        """
        決定使用本地模型還是 Gemini
        
        策略：
        - simple: 本地模型（快速響應）
        - medium: 優先本地，失敗則 Gemini
        - complex: Gemini（更強推理能力）
        """
        if not self.local_model:
            return False
        
        if not self.gemini_model:
            return True
        
        # 根據複雜度決策
        if task_complexity == "simple":
            return True
        elif task_complexity == "medium":
            return len(prompt) < 2000  # 短提示用本地
        else:  # complex
            return False
    
    def generate(
        self,
        prompt: str,
        task_complexity: str = "medium",
        max_tokens: int = 2048,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        混合推理生成
        
        Args:
            prompt: 用戶提示
            task_complexity: "simple", "medium", "complex"
            max_tokens: 最大生成 token 數
            temperature: 隨機性（0-1）
            system_prompt: 系統提示
            
        Returns:
            {
                "text": 生成的文本,
                "model": "local" or "gemini",
                "tokens": token 數量,
                "time": 推理時間（秒）
            }
        """
        start_time = datetime.now()
        
        use_local = self._should_use_local(task_complexity, prompt)
        
        try:
            if use_local and self.local_model:
                result = self._generate_local(prompt, max_tokens, temperature, system_prompt)
            elif self.gemini_model:
                result = self._generate_gemini(prompt, max_tokens, temperature, system_prompt)
            else:
                return {
                    "text": "❌ 沒有可用的推理引擎",
                    "model": "none",
                    "tokens": 0,
                    "time": 0,
                    "error": "No model available"
                }
            
            # 計算時間
            result["time"] = (datetime.now() - start_time).total_seconds()
            
            # 更新統計
            self._update_stats(result)
            
            return result
            
        except Exception as e:
            # 失敗回退機制
            if use_local and self.gemini_model:
                print(f"⚠️  本地模型失敗，切換到 Gemini: {e}")
                return self.generate(prompt, "complex", max_tokens, temperature, system_prompt)
            else:
                return {
                    "text": f"❌ 推理失敗: {str(e)}",
                    "model": "error",
                    "tokens": 0,
                    "time": 0,
                    "error": str(e)
                }
    
    def _generate_local(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """使用本地 Qwen3 模型生成"""
        # 構建完整提示
        if system_prompt:
            full_prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
        else:
            full_prompt = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
        
        # 生成
        response = self.local_model(
            full_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=["<|im_end|>"],
            echo=False
        )
        
        text = response['choices'][0]['text'].strip()
        tokens = response['usage']['completion_tokens']
        
        return {
            "text": text,
            "model": "local_qwen3",
            "tokens": tokens
        }
    
    def _generate_gemini(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """使用 Gemini API 生成"""
        # 構建完整提示
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt
        
        # 生成配置
        generation_config = {
            "max_output_tokens": max_tokens,
            "temperature": temperature,
        }
        
        # 生成
        response = self.gemini_model.generate_content(
            full_prompt,
            generation_config=generation_config
        )
        
        text = response.text
        tokens = response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
        
        return {
            "text": text,
            "model": "gemini",
            "tokens": tokens
        }
    
    def _update_stats(self, result: Dict[str, Any]):
        """更新性能統計"""
        if result["model"] == "local_qwen3":
            self.stats["local_calls"] += 1
            self.stats["local_tokens"] += result["tokens"]
            # 計算平均時間
            n = self.stats["local_calls"]
            self.stats["avg_local_time"] = (
                self.stats["avg_local_time"] * (n - 1) + result["time"]
            ) / n
        elif result["model"] == "gemini":
            self.stats["gemini_calls"] += 1
            self.stats["gemini_tokens"] += result["tokens"]
            n = self.stats["gemini_calls"]
            self.stats["avg_gemini_time"] = (
                self.stats["avg_gemini_time"] * (n - 1) + result["time"]
            ) / n
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取使用統計"""
        return self.stats.copy()
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        task_complexity: str = "medium",
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        對話模式（支持多輪對話）
        
        Args:
            messages: [{"role": "user"/"assistant", "content": "..."}]
            task_complexity: 任務複雜度
            max_tokens: 最大 token
            temperature: 隨機性
            
        Returns:
            生成結果字典
        """
        # 構建提示
        prompt_parts = []
        system_prompt = None
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                system_prompt = content
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        prompt = "\n\n".join(prompt_parts)
        
        return self.generate(prompt, task_complexity, max_tokens, temperature, system_prompt)


# 測試代碼
if __name__ == "__main__":
    print("🚀 測試混合 AI 系統\n")
    
    # 初始化（假設在 YK 目錄下運行）
    project_root = Path("C:/Users/YourUser/YK")  # 請修改為實際路徑
    ai = HybridAI(project_root)
    
    # 測試簡單任務（應該用本地模型）
    print("📝 測試 1: 簡單計算")
    result = ai.generate(
        "計算 15 * 23 = ?",
        task_complexity="simple",
        max_tokens=100
    )
    print(f"  模型: {result['model']}")
    print(f"  回答: {result['text']}")
    print(f"  時間: {result['time']:.2f}s\n")
    
    # 測試複雜任務（應該用 Gemini）
    print("📝 測試 2: 複雜推理")
    result = ai.generate(
        "設計一個自我進化的 AI 系統架構，需要包含記憶系統、沙盒測試、代碼生成和性能評估模塊。",
        task_complexity="complex",
        max_tokens=1024
    )
    print(f"  模型: {result['model']}")
    print(f"  回答: {result['text'][:200]}...")
    print(f"  時間: {result['time']:.2f}s\n")
    
    # 顯示統計
    print("📊 使用統計:")
    stats = ai.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
