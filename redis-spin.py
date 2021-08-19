from time import strftime
from sys import argv
from os import system, chdir, getcwd
import logging
from pydockercompose import DockerCompose, Service

logging.basicConfig(level=logging.DEBUG, filename="file.log")


def generate_development_redis_spin():
    redis_dockercompose = DockerCompose(file_name="docker-compose.yml", version="2.2")
    redis_dockercompose.add_network("redis-network", {"driver": "bridge"})
    redis_service = Service(image="redis:alpine",
                            networks=["redis-network"],
                            ports=["6379:6379"]
                            )
    redis_dockercompose.add_service("redis", redis_service)
    redis_dockercompose.add_volumes("redis-data", {"driver": "local"})
    return redis_dockercompose


def generate_production_redis_spin():
    redis_dockercompose = DockerCompose(file_name="docker-compose.yml", version="2")
    redis_dockercompose.add_network("redis-network", {"driver": "bridge"})

    redis_node_0_service = Service(image="redis:alpine",
                                   container_name="redis-0",
                                   networks=["redis-network"],
                                   ports=["6379:6379"],
                                   volumes=["./production/master_config/redis.conf:/usr/local/etc/redis/redis.conf"],
                                   commands="redis-server /usr/local/etc/redis/redis.conf --requirepass dadianas")

    redis_node_1_service = Service(image="redis:alpine",
                                   container_name="redis-1",
                                   networks=["redis-network"],
                                   ports=["7000:7000"],
                                   volumes=["./production/master_config/redis.conf:/usr/local/etc/redis/redis.conf"],
                                   commands="redis-server /usr/local/etc/redis/redis.conf --requirepass dadianas")

    redis_dockercompose.add_service("redis-0", redis_node_0_service)
    redis_dockercompose.add_service("redis-1", redis_node_1_service)

    return redis_dockercompose


def log_time(message):
    """
        This function helps to add time to log message
            message: the message that will be saved on the log file.
    """
    return strftime("%d/%m/%Y %H:%M:%S - " + message)


if __name__ == '__main__':
    try:
        if argv[1] == 'dev':
            generate_development_redis_spin().to_yaml(path="./development/")
            chdir(getcwd() + "/development")
            system("docker-compose up ")
        elif argv[1] == 'prod':
            generate_production_redis_spin().to_yaml(path="./production/")
            chdir(getcwd() + "/production")
            system("docker-compose up ")
    except:
        warning_message = """
        To use this script you should follow the following pattern:
        redis-spin.py <mode>
        where mode can be dev or prod.
        """
        logging.warning(log_time(warning_message))
        raise warning_message
