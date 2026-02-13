"""
測試 YK Evolution ↔️ Nebula 整合
立即可用的測試腳本
"""

from nebula_integration import NebulaIntegration
from pathlib import Path


def test_integration():
    """測試整合流程"""
    
    print("🧪 YK Evolution - Nebula 整合測試")
    print("="*60)
    
    # 1. 初始化
    print("\n📋 步驟 1: 初始化整合模組")
    integration = NebulaIntegration(
        repo_owner="kz9987265",
        repo_name="YK-evolution-system"
    )
    print(f"✅ 倉庫: {integration.repo_full_name}")
    
    # 2. 讀取代碼
    print("\n📋 步驟 2: 讀取當前代碼")
    code_file = Path(__file__).parent / "simple_evolution.py"
    
    if code_file.exists():
        with open(code_file, 'r', encoding='utf-8') as f:
            current_code = f.read()
        print(f"✅ 已讀取: {code_file.name} ({len(current_code)} 字元)")
    else:
        current_code = """
# YK Evolution System - 簡化版測試代碼

class YKEvolution:
    def __init__(self):
        self.version = "1.0.0"
    
    def evolve(self):
        print("開始進化...")
        # TODO: 實作進化邏輯
        
if __name__ == "__main__":
    yk = YKEvolution()
    yk.evolve()
"""
        print(f"⚠️  使用測試代碼 ({len(current_code)} 字元)")
    
    # 3. 創建 Issue 請求
    print("\n📋 步驟 3: 創建進化請求")
    issue_data = integration.create_evolution_request(
        code_content=current_code,
        version="1.0.0",
        context="""
這是第一次測試 Nebula 整合。

目標：
1. 驗證 Issue 創建流程
2. 測試 Nebula 回應機制
3. 確認自動化整合可行性

請 Nebula 提供：
- 代碼結構分析
- 改進建議
- 下一步發展方向
"""
    )
    
    print(f"✅ Issue 資料已準備")
    
    # 4. 嘗試自動創建（使用 GitHub CLI）
    print("\n📋 步驟 4: 創建 GitHub Issue")
    print("\n🔧 嘗試方式 1: GitHub CLI (gh)")
    
    result = integration.create_issue_via_github_cli(issue_data)
    
    if result["success"]:
        print(f"\n🎉 自動創建成功！")
        print(f"   Issue URL: {result['url']}")
        print(f"   Issue #: {result['number']}")
        print(f"\n💡 接下來：")
        print(f"   1. 在 Issue 中 @Nebula")
        print(f"   2. 等待 Nebula 分析回應")
        print(f"   3. 查看改進建議")
    else:
        print(f"\n⚠️  自動創建失敗: {result.get('error', '未知錯誤')}")
        print(f"\n🔧 切換到方式 2: 手動模式")
        
        manual_result = integration.create_issue_manual_mode(issue_data)
        
        print(f"\n💡 手動創建步驟：")
        print(f"   1. 打開文件: {manual_result['file']}")
        print(f"   2. 複製內容")
        print(f"   3. 前往: https://github.com/{integration.repo_full_name}/issues/new")
        print(f"   4. 貼上內容並提交")
        print(f"   5. 在 Issue 中確保有 @Nebula 標記")
    
    print("\n" + "="*60)
    print("✅ 測試完成！")
    
    return result


if __name__ == "__main__":
    test_integration()