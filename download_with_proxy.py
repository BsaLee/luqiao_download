import os
import sys
import requests
import tkinter as tk
from tkinter import ttk, Text, messagebox
from tkinter import PhotoImage, Label
from PIL import Image, ImageTk
import time
import threading

# 常量定义
CHUNK_SIZE = 8192  # 下载块大小
UPDATE_INTERVAL = 100  # 更新间隔（毫秒）
MAX_RETRIES = 3  # 最大重试次数

# 函数：根据 URL 和代理配置执行下载
def download_file(proxy_protocol, proxy_address, proxy_port, proxy_username, proxy_password, download_url, save_path, progress_var, speed_label, status_label, retry_button):
    # 处理代理配置：如果代理地址或端口为空，则直接连接
    if not (proxy_address and proxy_port) or (proxy_address == "-" and proxy_port == "-"):
        proxies = None  # 不使用代理
    else:
        proxy_username = None if proxy_username == "-" else proxy_username
        proxy_password = None if proxy_password == "-" else proxy_password

        proxy_auth = f"{proxy_username}:{proxy_password}@" if proxy_username and proxy_password else ""
        proxies = {
            "http": f"{proxy_protocol}://{proxy_auth}{proxy_address}:{proxy_port}",
            "https": f"{proxy_protocol}://{proxy_auth}{proxy_address}:{proxy_port}"
        }

    # 检查文件是否已存在
    if os.path.exists(save_path):
        downloaded_size = os.path.getsize(save_path)
        total_size = int(requests.head(download_url, proxies=proxies).headers.get('content-length', 0))

        if downloaded_size >= total_size:
            status_label.config(text="下载已完成，文件已存在")
            countdown_and_close(3)  # 启动 3 秒倒计时关闭窗口
            return

        headers = {'Range': f'bytes={downloaded_size}-'}
    else:
        downloaded_size = 0
        headers = {}

    retries = 0  # 重试计数

    while retries < MAX_RETRIES:
        try:
            # 请求下载文件，支持断点续传
            with requests.get(download_url, headers=headers, stream=True, proxies=proxies, timeout=10) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0)) + downloaded_size

                # 进度条最大值为总大小
                progress_var.set(0)
                progress_bar["maximum"] = total_size

                start_time = time.time()  # 记录开始时间
                with open(save_path, 'ab') as f:
                    for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)

                            # 更新进度条和速度
                            if time.time() - start_time >= UPDATE_INTERVAL / 1000:  # 限制更新频率
                                progress_var.set(downloaded_size)
                                elapsed_time = time.time() - start_time
                                speed = downloaded_size / elapsed_time / 1024  # KB/s
                                speed_label.config(text=f"下载速度: {speed:.2f} KB/s")
                                start_time = time.time()  # 重置开始时间

                            # 刷新窗口
                            root.update_idletasks()

                status_label.config(text="下载完成")
                countdown_and_close(3)  # 启动 3 秒倒计时关闭窗口
                return  # 下载成功，返回

        except requests.exceptions.RequestException:
            retries += 1  # 增加重试计数
            if retries < MAX_RETRIES:
                status_label.config(text=f"下载失败，正在重试... (尝试 {retries}/{MAX_RETRIES})")
                time.sleep(1)  # 等待 1 秒后重试
            else:
                # 代理失效，尝试直连
                status_label.config(text="代理无效，尝试本地直连")
                proxies = None  # 切换为直连
                try:
                    # 尝试直连下载
                    with requests.get(download_url, headers=headers, stream=True, timeout=10) as r:
                        r.raise_for_status()  # 检查请求是否成功
                        total_size = int(r.headers.get('content-length', 0)) + downloaded_size

                        # 进度条最大值为总大小
                        progress_var.set(0)
                        progress_bar["maximum"] = total_size

                        start_time = time.time()  # 记录开始时间
                        with open(save_path, 'ab') as f:
                            for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                                if chunk:
                                    f.write(chunk)
                                    downloaded_size += len(chunk)

                                    # 更新进度条和速度
                                    if time.time() - start_time >= UPDATE_INTERVAL / 1000:  # 限制更新频率
                                        progress_var.set(downloaded_size)
                                        elapsed_time = time.time() - start_time
                                        speed = downloaded_size / elapsed_time / 1024  # KB/s
                                        speed_label.config(text=f"下载速度: {speed:.2f} KB/s")
                                        start_time = time.time()  # 重置开始时间

                                    # 刷新窗口
                                    root.update_idletasks()

                        status_label.config(text="下载完成")
                        countdown_and_close(3)  # 启动 3 秒倒计时关闭窗口
                        return  # 下载成功，返回
                except Exception as e:
                    status_label.config(text="下载失败")
                    retry_button.pack(pady=10)  # 显示重试按钮
                    return  # 直连下载失败，返回

