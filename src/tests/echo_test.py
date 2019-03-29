from components.basic_commands import echo;

"""
    Return the test spec which contains info about the test
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "Echo test",
                    number_devices = 1,
                    description = "Test that we can echo to any connected device");
    return spec;


"""
    Run the test
"""
def main(args, transport, trace):
    trace.trace(3, "Starting echo test");

    try:
        for i in range(0,transport.n_devices):
            echo(transport, i, "Bananas in pyjamas", 100);
    except Exception as e:
        trace.trace(1,"Echo test failed: %s"%str(e));
        return 1;

    trace.trace(3,"Echo test passed with %i device(s)"% transport.n_devices);

    return 0;