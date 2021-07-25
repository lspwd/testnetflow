#!/usr/bin/env python
import os
import csv
import argparse
import yaml

try:
    import json
except ImportError:
    import simplejson as json

intCompArray = [
    'cmdbroker', 'pdbroker', 'pdnfs', 'pdweb', 'gameadmincdn', 'gsbroker', 'gsdynbroker',
    'cmddb', 'cmdpam', 'cmdconnect', 'cmdsync', 'cmdasync', 'cmdcontrol', 'cmdcontrolsolr', 'cmdcontrolgk',
    'cmdcontrolapache', 'cmdpad', 'cmdpadgk', 'cq5publish', 'cq5author', 'igamingrest', 'pddb', 'pdsecgateway', 
    'pdadmin', 'estega', 'pdgaming', 'pdcore', 'subcapst', 'subcapstint', 'pdloyalty', 'pdprocesses', 
    'payweb', 'payboweb', 'paycashier', 'payfe', 'paycs', 'paypg', 'payxs', 'paydb', 'paybroker', 'scdb',
    'scadmin', 'scapp', 'payapp', 'payboapp', 'cmdbosvc', 'pokerpx', 'cmdbot', 'pokerboapp', 'pokergp', 'payboapp',
    'bingomanager', 'jackpot', 'scboapp', 'bingoweb', 'payapp', 'bingochat', 'pokerdb', 'snsapp'
]
'''
Tuple definition: host, port, try_to_spawn_socket_on_remote_server, type (vip, prod, mgmt, nfs)
'''
relCompArray = {}

# Used to build config structure
relations = {}

# Final array of all relationships used to create the yaml file
config_out = []

