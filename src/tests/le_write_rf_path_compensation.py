from components.basic_commands import le_write_rf_path_compensation;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Write RF Path Compensation",
                    number_devices = 1,
                    description = "Test that we can execute the LE Write RF Path Compensation command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le write rf path compensation test");
    
    
    try:
        for i in range(0, transport.n_devices):
            status = le_write_rf_path_compensation(transport, i, TxPathComp, RxPathComp, 100);
    except Exception as e:
        trace.trace(1, "LE Write RF Path Compensation test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Write RF Path Compensation test passed with %i device(s)" %transport.n_devices);
    return 0;
