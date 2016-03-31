'''!
@brief Module holds Legionn server application
@date Created on 9 Jan 2016
@author [Ryu-CZ](https://github.com/Ryu-CZ)
'''
  
from flask import Flask
from flask_restplus import Resource, Api, fields
from werkzeug.contrib.fixers import ProxyFix
import cores
  
app_name = 'Legionn'
app_version = 'v16.01.00'
__version__ = app_version

  
class Legionn(Api, cores.Core):
    '''!
    @brief Represents main Core of platform.
    Legionn platform is just another Core. Legionn adds new functionality as all Cores should do:
     * Legionn manages and contains other Cores as Units
     * Legionn implements web server with restful API to enable third sides communicate with Cores and Units
    '''
    def __init__(self, app, name=app_name, url_prefix="api/1", description='Main Core of Legionn platform', *args, **kwargs):
        #init Api
        Api.__init__(self, 
                     app=app, 
                     version='0.2', 
                     title='Legionn API', 
                     description=description,
                     contact='Tom Trval', 
                     contact_email='trval@kajot.cz',
                     tags=['unit','core','module', 'platform', 'python', 'flask'])
        self._api_namespace = self.namespace(url_prefix, description=description)
        #init Core
        cores.Core.__init__(self, 
                            name=name, 
                            description=description)
        self.init_resources()
      
    @property
    def cores(self):
        '''"cores" property is alias for "units" from interface Core.'''
        return self.units
      
    def __contains__(self, other):
        return other in self.cores
      
    def add(self, obj, name=None):
        '''!
        @brief inserts obj indo cores dict under gven key name
        @param obj: core to add
        @param name: name of record in cores dict
        '''
        #check for core duplicity
        if not isinstance(obj, cores.Core):
            raise TypeError('core is not Core type')
        name = name or obj._name
        if name in self.cores:
            raise KeyError('Core "{0}" is already placed in Legionn'.format(name))
        self.cores[name] = obj
          
    def remove(self, name):
        return cores.Core.remove(self, name)
      
    def activate(self, context=None):
        for i in range(len(self.cores)):
            self.cores[i].activate()
              
    def deactivate(self, context=None):
        for i in range(len(self.cores)):
            self.cores[i].deactivate()
      
    def init_resources(self):
        ns = self._api_namespace
        _cores = self.cores
        server_fields = ns.model('ServerInfo', {
            'name': fields.String(required=True, description='Server name'),
            'version': fields.String(required=True, description='Server version')
        })
        ns.model('Info', {'server':fields.Nested(server_fields, description='Server info group')})
        ns.model('Core', {
            'core_id': fields.String(required=True, description='The Core unique identifier'),
            'description': fields.String(required=True, description='The Core details')
            })
        ns.model('Unit', {
            'unit_id': fields.String(required=True, description='The Unit unique identifier')
            })
        @ns.route('/', '/index')
        @ns.doc('info')
        class IndexInfo(Resource):
            '''Shows a list of all todos, and lets you POST to add new tasks'''
            @ns.doc('get_info')
            @ns.marshal_with(ns.models['Info'], code=200)#, envelope='server')
            def get(self):
                '''Fetch server info'''
                return {'server':{'name':app_name, 'version':app_version}}
  
          
        @ns.route('/cores')
        class Cores(Resource):
            '''Shows a list of all Cores'''
            @ns.doc('list_cores')
            @ns.marshal_list_with(ns.models['Core'])
            def get(self):
                '''List Cores registered in this Legionn'''
                return [{'core_id':k, 'description':_cores[k].description} for k in sorted(list(_cores.keys()))]
 
 
        @ns.param('core_id', 'The Core identifier')
        @ns.route('/cores/<core_id>/units')
        @ns.response(404, 'Core not found')
        class CoreUnits(Resource):
            '''Shows a list of all Units of given Core'''
            @ns.doc('list_units')
            @ns.marshal_list_with(ns.models['Unit'])
            def get(self, core_id):
                '''List Units registered in given Cores of Legionn'''
                if core_id in _cores:
                    return [{'unit_id':k} for k in sorted(list(_cores[core_id].keys()))]
                else:
                    api.abort(404, 'Core {} not found'.format(core_id))
          
  
app = Flask('Legionn')
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Legionn(app=app)
  
  
if __name__ == '__main__':
    app.run(debug=True)
