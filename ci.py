import os

commands = [
    "pytest --doctest-modules lj{sep}utils.py lj{sep}vendors -v".format(sep=os.sep),
    "pytest -v",
]
for command in commands:
    print(command)
    assert 0 == os.system(command)
