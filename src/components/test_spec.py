
class TestSpec():
    
    def __init__(self, name = "", number_devices = 2, description = ""):
        self.name = name;
        self.number_devices = number_devices;
        self.description = description;

    def __repr__(self):
        return "Test '%s'\n"%self.name + \
               " Requires %i device(s)\n"%self.number_devices + \
               " Description: %s"%self.description;