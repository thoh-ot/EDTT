from components.basic_commands import le_periodic_advertising_terminate_sync;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Periodic Advertising Terminate Sync",
                    number_devices = 1,
                    description = "Test that we can execute the LE Periodic Advertising Terminate Sync command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le periodic advertising terminate sync test");
    
    handle = 0;
    
    try:
        for i in range(0, transport.n_devices):
            status = le_periodic_advertising_terminate_sync(transport, i, handle, 100);
    except Exception as e:
        trace.trace(1, "LE Periodic Advertising Terminate Sync test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Periodic Advertising Terminate Sync test passed with %i device(s)" %transport.n_devices);
    return 0;
