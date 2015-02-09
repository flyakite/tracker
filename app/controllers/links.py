'''
Created on 2014/8/23

@author: sushih-wen
'''


import logging
from google.appengine.ext import ndb
from ferris import route_with
from app.models.link import Link
from app.models.access import Access
from app.models.signal import Signal
from accesses import Accesses


class Links(Accesses):

    @route_with('/l')
    def redirect_to_original_url(self):
        """
        1. redirect to original link
        2. save access record
        """

        #actually, this is not a json view. 
        #But if not specified, TemplateNotFound occurs in unittest
        self.meta.change_view('json') 
        
        token = self.request.get('t')
        url_id = self.request.get('h')  # url hash
        sync = self.request.get('sync', None)

        if not token or not url_id:
            logging.error('link not found: %s %s' % (token, url_id))
            self.abort(404)

        link = Link.find_by_properties(token=token, url_id=url_id)
        if not link:
            logging.error('link not found2: %s %s' % (token, url_id))
            self.abort(404)

        signal = Signal.find_by_properties(token=token)
        if not signal:
            logging.error('no signal')
            return

        accessor, ass = self._recognize_user(signal, sync)
        
        # prevent self access
        if accessor and signal.sender in accessor.keys():
            logging.info('self access')
        else:
            access = self._create_link_access_record(signal, link, accessor, ass, sync=sync)
            link.access_count += 1
            link.is_accessed = True
            link.country = access.country
            link.city = access.city
            link.device = access.device
            link.put()

        return self.redirect(str(link.url))

    def _create_link_access_record(self, signal, link, accessor, ass, sync=False):
        """
        """
        # TODO: should it be moved to taskqueue

        source = self._get_source_info()

        access = Access(parent=signal.key,
                        token=signal.token,
                        sender=signal.sender,
                        accessor=accessor.keys()[0] if accessor else None,
                        accessor_name=accessor[accessor.keys()[0]] if accessor else None,
                        url=link.url,
                        ass=ass if ass else None,
                        ip=self.request.remote_addr,
                        user_agent=self.request.headers.get('User-Agent', None),
                        proxy=source.proxy,
                        device=source.device,
                        tz_offset=source.tz_offset if source else None,
                        country=source.country if source else None,
                        city=source.city if source else None,
                        kind='link'
                        )
        # TODO: make it async
        # https://developers.google.com/appengine/docs/python/ndb/async?hl=es#Future_wait_any
        #access.put() if sync else access.put_async()
        access.put()
        self._notify_sender(signal, access, sync=sync)
        return access

    @route_with('/resource/links')
    def get_links(self):
        self.meta.change_view('json')
        self._enable_cors()
        
        sender = self.request.get('sender')
        accessed = self.request.get('accessed')
        logging.info('sender %s' % sender)
        if not sender:
            logging.error('no sender')
            return
        
        if accessed:
            #TODO: filter is_accessed
            links = Link.query(Link.sender==sender, Link.is_accessed==True).order(-Link.created).fetch(50)
        else:
            links = Link.query(Link.sender==sender).order(-Link.created).fetch(50)
        self.context['data'] = dict(data=[l.to_dict(
            include=['token', 'subject', 'url', 'access_count', 'receiver_emails',
            'country', 'city', 'device', 
            'created', 'modified']) for l in links])
