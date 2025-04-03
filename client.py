import tkinter as tk
from tkinter import messagebox
import os
import requests
import json
import math
import threading

def check_dir_exists(dir_path):
  return os.path.exists(dir_path) and os.path.isdir(dir_path)

class dlthread (threading.Thread):   #继承父类threading.Thread
    def __init__(self, name, url, btn):
        threading.Thread.__init__(self)
        self.name = name
        self.url = url
        self.btn = btn
    def run(self):                   #把要执行的代码写到run函数里面 线程在创建后会直接运行run函数 
        cursor = requests.get(self.url,stream=True)
        size = int(cursor.headers['Content-Length'])
        downloaded = 0

        chunk = 4096

        with open('download/'+self.name,'wb') as f:
            for data in cursor.iter_content(chunk_size=chunk):
                f.write(data)
                downloaded += len(data)
                self.btn.config(text='Downloading... '+str(math.floor((downloaded/size)*100))+'%',state=tk.DISABLED)
        self.btn.config(text='Download',state=tk.NORMAL)
        messagebox.showinfo(
            "Download", 
            f"Download {self.name} successfully!"
        )

class ListApp:
    def __init__(self, root):
        self.root = root
        self.root.title("List Application")
        
        # 初始化列表数据
        self.list_data = []
        self.download_data = []
        
        # 创建界面组件
        self.create_widgets()
        
        # 初始加载列表
        self.refresth_list()
    
    def create_widgets(self):
        # 列表框架
        list_frame = tk.Frame(self.root)
        list_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # 列表和滚动条
        self.listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 按钮框架
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)
        
        # Refresh按钮
        refresh_btn = tk.Button(
            button_frame, 
            text="Refresh", 
            command=self.refresth_list
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Download按钮
        self.download_btn = tk.Button(
            button_frame, 
            text="Download", 
            command=self.download_item
        )
        self.download_btn.pack(side=tk.LEFT, padx=5)
    
    def init_list(self):
        """初始化列表数据"""
        # 这里只是一个示例，返回一些测试数据
        # 你可以修改这个函数来返回你需要的实际数据
        self.list_data = []
        self.download_data = []
        profiles_raw = requests.get('https://profiles.23312355.xyz/profiles.json').json()
        for profile in profiles_raw:
            self.list_data.append(profile['name'])
            self.download_data.append(profile['url'])
        return self.list_data

    
    def refresth_list(self):
        """刷新列表内容"""
        # 清空当前列表
        self.listbox.delete(0, tk.END)
        
        # 获取新数据
        self.list_data = self.init_list()
        
        # 填充列表
        for item in self.list_data:
            self.listbox.insert(tk.END, item)
    
    def download_item(self):
        """下载选中的项目"""

        if not check_dir_exists('download'):
            os.makedirs('download')

        selection = self.listbox.curselection()
        
        if not selection:
            messagebox.showwarning("Warning", "Please select an item first!")
            return
        
        index = selection[0]
        selected_item = self.download_data[index]
        
        self.download_btn.config(text='Downloading...',state=tk.DISABLED)

        parseurl = requests.get('https://api.hanximeng.com/lanzou/?url='+selected_item).json()
        if parseurl['code'] != 200:
            messagebox.showwarning("Warning", "The content was removed!")
            self.download_btn.config(text='Download',state=tk.NORMAL)
            return
        
        url = parseurl['downUrl']
        name = parseurl['name']

        downloadth = dlthread(name,url,self.download_btn)
        downloadth.start()
        




def main():
    root = tk.Tk()
    root.geometry("400x300")
    app = ListApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()