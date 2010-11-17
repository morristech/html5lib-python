import sys
import os
import json
import re

import html5lib
import support
import test_parser
import test_tokenizer

p = html5lib.HTMLParser()

unnamespaceExpected = re.compile(r"^(\|\s*)<html ([^>]+)>", re.M).sub

def main(out_path):
    if not os.path.exists(out_path):
        sys.stderr.write("Path %s does not exist"%out_path)
        sys.exit(1)

    for filename in support.html5lib_test_files('tokenizer', '*.test'):
        run_file(filename, out_path)

def run_file(filename, out_path):
    try:
        tests_data = json.load(file(filename))
    except ValueError:
        sys.stderr.write("Failed to load %s\n"%filename)
        return
    name = os.path.splitext(os.path.split(filename)[1])[0]
    output_file = open(os.path.join(out_path, "tokenizer_%s.dat"%name), "w")

    if 'tests' in tests_data:
        for test_data in tests_data['tests']:
            if 'initialStates' not in test_data:
                test_data["initialStates"] = ["Data state"]
                
            for initial_state in test_data["initialStates"]:
                if initial_state != "Data state":
                    #don't support this yet
                    continue
                test = make_test(test_data)
                output_file.write(test)

    output_file.close()

def make_test(test_data):
    if 'doubleEscaped' in test_data:
        test_data = test_tokenizer.unescape_test(test_data)

    rv = []
    rv.append("#data")
    rv.append(test_data["input"].encode("utf8"))
    rv.append("#errors")
    rv.append("#document")
    tree = p.parse(test_data["input"])
    output = test_parser.convertTreeDump(p.tree.testSerializer(tree))
    output = test_parser.attrlist.sub(test_parser.sortattrs, output)
    output = unnamespaceExpected(r"\1<\2>", output)
    rv.append(output.encode("utf8"))
    rv.append("")
    return "\n".join(rv)

if __name__ == "__main__":
    main(sys.argv[1])
