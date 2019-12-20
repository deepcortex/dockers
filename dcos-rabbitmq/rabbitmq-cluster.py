#!/usr/bin/env python3
import logging
import os, os.path
import time
import socket
import requests
import shutil
import random

LOGGER = logging.getLogger(__name__)
APP_ID = os.getenv('MARATHON_APP_ID')
MESOS_TASK_ID = os.getenv('MESOS_TASK_ID')
MARATHON_AUTH = os.environ.get('MARATHON_AUTH', False)
DEFAULT_MARATHON_URI = 'http://marathon.mesos:8080' if not MARATHON_AUTH else 'https://master.mesos:8443'
MARATHON_URI = os.environ.get('MARATHON_URI', DEFAULT_MARATHON_URI)
HOST_IP = os.getenv('HOST', '127.0.0.1')
HOST_NAME = os.getenv('HOSTNAME')  # docker container_id

def get_authentication_token(marathon_client_marathon_username, marathon_client_marathon_password):
    payload = {"uid": marathon_client_marathon_username,"password": marathon_client_marathon_password}
    response = requests.post('https://master.mesos/acs/api/v1/auth/login', json=payload, verify=False)
    state = response.json()
    return state['token']

def get_marathon_app(app_id, authentication_token=None):
    response = requests.get('%s/v2/apps%s' % (MARATHON_URI, app_id)) if authentication_token is None else requests.get('%s/v2/apps%s' % (MARATHON_URI, app_id), headers={'Authorization': 'token=' + authentication_token}, verify=False)
    state = response.json()
    return state['app']


def get_marathon_tasks(app_id, authentication_token=None):
    response = requests.get('%s/v2/apps%s/tasks' % (MARATHON_URI, app_id)) if authentication_token is None else requests.get('%s/v2/apps%s/tasks' % (MARATHON_URI, app_id), headers={'Authorization': 'token=' + authentication_token}, verify=False)
    state = response.json()
    return state['tasks']


def get_node_ips(authentication_token=None):
    my_ip = ''
    other_ips = []
    if MARATHON_URI:
        LOGGER.info('Discovering configuration from %s for app %s', MARATHON_URI, APP_ID)
        tasks = get_marathon_tasks(APP_ID, authentication_token)
        LOGGER.info('Found %d tasks for %s', len(tasks), APP_ID)
        for task in tasks:
            if task['startedAt']:
                node_ip = task['host']
                # for private ips like in calico network, use ip per task
                # see https://mesosphere.github.io/marathon/docs/ip-per-task.html
                if 'ipAddresses' in task:
                    if len(task['ipAddresses']) > 0:
                        node_ip = task['ipAddresses'][0]['ipAddress']
                        LOGGER.info('Task ip is %s, slave ip is %s', node_ip, task['host'])

                LOGGER.info('Found started task %s at %s', task['id'], node_ip)
                if task['id'] == MESOS_TASK_ID:
                    my_ip = node_ip
                    LOGGER.info('My own ip/hostname is %s', my_ip)
                else:
                    other_ips.append(node_ip)
    return my_ip, other_ips


def wait_for_nodes_to_start(authentication_token=None):
    while True:
        current_app = get_marathon_app(APP_ID, authentication_token)
        configured_count = current_app['instances']
        running_count = current_app['tasksRunning']
        if running_count == configured_count:
            break
        LOGGER.info('%s is configured to have %d tasks,'
                    ' there are %d running tasks now,'
                    ' waiting for one minute...',
                    APP_ID, configured_count, running_count)
        time.sleep(5)
    LOGGER.info('%s has %d running tasks now', APP_ID, running_count)


def is_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.eror:
        return False


def get_node_name(node_ip):
    node_name = node_ip
    if is_ip(node_ip):
        node_name = node_ip.replace('.', '-')
    return node_name


def configure_name_resolving(current_node_ip, other_node_ips=None):
    LOGGER.info('Adding extra entries to /etc/hosts...')
    current_node_hostname = get_node_name(current_node_ip)
    with open('/etc/hosts', 'a') as f:
        LOGGER.info('Adding current node entries...')
        host_name_entry = '127.0.0.1 %s' % HOST_NAME
        f.write(host_name_entry + '\n')
        LOGGER.info('+' + host_name_entry)
        current_host_entry = '127.0.0.1 %s' % current_node_hostname
        f.write(current_host_entry + '\n')
        LOGGER.info('+' + current_host_entry)
        if other_node_ips:
            LOGGER.info('Adding other node entries...')
            for node_ip in other_node_ips:
                if node_ip != current_node_ip:
                    if not is_ip(node_ip):
                        # if mesos slaves using hostname instead of ip
                        # no need to add anything to /etc/hosts
                        # docker container is expected to resolve
                        # mesos-slave hostnames already.
                        LOGGER.info('Skipping %s, not an ip', node_ip)
                        continue
                    node_hostname = get_node_name(node_ip)
                    node_host_entry = '%s %s' % (node_ip, node_hostname)
                    f.write(node_host_entry + '\n')
                    LOGGER.info('+' + node_host_entry)
    LOGGER.info('Changing hostname as %s...', current_node_hostname)
    os.putenv('HOSTNAME', current_node_hostname)
    return current_node_hostname


