"""
This file is used to configure application settings.

Do not import this file directly.

You can use the settings API via:

    from ferris import settings

    mysettings = settings.get("mysettings")

The settings API will load the "settings" dictionary from this file. Anything else
will be ignored.

Optionally, you may enable the dynamic settings plugin at the bottom of this file.
"""

settings = {}

settings['timezone'] = {
    'local': 'US/Eastern'
}

settings['email'] = {
    # Configures what address is in the sender field by default.
    'sender': 'zenblip <notification@zenblip.com>'
}

settings['app_config'] = {
    'webapp2_extras.sessions': {
        # WebApp2 encrypted cookie key
        # You can use a UUID generator like http://www.famkruithof.net/uuid/uuidgen
        'secret_key': '9a788030-837b-11e1-b0c4-0800200c9b77',
    }
}

settings['oauth2'] = {
    # OAuth2 Configuration should be generated from
    # the google cloud console (Credentials for Web Application)
    'client_id': None,  # XXXXXXXXXXXXXXX.apps.googleusercontent.com
    'client_secret': None,
    'developer_key': None  # Optional
}

settings['oauth2_service_account'] = {
    # OAuth2 service account configuration should be generated
    # from the google cloud console (Service Account Credentials)
    'client_email': None,  # XXX@developer.gserviceaccount.com
    'private_key': None,  # Must be in PEM format
    'developer_key': None  # Optional
}

settings['upload'] = {
    # Whether to use Cloud Storage (default) or the blobstore to store uploaded files.
    'use_cloud_storage': True,
    # The Cloud Storage bucket to use. Leave as "None" to use the default GCS bucket.
    # See here for info: https://developers.google.com/appengine/docs/python/googlecloudstorageclient/activate#Using_the_Default_GCS_Bucket
    'bucket': None
}

# Enables or disables app stats.
# Note that appstats must also be enabled in app.yaml.
settings['appstats'] = {
    'enabled': False,
    'enabled_live': False
}


# IP DB
settings['db_ip_api_keys'] = ['b5547cd128bdb0bf797ae83e11bac77ee158b0bf',
                              '613c32282ed353efc9f26fb45b6b2d38cff6174a',
                              '30fb01d80b49d119518e665871c32d5c4c3af8a7']
settings['db_ip_base_url'] = 'http://api.db-ip.com/addrinfo'

# Optionally, you may use the settings plugin to dynamically
# configure your settings via the admin interface. Be sure to
# also enable the plugin via app/routes.py.

#import plugins.settings

# import any additional dynamic settings classes here.

# import plugins.my_plugin.settings

# Un-comment to enable dynamic settings
# plugins.settings.activate(settings)

# Project Secret
settings['PROJECT_SECRET'] = 'j34t5l3j'
settings['API_TOKEN_EXPIRE'] = 86400 * 30
# API key secret salt
settings['API_SECRET_SALTS'] = ['3$DF1k_3tqeghkqGQETG#TGAasfq3g35GQ']
settings['API_SECRET_AES_KEY'] = '8D1e5Bd1-5S07-45'  # length of 16
