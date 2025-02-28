import yaml
import docker
import argparse
import logging
import zipfile
import os

def print_hello_world():
    print(r"""
            ____                        _                  _                  
            |  _ \   _   _            __| |   ___     ___  | | __   ___   _ __ 
            | |_) | | | | |  _____   / _` |  / _ \   / __| | |/ /  / _ \ | '__|
            |  __/  | |_| | |_____| | (_| | | (_) | | (__  |   <  |  __/ | |   
            |_|      \__, |          \__,_|  \___/   \___| |_|\_\  \___| |_|   
                    |___/                                                     
        """)
def exit_and_log(msg, code=0):
    if code == 0:
        logging.info(msg)
    else:
        logging.error(msg)
    exit(code)

def zip_log():
    if os.path.exists('latest.log') and os.path.getsize('latest.log') > 1024*1024*5:
        print('检测日志文件 latest.log 超过5MB,开始压缩日志文件')
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

def pull_image(compose_file, client):
    services = compose_file.get("services")
    for service in services:
        image = services[service].get("image")
        try:
            client.images.pull(image)
            logging.info(f"拉取镜像:{image}成功")
        except Exception as e:
            exit_and_log(f"拉取镜像:{image}失败:{e}", 1)

def create_network_and_volumn(compose_file, client):
    logging.info("正在创建网络和卷")
    compose_list = list(compose_file.keys())
    # 启动服务之前创建相应的网络和卷
    if "networks" in compose_list:
        networks = compose_file["networks"]
        for network in networks:
            # 检查网络是否已经存在
            if client.networks.list(names=[network]):
                logging.info(f"网络:{network}已经存在,跳过创建")
                continue
            # 如果网络不存在，则创建网络
            if networks[network] == None:
                driver = "bridge"  # 默认使用bridge网络驱动
            else:
                driver = networks[network].get("driver", "bridge")
            client.networks.create(network, driver=driver)
            logging.info(f"创建网络:{network}成功,驱动:{driver}")
    if "volumes" in compose_list:
        volumes = compose_file["volumes"]
        for volume in volumes:
            # 检查卷是否已经存在
            if client.volumes.list(names=[volume]):
                logging.info(f"卷:{volume}已经存在,跳过创建")
                continue
            # 如果卷不存在，则创建卷
            if volumes[volume] == None:
                driver = "local"
            else:
                driver = volumes[volume].get("driver", "local")  # 默认使用local卷驱动
            client.volumes.create(volume, driver=driver)
            logging.info(f"创建卷:{volume}成功,驱动:{driver}")

    logging.info("网络和卷创建完成,开始启动服务")
def docker_compose_up(compose_file, client):
    compose_list = list(compose_file.keys())
    if "version"  not in compose_list or "services" not in compose_list:
        exit_and_log("无效的docker-compose文件", 1)
    create_network_and_volumn(compose_file, client)  # 创建网络和卷
    # 拉取镜像
    pull_image(compose_file, client)
    # 启动服务
    services = compose_file["services"]
    if len(services) == 0:
        exit_and_log("docker-compose文件中没有服务", 1)
        logging.info("读取到的服务:")
    for service in services:
        logging.info(f"服务: {service}  镜像: {services[service].get('image')}  容器名称: {services[service].get('container_name')}")
    containers = []
    for service in services:
        # 检查容器是否已经存在
        if not services[service].get("container_name"):
            exit_and_log(f"服务:{service}没有指定容器名称", 1)
        if client.containers.list(filters={"name": services[service].get("container_name")}):
            logging.warning(f"此服务的容器已经存在,跳过启动")
            continue
        container = client.containers.run(
            image=services[service].get("image"),
            name=services[service].get("container_name", None),  # 容器名称
            environment=services[service].get("environment", {}),  # 传递环境变量
            volumes={vol.split(":")[0]: {"bind": vol.split(":")[1], "mode": "rw"} for vol in services[service].get("volumes", [])},  # 处理卷挂载
            network=services[service].get("network", None),
            ports={f"{p.split(':')[0]}/tcp": int(p.split(":")[1]) for p in services[service].get("ports", [])},  # 端口映射
            detach=True  # 后台运行
        )
        containers.append(container)
        logging.info(f"启动服务:{service}")
        logging.info(f"容器名称:{container.name}")
        logging.info(f"容器ID:{container.id}")
    return containers
def docker_compose_down(compose_file, client):
    compose_list = list(compose_file.keys())
    if "version"  not in compose_list or "services" not in compose_list:
        exit_and_log("无效的docker-compose文件", 1)
    # 停止服务
    services = compose_file["services"]
    if len(services) == 0:
        exit_and_log("docker-compose文件中没有服务", 1)
    logging.info("读取到的服务:")
    for service in services:
        logging.info(f"服务: {service}  容器名称: {services[service].get('container_name')}")
    stopped_containers = []
    unrunning_containers = []
    for service in services:
        # 检查容器是否存在
        if not services[service].get("container_name"):
            exit_and_log(f"服务:{service}没有指定容器名称", 1)
        if not client.containers.list(filters={"name": services[service].get("container_name")}):
            logging.warning(f"此服务的容器不存在")
            continue
        container = client.containers.get(services[service].get("container_name"))
        if container.status == "running":
            container.stop()
            container.remove()
            stopped_containers.append(container.name)
            logging.info(f"停止并删除服务:{service},容器名称:{container.name},容器ID:{container.id}")
        else:
            unrunning_containers.append(container.name)
            logging.info(f"服务:{service}未运行,跳过执行")
    if stopped_containers:logging.info(f"{str(stopped_containers)}已停止运行,{len(stopped_containers)}个容器已删除")
    if unrunning_containers:logging.warning(f"{str(unrunning_containers)}未在运行,未执行删除操作,请检查容器状态")
    return 0

def main():
    # 设置运行参数
    parser = argparse.ArgumentParser(description="Python Docker Manager")
    parser.add_argument('-f', '--file', dest='compose_file', default='docker-compose.yml', help='指定docker-compose文件路径，默认当前目录下的docker-compose.yml')
    parser.add_argument('--up', action='store_true', help='启动docker-compose')
    parser.add_argument('--down', action='store_true', help='停止docker-compose,删除容器')
    args = parser.parse_args()

    if not args.down:print_hello_world()
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
    logging.info("================ Python Docker Manager Log================")
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

    except Exception as e:
        exit_and_log(f"读取docker-compose文件失败:{e}", 1)
    if args.up and args.down:
        exit_and_log("不能同时使用--up和--down参数", 1)
    if args.up:
        logging.info("正在启动docker-compose")
    #    try:
        docker_compose_up(compose_file, client)
    #    except Exception as e:
    #        exit_and_log(f"启动docker-compose失败:{e}", 1)
    if args.down:
        logging.info("正在停止docker-compose")
    #    try:
        docker_compose_down(compose_file, client)
    #    except Exception as e:
    #        exit_and_log(f"停止docker-compose失败:{e}", 1)
    if not args.up and not args.down:
        exit_and_log("请使用 --help 参数查看使用说明", 1)

if  __name__ == "__main__":
    main()
