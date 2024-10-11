# 下载器使用说明

## 使用方法
```
c:\路桥\download.exe http 127.0.0.1 10809 - - https://www.python.org/ftp/python/3.12.6/python-3.12.6-amd64.exe c:/1.zip
```
## 参数说明

下载器的完整路径：c:\路桥\download.exe  
代理协议：`http` 或 `https`  
代理地址：127.0.0.1  
代理端口：10809  
代理用户名：代理的用户名（若无则输入 `-`）  
代理密码：代理的密码（若无则输入 `-`）  
网络文件 URL：[要下载的文件的 URL](https://www.python.org/ftp/python/3.12.6/python-3.12.6-amd64.exe)  
存放绝对路径：c:/1.zip

每个参数之间用空格隔开，代理用户名和代理密码为空时输入 `-`。

## 功能

1. 多线程下载
2. 支持 HTTP/HTTPS 代理
3. 断点续传
4. 下载完毕自动关闭窗口
5. 下载失败可重试
6. 日志记录功能
7. 自定义广告：替换 `1.png` 和 `1.txt`
8. 删除广告：直接删除 `1.png` 和 `1.txt`
9. 文件重复下载时直接显示下载完成

## 说明

该工具旨在弥补自动操作魔法师无法使用代理下载文件的局限性。
##演示图片:![下载器界面](https://github.com/BsaLee/luqiao_download/raw/main/%E5%9B%BE%E7%89%87_20241011233616.png)

