#! /usr/bin/env python2
import os;

def parse_arguments():
    import argparse
    parser = argparse.ArgumentParser(description="Zephyr EDTT (Embedded Device Test Tool)",
                                     epilog="Note: A transport can have its own options")

    parser.add_argument("-v", "--verbose", default=2, type=int, help="Verbosity level");

    parser.add_argument("-t", "--transport", required=True,
                        help="Type of transport to connect to the devices (the "
                             "transport module must either exist as "
                             "src/components/edtt_<transport>.py, or be a path "
                             "to an importable transport module");

    parser.add_argument("-T", "--test", required=True, help="Which test to run (from src/tests)");

    parser.add_argument("-C", "--case", required=False, help="Which subtest to run")

    parser.add_argument("--seed", required=False, default=0x1234, help='Random generator seed (0x1234 by default)')

    return parser.parse_known_args()

def try_to_import(module_path, type, def_path):
    try:
        if (("." not in module_path) and ("/" not in module_path)):
            from importlib import import_module;
            loaded_module = import_module(def_path + module_path)
        else: #The user seems to want to load the module from a place off-tree
            #If the user forgot Let's fill in the extension
            if module_path[-3:] != ".py":
              module_path = module_path + ".py"
            import imp;
            loaded_module = imp.load_source('%s', module_path);

        return loaded_module;
    except ImportError as e:
        print("\n Could not load the %s %s . Does it exist?\n"% (type, module_path))
        raise;

# Initialize the transport and connect to devices
def init_transport(transport, xtra_args, trace):
    transport_module = try_to_import(transport, "transport", "components.edttt_");
    transport = transport_module.EDTTT(xtra_args, trace);
    transport.connect();
    return transport;

def run_test(args, transport, trace):
    from importlib import import_module;
    try:
        test = import_module("tests.%s"%args.test)
    except Exception as e:
        print("Could not load test %s. Does it exist?"% args.test)
        raise e;

    test_spec = test.spec();
    trace.trace(4, test_spec);

    if test_spec.number_devices > transport.n_devices:
        raise Exception("This test needs %i connected devices but you only "
                        "connected to %i"%
                        (test_spec.number_devices, transport.n_devices));

    result = test.main(args, transport, trace);
    return result;

class Trace():
    def __init__(self, level):
        self.level = level;

    def trace(self, level, msg):
        if ( level <= self.level ):
            print(msg);

def main():
    transport = None;
    try:
        (args, xtra_args) = parse_arguments();
        
        import random;
        random.seed(args.seed);

        trace = Trace(args.verbose); #TODO: replace with Logger

        transport = init_transport(args.transport, xtra_args, trace);

        result = run_test(args, transport, trace);

        transport.close();

        from sys import exit;
        exit(result);

    except:
        if transport:
            transport.close();
        raise;

if __name__ == "__main__":
  main();
