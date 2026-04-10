import sys
sys.path.insert(0, "src")

from file_parser import parse_ofx, parse_qif

#print(parse_ofx("data/sample.ofx"))
print(parse_qif("data/sample.qif"))
