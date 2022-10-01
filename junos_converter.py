#!/usr/bin/python

#
# Copyright (c) 2017 carles.kishimoto@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy
# of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations under
# the License.

import argparse


def print_set_command(lcommands, leaf):
    print(("%s %s" % (" ".join(lcommands), leaf)))


def replace_curly(s):
    return s.replace("{", "{\n").replace("}", "\n}")


def get_set_config(filein, ignore_annotations):
    try:
        with open(filein, "r") as f:
            data = f.read()
    except IOError:
        print("Error: Could not read input file:", filein)
        exit()

    # Add \n for one-line configs
    if not '"' in data:
        data = replace_curly(data)
    else:
        # Do not replace curly brackets if within double quotes
        # curly brackets can show up in as-path expressions
        # Assume an even number of double quotes
        data = '"'.join(
            [
                item if i % 2 != 0 else replace_curly(item)
                for i, item in enumerate(data.split('"'))
            ]
        )

    # Keep a list of annotations to be printed at the end
    lannotations = []
    annotation = ""
    lres = ["set"]
    for elem in data.split("\n"):
        elem = elem.strip()
        if elem == "" or elem.startswith("#"):
            continue

        if elem.startswith("/*"):
            # Store current annotation
            annotation = elem.replace("/* ", '"').replace(" */", '"')
        else:
            clean_elem = elem.strip("\t\n\r{ ")
            if annotation:
                lannotations.append("top")
                if len(lres) > 1:
                    level = lres[:]
                    # Replace "set" with "edit"
                    level[0] = "edit"
                    lannotations.append("%s" % " ".join(level))
                # Annotation in a leaf, keep only the keyword
                if ";" in clean_elem:
                    clean_elem = clean_elem.split()[0]
                lannotations.append("annotate %s %s" % (clean_elem, annotation))
                annotation = ""
            if "inactive" in clean_elem:
                clean_elem = clean_elem.replace("inactive: ", "")
                linactive = list(lres)
                linactive[0] = "deactivate"
                print_set_command(linactive, clean_elem)
            if "protect" in clean_elem:
                clean_elem = clean_elem.replace("protect: ", "")
                lprotect = list(lres)
                lprotect[0] = "protect"
                print_set_command(lprotect, clean_elem)
            if ";" in clean_elem:  # this is a leaf
                print_set_command(lres, clean_elem.split(";")[0])
            elif clean_elem == "}":  # Up one level remove parent
                lres.pop()
            else:
                lres.append(clean_elem)

    if not ignore_annotations:
        # Print all annotations at the end
        for a in lannotations:
            print(a)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=">>> Juniper display set")
    parser.add_argument(
        "--ignore-annotations",
        required=False,
        default=False,
        action="store_true",
        help="Specify if annotations should be removed from the output",
    )
    parser.add_argument(
        "--input",
        required=True,
        type=str,
        help="Specify the input Junos configuration file",
    )
    args = parser.parse_args()

    get_set_config(args.input, args.ignore_annotations)
