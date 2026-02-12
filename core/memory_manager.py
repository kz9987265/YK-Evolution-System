"""
三層記憶管理系統
- Instant Memory: 當前對話上下文（RAM）
- Short-term Memory: 近期經驗和學習（可序列化）
- Long-term Memory: 永久知識庫（持久化存儲）
"""

import os
import json
import pickle
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque
import hashlib


class MemoryEntry:
    """記憶條目基類"""
    
    def __init__(self, content: Any, metadata: Optional[Dict] = None):
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
        self.access_count = 0
        self.last_access = self.timestamp
        self.importance = 1.0  # 0-1 之間
        
        # 生成唯一 ID
        self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """生成基於內容的唯一 ID"""
        content_str = str(self.content) + str(self.timestamp)
        return hashlib.md5(content_str.encode()).hexdigest()[:16]
    
    def access(self):
        """記錄訪問"""
        self.access_count += 1
        self.last_access = datetime.now()
    
    def boost_importance(self, amount: float = 0.1):
        """提升重要性"""
        self.importance = min(1.0, self.importance + amount)
    
    def decay_importance(self, amount: float = 0.05):
        """降低重要性"""
        self.importance = max(0.0, self.importance - amount)
    
    def to_dict(self) -> Dict:
        """序列化"""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "access_count": self.access_count,
            "last_access": self.last_access.isoformat(),
            "importance": self.importance
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryEntry':
        """反序列化"""
        entry = cls(data["content"], data.get("metadata"))
        entry.id = data["id"]
        entry.timestamp = datetime.fromisoformat(data["timestamp"])
        entry.access_count = data["access_count"]
        entry.last_access = datetime.fromisoformat(data["last_access"])
        entry.importance = data["importance"]
        return entry


class InstantMemory:
    """即時記憶 - 當前對話上下文"""
    
    def __init__(self, max_entries: int = 50):
        self.max_entries = max_entries
        self.entries: deque = deque(maxlen=max_entries)
        self.context: Dict[str, Any] = {}
    
    def add(self, content: Any, metadata: Optional[Dict] = None):
        """添加記憶條目"""
        entry = MemoryEntry(content, metadata)
        self.entries.append(entry)
    
    def get_recent(self, n: int = 10) -> List[MemoryEntry]:
        """獲取最近 n 條記憶"""
        return list(self.entries)[-n:]
    
    def search(self, query: str) -> List[MemoryEntry]:
        """簡單搜索"""
        results = []
        query_lower = query.lower()
        
        for entry in self.entries:
            if query_lower in str(entry.content).lower():
                entry.access()
                results.append(entry)
        
        return results
    
    def set_context(self, key: str, value: Any):
        """設置上下文變量"""
        self.context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """獲取上下文變量"""
        return self.context.get(key, default)
    
    def clear(self):
        """清空即時記憶"""
        self.entries.clear()
        self.context.clear()
    
    def get_summary(self) -> str:
        """生成記憶摘要"""
        if not self.entries:
            return "No recent memories"
        
        recent = self.get_recent(5)
        summary_parts = []
        
        for entry in recent:
            content_preview = str(entry.content)[:100]
            summary_parts.append(f"- {content_preview}...")
        
        return "\n".join(summary_parts)


