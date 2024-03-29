# Tested with CherryPy 3.1.2
import cherrypy
expose = cherrypy.expose

# Tested with Django 1.1
from django.conf import settings
from django.template import loader, Context

import os.path
from StringIO import StringIO

from kahnsept import *

""" Configure server and django templates """
cur_dir = os.path.dirname(__file__)
config_file = os.path.join(cur_dir, 'web_server.conf')
print "Templates: %s" % os.path.join(cur_dir, 'templates')
settings.configure(TEMPLATE_DIRS=(os.path.join(cur_dir, 'templates').replace('\\', '/'),),
                   TEMPLATE_LOADERS = ('django.template.loaders.filesystem.load_template_source',)
                   )

# We want a persisent global Kahnsept world for all web requests - this only works if
# all requests share the same process space (single thread?)
world = World()
error = ""
keep_running = True
history = []
count = 0

class KHandler(object):
    """ Handle web requests for Kahnsept commands """

    @expose
    def index(self):
        global world, error, history
        
        string_file = StringIO()
        world.write_json(string_file)
        return render_to_string('home.html', {'body':string_file.getvalue(), 'error':error, 'history':history})
        
    @expose
    def command(self, command=None):
        global world, error, history, count

        result = None
        error = ""
        
        count += 1

        try:
            try:
                result = eval(command, globals(), World.scope)
            except SyntaxError:
                result = "(Command completed)"
                exec command in globals(), World.scope
        except Exception, e:
            result = None
            error = "Eval error: %r" % e
        else:
            history.insert(0, {'counter': count, 'command':command, 'result':result})

        raise cherrypy.HTTPRedirect('/')
    
def render_to_string(template_name, d):
    """ django template helper function - like render_to_response """
    t = loader.get_template(template_name)
    c = Context(d)
    return t.render(c)
                
if __name__ == '__main__':
    cherrypy.quickstart(KHandler(), config=config_file)
