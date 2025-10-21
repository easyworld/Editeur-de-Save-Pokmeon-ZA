"""
宝可梦传说 Z-A 存档编辑器预设管理器
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

class PresetManager:
    """物品预设管理器"""
    
    def __init__(self, preset_dir="presets"):
        self.preset_dir = preset_dir
        self.ensure_preset_dir()
        self.create_default_presets()
    
    def ensure_preset_dir(self):
        """确保预设目录存在"""
        if not os.path.exists(self.preset_dir):
            os.makedirs(self.preset_dir)
    
    def create_default_presets(self):
        """创建默认预设"""
        default_presets = {
            "starter_pack": {
                "name": "新手礼包",
                "description": "在密阿雷城开始冒险所需的基本物品",
                "author": "MiniMax Agent",
                "created": "2025-10-19",
                "items": [
                    {"id": 1, "name": "大师球", "quantity": 5},
                    {"id": 2, "name": "高级球", "quantity": 30},
                    {"id": 3, "name": "超级球", "quantity": 50},
                    {"id": 4, "name": "精灵球", "quantity": 99},
                    {"id": 17, "name": "伤药", "quantity": 20},
                    {"id": 18, "name": "好伤药", "quantity": 15},
                    {"id": 19, "name": "厉害伤药", "quantity": 10},
                    {"id": 20, "name": "全满药", "quantity": 5}
                ]
            },
            
            "mega_collection": {
                "name": "超级进化收藏",
                "description": "开始使用超级进化的主要超级石",
                "author": "MiniMax Agent", 
                "created": "2025-10-19",
                "items": [
                    # 卡洛斯御三家的超级石
                    {"id": 658, "name": "喷火龙石X", "quantity": 1},
                    {"id": 659, "name": "喷火龙石Y", "quantity": 1},
                    {"id": 660, "name": "妙蛙花石", "quantity": 1},
                    {"id": 661, "name": "水箭龟石", "quantity": 1},
                    
                    # 热门超级进化
                    {"id": 662, "name": "路卡利欧石", "quantity": 1},
                    {"id": 663, "name": "烈咬陆鲨石", "quantity": 1},
                    {"id": 664, "name": "超梦石X", "quantity": 1},
                    {"id": 665, "name": "超梦石Y", "quantity": 1},
                    {"id": 666, "name": "烈空坐石", "quantity": 1},
                    
                    # Z-A的新超级进化
                    {"id": 700, "name": "捷拉奥拉石", "quantity": 1},
                    {"id": 701, "name": "索罗亚克石", "quantity": 1},
                    {"id": 702, "name": "君主蛇石", "quantity": 1},
                    {"id": 703, "name": "炎武王石", "quantity": 1}
                ]
            },
            
            "competitive_setup": {
                "name": "竞技配置",
                "description": "竞技对战和严肃战斗的必备物品",
                "author": "MiniMax Agent",
                "created": "2025-10-19", 
                "items": [
                    # 优质精灵球
                    {"id": 1, "name": "大师球", "quantity": 10},
                    {"id": 2, "name": "高级球", "quantity": 99},
                    {"id": 12, "name": "纪念球", "quantity": 50},
                    
                    # 恢复道具
                    {"id": 19, "name": "厉害伤药", "quantity": 50},
                    {"id": 20, "name": "全满药", "quantity": 30},
                    {"id": 21, "name": "全面恢复", "quantity": 20},
                    {"id": 22, "name": "活力碎片", "quantity": 10},
                    {"id": 23, "name": "活力块", "quantity": 5},
                    
                    # 战斗物品
                    {"id": 50, "name": "替身娃娃", "quantity": 10},
                    {"id": 51, "name": "逃脱绳", "quantity": 10},
                    
                    # PP和属性
                    {"id": 60, "name": "PP单项小补剂", "quantity": 10},
                    {"id": 61, "name": "PP单项全补剂", "quantity": 5},
                    {"id": 62, "name": "PP多项小补剂", "quantity": 10},
                    {"id": 63, "name": "PP多项全补剂", "quantity": 5}
                ]
            },
            
            "tm_collection": {
                "name": "招式学习器精选集", 
                "description": "训练最有用的招式学习器",
                "author": "MiniMax Agent",
                "created": "2025-10-19",
                "items": [
                    # 热门基础招式学习器（大致ID）
                    {"id": 328, "name": "招式01 撞击", "quantity": 1},
                    {"id": 329, "name": "招式02 龙爪", "quantity": 1},
                    {"id": 330, "name": "招式03 意念头锤", "quantity": 1},
                    {"id": 331, "name": "招式04 滚动", "quantity": 1},
                    {"id": 332, "name": "招式05 污泥炸弹", "quantity": 1},
                    {"id": 350, "name": "招式25 硬撑", "quantity": 1},
                    {"id": 360, "name": "招式35 睡觉", "quantity": 1},
                    {"id": 380, "name": "招式55 热水", "quantity": 1},
                    {"id": 400, "name": "招式75 剑舞", "quantity": 1},
                    {"id": 420, "name": "招式95 大地之力", "quantity": 1}
                ]
            },
            
            "lumiose_explorer": {
                "name": "密阿雷探险家",
                "description": "高效探索密阿雷地区所需的一切",
                "author": "MiniMax Agent",
                "created": "2025-10-19",
                "items": [
                    # 多样化捕捉
                    {"id": 2, "name": "高级球", "quantity": 50},
                    {"id": 3, "name": "超级球", "quantity": 99},
                    {"id": 4, "name": "精灵球", "quantity": 99},
                    {"id": 6, "name": "捕网球", "quantity": 30},
                    {"id": 7, "name": "潜水球", "quantity": 20},
                    {"id": 8, "name": "巢穴球", "quantity": 30},
                    {"id": 10, "name": "计时球", "quantity": 30},
                    {"id": 13, "name": "黑暗球", "quantity": 30},
                    {"id": 15, "name": "速度球", "quantity": 30},
                    
                    # 全面恢复
                    {"id": 17, "name": "伤药", "quantity": 30},
                    {"id": 18, "name": "好伤药", "quantity": 25},
                    {"id": 19, "name": "厉害伤药", "quantity": 20},
                    {"id": 24, "name": "解毒药", "quantity": 15},
                    {"id": 25, "name": "麻痹治疗", "quantity": 15},
                    {"id": 26, "name": "灼伤治疗", "quantity": 15},
                    {"id": 27, "name": "冰冻治疗", "quantity": 15},
                    {"id": 28, "name": "觉醒药", "quantity": 15},
                    
                    # 探索工具
                    {"id": 80, "name": "逃脱绳", "quantity": 10},
                    {"id": 81, "name": "除虫喷雾", "quantity": 20},
                    {"id": 82, "name": "超级除虫喷雾", "quantity": 15},
                    {"id": 83, "name": "最高级除虫喷雾", "quantity": 10}
                ]
            },
            
            "berry_garden": {
                "name": "树果园",
                "description": "用于恢复和特殊效果的有用树果收藏",
                "author": "MiniMax Agent",
                "created": "2025-10-19", 
                "items": [
                    # 基础恢复树果
                    {"id": 149, "name": "橙橙果", "quantity": 50},
                    {"id": 150, "name": "桃桃果", "quantity": 30},
                    {"id": 151, "name": "莓莓果", "quantity": 30},
                    {"id": 152, "name": "利木果", "quantity": 30},
                    {"id": 153, "name": "苹野果", "quantity": 30},
                    {"id": 154, "name": "柿仔果", "quantity": 30},
                    
                    # 特殊树果
                    {"id": 155, "name": "文柚果", "quantity": 20},
                    {"id": 156, "name": "勿花果", "quantity": 15},
                    {"id": 157, "name": "异奇果", "quantity": 15},
                    {"id": 158, "name": "木子果", "quantity": 15},
                    {"id": 159, "name": "芒芒果", "quantity": 15},
                    {"id": 160, "name": "乐芭果", "quantity": 15},
                    
                    # 稀有树果
                    {"id": 168, "name": "谜芝果", "quantity": 5},
                    {"id": 169, "name": "奇秘果", "quantity": 5},
                    {"id": 170, "name": "释陀果", "quantity": 5}
                ]
            }
        }
        
        # 如果预设文件不存在则创建
        for preset_id, preset_data in default_presets.items():
            filename = os.path.join(self.preset_dir, f"{preset_id}.json")
            if not os.path.exists(filename):
                self.save_preset(preset_data, filename)
    
    def save_preset(self, preset_data: Dict[str, Any], filename: str = None):
        """保存预设"""
        if filename is None:
            preset_name = preset_data.get("name", "preset").lower().replace(" ", "_")
            filename = os.path.join(self.preset_dir, f"{preset_name}.json")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(preset_data, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def load_preset(self, filename: str) -> Dict[str, Any]:
        """加载预设"""
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_presets(self) -> List[Dict[str, Any]]:
        """列出所有可用的预设"""
        presets = []
        
        if not os.path.exists(self.preset_dir):
            return presets
        
        for filename in os.listdir(self.preset_dir):
            if filename.endswith('.json'):
                try:
                    filepath = os.path.join(self.preset_dir, filename)
                    preset = self.load_preset(filepath)
                    presets.append({
                        "filename": filename,
                        "filepath": filepath,
                        "name": preset.get("name", filename),
                        "description": preset.get("description", "无描述"),
                        "author": preset.get("author", "未知"),
                        "created": preset.get("created", "日期未知"),
                        "items_count": len(preset.get("items", []))
                    })
                except Exception as e:
                    print(f"加载{filename}时出错: {e}")
        
        return sorted(presets, key=lambda x: x["name"])
    
    def create_custom_preset(self, name: str, description: str, items: List[Dict[str, Any]], author: str = "用户"):
        """创建自定义预设"""
        preset_data = {
            "name": name,
            "description": description,
            "author": author,
            "created": datetime.now().strftime("%Y-%m-%d"),
            "items": items
        }
        
        filename = self.save_preset(preset_data)
        return filename
    
    def delete_preset(self, filename: str) -> bool:
        """删除预设"""
        filepath = os.path.join(self.preset_dir, filename)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
        except Exception as e:
            print(f"删除{filename}时出错: {e}")
        return False
    
    def export_bag_to_preset(self, bag_items: List[Dict[str, Any]], name: str, description: str = ""):
        """将背包内容导出为新预设"""
        return self.create_custom_preset(name, description, bag_items)
    
    def get_preset_categories(self) -> Dict[str, List[str]]:
        """获取预设类别"""
        categories = {
            "入门": ["starter_pack.json"],
            "战斗": ["competitive_setup.json", "mega_collection.json"],
            "探索": ["lumiose_explorer.json"],
            "收藏": ["tm_collection.json", "berry_garden.json"],
            "自定义": []
        }
        
        all_presets = self.list_presets()
        default_files = [item for sublist in categories.values() for item in sublist]
        
        for preset in all_presets:
            if preset["filename"] not in default_files:
                categories["自定义"].append(preset["filename"])
        
        return categories

def create_sample_presets():
    """创建示例预设用于演示"""
    manager = PresetManager()
    
    print("预设管理器已初始化！")
    print(f"预设已在文件夹中创建: {manager.preset_dir}")
    
    # 列出可用的预设
    presets = manager.list_presets()
    print(f"\n可用的预设 ({len(presets)}):")
    for preset in presets:
        print(f"  • {preset['name']} - {preset['items_count']}个物品")
        print(f"    {preset['description']}")
        print(f"    作者: {preset['author']} | 创建于: {preset['created']}")
        print()

if __name__ == "__main__":
    create_sample_presets()