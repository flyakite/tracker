# -*- coding: utf-8 -*-
'''
Created on 2014/8/18

@author: sushih-wen
'''
import json
import datetime
import re
import logging
from uuid import uuid4
from urllib import urlencode
from google.appengine.api import users, urlfetch, channel
from google.appengine.ext import deferred
from ferris import Controller, route_with, scaffold
from ferris.core import mail
from ferris.core.template import render_template
from app.models.channel_client import ChannelClient
from base import BaseController


class Channels(BaseController):

    @route_with('/channels')
    def index(self):
        # render channel/index.html automatically
        pass

#         deferred.defer(channel.send_message, client_id, "Delay 2", _countdown=2)

#         self.context.update({
#                    "token":channel_token,
#                    "client_id":client_id
#                    })
#         return render_template("channel/index.html", context=context)

    def _create_token(self, owner, sync=False):
        logging.info('_create_token')
        logging.info(owner)
        client_id = str(uuid4()).replace("-", '')
        channel_token = channel.create_channel(client_id)
        cclient = ChannelClient.find_by_properties(owner=owner)
        if cclient:
            logging.info('token_exist')
            cclient.client_id = client_id
            cclient.channel_token = channel_token
        else:
            logging.info('token_create')
            cclient = ChannelClient(client_id=client_id,
                                    owner=owner,
                                    channel_token=channel_token)
        # TODO: async?
        cclient.put()  # if sync else cclient.put_async()

        return cclient.to_dict_output()

    @route_with('/channels/create_token')
    def create_token(self):
        self.meta.change_view('json')
        owner = self.request.get('owner')
        self.context['data'] = self._create_token(owner)
        self._enable_cors()

    @route_with('/channels/get_token')
    def get_token(self):
        self.meta.change_view('json')
        owner = self.request.get('owner')
        cclient = ChannelClient.find_by_properties(owner=owner)
        logging.info(cclient)
        if cclient:
            logging.info('found channel client in use by %s' % owner)
            self.context['data'] = cclient.to_dict_output()
        else:
            self.context['data'] = self._create_token(owner)
        self._enable_cors()

    @route_with('/message')
    def message(self):
        """
        This is just an example send_message
        """
        self.context.update({
            "token": self.session.get('channel_token'),
            "client_id": self.session.get('client_id')
        })
        if self.request.method == 'POST':
            message = self.request.params.get("message")
            logging.info('message')
            logging.info(message)
            client_id = self.session['client_id']
            channel.send_message(client_id, message)
            self.redirect('/message')

    @route_with('/_ah/channel/connected/')
    def connected(self):
        self.meta.change_view('json')
        logging.info('channel_connected')
        logging.info(self.request.params)
        self.context['data'] = {}

    @route_with('/_ah/channel/disconnected/')
    def disconnected(self):
        self.meta.change_view('json')
        logging.info('channel_disconnected')
        logging.info(self.request.params)
        self.context['data'] = {}
