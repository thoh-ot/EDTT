#! /usr/bin/env python2
def parse_arguments():
    import argparse
    parser = argparse.ArgumentParser(description="Zephyr EDTT (Embedded Device Test Tool)")

    parser.add_argument("-v", "--verbose", default=2, type=int, help="Verbosity level");

    parser.add_argument("-t", "--transport", required=True, help="Type of transport to connect to device");

    parser.add_argument("-T", "--test", required=True, help="Which test to run (from src/tests)");

    parser.add_argument("-C", "--case", required=False, help="Which subtest to run")

    parser.add_argument("--seed", required=False, default=0x1234, help='Random generator seed (0x1234 by default)')

    #NWTSIM & BabbleSim transport related arguments

    parser.add_argument("-s", "--sim_id", help="When connecting to a simulated device, simulation id");

    parser.add_argument("-d","--bridge-device-nbr", help="When connecting to a simulated device, device number of the PTT bridge");

    parser.add_argument("-D","--num-devices", help="When connecting to a target proxies, number of PTT proxies to connect to");

    return parser.parse_args()

def init_transport(args, trace):
    #Initialize the transport and connect to devices
    if (args.transport == "nwtsim"):
        from components.edttt_nwtsim import PTTT_nwtsim;
        transport = PTTT_nwtsim(args, trace);
        transport.connect();
        return transport;
    elif (args.transport == "bsim"):
        from components.edttt_bsim import PTTT_bsim;
        transport = PTTT_bsim(args, trace);
        transport.connect();
        return transport;
    elif (args.transport == "target"):
        from components.edttt_target import PTTT_target_bridge;
        transport = PTTT_target_bridge(args, trace);
        transport.connect();
        return transport;
    else:
        raise Exception("Unknown transport %s\n"%args.transport)

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
        args = parse_arguments();
        import random;
        random.seed(args.seed);

        trace = Trace(args.verbose); #TODO: replace with Logger

        transport = init_transport(args, trace);

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