# 显示倒计时并关闭窗口
def countdown_and_close(seconds):
    if seconds > 0:
        tk.Label(root, text=f"窗口将在 {seconds} 秒后关闭").pack(padx=10, pady=5)
        root.after(1000, countdown_and_close, seconds - 1)  # 每秒调用一次
    else:
        root.quit()  # 倒计时结束后关闭窗口

# 启动下载
def start_download(proxy_protocol, proxy_address, proxy_port, proxy_username, proxy_password, download_url, save_path, progress_var, speed_label, status_label, retry_button):
    threading.Thread(target=download_file, args=(proxy_protocol, proxy_address, proxy_port, proxy_username, proxy_password, download_url, save_path, progress_var, speed_label, status_label, retry_button)).start()

# 创建图形界面，并显示传递的参数
def create_gui(proxy_protocol="", proxy_address="", proxy_port="", proxy_username="", proxy_password="", download_url="", save_path=""):
    global root, progress_bar, retry_button

    root = tk.Tk()
    root.title("文件下载器")

    # 加载图片
    image_path = "1.png"
    if os.path.exists(image_path):
        root.geometry("500x800")  # 如果有图片，窗口高度为800
        img = Image.open(image_path)  # 打开图像
        img = img.resize((500, 300), Image.LANCZOS)  # 使用 LANCZOS 缩放图像
        image = ImageTk.PhotoImage(img)  # 转换为 PhotoImage
        img_label = Label(root, image=image)
        img_label.image = image  # 保持对图像的引用
        img_label.pack(pady=10)  # 在底部展示图片
    else:
        root.geometry("500x500")  # 如果没有图片，窗口高度为500

    # 创建输入框并显示传递的参数
    for label_text, default_value in [
        ("代理协议:", proxy_protocol),
        ("代理地址:", proxy_address),
        ("代理端口:", proxy_port),
        ("代理用户名:", proxy_username if proxy_username != '-' else ''),
        ("代理密码:", proxy_password if proxy_password != '-' else ''),
        ("下载 URL:", download_url),
        ("保存路径:", save_path)
    ]:
        frame = tk.Frame(root)
        frame.pack(padx=10, pady=5, fill='x')

        label = tk.Label(frame, text=label_text)
        label.pack(side='left')

        entry = tk.Entry(frame)
        entry.insert(0, default_value)
        entry.pack(side='right', expand=True, fill='x')

    # 创建进度条
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
    progress_bar.pack(padx=10, pady=10, fill="x")

    # 显示下载速度
    speed_label = tk.Label(root, text="下载速度: 0 KB/s")
    speed_label.pack(padx=10, pady=5)

    # 状态标签，用于显示下载状态信息
    status_label = tk.Label(root, text="正在下载，请稍候...")
    status_label.pack(padx=10, pady=10)

    # 创建重试按钮
    retry_button = tk.Button(root, text="重试", command=lambda: start_download(proxy_protocol, proxy_address, proxy_port, proxy_username, proxy_password, download_url, save_path, progress_var, speed_label, status_label, retry_button))
    retry_button.pack(pady=10)
    retry_button.pack_forget()  # 初始时隐藏重试按钮

    # 加载并展示同目录下的 1.txt 文本内容
    text_path = "1.txt"
    if os.path.exists(text_path):
        with open(text_path, "r", encoding='utf-8') as f:
            text_content = f.read().strip()  # 读取内容并移除多余空白

        text_box = Text(root, height=5, wrap=tk.WORD)
        text_box.insert(tk.END, text_content)
        text_box.config(state=tk.DISABLED)  # 设置为只读
        text_box.pack(padx=10, pady=10, fill="x")

    # 启动下载
    root.after(100, start_download, proxy_protocol, proxy_address, proxy_port, proxy_username, proxy_password, download_url, save_path, progress_var, speed_label, status_label, retry_button)

    root.mainloop()

# 自动下载函数
def main():
    # 检查是否传入参数
    if len(sys.argv) == 8:
        proxy_protocol = sys.argv[1]
        proxy_address = sys.argv[2]
        proxy_port = sys.argv[3]
        proxy_username = sys.argv[4]  # 使用 "-" 代表空值
        proxy_password = sys.argv[5]  # 使用 "-" 代表空值
        download_url = sys.argv[6]
        save_path = sys.argv[7]
    else:
        # 参数为空，使用默认值
        proxy_protocol = ""
        proxy_address = "-"
        proxy_port = "-"
        proxy_username = "-"
        proxy_password = "-"
        download_url = ""
        save_path = ""

    create_gui(proxy_protocol, proxy_address, proxy_port, proxy_username, proxy_password, download_url, save_path)

if __name__ == "__main__":
    main()
