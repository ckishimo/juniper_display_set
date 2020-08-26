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

import sys


def print_set_command(lcommands, leaf):
    c = " "
    c = c.join(lcommands)
    print(("%s %s" % (c, leaf)))
    return


def get_set_config(filein):
    try:
        f = open(filein, "r")
    except IOError:
        print("Error: could not read input file:", filein)
        sys.exit()

    data = f.read()
    f.close()

    # Keep a list of annotations to be printed at the end
    lannotations = []
    annotation = ""

    lines = data.split("\n")
    lres = ["set"]
    for elem in lines:
        elem = elem.strip()
        if elem is "":
            continue
        if (not elem.startswith("#")) and (not elem.startswith("/*")):
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
        else:
            # keep current annotation
            if elem.startswith("/*"):
                annotation = elem.replace("/* ", '"')
                annotation = annotation.replace(" */", '"')

    # Print all annotations at the end
    for a in lannotations:
        print(a)


if len(sys.argv) != 2:
    print("Usage: %s FILEIN\n" % sys.argv[0])
else:
    get_set_config(sys.argv[1])
