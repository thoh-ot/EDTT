# -*- coding: utf-8 -*-
import string;
import re;
from xml.dom import minidom;

class GATTData:

    def __init__(self):
        self.mydoc = minidom.parse('src/components/GATT Database.xml');

    def __handleRange(self, service):
        characteristics = service.getElementsByTagName('Characteristic');
        descriptors = service.getElementsByTagName('Descriptor');
        includes = service.getElementsByTagName('Include');

        first = int(service.attributes['handle'].value);
        last = [];
        if len(includes) > 0:
            last += [ max([int(include.attributes['handle'].value) for include in includes]) ];
        if len(descriptors) > 0:
            last += [ max([int(descriptor.attributes['handle'].value) for descriptor in descriptors]) ];
        if len(characteristics) > 0:
            last += [ max([int(characteristic.attributes['handle'].value) for characteristic in characteristics]) ];
            last[-1] += 1;
        return first, max(last) if len(last) > 0 else first;
    
    def __allInSet(self, setNo, elementType):
        sets = self.mydoc.getElementsByTagName('ServiceSet_%d' % setNo);
        return sets[0].getElementsByTagName(elementType);
        
    def __services(self, setNo, serviceType=None, uuid=None):
        services = { 'uuids': [], 'handles': [] };
        
        alls = self.__allInSet(setNo, 'Service');
        for service in alls:
            if (serviceType is None) or (serviceType == service.attributes['type'].value):
                _uuid = int(service.attributes['uuid'].value, 16);
                if (uuid is None) or (uuid == _uuid):
                    services['uuids'] += [ _uuid ];
                    first, last = self.__handleRange( service );
                    services['handles'] += [ [first, last] ];
        return services;
 
    def allServices(self, setNo):
        return self.__services(setNo);
   
    def primaryServices(self, setNo, uuid=None):
        return self.__services(setNo, 'Primary Service', uuid);
    
    def secondaryServices(self, setNo, uuid=None):
        return self.__services(setNo, 'Secondary Service', uuid);
    
    def includedServices(self, setNo):
        includes = { 'uuids': [], 'handles': [] };
        
        alls = self.__allInSet(setNo, 'Include');
        for include in alls:
            includes['uuids'] += [ int(include.attributes['uuid'].value, 16) ];
            includes['handles'] += [ [ int(include.attributes['first'].value), int(include.attributes['last'].value) ] ];
        return includes;
    
    def descriptors(self, setNo, serviceHandle=None):
        descriptors = { 'uuid': [], 'handle': [] };

        alls = self.__allInSet(setNo, 'Service');
        for service in alls:
            _serviceHandle = int(service.attributes['handle'].value);
            if (serviceHandle is None) or (serviceHandle == _serviceHandle): 
                for descriptor in service.getElementsByTagName('Descriptor'):
                    descriptors['uuid'] += [ int(descriptor.attributes['uuid'].value, 16) ];
                    descriptors['handle'] += [ int(descriptor.attributes['handle'].value) ];
                if not serviceHandle is None:
                    break;
        return descriptors;
    
    def characteristics(self, setNo, serviceHandle=None, permissions=False):
        characteristics = { 'uuid': [], 'handle': [], 'value_handle': [], 'property': [] };
        if permissions:
            characteristics['permission'] = [];

        alls = self.__allInSet(setNo, 'Service');
        for service in alls:
            _serviceHandle = int(service.attributes['handle'].value);
            if (serviceHandle is None) or (serviceHandle == _serviceHandle):
                for characteristic in service.getElementsByTagName('Characteristic'):
                    characteristics['uuid'] += [ int(characteristic.attributes['uuid'].value, 16) ];
                    characteristics['handle'] += [ int(characteristic.attributes['handle'].value) ];
                    characteristics['value_handle'] += [ int(characteristic.attributes['handle'].value)+1 ];
                    characteristics['property'] += [ int(characteristic.attributes['properties'].value) ];
                    if permissions:
                        characteristics['permission'] += [ int(characteristic.attributes['permissions'].value) ];
                if not serviceHandle is None:
                    break;
        return characteristics;

    def __toArray(self, value):
        data = [];
        if value:
            if re.match('[0-9A-F]{2}( [0-9A-F]{2})+', value):
               data = [ int(hexNumber, 16) for hexNumber in value.split(' ') ];
            elif len(value) > 2:
               data = [ ord(char) for char in value ];
            else:
               data = [ int(value, 16) ];
        return data;    
    
    def characteristicValue(self, setNo, handle):
        value = None;
        alls = self.__allInSet(setNo, 'Characteristic');
        for characteristic in alls:
            if int(characteristic.attributes['handle'].value) == handle:
                value = characteristic.firstChild.data.strip('\r\n\t');
                break;
        return self.__toArray(value);

    def descriptorValue(self, setNo, handle):
        value = None;
        alls = self.__allInSet(setNo, 'Descriptor');
        for descriptor in alls:
            if int(descriptor.attributes['handle'].value) == handle:
                value = descriptor.firstChild.data.strip('\r\n\t');
                break;
        return self.__toArray(value);
        
        
