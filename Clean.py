import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog, messagebox

class PointCloud:
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.data = pd.read_csv(filepath, sep=' ', header=0)
        self.min_x = self.data['//X'].min()
        self.max_x = self.data['//X'].max()
        self.min_y = self.data['Y'].min()
        self.max_y = self.data['Y'].max()
        self.selected = False
        self.deleted = False
        self.rect_patch = None

class PointCloudApp:
    def __init__(self, master, folder_path):
        self.master = master
        self.master.title("点云可视化与管理")
        self.folder_path = folder_path
        self.point_clouds = []
        self.deleted_stack = []
        self.load_point_clouds()

        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.plot_point_clouds()

        self.canvas.mpl_connect('button_press_event', self.on_click)

        btn_frame = tk.Frame(self.master)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.delete_btn = tk.Button(btn_frame, text="删除选中", command=self.delete_selected)
        self.delete_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.undo_btn = tk.Button(btn_frame, text="撤销删除", command=self.undo_delete)
        self.undo_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.save_btn = tk.Button(btn_frame, text="保存", command=self.save_point_clouds)
        self.save_btn.pack(side=tk.LEFT, padx=5, pady=5)

    def load_point_clouds(self):
        txt_files = [f for f in os.listdir(self.folder_path) if f.endswith('.txt')]
        for file in txt_files:
            filepath = os.path.join(self.folder_path, file)
            try:
                pc = PointCloud(filepath)
                self.point_clouds.append(pc)
            except Exception as e:
                print(f"读取文件 {file} 失败: {e}")

    def plot_point_clouds(self):
        self.ax.clear()
        for pc in self.point_clouds:
            if not pc.deleted:
                self.ax.scatter(pc.data['//X'], pc.data['Y'], s=1, label=pc.filename)
                width = pc.max_x - pc.min_x
                height = pc.max_y - pc.min_y
                rect = Rectangle((pc.min_x, pc.min_y), width, height,
                                 linewidth=1, edgecolor='red' if pc.selected else 'blue',
                                 facecolor='none')
                self.ax.add_patch(rect)
                pc.rect_patch = rect
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_title('点云XY投影及边界框')
        self.ax.legend(fontsize='small', markerscale=5, bbox_to_anchor=(1.05, 1), loc='upper left')
        self.fig.tight_layout()
        self.canvas.draw()

    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        clicked_pc = None
        for pc in self.point_clouds:
            if pc.deleted:
                continue
            rect = pc.rect_patch
            contains, attr = rect.contains(event)
            if contains:
                clicked_pc = pc
                break
        if clicked_pc:
            clicked_pc.selected = not clicked_pc.selected
            clicked_pc.rect_patch.set_edgecolor('green' if clicked_pc.selected else 'blue')
            self.canvas.draw()

    def delete_selected(self):
        selected_pcs = [pc for pc in self.point_clouds if pc.selected and not pc.deleted]
        if not selected_pcs:
            messagebox.showinfo("提示", "没有选中的点云进行删除。")
            return
        for pc in selected_pcs:
            pc.deleted = True
            pc.selected = False
            self.deleted_stack.append(pc)
        self.plot_point_clouds()

    def undo_delete(self):
        if not self.deleted_stack:
            messagebox.showinfo("提示", "没有已删除的点云可以撤销。")
            return
        pc = self.deleted_stack.pop()
        pc.deleted = False
        self.plot_point_clouds()

    def save_point_clouds(self):
        save_folder = filedialog.askdirectory(title="选择保存点云的文件夹")
        if not save_folder:
            messagebox.showinfo("提示", "未选择保存文件夹。")
            return
        try:
            for pc in self.point_clouds:
                if not pc.deleted:
                    save_path = os.path.join(save_folder, pc.filename)
                    pc.data.to_csv(save_path, sep=' ', index=False)
            messagebox.showinfo("成功", "点云已成功保存。")
        except Exception as e:
            messagebox.showerror("错误", f"保存过程中出错: {e}")

def main():
    root = tk.Tk()
    root.geometry("900x700")
    folder_selected = filedialog.askdirectory(title="选择包含点云txt文件的文件夹")
    if not folder_selected:
        messagebox.showerror("错误", "未选择任何文件夹。程序将退出。")
        return
    app = PointCloudApp(root, folder_selected)
    root.mainloop()

if __name__ == "__main__":
    main()
