import re


class ConfigLogic:
    def __init__(self, server_final_list, client_final_list):
        self.client_final_list = client_final_list
        self.server_final_list = server_final_list

    def __checkMgmtServerDuplicates(self, mgmtip, lst, socketlst):

        # print "-"*100
        # print "entro in __checkMgmtServerDuplicates"
        # print "-"*100

        for idx in range(len(lst)):

            # print "-"*40 +">"
            # print "LST[IDX][INDEX] ---> " +str(lst[idx][0].keys()[0])
            # print "MGMTIP ----> " +mgmtip
            # print "-"*40 +">"

            if mgmtip == lst[idx]["mgmtip"]:
                # print "Entro nella gestione duplicati di __checkMgmtServerDuplicates"
                for socket in socketlst:
                    # print "Socket analizzato " +str(socket)
                    if socket not in lst[idx]["socket"]:
                        # print "Socket da aggiungere " +str(socket) + " alla lista " +str(lst[idx]["socket"])
                        lst[idx]["socket"].append(socket)
                # print "__checkMgmtServerDuplicates ha fatto modifiche"
                return True
            else:
                continue
        # print "__checkMgmtServerDuplicates non ha fatto modifiche"
        return False

    def __addSocketToClient(self, lbsocketlst, dct):
        for socket in lbsocketlst:
            if socket not in dct["socket"]:
                # print "Socket da aggiungere " +str(socket) + " alla lista " +str(lst[idx]["socket"])
                dct["socket"].append(socket)

    def __normalizeList(self, lst):
        for (index, value) in enumerate(lst):
            if not value:
                lst.pop(index)

    def __internalLogicServer(self, dct, lst):

        # server[mgmtip],server[username],server[password],server[socket]

        # print "*"*100
        # print "Entro in __internalLogicServer"
        # print "Server Global list in entrata ---> " +str(lst)
        # print "*"*100

        found = ""
        for key in dct.keys():
            server = {}
            if key.find("mgmtserver") >= 0 and key != found:
                found = key
                server["mgmtip"] = dct[key]
                pattern = re.compile("[a-zA-Z]+([0-9]+)")
                # print "Found: " +found +" with value " +dct[key]
                match = pattern.match(found)
                try:
                    index_list = match.group(1)
                    for i in dct.keys():
                        # if i.find("hostserver"+index_list) >= 0:
                        if i == "hostserver" + index_list:
                            # print "In the second loop, looking for hostserver" +index_list
                            server["socket"] = dct[i].split(" ")
                            self.__normalizeList(server["socket"])

                        # elif i.find("usernameserver"+index_list) >= 0:
                        elif i == "usernameserver" + index_list:
                            server["username"] = dct[i]

                        # elif i.find("passwordserver"+index_list) >= 0:
                        elif i == "passwordserver" + index_list:
                            server["password"] = dct[i]
                        else:
                            continue
                    # print "Checking duplicates for " +server["mgmtip"]
                    if self.__checkMgmtServerDuplicates(server["mgmtip"], lst, server["socket"]):
                        # print "__checkMgmtServerDuplicates has found duplicated data!"
                        continue
                    else:
                        # print "duplicated data were not found !"
                        lst.append(server)

                except Exception, e:
                    raise NameError("Exception in __internalLogicServer method!", e)

                # print "Dizionario al termine del loop -> " +str(server)
            else:
                continue

        # print "*"*100
        # print "Esco da __internalLogicServer"
        # print "Server Global List in uscita dalla Logica di parsing -----> " +str(lst)
        # print "*"*100

        return lst

    def __internalLogicLoadBalancer(self, dct, lst):

        # server[mgmtip],server[username],server[password],server[socket]

        found = ""
        loadbalancer = {}
        loadbalancer["members"] = []
        clientsocket = []

        pattern = re.compile("lb([0-9]+)vip")
        for key in dct.keys():
            match = pattern.match(key)
            if match and key != found:
                try:
                    found = key
                    index_list = match.group(1)
                    loadbalancer["vip"] = dct[key]
                    clientsocket.append(dct[key])

                    found2 = ""

                    for i in dct.keys():

                        member = {}
                        search_string = "lb" + index_list + "membermgmtip([0-9]+)"
                        pattern2 = re.compile(search_string)
                        match2 = pattern2.match(i)

                        if match2 and i != found2:
                            found2 = i
                            member["mgmtip"] = dct[i]
                            index_list2 = match2.group(1)

                            for k in dct.keys():
                                if k.find("lb" + index_list + "memberusername" + index_list2) >= 0:
                                    member["username"] = dct[k]

                                elif k.find("lb" + index_list + "memberpassword" + index_list2) >= 0:
                                    member["password"] = dct[k]

                                elif k.find("lb" + index_list + "membersocket" + index_list2) >= 0:
                                    member["socket"] = [dct[k]]
                                else:
                                    continue

                            loadbalancer["members"].append(member)
                            self.__normalizeList(loadbalancer["members"])

                        else:
                            continue

                    # print "LB dict -> " +str(loadbalancer)

                    # lb[vip],lb[socket],lb[members]

                    for member in loadbalancer["members"]:

                        server = {}

                        server["mgmtip"] = member["mgmtip"]
                        server["username"] = member["username"]
                        server["password"] = member["password"]
                        server["socket"] = member["socket"]

                        # print "Server Dict from LB -> " +str(server)

                        if self.__checkMgmtServerDuplicates(server["mgmtip"], lst, server["socket"]):
                            # print "For Load Balancer __checkMgmtServerDuplicates has found duplicated data!"
                            continue
                        else:
                            # print "For Load Balancer duplicated data were not found !"
                            lst.append(server)

                except Exception, e:
                    raise NameError("Exception in __internalLogicLoadBalancer method!", e)

                # print "Lista in uscita! -->" +str(lst)
            else:
                continue

        return clientsocket

    def __internalLogicClient(self, dct):

        # print "*"*100
        # print "Entro in __internalLogicClient"
        # print "La lista degli Oggetti Client in entrata ---> " +str(dct)
        # print "*"*100
        tmp_server_list = []

        # client[mgmtip],client[username],client[password],client[socket]

        client = {}

        client["mgmtip"] = dct["mgmtclient"]
        client["username"] = dct["usernameclient"]
        client["password"] = dct["passwordclient"]

        for key in dct.keys():
            if key.find("hostserver") >= 0:
                # print dct[key]
                # print dct[key].split(" ")
                # Problema di configurazione dei duplicati su client
                # tmp_server_list.append(dct[key].split(" "))
                for socket in dct[key].split(" "):
                    if socket not in tmp_server_list:
                        tmp_server_list.append(socket)
            else:
                continue
        self.__normalizeList(tmp_server_list)
        client["socket"] = tmp_server_list

        # print "*"*100
        # print "Esco da __internalLogicClient"
        # print "La lista degli Oggetti Client in uscita ---> " +str(client)
        # print "*"*100

        return client

    def internalLogicP2p(self, dct):

        p2plist = []
        p2plist = dct["p2phostlist"].split(" ")
        self.__normalizeList(p2plist)
        return p2plist

    def mainLogic(self, configlist, serverlist, clientlist):
        for idx in range(len(configlist)):

            clientdct = {}
            p2pserver = []

            #			print "In Entrata Nel Main CFG Logic - con Indice: ->" +str(idx)
            #			print "self.client_final_list: ->" +str(clientlist)
            #			print "self.serverlist: ->" +str(clientlist)
            #
            clientdct = self.__internalLogicClient(configlist[idx])

            self.__internalLogicServer(configlist[idx], serverlist)

            if configlist[idx].has_key("lb1vip"):
                clientsocket = self.__internalLogicLoadBalancer(configlist[idx], serverlist)
                self.__addSocketToClient(clientsocket, clientdct)

            if configlist[idx].has_key("p2phostlist"):
                p2pserver = self.internalLogicP2p(configlist[idx])
                self.__addSocketToClient(p2pserver, clientdct)

            clientlist.append(clientdct)


        # print "In Uscita dal Main CFG Logic - con Indice: ->" +str(idx)
