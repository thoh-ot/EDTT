from components.basic_commands import le_periodic_advertising_create_sync;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Periodic Advertising Create Sync",
                    number_devices = 1,
                    description = "Test that we can execute the LE Periodic Advertising Create Sync command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le periodic advertising create sync test");
    
    FilterPolicy = 0;
    sid = 0;
    AddrType = 0;
    AVal = [0 for i in range(6)];
    skip = 0;
    SyncTimeout = 0;
    unused = 0;
    
    try:
        for i in range(0, transport.n_devices):
            le_periodic_advertising_create_sync(transport, i, FilterPolicy, sid, AddrType, AVal, skip, SyncTimeout, unused, 100);
    except Exception as e:
        trace.trace(1, "LE Periodic Advertising Create Sync test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Periodic Advertising Create Sync test passed with %i device(s)" %transport.n_devices);
    return 0;
