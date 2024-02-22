#!/usr/bin/python3
import os
import os.path
import shutil

VERSION = "0.2"

class ToolChainFinder:
    INSTALL_ROOT = "/usr/lib"
    LIBS = [
        "libasan",
        "libatomic",
        "libgcc",
        "libgomp",
        "libssp",
        "libstc++",
    ]

    def __init__(self):
        self.libs:list[str] = self._find_lib(*self.LIBS)
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
    ToolChainFinder()
