from components.basic_commands import le_start_encryption;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Start Encryption",
                    number_devices = 1,
                    description = "Test that we can execute the LE Start Encryption command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le start encryption test");
    
    handle = 0;
    rand = 0;
    ediv = 0;
    ltk = [0 for i in range(16)];
    
    try:
        for i in range(0, transport.n_devices):
            le_start_encryption(transport, i, handle, rand, ediv, ltk, 100);
    except Exception as e:
        trace.trace(1, "LE Start Encryption test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Start Encryption test passed with %i device(s)" %transport.n_devices);
    return 0;
