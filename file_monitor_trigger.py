"""
YK Evolution System - 檔案監控觸發方案
當代碼檔案更新時自動觸發 Nebula 分析
"""

import os
import time
import hashlib
from pathlib import Path
from datetime import datetime
from nebula_integration import NebulaIntegration


class FileMonitor:
    """監控檔案變化並觸發 Nebula"""
    
    def __init__(self, watch_files=None, check_interval=10):
        """
        初始化檔案監控器
        
        參數:
            watch_files: 要監控的檔案列表
            check_interval: 檢查間隔（秒）
        """
        self.watch_files = watch_files or []
        self.check_interval = check_interval
        self.file_hashes = {}
        self.integration = NebulaIntegration()
        
        # 初始化檔案哈希值
        self._init_hashes()
    
    def _init_hashes(self):
        """初始化所有監控檔案的哈希值"""
        for file_path in self.watch_files:
            if Path(file_path).exists():
                self.file_hashes[file_path] = self._get_file_hash(file_path)
                print(f"📝 開始監控: {file_path}")
            else:
                print(f"⚠️  檔案不存在: {file_path}")
    
    def _get_file_hash(self, file_path):
        """計算檔案的 SHA256 哈希值"""
        sha256 = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            print(f"❌ 無法讀取檔案 {file_path}: {e}")
            return None
    
    def check_changes(self):
        """檢查檔案是否有變化"""
        changes = []
        
        for file_path in self.watch_files:
            if not Path(file_path).exists():
                continue
            
            current_hash = self._get_file_hash(file_path)
            old_hash = self.file_hashes.get(file_path)
            
            if current_hash != old_hash:
                changes.append({
                    'file': file_path,
                    'old_hash': old_hash,
                    'new_hash': current_hash,
                    'timestamp': datetime.now()
                })
                
                # 更新哈希值
                self.file_hashes[file_path] = current_hash
        
        return changes
    
    def on_file_changed(self, change_info):
        """當檔案變化時的處理"""
        file_path = change_info['file']
        timestamp = change_info['timestamp']
        
        print(f"\n🔔 檔案變化偵測！")
        print(f"   檔案: {file_path}")
        print(f"   時間: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 讀取變更後的代碼
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                new_code = f.read()
        except Exception as e:
            print(f"❌ 無法讀取檔案: {e}")
            return
        
        # 創建 Issue 請求 Nebula 分析
        print(f"📋 創建 Nebula 分析請求...")
        
        issue_data = self.integration.create_evolution_request(
            code_content=new_code,
            version=self._extract_version(new_code),
            context=f"""
檔案監控觸發

變更檔案: {file_path}
變更時間: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}

請 Nebula 分析這次變更：
1. 檢查新代碼的正確性
2. 評估改進效果
3. 提出進一步優化建議
"""
        )
        
        # 嘗試自動創建 Issue
        result = self.integration.create_issue_via_github_cli(issue_data)
        
        if result["success"]:
            print(f"✅ 已自動創建 Issue: {result['url']}")
        else:
            print(f"⚠️  自動創建失敗，切換到手動模式")
            self.integration.create_issue_manual_mode(issue_data)
    
    def _extract_version(self, code_content):
        """從代碼中提取版本號"""
        import re
        
        # 尋找 version = "x.x.x" 或 __version__ = "x.x.x"
        patterns = [
            r'version\s*=\s*["\'](["\']+)["\']+)',
            r'__version__\s*=\s*["\'](["\']+)["\']+)',
            r'VERSION\s*=\s*["\'](["\']+)["\']+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, code_content, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "unknown"
    
    def start_monitoring(self, duration=None):
        """
        開始監控
        
        參數:
            duration: 監控時長（秒），None 表示持續監控
        """
        print(f"\n🔍 開始監控檔案變化...")
        print(f"   監控間隔: {self.check_interval} 秒")
        print(f"   監控檔案: {len(self.watch_files)} 個")
        
        if duration:
            print(f"   監控時長: {duration} 秒")
        else:
            print(f"   持續監控（按 Ctrl+C 停止）")
        
        print("\n" + "="*60)
        
        start_time = time.time()
        
        try:
            while True:
                # 檢查是否超時
                if duration and (time.time() - start_time) > duration:
                    print(f"\n⏰ 監控時間結束")
                    break
                
                # 檢查變化
                changes = self.check_changes()
                
                if changes:
                    for change in changes:
                        self.on_file_changed(change)
                else:
                    # 顯示監控中的提示
                    elapsed = int(time.time() - start_time)
                    print(f"\r⏳ 監控中... ({elapsed}s)", end="", flush=True)
                
                # 等待下一次檢查
                time.sleep(self.check_interval)
        
        except KeyboardInterrupt:
            print(f"\n\n⏹️  監控已停止（用戶中斷）")
        
        print("\n" + "="*60)
        print("✅ 監控結束")


class GitCommitTrigger:
    """基於 Git Commit 的觸發器"""
    
    def __init__(self):
        self.integration = NebulaIntegration()
        self.last_commit = None
    
    def get_latest_commit(self):
        """獲取最新的 commit hash"""
        import subprocess
        
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except Exception as e:
            print(f"❌ 無法獲取 commit: {e}")
            return None
    
    def get_commit_changes(self, commit_hash):
        """獲取 commit 的變更檔案"""
        import subprocess
        
        try:
            result = subprocess.run(
                ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', commit_hash],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip().split('\n')
        except Exception as e:
            print(f"❌ 無法獲取變更檔案: {e}")
            return []
    
    def on_new_commit(self, commit_hash, changed_files):
        """當有新 commit 時觸發"""
        print(f"\n🔔 新 Commit 偵測！")
        print(f"   Commit: {commit_hash[:8]}")
        print(f"   變更檔案: {len(changed_files)} 個")
        
        for file_path in changed_files:
            print(f"      - {file_path}")
        
        # 對每個 Python 檔案創建分析請求
        for file_path in changed_files:
            if file_path.endswith('.py'):
                self._analyze_file(file_path, commit_hash)
    
    def _analyze_file(self, file_path, commit_hash):
        """分析單個檔案"""
        if not Path(file_path).exists():
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
        except Exception as e:
            print(f"❌ 無法讀取 {file_path}: {e}")
            return
        
        # 創建 Issue
        issue_data = self.integration.create_evolution_request(
            code_content=code_content,
            version=commit_hash[:8],
            context=f"""
Git Commit 觸發

Commit: {commit_hash}
檔案: {file_path}

請 Nebula 分析這次 commit 的變更。
"""
        )
        
        result = self.integration.create_issue_via_github_cli(issue_data)
        
        if result["success"]:
            print(f"✅ 已創建分析 Issue: {result['url']}")
    
    def start_monitoring(self, check_interval=30):
        """開始監控 Git commits"""
        print(f"\n🔍 開始監控 Git Commits...")
        print(f"   檢查間隔: {check_interval} 秒")
        
        self.last_commit = self.get_latest_commit()
        print(f"   當前 Commit: {self.last_commit[:8] if self.last_commit else 'unknown'}")
        
        print("\n按 Ctrl+C 停止監控\n")
        
        try:
            while True:
                current_commit = self.get_latest_commit()
                
                if current_commit and current_commit != self.last_commit:
                    changed_files = self.get_commit_changes(current_commit)
                    self.on_new_commit(current_commit, changed_files)
                    self.last_commit = current_commit
                
                time.sleep(check_interval)
        
        except KeyboardInterrupt:
            print(f"\n⏹️  監控已停止")


# 使用範例
if __name__ == "__main__":
    import sys
    
    print("🚀 YK Evolution - 檔案監控觸發器")
    print("="*60)
    
    # 選擇模式
    print("\n請選擇監控模式：")
    print("1. 檔案變化監控（監控特定檔案的內容變化）")
    print("2. Git Commit 監控（監控 Git 提交）")
    
    choice = input("\n請輸入選項 (1/2): ").strip()
    
    if choice == "1":
        # 檔案監控模式
        monitor = FileMonitor(
            watch_files=[
                "simple_evolution.py",
                "nebula_integration.py",
                "forgetting_system.py"
            ],
            check_interval=5
        )
        
        print("\n提示：修改以上任何檔案都會觸發 Nebula 分析")
        monitor.start_monitoring()
    
    elif choice == "2":
        # Git Commit 監控
        trigger = GitCommitTrigger()
        trigger.start_monitoring(check_interval=30)
    
    else:
        print("❌ 無效選項")