class ShortTermMemory:
    """短期記憶 - 近期經驗和學習"""
    
    def __init__(self, storage_path: Path, max_entries: int = 500, retention_days: int = 30):
        self.storage_path = storage_path
        self.max_entries = max_entries
        self.retention_days = retention_days
        self.entries: List[MemoryEntry] = []
        
        # 創建存儲目錄
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 加載現有記憶
        self._load()
    
    def add(self, content: Any, metadata: Optional[Dict] = None, importance: float = 0.5):
        """添加短期記憶"""
        entry = MemoryEntry(content, metadata)
        entry.importance = importance
        self.entries.append(entry)
        
        # 自動清理
        self._cleanup()
    
    def search(self, query: str, top_k: int = 10) -> List[MemoryEntry]:
        """搜索相關記憶"""
        results = []
        query_lower = query.lower()
        
        for entry in self.entries:
            # 簡單的關鍵詞匹配
            content_str = str(entry.content).lower()
            if query_lower in content_str:
                entry.access()
                results.append((entry, entry.importance * (1 + entry.access_count * 0.1)))
        
        # 按相關性排序
        results.sort(key=lambda x: x[1], reverse=True)
        
        return [entry for entry, _ in results[:top_k]]
    
    def get_important(self, threshold: float = 0.7, top_k: int = 20) -> List[MemoryEntry]:
        """獲取重要記憶"""
        important = [e for e in self.entries if e.importance >= threshold]
        important.sort(key=lambda x: x.importance, reverse=True)
        return important[:top_k]
    
    def decay_old_memories(self):
        """衰減舊記憶的重要性"""
        now = datetime.now()
        
        for entry in self.entries:
            age_days = (now - entry.timestamp).days
            if age_days > 7:
                decay_rate = 0.02 * (age_days - 7)
                entry.decay_importance(decay_rate)
    
    def _cleanup(self):
        """清理過期和不重要的記憶"""
        now = datetime.now()
        retention_threshold = now - timedelta(days=self.retention_days)
        
        # 移除過期記憶
        self.entries = [
            e for e in self.entries
            if e.timestamp > retention_threshold or e.importance > 0.8
        ]
        
        # 如果超過容量，移除最不重要的
        if len(self.entries) > self.max_entries:
            self.entries.sort(key=lambda x: x.importance, reverse=True)
            self.entries = self.entries[:self.max_entries]
    
    def save(self):
        """保存到磁盤"""
        save_file = self.storage_path / "short_term_memory.json"
        
        data = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "entries": [e.to_dict() for e in self.entries]
        }
        
        with open(save_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load(self):
        """從磁盤加載"""
        save_file = self.storage_path / "short_term_memory.json"
        
        if not save_file.exists():
            return
        
        try:
            with open(save_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.entries = [MemoryEntry.from_dict(e) for e in data.get("entries", [])]
            
            # 加載後清理
            self._cleanup()
        except Exception as e:
            print(f"⚠️  加載短期記憶失敗: {e}")


class LongTermMemory:
    """長期記憶 - 永久知識庫"""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 知識分類
        self.categories = {
            "skills": [],      # 學到的技能
            "knowledge": [],   # 知識條目
            "experiences": [], # 經驗教訓
            "optimizations": [], # 代碼優化
            "failures": [],    # 失敗記錄
            "successes": []    # 成功案例
        }
        
        self._load()
    
    def add(self, content: Any, category: str = "knowledge", metadata: Optional[Dict] = None):
        """添加長期記憶"""
        if category not in self.categories:
            category = "knowledge"
        
        entry = MemoryEntry(content, metadata)
        entry.importance = 1.0  # 長期記憶預設重要
        
        self.categories[category].append(entry)
    
    def search(self, query: str, category: Optional[str] = None, top_k: int = 10) -> List[Tuple[str, MemoryEntry]]:
        """搜索知識庫"""
        results = []
        query_lower = query.lower()
        
        # 選擇搜索範圍
        if category and category in self.categories:
            search_categories = {category: self.categories[category]}
        else:
            search_categories = self.categories
        
        # 搜索
        for cat_name, entries in search_categories.items():
            for entry in entries:
                content_str = str(entry.content).lower()
                if query_lower in content_str:
                    entry.access()
                    score = entry.importance * (1 + entry.access_count * 0.1)
                    results.append((cat_name, entry, score))
        
        # 排序
        results.sort(key=lambda x: x[2], reverse=True)
        
        return [(cat, entry) for cat, entry, _ in results[:top_k]]
    
    def get_category(self, category: str) -> List[MemoryEntry]:
        """獲取特定分類的所有記憶"""
        return self.categories.get(category, [])
    
    def get_all_categories(self) -> Dict[str, int]:
        """獲取所有分類及其數量"""
        return {cat: len(entries) for cat, entries in self.categories.items()}
    
    def save(self):
        """保存到磁盤"""
        save_file = self.storage_path / "long_term_memory.json"
        
        data = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "categories": {
                cat: [e.to_dict() for e in entries]
                for cat, entries in self.categories.items()
            }
        }
        
        with open(save_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load(self):
        """從磁盤加載"""
        save_file = self.storage_path / "long_term_memory.json"
        
        if not save_file.exists():
            return
        
        try:
            with open(save_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for cat, entries in data.get("categories", {}).items():
                if cat in self.categories:
                    self.categories[cat] = [MemoryEntry.from_dict(e) for e in entries]
        except Exception as e:
            print(f"⚠️  加載長期記憶失敗: {e}")


class MemoryManager:
    """統一記憶管理器"""
    
    def __init__(self, memory_root: Path):
        self.memory_root = memory_root
        
        # 初始化三層記憶
        self.instant = InstantMemory()
        self.short_term = ShortTermMemory(memory_root / "short_term_memory")
        self.long_term = LongTermMemory(memory_root / "long_term_memory")
        
        print("✅ 記憶系統初始化完成")
        self._print_stats()
    
    def remember(self, content: Any, importance: float = 0.5, metadata: Optional[Dict] = None):
        """智能記憶：根據重要性自動分層"""
        # 總是添加到即時記憶
        self.instant.add(content, metadata)
        
        # 中等以上重要性：添加到短期記憶
        if importance >= 0.5:
            self.short_term.add(content, metadata, importance)
        
        # 高重要性：添加到長期記憶
        if importance >= 0.8:
            category = metadata.get("category", "knowledge") if metadata else "knowledge"
            self.long_term.add(content, category, metadata)
    
    def recall(self, query: str, include_instant: bool = True, include_short: bool = True, 
               include_long: bool = True) -> Dict[str, List]:
        """全局檢索記憶"""
        results = {
            "instant": [],
            "short_term": [],
            "long_term": []
        }
        
        if include_instant:
            results["instant"] = self.instant.search(query)
        
        if include_short:
            results["short_term"] = self.short_term.search(query)
        
        if include_long:
            long_results = self.long_term.search(query)
            results["long_term"] = [entry for _, entry in long_results]
        
        return results
    
    def consolidate_memories(self):
        """記憶整合：將重要的短期記憶提升到長期記憶"""
        important_short = self.short_term.get_important(threshold=0.85)
        
        promoted_count = 0
        for entry in important_short:
            # 根據元數據確定分類
            category = entry.metadata.get("category", "experiences")
            
            # 檢查是否已存在
            existing = self.long_term.search(str(entry.content)[:50], category=category, top_k=1)
            if not existing:
                self.long_term.add(entry.content, category, entry.metadata)
                promoted_count += 1
        
        if promoted_count > 0:
            print(f"✅ 整合記憶：{promoted_count} 條短期記憶提升到長期記憶")
        
        return promoted_count
    
    def save_all(self):
        """保存所有記憶"""
        self.short_term.save()
        self.long_term.save()
        print("💾 所有記憶已保存")
    
    def _print_stats(self):
        """打印記憶統計"""
        print(f"  即時記憶: {len(self.instant.entries)} 條")
        print(f"  短期記憶: {len(self.short_term.entries)} 條")
        
        long_stats = self.long_term.get_all_categories()
        total_long = sum(long_stats.values())
        print(f"  長期記憶: {total_long} 條")
        for cat, count in long_stats.items():
            if count > 0:
                print(f"    - {cat}: {count}")


# 測試代碼
if __name__ == "__main__":
    print("🧠 測試記憶管理系統\n")
    
    # 初始化
    memory_root = Path("C:/Users/YourUser/YK/memory")  # 請修改路徑
    manager = MemoryManager(memory_root)
    
    # 測試記憶添加
    print("\n📝 測試 1: 添加不同重要性的記憶")
    manager.remember("學習了如何使用 pytest", importance=0.3, metadata={"type": "learning"})
    manager.remember("成功優化了推理速度，提升 40%", importance=0.9, 
                     metadata={"category": "optimizations", "improvement": 0.4})
    manager.remember("Gemini API 調用失敗時要切換到本地模型", importance=0.95,
                     metadata={"category": "experiences", "type": "failure_handling"})
    
    # 測試檢索
    print("\n🔍 測試 2: 檢索記憶")
    results = manager.recall("優化")
    for layer, entries in results.items():
        if entries:
            print(f"\n  {layer}: 找到 {len(entries)} 條")
            for entry in entries[:2]:
                print(f"    - {str(entry.content)[:60]}")
    
    # 測試整合
    print("\n🔄 測試 3: 記憶整合")
    manager.consolidate_memories()
    
    # 保存
    print("\n💾 測試 4: 保存記憶")
    manager.save_all()
    
    print("\n✅ 測試完成！")
