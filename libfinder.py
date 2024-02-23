#!/usr/bin/python3
import os
import sys
import os.path
import shutil
import argparse
import yaml
import hashlib

VERSION = "0.2"
DST = "./target"

class TcLibFinder:
    def __init__(self, conf:dict):
        self.INSTALL_ROOT = conf.get("root", "/usr/lib")

        self.pkgs = set()
        for p in conf.get("packages", []) or []:
            self.pkgs.add(p)

        self.libs:list[str] = self._find_lib(conf.get("patterns_packages", False), *conf.get("patterns", []))
        for l in self.libs:
            self._copy_to(l, DST)

    def _find_lib(self, pkg=False, *lib:str) -> list[str]:
        out:set[str] = set()
        for d in os.popen(f"find {self.INSTALL_ROOT}").read().split("\n"):
            for l in lib:
                if l in os.path.basename(d):
                    out.add(d)
                    break

        for f in out:
            p = self._find_pn(f)
            if p:
                self.pkgs.add(p)

        for p in self.pkgs:
            for f in self._find_pc(p):
                out.add(f)

        return list(out)

    def _find_pn(self, f) -> str:
        print(f"Getting package info on {f}")
        p = os.popen(f"dpkg -S {f}").read().strip().split(" ")[0].split(":")[0]
        if p:
            return p

        print(f"WARNING: No idea to what package {f} belongs to!")

    def _find_pc(self, p) -> list[str]:
        def ok(p) -> bool:
            for fx in ["/usr/bin", "/usr/share/doc", "/usr/share/man"]:
                if p.startswith(fx):
                    return False
            return True

        print(f"Getting package content of {p}")
        f = os.popen(f"dpkg -L {p}").read().strip()
        if not f:
            print(f"!!! ERROR: unable to get content of package \"{p}\". Did you list it as build-required?")
            sys.exit(1)
        return [x for x in list(filter(None, [x.strip() for x in f.split("\n")])) if os.path.isfile(x) and ok(x)]


    def _copy_to(self, lib, dst):
        lp = os.path.dirname(lib)
        if lp.startswith(self.INSTALL_ROOT):
            lp = lp.split(self.INSTALL_ROOT)[-1]

        dst = dst + lp
        os.makedirs(dst, exist_ok=True)
        shutil.copy2(lib, dst)


class TcLibSymlinker:
    DEFAULT_TOOLCHAIN = "/opt/toolchain"
    def __init__(self, dst:str) -> None:
        self._pairs:dict[str, list[str]] = {}
        self._p_dst = dst or self.DEFAULT_TOOLCHAIN
        if self._p_dst == self.DEFAULT_TOOLCHAIN:
            sys.stderr.write(f"WARNING: Toolchain is going to be installed into default {self._p_dst}\n")
        self._fp()
        self._rl()

    def _rl(self):
        os.makedirs("debian", exist_ok=True)
        links = open("debian/links", "w")
        for p in [sorted(x) for x in self._pairs.values() if len(x) > 1]:
            base = p.pop()
            for x in p:
                inner = os.path.sep.join(os.path.dirname(x).split(os.path.sep)[2:])
                dst = os.path.join(
                    self._p_dst, inner,
                    os.path.basename(base)
                )
                src = os.path.join(inner, os.path.basename(x))
                links.write(f"{os.path.join(self._p_dst, src)} {dst}\n")
        links.close()

    def _fp(self):
        for (r, _, f) in os.walk(DST):
            if not f: continue
            for fn in f:
                p = os.path.join(r, fn)
                s = self._get_cs(p)
                if s in self._pairs:
                    self._pairs[s].append(p)
                else:
                    self._pairs[s] = [p]

    def _get_cs(self, p:str) -> str:
        with open(p, 'rb') as f:
            h = hashlib.sha1()  # md5 would also do
            while c := f.read(0x2000):
                h.update(c)
            return h.hexdigest()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append("-h")

    p = argparse.ArgumentParser()
    p.add_argument("-c", "--config", type=str, help="Configuration file")
    p.add_argument("-r", "--compact", action="store_true", help="Resymlink same files, remove the rest")
    p.add_argument("-d", "--symlink-dest", type=str, help="Destination of the symlinking, used in actual packaging section")
    p.add_argument("-v", "--version", action="store_true", help="Show current version")
    args = p.parse_args()

    if args.version:
        print(f"Version: {VERSION}")
        sys.exit(0)

    if not args.config:
        print("ERROR: no configuration passed")
        sys.exit(1)

    conf=yaml.load(open(args.config), Loader=yaml.SafeLoader)

    if args.compact:
        if not os.path.exists(DST):
            TcLibFinder(conf=conf)
        TcLibSymlinker(dst=args.symlink_dest)
    else:
        TcLibFinder(conf=conf)
