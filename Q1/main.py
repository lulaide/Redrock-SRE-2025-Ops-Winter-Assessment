import yaml
import docker
import argparse
import logging
import zipfile
import os

def exit_and_log(msg, code=0):
    if code == 0:
        logging.info(msg)
    else:
        logging.error(msg)
    exit(code)

def zip_log():
    if os.path.exists('latest.log'):
        print('检测到上一次的日志文件:latest.log')
        try:
            with open('latest.log', 'r', encoding='utf-8') as file:
                # 读取前19个字符，作为日志时间
                content = file.read(19)
                log_time = '_'.join(content.split(' ')).replace(':', '-')
                with zipfile.ZipFile(f'{log_time}.zip', 'w') as zip_file:
                    zip_file.write('latest.log')
                print('日志压缩成功:latest.log -> ' + f'{log_time}.zip')
            os.remove('latest.log')
        except Exception as e:
            print(f'日志压缩失败: {e}')

def main():

    # 设置运行参数

    parser = argparse.ArgumentParser(description="Python Docker Manager")
    parser.add_argument('-f', '--file', dest='compose_file', default='docker-compose.yml', help='指定docker-compose文件路径，默认当前目录下的docker-compose.yml')
    parser.add_argument('--up', action='store_true', help='启动docker-compose')
    parser.add_argument('--down', action='store_true', help='停止docker-compose，删除容器、网络和卷')
    parser.add_argument('-d', '--detached', action='store_true', help='后台运行docker-compose')
    args = parser.parse_args()

    print("""
  ____                        _                  _                  
 |  _ \   _   _            __| |   ___     ___  | | __   ___   _ __ 
 | |_) | | | | |  _____   / _` |  / _ \   / __| | |/ /  / _ \ | '__|
 |  __/  | |_| | |_____| | (_| | | (_) | | (__  |   <  |  __/ | |   
 |_|      \__, |          \__,_|  \___/   \___| |_|\_\  \___| |_|   
          |___/                                                     
        """)
    # 配置日志，日志写入文件
    zip_log()
    logging.basicConfig(
        filename='latest.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        encoding='utf-8')
    # 创建一个StreamHandler处理器，打印日志到控制台
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # 控制台日志级别

    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    console_handler.setFormatter(formatter)

    # 将StreamHandler添加到根logger
    logging.getLogger().addHandler(console_handler)
    logging.info("================ Python Docker Manager ================")
    logging.info('日志记录开始')
    logging.info('命令行参数:' + str(args))

    # 连接到docker

    try:
        client = docker.from_env()
        logging.info("Docker连接成功!")
        logging.info("Docker版本: " + client.version()['Version'])
    except Exception as e:
        exit_and_log(f"连接Docker失败:{e}", 1)

    # 读取docker-compose文件

    try:
        yaml_file = open(args.compose_file, 'r')
        compose_file = yaml.load(yaml_file, Loader=yaml.FullLoader)
        compose_list = list(compose_file.keys())
    except Exception as e:
        exit_and_log(f"读取docker-compose文件失败:{e}", 1)

    print(compose_list)

    # 检查docker-compose文件是否有效

    if "version"  not in compose_list or "services" not in compose_list:
        exit_and_log("无效的docker-compose文件", 1)
    else:
        version = compose_file["version"]
        services = compose_file["services"]

    if "networks" in compose_list:
        networks = compose_file["networks"]
    if "volumes" in compose_list:
        volumes = compose_file["volumes"]


if  __name__ == "__main__":
    main()
