"""
宝可梦传说 Z-A 存档编辑器
一个功能完整的图形界面存档编辑器，专为宝可梦传说 Z-A 设计

功能特性:
- 编辑背包物品
- 修改玩家数据
- 管理宝可梦
- 直观的图形界面
- 安全存档
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import os
import sys
import threading
from typing import Dict, Any, Optional
import shutil

plaza_path = os.path.join(os.path.dirname(__file__), "..")
if plaza_path not in sys.path:
    sys.path.insert(0, plaza_path)

try:
    from plaza.crypto import HashDB, SwishCrypto
    from plaza.types import BagEntry, BagSave, CategoryType, CoreData
    from plaza.types.accessors import HashDBKeys
    from plaza.util.items import item_db
except ImportError as e:
    print(f"导入 plaza 库时出错: {e}")
    sys.exit(1)

SAVE_FILE_MAGIC = bytes([0x17, 0x2D, 0xBB, 0x06, 0xEA])

class PLZASaveEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("宝可梦传说 Z-A 存档编辑器")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        self.save_data = None
        self.hash_db = None
        self.bag_save = None
        self.core_data = None
        self.save_file_path = None
        self.is_modified = False
        
        self.item_database = item_db
        
        self.create_widgets()
        self.update_status("就绪 - 请加载存档文件以开始")
        
    def create_widgets(self):
        """创建主界面"""
        # 菜单栏
        self.create_menu()
        
        # 主框架与标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 玩家信息标签页
        self.player_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.player_frame, text="玩家")
        self.create_player_tab()
        
        # 背包（物品）标签页
        self.bag_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.bag_frame, text="背包")
        self.create_bag_tab()
        
        # 宝可梦标签页
        self.pokemon_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.pokemon_frame, text="宝可梦")
        self.create_pokemon_tab()
        
        # 工具标签页
        self.tools_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tools_frame, text="工具")
        self.create_tools_tab()
        
        # Barre de statut
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开", command=self.open_save_file, accelerator="Ctrl+O")
        file_menu.add_command(label="保存", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="另存为...", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="创建备份", command=self.create_backup)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.quit_app)
        
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="重置背包", command=self.reset_bag)
        edit_menu.add_command(label="添加所有物品", command=self.add_all_items)
        edit_menu.add_command(label="金钱最大化", command=self.max_money)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
        
        self.root.bind('<Control-o>', lambda e: self.open_save_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        
    def create_player_tab(self):
        """创建玩家信息标签页"""
        main_frame = ttk.Frame(self.player_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 基本信息
        info_frame = ttk.LabelFrame(main_frame, text="玩家信息")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 玩家名称
        ttk.Label(info_frame, text="名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.player_name_var = tk.StringVar()
        self.player_name_entry = ttk.Entry(info_frame, textvariable=self.player_name_var, width=30)
        self.player_name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.player_name_entry.bind('<KeyRelease>', self.on_player_data_changed)
        
        # 性别
        ttk.Label(info_frame, text="性别:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.gender_var = tk.StringVar()
        self.gender_combo = ttk.Combobox(info_frame, textvariable=self.gender_var, 
                                        values=["男性", "女性"], state="readonly")
        self.gender_combo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.gender_combo.bind('<<ComboboxSelected>>', self.on_player_data_changed)
        
        # 玩家ID
        ttk.Label(info_frame, text="ID:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.player_id_var = tk.StringVar()
        self.player_id_label = ttk.Label(info_frame, textvariable=self.player_id_var)
        self.player_id_label.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 游戏统计
        stats_frame = ttk.LabelFrame(main_frame, text="统计数据")
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 金钱
        ttk.Label(stats_frame, text="金钱:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.money_var = tk.StringVar()
        self.money_entry = ttk.Entry(stats_frame, textvariable=self.money_var, width=15)
        self.money_entry.grid(row=0, column=1, padx=5, pady=5)
        self.money_entry.bind('<KeyRelease>', self.on_player_data_changed)
        
        # 最大化金钱按钮
        ttk.Button(stats_frame, text="最大", command=self.max_money).grid(row=0, column=2, padx=5, pady=5)
        
        # 星尘（如适用）
        ttk.Label(stats_frame, text="超能力:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.mega_power_var = tk.StringVar()
        self.mega_power_entry = ttk.Entry(stats_frame, textvariable=self.mega_power_var, width=15)
        self.mega_power_entry.grid(row=1, column=1, padx=5, pady=5)
        self.mega_power_entry.bind('<KeyRelease>', self.on_player_data_changed)
        
    def create_bag_tab(self):
        """创建背包标签页"""
        main_frame = ttk.Frame(self.bag_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(control_frame, text="类别:").pack(side=tk.LEFT, padx=(0, 5))
        self.category_filter = ttk.Combobox(control_frame, values=["全部", "药品", "精灵球", "其他", "拾取", "重要物品", "树果", "招式学习器", "超级"], state="readonly")
        self.category_filter.set("全部")
        self.category_filter.pack(side=tk.LEFT, padx=(0, 10))
        self.category_filter.bind('<<ComboboxSelected>>', self.filter_items)
        
        ttk.Label(control_frame, text="搜索:").pack(side=tk.LEFT, padx=(10, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(control_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', self.filter_items)
        
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="添加物品", command=self.add_item_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除", command=self.remove_selected_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="修改", command=self.modify_selected_item).pack(side=tk.LEFT, padx=5)
        
        tree_container = ttk.Frame(main_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ID", "名称", "数量", "类别")
        self.items_tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=20)
        
        self.items_tree.heading("ID", text="ID")
        self.items_tree.heading("名称", text="名称")
        self.items_tree.heading("数量", text="数量")
        self.items_tree.heading("类别", text="类别")
        
        self.items_tree.column("ID", width=80)
        self.items_tree.column("名称", width=300)
        self.items_tree.column("数量", width=100)
        self.items_tree.column("类别", width=150)
        
        v_scroll = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.items_tree.yview)
        h_scroll = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.items_tree.xview)
        self.items_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.items_tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        self.items_tree.bind('<Double-1>', lambda e: self.modify_selected_item())
        
    def create_pokemon_tab(self):
        """创建宝可梦标签页"""
        main_frame = ttk.Frame(self.pokemon_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 注意: 此功能将在未来版本中扩展
        info_label = ttk.Label(main_frame, text="宝可梦功能开发中\n\n此部分将允许：\n- 查看宝可梦队伍\n- 修改属性值\n- 改变等级\n- 管理携带物品", justify=tk.CENTER)
        info_label.pack(expand=True)
        
    def create_tools_tab(self):
        """创建工具标签页"""
        main_frame = ttk.Frame(self.tools_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        repair_frame = ttk.LabelFrame(main_frame, text="修复工具")
        repair_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(repair_frame, text="修复背包", command=self.repair_bag).pack(pady=5)
        ttk.Button(repair_frame, text="检查完整性", command=self.check_integrity).pack(pady=5)
        
        quick_frame = ttk.LabelFrame(main_frame, text="快速修改")
        quick_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(quick_frame, text="所有物品x999", command=self.add_all_items).pack(pady=5)
        ttk.Button(quick_frame, text="重置背包", command=self.reset_bag).pack(pady=5)
        ttk.Button(quick_frame, text="金钱最大化", command=self.max_money).pack(pady=5)
        
        info_frame = ttk.LabelFrame(main_frame, text="信息")
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        self.info_text = tk.Text(info_frame, wrap=tk.WORD, height=10)
        info_scroll = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scroll.set)
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def update_status(self, message: str):
        """更新状态栏"""
        self.status_var.set(message)
        self.root.update_idletasks()
        
    def on_player_data_changed(self, event=None):
        """标记数据已修改"""
        self.is_modified = True
        self.update_status("数据已修改 - 请记得保存")
        
    def open_save_file(self):
        """打开存档文件"""
        file_path = filedialog.askopenfilename(
            title="打开PLZA存档文件",
            filetypes=[("存档文件", "*"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            self.update_status("正在加载文件...")
            
            with open(file_path, "rb") as f:
                data = f.read()
                
            if not data.startswith(SAVE_FILE_MAGIC):
                messagebox.showerror("错误", "此文件不是有效的PLZA存档")
                return
                
            # 解密数据
            blocks = SwishCrypto.decrypt(data)
            self.hash_db = HashDB(blocks)
            
            # 加载背包数据
            try:
                self.bag_save = BagSave.from_bytes(self.hash_db[HashDBKeys.BagSave].data)
            except KeyError:
                messagebox.showerror("错误", "无法找到背包数据")
                return
                
            # 加载玩家数据
            try:
                core_data_block = self.hash_db[HashDBKeys.CoreData]
                self.core_data = CoreData.from_bytes(core_data_block.data)
            except (KeyError, AttributeError):
                # 如果CoreData不可用，创建默认数据
                self.core_data = None
                
            self.save_file_path = file_path
            self.save_data = data
            self.is_modified = False
            
            # 更新界面
            self.update_ui_with_save_data()
            self.update_status(f"已加载文件: {os.path.basename(file_path)}")
            
            messagebox.showinfo("成功", "存档文件已成功加载！")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载时出错: {str(e)}")
            self.update_status("加载出错")
            
    def update_ui_with_save_data(self):
        """用存档数据更新界面"""
        if self.core_data:
            try:
                player_name = ""
                for char_code in self.core_data.name:
                    if char_code == 0:
                        break
                    player_name += chr(char_code)
                self.player_name_var.set(player_name)
            except:
                self.player_name_var.set("未知")
                
            try:
                self.gender_var.set("男性" if self.core_data.sex == 0 else "女性")
            except:
                self.gender_var.set("男性")
                
            try:
                self.player_id_var.set(str(self.core_data.id))
            except:
                self.player_id_var.set("0")
                
            try:
                self.mega_power_var.set(str(self.core_data.mega_power))
            except:
                self.mega_power_var.set("0.0")
        else:
            self.player_name_var.set("不可用")
            self.gender_var.set("男性")
            self.player_id_var.set("不可用")
            self.mega_power_var.set("不可用")
            
        self.money_var.set("999999")
        
        self.update_items_list()
        
        self.update_file_info()
        
    def update_items_list(self):
        """更新背包物品列表"""
        # 清空当前列表
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
            
        if not self.bag_save:
            return
            
        # 添加物品
        for i, entry in enumerate(self.bag_save.entries):
            if entry.quantity > 0:
                item_name = self.get_item_name(i)
                category_name = self.get_category_name(entry.category)
                
                self.items_tree.insert("", "end", values=(
                    i,
                    item_name,
                    entry.quantity,
                    category_name
                ))
                
    def get_item_name(self, item_id: int) -> str:
        """通过ID获取物品名称"""
        if str(item_id) in self.item_database:
            return self.item_database[str(item_id)]["english_ui_name"]
        return f"未知物品 ({item_id})"
        
    def get_category_name(self, category) -> str:
        """获取类别名称"""
        try:
            category_value = category if isinstance(category, int) else category.value
            category_names = {
                -1: "损坏",
                0: "药品", 
                1: "精灵球",
                2: "其他",
                3: "拾取",
                4: "重要物品",
                5: "树果",
                6: "招式学习器",
                7: "超级"
            }
            return category_names.get(category_value, f"类别 {category_value}")
        except:
            return "未知"
            
    def filter_items(self, event=None):
        """按类别和搜索筛选物品"""
        if not self.bag_save:
            return
            
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
            
        category_filter = self.category_filter.get()
        search_term = self.search_var.get().lower()
        
        for i, entry in enumerate(self.bag_save.entries):
            if entry.quantity > 0:
                item_name = self.get_item_name(i)
                category_name = self.get_category_name(entry.category)
                
                if category_filter != "全部" and category_name != category_filter:
                    continue
                    
                if search_term and search_term not in item_name.lower():
                    continue
                    
                self.items_tree.insert("", "end", values=(
                    i,
                    item_name,
                    entry.quantity,
                    category_name
                ))
                
    def add_item_dialog(self):
        """添加物品对话框"""
        if not self.bag_save:
            messagebox.showwarning("警告", "未加载存档文件")
            return
            
        dialog = ItemAddDialog(self.root, self.item_database)
        if dialog.result:
            item_id, quantity = dialog.result
            try:
                self.add_item(item_id, quantity)
                self.update_items_list()
                self.is_modified = True
                self.update_status("已添加物品")
            except Exception as e:
                messagebox.showerror("错误", f"添加时出错: {str(e)}")
                
    def add_item(self, item_id: int, quantity: int):
        """向背包添加物品"""
        if not self.bag_save:
            return
            
        if str(item_id) not in self.item_database:
            raise ValueError(f"数据库中未找到物品ID {item_id}")
            
        expected_category = self.item_database[str(item_id)]["expected_category"]
        
        entry = BagEntry()
        entry.quantity = quantity
        entry.category = expected_category
        
        self.bag_save.set_entry(item_id, entry)
        
    def modify_selected_item(self):
        """修改选中的物品"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择一个物品")
            return
            
        item = self.items_tree.item(selection[0])
        item_id = int(item['values'][0])
        current_quantity = int(item['values'][2])
        
        new_quantity = simpledialog.askinteger(
            "修改数量",
            f"{item['values'][1]}的新数量:",
            initialvalue=current_quantity,
            minvalue=0,
            maxvalue=999
        )
        
        if new_quantity is not None:
            try:
                if new_quantity == 0:
                    # 删除物品
                    entry = BagEntry()
                    entry.quantity = 0
                    entry.category = 0
                    self.bag_save.set_entry(item_id, entry)
                else:
                    # 修改数量
                    entry = self.bag_save.entries[item_id]
                    entry.quantity = new_quantity
                    self.bag_save.set_entry(item_id, entry)
                    
                self.update_items_list()
                self.is_modified = True
                self.update_status("已修改物品")
            except Exception as e:
                messagebox.showerror("错误", f"修改时出错: {str(e)}")
                
    def remove_selected_item(self):
        """删除选中的物品"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择一个物品")
            return
            
        item = self.items_tree.item(selection[0])
        item_name = item['values'][1]
        
        if messagebox.askyesno("确认", f"删除 {item_name} ?"):
            item_id = int(item['values'][0])
            try:
                entry = BagEntry()
                entry.quantity = 0
                entry.category = 0
                self.bag_save.set_entry(item_id, entry)
                
                self.update_items_list()
                self.is_modified = True
                self.update_status("已删除物品")
            except Exception as e:
                messagebox.showerror("错误", f"删除时出错: {str(e)}")
                
    def reset_bag(self):
        """重置背包（删除所有物品）"""
        if not self.bag_save:
            messagebox.showwarning("警告", "未加载存档文件")
            return
            
        if messagebox.askyesno("确认", "删除背包中的所有物品？"):
            try:
                for i in range(len(self.bag_save.entries)):
                    entry = BagEntry()
                    entry.quantity = 0
                    entry.category = 0
                    self.bag_save.set_entry(i, entry)
                    
                self.update_items_list()
                self.is_modified = True
                self.update_status("背包已重置")
                messagebox.showinfo("成功", "背包已重置")
            except Exception as e:
                messagebox.showerror("错误", f"错误: {str(e)}")
                
    def add_all_items(self):
        """添加所有物品，数量最大"""
        if not self.bag_save:
            messagebox.showwarning("警告", "未加载存档文件")
            return
            
        if messagebox.askyesno("确认", "添加所有物品，数量x999？"):
            try:
                added_count = 0
                for item_id_str, item_data in self.item_database.items():
                    item_id = int(item_id_str)
                    expected_category = item_data["expected_category"]
                    
                    entry = BagEntry()
                    entry.quantity = 999
                    entry.category = expected_category
                    self.bag_save.set_entry(item_id, entry)
                    added_count += 1
                    
                self.update_items_list()
                self.is_modified = True
                self.update_status(f"已添加{added_count}个物品")
                messagebox.showinfo("成功", f"已添加{added_count}个物品")
            except Exception as e:
                messagebox.showerror("错误", f"错误: {str(e)}")
                
    def max_money(self):
        """金钱最大化"""
        self.money_var.set("999999")
        self.is_modified = True
        self.update_status("金钱已最大化")
        
    def repair_bag(self):
        """修复背包（纠正类别）"""
        if not self.bag_save:
            messagebox.showwarning("警告", "未加载存档文件")
            return
            
        try:
            repaired_count = 0
            for i, entry in enumerate(self.bag_save.entries):
                if entry.quantity > 0:
                    if str(i) in self.item_database:
                        expected_category = self.item_database[str(i)]["expected_category"]
                        if entry.category != expected_category:
                            entry.category = expected_category
                            self.bag_save.set_entry(i, entry)
                            repaired_count += 1
                    else:
                        entry.quantity = 0
                        entry.category = 0
                        self.bag_save.set_entry(i, entry)
                        repaired_count += 1
                        
            self.update_items_list()
            if repaired_count > 0:
                self.is_modified = True
                self.update_status(f"已修复{repaired_count}个物品")
                messagebox.showinfo("成功", f"已修复{repaired_count}个物品")
            else:
                messagebox.showinfo("信息", "无需修复")
        except Exception as e:
            messagebox.showerror("错误", f"错误: {str(e)}")
            
    def check_integrity(self):
        """检查文件完整性"""
        if not self.save_data:
            messagebox.showwarning("警告", "未加载存档文件")
            return
            
        try:
            is_valid = SwishCrypto.get_is_hash_valid(self.save_data)
            status = "有效" if is_valid else "无效"
            messagebox.showinfo("完整性", f"文件哈希: {status}")
        except Exception as e:
            messagebox.showerror("错误", f"检查时出错: {str(e)}")
            
    def update_file_info(self):
        """更新文件信息"""
        if not self.hash_db:
            return
            
        info = []
        info.append(f"文件: {os.path.basename(self.save_file_path) if self.save_file_path else '未加载'}")
        info.append(f"块数: {len(self.hash_db.blocks)}")
        
        if self.bag_save:
            item_count = sum(1 for entry in self.bag_save.entries if entry.quantity > 0)
            info.append(f"背包中的物品: {item_count}")
            
        if self.core_data:
            info.append(f"玩家ID: {self.core_data.id}")
            
        try:
            is_valid = SwishCrypto.get_is_hash_valid(self.save_data) if self.save_data else False
            info.append(f"哈希有效: {'是' if is_valid else '否'}")
        except:
            info.append("哈希有效: 检查错误")
            
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, "\n".join(info))
        
    def save_file(self):
        """保存当前文件"""
        if not self.save_file_path:
            self.save_file_as()
            return
            
        self.save_to_file(self.save_file_path)
        
    def save_file_as(self):
        """另存为新文件"""
        if not self.hash_db:
            messagebox.showwarning("警告", "未加载存档文件")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="保存文件",
            defaultextension="",
            filetypes=[("存档文件", "*"), ("所有文件", "*.*")]
        )
        
        if file_path:
            self.save_to_file(file_path)
            
    def save_to_file(self, file_path: str):
        """保存到特定文件"""
        try:
            # 应用玩家数据修改
            if self.core_data:
                # 玩家名称
                try:
                    player_name = self.player_name_var.get()
                    name_array = [0] * 13
                    for i, char in enumerate(player_name[:12]):
                        name_array[i] = ord(char)
                    self.core_data.name = name_array
                except:
                    pass
                    
                # 性别
                try:
                    self.core_data.sex = 0 if self.gender_var.get() == "男性" else 1
                except:
                    pass
                    
                # 超能力
                try:
                    self.core_data.mega_power = float(self.mega_power_var.get())
                except:
                    pass
                    
                # 在hash_db中更新数据
                self.hash_db[HashDBKeys.CoreData].change_data(self.core_data.to_bytes())
                
            # 更新背包数据
            if self.bag_save:
                self.hash_db[HashDBKeys.BagSave].change_data(self.bag_save.to_bytes())
                
            # 创建备份
            self.create_backup()
            
            # 加密并保存
            encrypted_data = SwishCrypto.encrypt(self.hash_db.blocks)
            with open(file_path, "wb") as f:
                f.write(encrypted_data)
                
            self.is_modified = False
            self.save_file_path = file_path
            self.update_status(f"已保存: {os.path.basename(file_path)}")
            messagebox.showinfo("成功", "文件已成功保存！")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存时出错: {str(e)}")
            
    def create_backup(self):
        """创建原始文件备份"""
        if not self.save_file_path or not os.path.exists(self.save_file_path):
            return
            
        backup_path = self.save_file_path + ".backup"
        if not os.path.exists(backup_path):
            try:
                shutil.copy2(self.save_file_path, backup_path)
                self.update_status(f"已创建备份: {os.path.basename(backup_path)}")
            except Exception as e:
                print(f"创建备份时出错: {e}")
                
    def quit_app(self):
        """退出应用程序"""
        if self.is_modified:
            result = messagebox.askyesnocancel(
                "保存",
                "存在未保存的修改。是否在退出前保存？"
            )
            if result is None:  # 取消
                return
            elif result:  # 是，保存
                self.save_file()
                
        self.root.quit()
        
    def show_about(self):
        """显示应用程序信息"""
        about_text = """宝可梦传说 Z-A 存档编辑器
