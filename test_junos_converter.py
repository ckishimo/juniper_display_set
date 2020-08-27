import os
from junos_converter import get_set_config


def test_junos_converter(capsys):
    """Test conversion of Junos curly config to list of set commands."""
    directory = "tests/"

    test_files = filter(lambda x: ".set" not in x, os.listdir(directory))
    for file in test_files:

        get_set_config(directory + file, False)
        out, err = capsys.readouterr()

        # Make the output visible in the pytest report
        # sys.stdout.write(out)

        # Convert unicode to str and remove the last carriage return
        lout = list(map(str, out.split("\n")))[:-1]

        result = file.replace(".conf", ".set")
        with open(directory + result, "r") as fexp:
            expected = [x.strip() for x in fexp.readlines()]
            assert sorted(lout) == sorted(expected)
