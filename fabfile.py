"""
    REQUIREMENTS:
        - install pip with distribute (http://packages.python.org/distribute/)
        - sudo pip install Fabric

"""

from fabric.api import *

def start(mode="normal"):
    """
        HOW TO RUN:

            option 1) fab start
            option 2) fab start:clear

    """
    if mode == "clear":
        local("dev_appserver.py . --host localhost --port 8888 --clear_datastore")
    else:
        local("dev_appserver.py . --host localhost --port 8888")

def deploy(app_id="zenblip", version=""):
    """
        app.yaml never has to be version:default

        HOW TO RUN:

            option 1) fab deploy
            option 2) fab deploy:preview
            option 3) fab deploy:prod
            option 4) fab deploy:homo

    """

    #local("appcfg.py --no_cookies --oauth2 -A {0} -V {1} update .".format(app_id, version))
    if version:
        local("appcfg.py --email=sushi@zenblip.com -A {0} -V {1} update .".format(app_id, version))
    else:
        local("appcfg.py --email=sushi@zenblip.com -A {0} update .".format(app_id))

def clean(mode="cert"):
    """
        remove local cert to solve fancy_urllib.InvalidCertificateException

        HOW TO RUN:

            option 1) fab clean
            option 2) fab clean:cert

    """

    local("rm /Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine/lib/cacerts/cacerts.txt")

def test(level='INFO'):
    """
    run ferri test
    """
    
    #test libs
    with lcd("libs"):
        local("python -m unittest discover")
        
    #test app
    local("nosetests --with-ferris --logging-level=%s app/tests" % level)
    
def autopep8(dir_or_file):
    """
    auto fix pep8; pip install --upgrade autopep8
    """
    local('autopep8 --exclude venv -aaair --max-line-length 140 %s' % dir_or_file)

def rollback():
    """
    auto fix pep8; pip install --upgrade autopep8
    """
    local("appcfg.py --email=sushi@zenblip.com rollback .")
    
def z(plugin="chrome"):
    if plugin == "chrome":
        with lcd("chrome_plugin"):
            local("rm -rf dashboard/.sass-cache/")
            local("rm -rf dashboard/js-build/.module-cache/")
            local("zip zb.zip * -v -r -x *.sass-cache* *sass* *.module-cache* *.sh* test/* *.html")

def firefox(action="activate"):
    """
    WARNING: not usable
    """
    if action == 'activate':
        with lcd("/Users/sushih-wen/Code/addon-sdk-1.17/"):
            local('source bin/activate')
    elif action == 'run':
        with lcd('firefox_plugin'):
            local('cfx run')