compArray = intCompArray[:]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--propsDir', action='store')
    parser.add_argument('-r', '--relationsDir', action='store')
    parser.add_argument('-u', '--user', action='store')
    parser.add_argument('-p', '--password', action='store')
    parser.add_argument('-o', '--outDir', action='store')
    args = parser.parse_args()
    print("Using compArray:")
    print("[" + ', '.join(compArray) + "]")
    counter_array = [0] * len(compArray)

    # Load relations file
    with open(args.relationsDir + "relations.yml", 'r') as stream:
        rel_data = yaml.safe_load(stream)
    for client in rel_data:
        relCompArray[client] = []
        for server in rel_data[client]:
            relCompArray[client].append((server, rel_data.get(client, None).get(server, None).get('port', None),
                                         rel_data.get(client, None).get(
                                             server, None).get('vip_port', None),
                                         rel_data.get(client, None).get(server, None).get('try_to_spawn_socket_on_remote_server', None)))
    print(relCompArray)

    print("Reading properties.json ...")
    pf = open(args.propsDir + "properties.json", 'r').read()
    p = json.loads(pf)
    print(json.dumps(p, indent=2))

    prod_he = {}
    nfs_he = {}
    vip_he = {}
    for i in compArray:
        prod_he[i + "00" + p['prodSuffix']] = "127.0.0.1"
        nfs_he[i + "00" + p['nfsSuffix']] = "127.0.0.1"

    host_prefix = p['siteID'] + "-" + p['envID'] + "-"

    print("Reading hosts.csv...")
    hcsv_file = open(args.propsDir + "hosts.csv", 'r')
    hcsv_reader = csv.reader(hcsv_file)
    hosts = []
    for row in hcsv_reader:
        # print(','.join(row))
        hosts.append(row[0])
        if len(row) == 4 and row[0] in compArray:
            c = counter_array[compArray.index(row[0])]
            counter_array[compArray.index(row[0])] = c + 1
            key_prefix = row[0] + str(c).rjust(2, '0')

            if row[1] != "":
                prod_he[key_prefix + p['prodSuffix']] = row[1]
                if row[0] in relCompArray:
                    client = {'ssh_client_ip_address': str(host_prefix + key_prefix + p['prodSuffix']),
                              'ssh_client_username': args.user, 'ssh_client_password': args.password,
                              'server_list_to_test': [], 'simple_name': row[0]}
                    relations[key_prefix + p['prodSuffix']] = client
            else:
                prod_he[key_prefix + p['prodSuffix']] = "127.0.0.1"
            if row[3] != "":
                nfs_he[key_prefix + p['nfsSuffix']] = row[3]
                if row[0] in relCompArray:
                    client = {'ssh_client_ip_address': str(host_prefix + key_prefix + p['nfsSuffix']),
                              'ssh_client_username': args.user, 'ssh_client_password': args.password,
                              'server_list_to_test': [], 'simple_name': row[0]}
                    relations[key_prefix + p['nfsSuffix']] = client
            else:
                nfs_he[key_prefix + p['nfsSuffix']] = "127.0.0.1"

    for i in compArray:
        vip_he[i + p['vipSuffix']] = prod_he[i + "00" + p['prodSuffix']]

    print("Reading vips.csv...")
    vips = []
    vcsv_file = open(args.propsDir + "vips.csv", 'r')
    vcsv_reader = csv.reader(vcsv_file)
    for row in vcsv_reader:
        print(','.join(row))
        if len(row) == 2 and row[0] in compArray:
            vips.append(row[0])
            if row[1] != "":
                vip_he[row[0] + p['vipSuffix']] = row[1]

    # Check if all hosts are defined in hosts.csv or vips.csv
    def recursive_items(dictionary):
        for key, value in dictionary.items():
            if type(value) is dict:
                yield (key, value)
                yield recursive_items(value)
            else:
                yield (key, value)

    not_defined_hosts = []
    for key, value in recursive_items(relCompArray):
        print(key)
        if key not in hosts and key not in vips:
            not_defined_hosts.append(key)

    if len(not_defined_hosts) > 0:
        raise SystemExit('Server {} ip not defined in hosts.csv or vips.csv'.format(
            [h for h in not_defined_hosts]))

    all_hosts = {}
    all_hosts.update(prod_he)
    all_hosts.update(nfs_he)
    for r in relations:
        server_list_to_test = []
        if relations[r]['simple_name'] in relCompArray:
            # print(relCompArray[relations[r]['simple_name']])
            for rc in relCompArray[relations[r]['simple_name']]:
                # print(rc)
                servers_to_test = dict(
                    filter(lambda item: item[0].startswith(rc[0]), all_hosts.items()))
                for server in servers_to_test:
                    print(servers_to_test[server])
                    if servers_to_test[server] != '127.0.0.1':
                        # Check if vip_port is defined
                        if rc[2] is not None:
                            vip_servers_to_test = dict(
                                filter(lambda item: item[0].startswith(rc[0]), vip_he.items()))
                            if ',' in str(rc[1]) and len(rc[1].split(',')) > 1:
                                print('Found multiple ports')
                                ports = rc[1].split(',')
                                for p in ports:
                                    server_list_to_test.append({
                                        'ssh_server_ip_address': str(host_prefix + server),
                                        'ssh_server_username': args.user,
                                        'ssh_server_password': args.password,
                                        'try_to_spawn_socket_on_remote_server': rc[2],
                                        'socket_to_test': [{
                                            'address': str(host_prefix + server),
                                            'port': int(p),
                                            'under_load_balancer': True,
                                            'load_balancer_address': str(host_prefix + server_vip) + ':' + str(p)
                                        } for server_vip in vip_servers_to_test]
                                    })
                            else:
                                server_list_to_test.append({
                                    'ssh_server_ip_address': str(host_prefix + server),
                                    'ssh_server_username': args.user,
                                    'ssh_server_password': args.password,
                                    'try_to_spawn_socket_on_remote_server': rc[2],
                                    'socket_to_test': [{
                                        'address': str(host_prefix + server),
                                        'port': rc[1],
                                        'under_load_balancer': True,
                                        'load_balancer_address': str(host_prefix + server_vip) + ':' + str(rc[1])
                                    } for server_vip in vip_servers_to_test]
                                })
                        # Check if port is defined
                        if rc[1] is not None:
                            if ',' in str(rc[1]) and len(rc[1].split(',')) > 1:
                                print('Found multiple ports')
                                ports = rc[1].split(',')
                                for p in ports:
                                    server_list_to_test.append({
                                        'ssh_server_ip_address': str(host_prefix + server),
                                        'ssh_server_username': args.user,
                                        'ssh_server_password': args.password,
                                        'try_to_spawn_socket_on_remote_server': rc[2],
                                        'socket_to_test': [{
                                            'address': str(host_prefix + server),
                                            'port': int(p),
                                            'under_load_balancer': False,
                                            'load_balancer_address': ''
                                        }]
                                    })
                            else:
                                server_list_to_test.append({
                                    'ssh_server_ip_address': str(host_prefix + server),
                                    'ssh_server_username': args.user,
                                    'ssh_server_password': args.password,
                                    'try_to_spawn_socket_on_remote_server': rc[2],
                                    'socket_to_test': [{
                                        'address': str(host_prefix + server),
                                        'port': rc[1],
                                        'under_load_balancer': False,
                                        'load_balancer_address': ''
                                    }]
                                })
                    relations[r]['server_list_to_test'] = server_list_to_test

    config_output = []
    for r in relations:
        del relations[r]['simple_name']
        config_output.append({'client': relations[r]})

    with open(args.outDir + r'config.yml', 'w') as file:
        documents = yaml.dump(config_output, file,
                              default_flow_style=False)


if __name__ == '__main__':
    main()
