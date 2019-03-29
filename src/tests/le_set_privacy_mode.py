from components.basic_commands import le_set_privacy_mode;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Set Privacy Mode",
                    number_devices = 1,
                    description = "Test that we can execute the LE Set Privacy Mode command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le set privacy mode test");
    
    IdAddrType = 0;
    AVal = [0 for i in range(6)];
    mode = 0;
    
    try:
        for i in range(0, transport.n_devices):
            status = le_set_privacy_mode(transport, i, IdAddrType, AVal, mode, 100);
    except Exception as e:
        trace.trace(1, "LE Set Privacy Mode test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Set Privacy Mode test passed with %i device(s)" %transport.n_devices);
    return 0;
