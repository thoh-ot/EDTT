from components.basic_commands import read_local_supported_commands;
from components.utils import *;
from shutil import copy;

class fileTrace:

    def __init__(self, path):
        self.__file = open(path, "w+");

    def trace(self, level, text):
        self.__file.write(text + '\r\n');

    def close(self):
        self.__file.close();
        self.__file = None;
        
"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "Read Local Supported Commands",
                    number_devices = 1,
                    description = "Test that we can execute the Read Local Supported Commands command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting read local supported commands test");
    
    try:
        for i in range(0, transport.n_devices):
            status, commands = read_local_supported_commands(transport, i, 100);
            if (status == 0):
                showCommands(commands, trace);
                showCommands(commands, fileTrace("commands.txt"));
                copy("commands.txt", "../bsim/results/Hola/commands.txt");
    except Exception as e:
        trace.trace(1, "Read Local Supported Commands test failed: %s" %str(e));
        return 1;

    trace.trace(3, "Read Local Supported Commands test passed with %i device(s)" %transport.n_devices);
    return 0;
