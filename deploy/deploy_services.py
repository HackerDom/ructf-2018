import os
import re
import shutil

from config import CONFIG, SERVICES_PATH, NGINX_CONF_PATH

STATIC_LOCATION_TEMPLATE = """
    location /%s {
                alias %s;
        }
"""

NGINX_CONF_TEMPLATE = """server {
        listen %d default_server;
        server_name %s;
        %s
        location / {
                proxy_pass http://0.0.0.0:%d;
        }
}"""


def render_nginx_conf(name, external_port, docker_port, static_dir_path, static_dir_full_path):
    static_record = STATIC_LOCATION_TEMPLATE % (static_dir_path, static_dir_full_path)\
        if static_dir_path is not None else ""
    return NGINX_CONF_TEMPLATE % (
        external_port,
        name,
        static_record,
        docker_port,
    )


def find_ports(service_name):
    flag = False
    with open(os.path.join(SERVICES_PATH, service_name, 'docker-compose.yml')) as service_file:
        for line in service_file:
            if flag:
                ports = re.search(r'\"(\d+):(\d+)\"', line)
                return int(ports.group(1)), int(ports.group(2))
            if line.strip() == "ports:":
                flag = True


def main():
    print("copying files")
    if os.path.isdir(SERVICES_PATH):
        shutil.rmtree(SERVICES_PATH)
    shutil.copytree('../services', SERVICES_PATH)
    os.chdir(SERVICES_PATH)
    for service_name, service_settings in CONFIG.items():
        print("deploying", service_name)
        docker_port, external_port = find_ports(service_name)
        os.chdir(service_name)
        os.system('sudo docker-compose up -d')
        config = CONFIG[service_name]
        if not config.get('nonginx', False):
            with open(os.path.join(NGINX_CONF_PATH, 'sites-available', service_name), 'w') as nginx_conf:
                nginx_conf.write(render_nginx_conf(
                    service_name,
                    external_port,
                    docker_port,
                    config.get('static_dir_path', None),
                    os.path.join(os.getcwd(), config['static_dir_path']) if 'static_dir_path' in config else None,
                ))
            os.chdir('..')
            os.system('ln -s {} {}'.format(
                os.path.join(NGINX_CONF_PATH, 'sites-available', service_name),
                os.path.join(NGINX_CONF_PATH, 'sites-enabled', service_name),
            ))
    os.system('sudo service nginx restart')


if __name__ == '__main__':
    main()

