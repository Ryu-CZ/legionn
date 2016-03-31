'''!
@brief Collection of Legionn base classes.
@date Created on 10 Jan 2016
@author [Ryu-CZ](https://github.com/Ryu-CZ)
'''
import json


class JSONSerializable(object):
    def __repr__(self):
        return json.dumps(self.__dict__)


class Unit(JSONSerializable):
    '''!
    @brief Basic interface of Unit handling requests
    '''
    def get(self, msg=None):
        return NotImplemented
    
    def post(self, msg=None):
        return NotImplemented
    
    def put(self, msg=None):
        return NotImplemented
        

class Core(JSONSerializable):
    '''!
    @brief Interface of Core. 
    Core is master on Units and contains common knowledge of Units. Also Core handles production and destruction of Units. Core consists of 1 or more Units. 
    '''
    def __init__(self, name, description="Hi i am Core interface"):
        self._name = name
        self.description = description
        self.units = {}
        
    def __del__(self, *args, **kwargs):
        self.deactivate(context=None)
        
    def __contains__(self, other):
        if isinstance(other, Unit):
            return other in self.units.values()
        return other in self.units
    
    def add(self, obj, name):
        '''! 
        @brief insert object into my Units
        @param obj: object to add into units
        @param name: unique name of record for object
        '''
        if not isinstance(obj, Unit):
            raise TypeError('"obj" is not "Unit" type.')
        if name in self.units:
            raise KeyError('Unit "{0}" is already in Core "{1}"'.format(self._name, obj.name))
        self.units[name] = obj
        
    def remove(self, name):
        if name in self.units:
            ret = self.units[name]
            del self.units[name]
            return ret
        return None
    
    def activate(self, context=None):
        '''!
        @brief function is called by server on module registration (born of module)
        @return returns None value on successful activation
        '''
        raise NotImplementedError
    
    def deactivate(self, context=None):
        '''
        @brief function is called by server on module destruction (death of module)
        @return returns None value on successful deactivation
        '''
        raise NotImplementedError
    
    def create_unit(self):
        '''!
        @brief Produce new unit for communication
        @return Unit instance
        '''
        raise NotImplementedError
    

    
