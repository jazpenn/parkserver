# -*- coding: utf-8  -*-


import json
import requests



class PushStream(object):


    def __init__(self,base_url=None):

        self.CHAT_SERVER_URL = base_url


    def pub_message(self,room,message,data,token=''):

        pub_url = self.CHAT_SERVER_URL + '/pub?id=' + str(room)

        _data = json.dumps({message:data})

        res = requests.post(pub_url,data=_data)

        print(res.text)


    def status(self,room):

        status_url = self.CHAT_SERVER_URL + '/channels-stats?id=' + str(room)

        res = requests.get(status_url)

        return res.json()

    def pub_all(self):
        """
        向所有的房间发一个消息
        """
        pass