def set_erlang_cookie():
    cookie_file = '/var/lib/rabbitmq/.erlang.cookie'
    rabbitmq_erlang_cookie = os.getenv('RABBITMQ_ERLANG_COOKIE', None)
    existing_rabbitmq_erlang_cookie = None
    cookie_file_exists = os.path.isfile(cookie_file)
    if cookie_file_exists:
        LOGGER.info('Found %s', cookie_file)
        with open(cookie_file, 'r') as f:
            existing_rabbitmq_erlang_cookie = f.read().strip()
            LOGGER.info('Existing erlang cookie is %s', existing_rabbitmq_erlang_cookie)

    if not rabbitmq_erlang_cookie and not existing_rabbitmq_erlang_cookie:
        raise RuntimeError('No erlang cookie is set!')

    if existing_rabbitmq_erlang_cookie\
            and existing_rabbitmq_erlang_cookie != rabbitmq_erlang_cookie:
        LOGGER.info('Changing erlang cookie to "%s"', rabbitmq_erlang_cookie)
        with open(cookie_file, 'w') as f:
            f.write(rabbitmq_erlang_cookie)

    if not existing_rabbitmq_erlang_cookie:
        LOGGER.info('Creating erlang cookie file with secret "%s"', rabbitmq_erlang_cookie)
        with open(cookie_file, 'w') as f:
            f.write(rabbitmq_erlang_cookie)
        shutil.chown(cookie_file, user='rabbitmq')
        os.chmod(cookie_file, 0o600)


def create_rabbitmq_config_file(node_ips=None):
    rabbitmq_config_file = '/etc/rabbitmq/rabbitmq.config'
    LOGGER.info('Creating %s', rabbitmq_config_file)
    default_user = os.getenv('RABBITMQ_DEFAULT_USER', 'guest')
    default_pass = os.getenv('RABBITMQ_DEFAULT_PASS', 'guest')
    default_vhost = os.getenv('RABBITMQ_DEFAULT_VHOST', '/')
    net_ticktime = os.getenv('RABBITMQ_NET_TICKTIME', '60')
    cluster_partition_handling = os.getenv('RABBITMQ_CLUSTER_PARTITION_HANDLING', 'ignore')
    rabbitmq_management_port = os.getenv('RABBITMQ_MANAGEMENT_PORT', '/')
    with open(rabbitmq_config_file, 'w') as f:
        f.write('[\n')
        f.write('  {kernel, [{net_ticktime,  %s}]},\n' % net_ticktime)
        f.write('  {rabbit,\n')
        f.write('    [\n')
        f.write('     {loopback_users, []},\n')
        f.write('     {heartbeat, 580},\n')
        f.write('     {default_user, <<"%s">>},\n' % default_user)
        f.write('     {default_pass, <<"%s">>},\n' % default_pass)
        f.write('     {default_vhost, <<"%s">>},\n' % default_vhost)
        f.write('     {cluster_partition_handling, %s},\n' % cluster_partition_handling)
        f.write('     {cluster_nodes, {[\n')
        if node_ips:
            nodes_str = ','.join(["'rabbit@%s'" % get_node_name(n)
                                  for n in node_ips])
            f.write('      %s\n' % nodes_str)
        f.write('      ], disc}}\n')
        f.write('    ]\n')
        f.write('  },\n')
        f.write('  {rabbitmq_management, [{listener, [{port, %s}]}]}\n'
                % rabbitmq_management_port)
        f.write('].\n')
    LOGGER.info('Done')


def configure_rabbitmq(current_node_hostname, node_ips):
    with open('/etc/rabbitmq/rabbitmq-env.conf', 'a') as f:
        f.write('NODENAME=rabbit@%s\n' % current_node_hostname)
    # other settings are already in environment like port settings, see Dockerfile
    path = '/var/lib/rabbitmq'
    for root, _, files in os.walk('/var/lib/rabbitmq'):
        for f in files:
            path = os.path.join(root, f)
            shutil.chown(path, user='rabbitmq')
    set_erlang_cookie()
    create_rabbitmq_config_file(node_ips)

def smallest(my_ip, other_ips):
    for ip in other_ips:
        if my_ip > ip:
            return False
        else:
            return True

def run():
    marathon_client_marathon_username = os.getenv('MARATHON_CLIENT_MARATHON_USERNAME', None)
    marathon_client_marathon_password = os.getenv('MARATHON_CLIENT_MARATHON_PASSWORD', None)
    authentication_token = None if not MARATHON_AUTH else get_authentication_token(marathon_client_marathon_username, marathon_client_marathon_password)
    wait_for_nodes_to_start(authentication_token)
    my_ip, other_ips = get_node_ips(authentication_token)
    current_node_hostname = configure_name_resolving(my_ip, other_ips)
    configure_rabbitmq(current_node_hostname, other_ips)
    import subprocess
    delay = 90

    if not smallest(my_ip, other_ips):
        time.sleep(delay)

    LOGGER.info('Launching server')
    subprocess.call(['/opt/rabbitmq/sbin/rabbitmq-server'], shell=False)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )
    run()
