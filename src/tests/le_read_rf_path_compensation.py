from components.basic_commands import le_read_rf_path_compensation;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Read RF Path Compensation",
                    number_devices = 1,
                    description = "Test that we can execute the LE Read RF Path Compensation command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le read rf path compensation test");
    
    try:
        for i in range(0, transport.n_devices):
            status, TxPathComp, RxPathComp = le_read_rf_path_compensation(transport, i, 100);
    except Exception as e:
        trace.trace(1, "LE Read RF Path Compensation test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Read RF Path Compensation test passed with %i device(s)" %transport.n_devices);
    return 0;