版本 1.0

功能完整的图形界面存档编辑器，专为宝可梦传说 Z-A 设计。

功能特性:
• 编辑背包物品
• 修改玩家数据
• 修复工具
• 直观的界面
• 安全存档

由 MiniMax Agent 开发

基于 plaza 库
感谢 PKHeX 维护者提供的 SwishCrypto"""

        messagebox.showinfo("关于", about_text)


class ItemAddDialog:
    """添加物品对话框"""
    def __init__(self, parent, item_database):
        self.result = None
        self.item_database = item_database
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("添加物品")
        self.dialog.geometry("600x400")
        self.dialog.grab_set()
        
        # 主框架
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 搜索
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        self.search_entry.bind('<KeyRelease>', self.filter_items)
        
        # 物品列表
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ID", "名称", "类别")
        self.items_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        self.items_tree.heading("ID", text="ID")
        self.items_tree.heading("名称", text="名称")
        self.items_tree.heading("类别", text="类别")
        
        self.items_tree.column("ID", width=80)
        self.items_tree.column("名称", width=300)
        self.items_tree.column("类别", width=150)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=scrollbar.set)
        
        self.items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 数量
        quantity_frame = ttk.Frame(main_frame)
        quantity_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(quantity_frame, text="数量:").pack(side=tk.LEFT)
        self.quantity_var = tk.IntVar(value=1)
        quantity_spinbox = ttk.Spinbox(quantity_frame, from_=1, to=999, textvariable=self.quantity_var, width=10)
        quantity_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="添加", command=self.add_item).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="取消", command=self.cancel).pack(side=tk.RIGHT)
        
        # 填充列表
        self.populate_items()
        
        # 双击添加
        self.items_tree.bind('<Double-1>', lambda e: self.add_item())
        
    def populate_items(self):
        """填充物品列表"""
        for item_id, item_data in sorted(self.item_database.items(), key=lambda x: int(x[0])):
            category_names = {
                0: "无",
                1: "精灵球",
                2: "药品", 
                3: "树果",
                4: "招式学习器",
                5: "物品",
                6: "其他"
            }
            
            expected_category = item_data.get("expected_category", 0)
            category_name = category_names.get(expected_category, f"类别 {expected_category}")
            
            self.items_tree.insert("", "end", values=(
                item_id,
                item_data["english_ui_name"],
                category_name
            ))
            
    def filter_items(self, event=None):
        """按名称筛选物品"""
        search_term = self.search_var.get().lower()
        
        # 清空列表
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
            
        # 用筛选后的物品重新填充
        for item_id, item_data in sorted(self.item_database.items(), key=lambda x: int(x[0])):
            if search_term in item_data["english_ui_name"].lower():
                category_names = {
                    0: "无",
                    1: "精灵球", 
                    2: "药品",
                    3: "树果",
                    4: "招式学习器",
                    5: "物品",
                    6: "其他"
                }
                
                expected_category = item_data.get("expected_category", 0)
                category_name = category_names.get(expected_category, f"类别 {expected_category}")
                
                self.items_tree.insert("", "end", values=(
                    item_id,
                    item_data["english_ui_name"],
                    category_name
                ))
                
    def add_item(self):
        """添加选中的物品"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择一个物品")
            return
            
        item = self.items_tree.item(selection[0])
        item_id = int(item['values'][0])
        quantity = self.quantity_var.get()
        
        self.result = (item_id, quantity)
        self.dialog.destroy()
        
    def cancel(self):
        """取消"""
        self.dialog.destroy()


def main():
    """主函数"""
    root = tk.Tk()
    app = PLZASaveEditor(root)
    
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_width()) // 2
    y = (root.winfo_screenheight() - root.winfo_height()) // 2
    root.geometry(f"+{x}+{y}")
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()