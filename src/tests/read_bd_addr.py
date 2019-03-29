from components.basic_commands import read_bd_addr;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "Read BD_ADDR",
                    number_devices = 1,
                    description = "Test that we can execute the Read BD_ADDR command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting read bd_addr test");
    
    try:
        for i in range(0, transport.n_devices):
            status, BdaddrVal = read_bd_addr(transport, i, 100);
    except Exception as e:
        trace.trace(1, "Read BD_ADDR test failed: %s" %str(e));
        return 1;

    trace.trace(3, "Read BD_ADDR test passed with %i device(s)" %transport.n_devices);
    return 0;
