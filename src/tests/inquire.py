from components.basic_commands import inquire;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "Inquire",
                    number_devices = 1,
                    description = "Test that we can execute the Inquire command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting inquire test");
    
    lap = [0 for i in range(3)];
    length = 0;
    NumRsp = 0;
    
    try:
        for i in range(0, transport.n_devices):
            inquire(transport, i, lap, length, NumRsp, 100);
    except Exception as e:
        trace.trace(1, "Inquire test failed: %s" %str(e));
        return 1;

    trace.trace(3, "Inquire test passed with %i device(s)" %transport.n_devices);
    return 0;
