from components.basic_commands import le_encrypt;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Encrypt",
                    number_devices = 1,
                    description = "Test that we can execute the LE Encrypt command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le encrypt test");
    
    key = [0 for i in range(16)];
    plaintext = [0 for i in range(16)];
    
    try:
        for i in range(0, transport.n_devices):
            status, EncData = le_encrypt(transport, i, key, plaintext, 100);
    except Exception as e:
        trace.trace(1, "LE Encrypt test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Encrypt test passed with %i device(s)" %transport.n_devices);
    return 0;
