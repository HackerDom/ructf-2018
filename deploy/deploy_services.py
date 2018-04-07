import os
import re
import shutil

from config import CONFIG, SERVICES_PATH, NGINX_CONF_PATH


NGINX_CONF_TEMPLATE = """server {
        listen %d default_server;

        server_name %s;

        location /%s {
                alias %s;
        }
        location / {
                proxy_pass http://0.0.0.0:%d;
        }
}"""


def render_nginx_conf(name, external_port, docker_port, static_dir_path, static_dir_full_path):
    return NGINX_CONF_TEMPLATE % (
        external_port,
        name,
        static_dir_path,
        static_dir_full_path,
        docker_port,
    )


def find_ports(service_name):
    flag = False
    with open(os.path.join(SERVICES_PATH, service_name, 'docker-compose.yml')) as service_file:
        for line in service_file:
            if flag:
                ports = re.search(r'\"(\d{4}):(\d{4})\"', line)
                return int(ports.group(1)), int(ports.group(2))
            if line.strip() == "ports:":
                flag = True


def main():
    print("copying files")
    shutil.rmtree(SERVICES_PATH)
    shutil.copytree('../services', SERVICES_PATH)
    os.chdir(SERVICES_PATH)
    for service_name, service_settings in CONFIG.items():
        print("deploying", service_name)
        docker_port, external_port = find_ports(service_name)
        os.chdir(service_name)
        os.system('sudo docker-compose up -d')
        config = CONFIG[service_name]
        with open(os.path.join(NGINX_CONF_PATH, 'sites-available', service_name), 'w') as nginx_conf:
            nginx_conf.write(render_nginx_conf(
                service_name,
                external_port,
                docker_port,
                config['static_dir_path'],
                os.path.join(os.getcwd(), config['static_dir_path']),
            ))
        os.chdir('..')
        os.system('ln -s {} {}'.format(
            os.path.join(NGINX_CONF_PATH, 'sites-available', service_name),
            os.path.join(NGINX_CONF_PATH, 'sites-enabled', service_name),
        ))
    os.system('sudo service nginx restart')


if __name__ == '__main__':
    main()
