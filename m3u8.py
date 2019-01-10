#!/usr/bin/env python3
import argparse
import os
import subprocess
from urllib.parse import urljoin


def run(*args, check_returncode=False):
    result = subprocess.run(args)
    if check_returncode:
        result.check_returncode()
    return result.returncode


def path(*args):
    return os.path.join(*args)


def download(url, output_dir='output'):
    def p(*args):
        return path(output_dir, *args)

    def f(*args):
        return os.path.isfile(p(*args))

    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    merge_flag = False
    if url == 'merge':
        merge_flag = True
    if not f("url.txt"):
        if url is None:
            raise RuntimeError("You shouldn't use continue mode without a url")
        with open(p("url.txt"), 'w') as _f:
            _f.write(url+'\n')
    else:
        with open(p("url.txt")) as _f:
            url = _f.read().strip('\n')

    if not f('m3u8.txt'):
        run("curl", url, '-o', p("m3u8.txt"))

    with open(p("m3u8.txt")) as target_file:
        targets = []
        for line in target_file:
            line = line.strip('\n').strip(' ')
            if not line.startswith("#") and line.endswith(".ts"):
                targets.append(line)

    if merge_flag:
        if f(output_dir+'.ts'):
            raise FileExistsError(output_dir+'.ts')
        with open(output_dir+'.ts', 'wb') as output_ts:
            for one in targets:
                if f(one):
                    with open(p(one), 'rb') as input_file:
                        output_ts.write(input_file.read())
        return

    if not f('progress.txt'):
        run("touch", p('progress.txt'))

    with open(p("progress.txt")) as progress:
        done = set()
        for line in progress:
            done.add(line.strip('\n'))
    n = len(targets)
    for i, line in enumerate(targets):
        print(f"downloading {line}, {i+1} of {n}, {i/n*100:.2f}%")
        if f(line) and line in done:
            continue
        target_url = urljoin(url, line)
        if run("curl", target_url, '-o', p(line), check_returncode=True) == 0:
            with open(p("progress.txt"), 'a') as progress:
                progress.write(line+'\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", default=None)
    parser.add_argument("--output", "-o", default="output")
    args = parser.parse_args()
    download(
        args.url,
        output_dir=args.output
    )


if __name__ == '__main__':
    exit(main())
