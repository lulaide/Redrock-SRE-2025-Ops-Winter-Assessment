# Python Docker Manager
此工具使用 Python编写，使用 [docker](https://pypi.org/project/docker/) 库与 docker进程 进行交互
[**@lulaide**](https://github.com/lulaide)
## 1.快速开始
- 安装依赖
```bash
pip install -r requirements.txt
```
- 查看帮助
```bash
python main.py --help
```
```bash
usage: main.py [-h] [-f COMPOSE_FILE] [--up] [--down]

Python Docker Manager

options:
  -h, --help            show this help message and exit
  -f COMPOSE_FILE, --file COMPOSE_FILE
                        指定docker-compose文件路径，默认当前目录下的docker-compose.yml
  --up                  启动docker-compose
  --down                停止docker-compose,删除容器
  ```
  - 启动示例
  ```bash
  python main.py -f docker-compose.yml --up
  ```
  ```bash
  
            ____                        _                  _                  
            |  _ \   _   _            __| |   ___     ___  | | __   ___   _ __ 
            | |_) | | | | |  _____   / _` |  / _ \   / __| | |/ /  / _ \ | '__|
            |  __/  | |_| | |_____| | (_| | | (_) | | (__  |   <  |  __/ | |   
            |_|      \__, |          \__,_|  \___/   \___| |_|\_\  \___| |_|   
                    |___/                                                     
        
2025-03-01 03:13:05,974 - INFO - ================ Python Docker Manager Log================
2025-03-01 03:13:05,976 - INFO - 日志记录开始
2025-03-01 03:13:05,976 - INFO - 命令行参数:Namespace(compose_file='docker-compose.yml', up=True, down=False)
2025-03-01 03:13:05,993 - INFO - Docker连接成功!
2025-03-01 03:13:06,000 - INFO - Docker版本: 27.3.1-1
2025-03-01 03:13:06,003 - INFO - 正在启动docker-compose
2025-03-01 03:13:06,003 - INFO - 正在创建网络和卷
2025-03-01 03:13:06,010 - INFO - 网络:lamp_network已经存在,跳过创建
2025-03-01 03:13:06,010 - INFO - 网络和卷创建完成,开始启动服务
2025-03-01 03:13:06,978 - INFO - 拉取镜像:mysql:latest成功
2025-03-01 03:13:06,979 - INFO - 服务: mysql  镜像: mysql:latest  容器名称: mysql_container
2025-03-01 03:13:07,488 - INFO - 启动服务:mysql
2025-03-01 03:13:07,489 - INFO - 容器名称:mysql_container
2025-03-01 03:13:07,489 - INFO - 容器ID:fe3e6f25a221c35b80aebb5055cd51d0ffde8d50db033867b92ae69654687ecc
```
- 关闭 `Python Docker Manager`
```bash
python main.py -f docker-compose.yml --down
```
```bash
2025-03-01 03:15:11,026 - INFO - ================ Python Docker Manager Log================
2025-03-01 03:15:11,026 - INFO - 日志记录开始
2025-03-01 03:15:11,026 - INFO - 命令行参数:Namespace(compose_file='docker-compose.yml', up=False, down=True)
2025-03-01 03:15:11,035 - INFO - Docker连接成功!
2025-03-01 03:15:11,042 - INFO - Docker版本: 27.3.1-1
2025-03-01 03:15:11,043 - INFO - 正在停止docker-compose
2025-03-01 03:15:11,044 - INFO - 读取到的服务:
2025-03-01 03:15:11,044 - INFO - 服务: mysql  容器名称: mysql_container
2025-03-01 03:15:12,132 - INFO - 停止并删除服务:mysql,容器名称:mysql_container,容器ID:fe3e6f25a221c35b80aebb5055cd51d0ffde8d50db033867b92ae69654687ecc
2025-03-01 03:15:12,133 - INFO - ['mysql_container']已停止运行,1个容器已删除
```
## 2.已实现功能
|功能|Y/N|
|----|---|
|能识别 Docker-Compose 文件中的 volumes，ports，environment，container_name 和 image 字段，并能成功启动和停止容器|✅|
|每次启动时拉取镜像|✅|
|完成对卷和网络的支持|✅|
|详细的运行日志|✅|
|自动打包大于5M的日志|✅|
|支持自定义 build|❌|
|处理 depends_on|❌|