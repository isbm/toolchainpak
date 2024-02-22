#!/usr/bin/python3
import os
import sys
import os.path
import shutil
import argparse
import yaml

VERSION = "0.2"

class ToolChainFinder:
    INSTALL_ROOT = "/usr/lib"

    def __init__(self, conf:dict):
        self.libs:list[str] = self._find_lib(*conf.get("patterns", []))
        for l in self.libs:
            self._copy_to(l, "./target")

    def _find_lib(self, *lib:str) -> list[str]:
        out:list[str] = []
        for d in os.popen(f"find {self.INSTALL_ROOT}").read().split("\n"):
            for l in lib:
                if l in os.path.basename(d):
                    out.append(d)
                    break

        return out

    def _copy_to(self, lib, dst):
        lp = os.path.dirname(lib)
        if lp.startswith(self.INSTALL_ROOT):
            lp = lp.split(self.INSTALL_ROOT)[-1]

        dst = dst + lp
        os.makedirs(dst, exist_ok=True)
        shutil.copy2(lib, dst)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append("-h")

    p = argparse.ArgumentParser()
    p.add_argument("-c", "--config", type=str, help="Configuration file")
    p.add_argument("-s", "--symlink", action="store_true", help="Resymlink same files")
    p.add_argument("-v", "--version", action="store_true", help="Show current version")
    args = p.parse_args()

    if args.version:
        print(f"Version: {VERSION}")
    elif args.symlink:
        print("ERROR: Resymlinking is just not implemented yet")
        sys.exit(1)
    else:
        if not args.config:
            print("ERROR: no configuration passed")
            sys.exit(1)

        ToolChainFinder(conf=yaml.load(open(args.config), Loader=yaml.SafeLoader))
