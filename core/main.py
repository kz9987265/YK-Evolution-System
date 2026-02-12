"""
YK 自我進化系統 - 主控制器
完全自主的 AI 進化循環
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import time
import schedule
import threading

# 導入核心組件
from hybrid_ai import HybridAI
from memory_manager import MemoryManager
from sandbox_executor import SandboxExecutor
from evolution_engine import EvolutionEngine


class YKEvolutionSystem:
    """YK 自我進化系統主控制器"""
    
    def __init__(self, project_root: Path):
        """
        初始化 YK 進化系統
        
        Args:
            project_root: YK 專案根目錄
        """
        self.project_root = project_root
        self.core_path = project_root / "core"
        
        print(f"\n{'='*60}")
        print(f"🚀 YK 自我進化系統啟動中...")
        print(f"{'='*60}\n")
        print(f"📁 專案路徑: {project_root}")
        print(f"📁 核心路徑: {self.core_path}\n")
        
        # 初始化各個組件
        print("🔧 初始化組件...\n")
        
        # 1. 混合 AI 系統
        self.ai = HybridAI(project_root)
        
        # 2. 記憶管理器
        self.memory = MemoryManager(project_root / "memory")
        
        # 3. 沙盒執行器
        self.sandbox = SandboxExecutor(project_root / "Sandbox")
        
        # 4. 進化引擎
        self.evolution = EvolutionEngine(
            self.ai,
            self.memory,
            self.sandbox,
            self.core_path
        )
        
        # 系統狀態
        self.is_running = False
        self.evolution_cycle_count = 0
        self.last_evolution_time = None
        self.last_activity_time = datetime.now()  # 最後活動時間
        
        # 配置
        self.config = {
            "auto_evolution_interval_hours": 24,  # 每 24 小時自動進化一次
            "auto_apply_improvements": True,      # 自動應用改進
            "min_quality_threshold": 0.6,         # 最低質量閾值
            "evolution_on_startup": False,        # 啟動時是否立即進化
            "idle_evolution_minutes": 3,          # 閒置 3 分鐘後自動進化
            "enable_idle_evolution": True,        # 啟用閒置進化
        }
        
        print(f"\n{'='*60}")
        print(f"✅ 系統初始化完成！")
        print(f"{'='*60}\n")
    
    def evolve_once(self, target_module: Optional[str] = None) -> Dict[str, Any]:
        """
        執行一次進化循環
        
        Args:
            target_module: 指定要進化的模塊，None 表示全部
            
        Returns:
            進化結果報告
        """
        self.evolution_cycle_count += 1
        self.last_evolution_time = datetime.now()
        
        print(f"\n{'='*60}")
        print(f"🧬 開始第 {self.evolution_cycle_count} 次進化循環")
        print(f"⏰ 時間: {self.last_evolution_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        # 1. 記憶整合（提升重要短期記憶到長期記憶）
        print("🧠 整合記憶...")
        consolidated = self.memory.consolidate_memories()
        print(f"✅ 整合了 {consolidated} 條記憶\n")
        
        # 2. 執行代碼進化
        if target_module:
            # 進化指定模塊
            module_path = self.core_path / target_module
            if not module_path.exists():
                module_path = self.core_path / f"{target_module}.py"
            
            result = self.evolution.evolve_module(
                module_path,
                auto_apply=self.config["auto_apply_improvements"]
            )
            
            evolution_report = {
                "total": 1,
                "improved": 1 if result.get("improved", False) else 0,
                "failed": 0 if result.get("success", True) else 1,
                "results": [{"module": target_module, "result": result}]
            }
        else:
            # 進化所有模塊
            evolution_report = self.evolution.evolve_all_modules(
                auto_apply=self.config["auto_apply_improvements"]
            )
        
        # 3. 保存記憶和狀態
        print("💾 保存系統狀態...")
        self.memory.save_all()
        self._save_system_state()
        
        # 4. 清理沙盒
        self.sandbox.cleanup()
        
        print(f"\n{'='*60}")
        print(f"✅ 第 {self.evolution_cycle_count} 次進化循環完成")
        print(f"{'='*60}\n")
        
        return evolution_report
    
    def start_autonomous_evolution(self):
        """啟動完全自主進化模式"""
        self.is_running = True
        
        print(f"\n{'='*60}")
        print(f"🌟 啟動自主進化模式")
        print(f"{'='*60}")
        print(f"⏱️  進化間隔: 每 {self.config['auto_evolution_interval_hours']} 小時")
        print(f"🔄 自動應用: {'是' if self.config['auto_apply_improvements'] else '否'}")
        print(f"{'='*60}\n")
        
        # 如果配置了啟動時進化
        if self.config["evolution_on_startup"]:
            print("🚀 執行啟動進化...\n")
            self.evolve_once()
        
        # 設置定時任務
        interval_hours = self.config['auto_evolution_interval_hours']
        
        def evolution_job():
            """定時進化任務"""
            if self.is_running:
                self.evolve_once()
        
        # 使用 schedule 庫設置定時任務
        schedule.every(interval_hours).hours.do(evolution_job)
        
        print(f"⏰ 下次自動進化時間: {datetime.now() + timedelta(hours=interval_hours)}")
        
        # 閒置進化設置
        if self.config["enable_idle_evolution"]:
            idle_minutes = self.config["idle_evolution_minutes"]
            print(f"💤 閒置進化: 啟用（閒置 {idle_minutes} 分鐘後自動進化）")
        
        print(f"🔄 系統正在運行，按 Ctrl+C 停止\n")
        
        # 運行調度循環
        try:
            while self.is_running:
                schedule.run_pending()
                
                # 檢查閒置進化
                if self.config["enable_idle_evolution"]:
                    self._check_idle_evolution()
                
                time.sleep(60)  # 每分鐘檢查一次
        except KeyboardInterrupt:
            print("\n\n⚠️  收到停止信號...")
            self.stop()
    
    def _check_idle_evolution(self):
        """檢查是否需要執行閒置進化"""
        idle_minutes = self.config["idle_evolution_minutes"]
        time_since_activity = datetime.now() - self.last_activity_time
        
        # 如果閒置時間超過設定值，觸發進化
        if time_since_activity >= timedelta(minutes=idle_minutes):
            print(f"\n💤 系統已閒置 {idle_minutes} 分鐘，開始自動進化...\n")
            self.evolve_once()
            # 重置活動時間
            self.last_activity_time = datetime.now()
    
    def _start_idle_monitor(self):
        """啟動閒置監控線程（後台運行）"""
        def monitor():
            print(f"💤 閒置監控已啟動（{self.config['idle_evolution_minutes']} 分鐘無活動後自動進化）\n")
            while self.is_running or True:  # 在互動模式下也運行
                time.sleep(60)  # 每分鐘檢查
                if not self.is_running:  # 互動模式
                    self._check_idle_evolution()
        
        self.is_running = False  # 互動模式標記
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def mark_activity(self):
        """標記用戶活動（外部調用以重置閒置計時器）"""
        self.last_activity_time = datetime.now()
        # 靜默更新，不打印（避免干擾互動）
    
    def stop(self):
        """停止自主進化"""
        self.is_running = False
        
        print(f"\n{'='*60}")
        print(f"🛑 停止自主進化")
        print(f"{'='*60}")
        print(f"📊 總進化次數: {self.evolution_cycle_count}")
        
        if self.last_evolution_time:
            print(f"⏰ 最後進化: {self.last_evolution_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 保存最終狀態
        print(f"\n💾 保存最終狀態...")
        self.memory.save_all()
        self._save_system_state()
        
        # 顯示統計
        stats = self.evolution.get_stats()
        print(f"\n📈 進化統計:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print(f"\n{'='*60}")
        print(f"✅ 系統已安全關閉")
        print(f"{'='*60}\n")
    
    def interact(self):
        """互動模式 - 允許手動控制"""
        print(f"\n{'='*60}")
        print(f"💬 進入互動模式")
        print(f"{'='*60}\n")
        
        print("可用命令:")
        print("  evolve [module_name] - 進化指定模塊（或全部）")
        print("  status              - 顯示系統狀態")
        print("  stats               - 顯示進化統計")
        print("  memory <query>      - 搜索記憶")
        print("  config <key> <value> - 修改配置")
        print("  auto                - 啟動自主進化")
        print("  exit                - 退出\n")
        
        # 啟動閒置監控線程
        if self.config["enable_idle_evolution"]:
            self._start_idle_monitor()
        
        while True:
            try:
                command = input("YK> ").strip()
                
                if not command:
                    continue
                
                # 標記用戶活動
                self.mark_activity()
                
                parts = command.split()
                cmd = parts[0].lower()
                
                if cmd == "exit":
                    break
                
                elif cmd == "evolve":
                    target = parts[1] if len(parts) > 1 else None
                    self.evolve_once(target)
                
                elif cmd == "status":
                    self._show_status()
                
                elif cmd == "stats":
                    stats = self.evolution.get_stats()
                    print("\n📈 進化統計:")
                    for key, value in stats.items():
                        print(f"  {key}: {value}")
                    print()
                
                elif cmd == "memory":
                    query = " ".join(parts[1:]) if len(parts) > 1 else ""
                    results = self.memory.recall(query)
                    
                    print(f"\n🔍 搜索結果: '{query}'")
                    for layer, entries in results.items():
                        if entries:
                            print(f"\n  {layer}: {len(entries)} 條")
                            for entry in entries[:3]:
                                print(f"    - {str(entry.content)[:80]}")
                    print()
                
                elif cmd == "config":
                    if len(parts) >= 3:
                        key = parts[1]
                        value = parts[2]
                        
                        if key in self.config:
                            # 類型轉換
                            if isinstance(self.config[key], bool):
                                self.config[key] = value.lower() in ['true', '1', 'yes']
                            elif isinstance(self.config[key], int):
                                self.config[key] = int(value)
                            elif isinstance(self.config[key], float):
                                self.config[key] = float(value)
                            else:
                                self.config[key] = value
                            
                            print(f"✅ 已更新 {key} = {self.config[key]}\n")
                        else:
                            print(f"❌ 未知配置項: {key}\n")
                    else:
                        print("\n當前配置:")
                        for key, value in self.config.items():
                            print(f"  {key}: {value}")
                        print()
                
                elif cmd == "auto":
                    self.start_autonomous_evolution()
                
                else:
                    print(f"❌ 未知命令: {cmd}\n")
                
            except KeyboardInterrupt:
                print("\n")
                break
            except Exception as e:
                print(f"❌ 錯誤: {e}\n")
        
        print("\n👋 退出互動模式\n")
    
    def _show_status(self):
        """顯示系統狀態"""
        print(f"\n{'='*60}")
        print(f"📊 系統狀態")
        print(f"{'='*60}")
        print(f"運行狀態: {'運行中' if self.is_running else '已停止'}")
        print(f"進化次數: {self.evolution_cycle_count}")
        
        if self.last_evolution_time:
            print(f"最後進化: {self.last_evolution_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n🧠 記憶系統:")
        print(f"  即時記憶: {len(self.memory.instant.entries)} 條")
        print(f"  短期記憶: {len(self.memory.short_term.entries)} 條")
        
        long_stats = self.memory.long_term.get_all_categories()
        total_long = sum(long_stats.values())
        print(f"  長期記憶: {total_long} 條")
        
        print(f"\n🤖 AI 系統:")
        ai_stats = self.ai.get_stats()
        print(f"  本地調用: {ai_stats['local_calls']}")
        print(f"  Gemini 調用: {ai_stats['gemini_calls']}")
        
        print(f"\n⚙️  配置:")
        for key, value in self.config.items():
            print(f"  {key}: {value}")
        
        print(f"{'='*60}\n")
    
    def _save_system_state(self):
        """保存系統狀態"""
        state = {
            "evolution_cycle_count": self.evolution_cycle_count,
            "last_evolution_time": self.last_evolution_time.isoformat() if self.last_evolution_time else None,
            "config": self.config,
            "stats": self.evolution.get_stats()
        }
        
        state_file = self.project_root / "system_state.json"
        import json
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)


def main():
    """主入口"""
    # 獲取 YK 專案路徑
    if len(sys.argv) > 1:
        project_root = Path(sys.argv[1])
    else:
        # 預設路徑（請根據實際情況修改）
        project_root = Path(__file__).parent.parent
    
    # 確保路徑存在
    if not project_root.exists():
        print(f"❌ 錯誤: 專案路徑不存在: {project_root}")
        sys.exit(1)
    
    # 創建系統實例
    system = YKEvolutionSystem(project_root)
    
    # 檢查啟動模式
    if "--auto" in sys.argv:
        # 自主進化模式
        system.start_autonomous_evolution()
    elif "--evolve" in sys.argv:
        # 單次進化模式
        system.evolve_once()
    else:
        # 互動模式
        system.interact()
    
    # 安全關閉
    if system.is_running:
        system.stop()


if __name__ == "__main__":
    main()
