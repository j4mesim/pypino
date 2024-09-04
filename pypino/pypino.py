from time import time
from socket import gethostname
from os import getpid
from json import dumps
import sys 


class PyPino:
    __opts = None
    __level_threshold = 30
    __base = {}
    __level_map = {
        "trace": 10,
        "debug": 20,
        "info": 30,
        "warn": 40,
        "error": 50,
        "fatal": 60,
    }

    # def __init__(self, opts={}):
    def __init__(self, name=None, level=30, base=None, showVersion=None):
        if level is not None:
            self.level(level)
        base = {
            "hostname": gethostname(),
            "pid": getpid(),
        }
        if base is not None:
            self.__base = base
        if name is not None:
            self.__base["name"] = name
        if showVersion is not None:
            self.__base["v"] = showVersion

    def format(self, level, *args):
        print(self.sformat(level, *args))
        sys.stdout.flush()

    def sformat(self, level, *args):
        return self.__output(level, *args)

    def __output(self, level, *args):
        args = list(args)
        if level < self.__level_threshold:
            return
        out = self.__base.copy()
        out["level"] = level
        out["time"] = int(1000 * time())
        for key in self.__base:
            if key not in out:
                out[key] = self.__base[key]

        if len(args):
            # If first is a dict, pop it from the list and add each k/v to out
            if isinstance(args[0], dict):
                obj_dict = args.pop(0)
                for arg in obj_dict:
                    out[arg] = obj_dict[arg]
            if len(args) > 0:
                msg = args[0]
                if isinstance(msg, int):
                    out["msg"] = msg
                elif isinstance(msg, str):
                    if len(args) == 1:
                        out["msg"] = msg
                    else:
                        # Handle string formatting
                        out["msg"] = msg % tuple(args[1:])
                elif isinstance(msg, BaseException):
                    out["msg"] = str(msg)
                elif msg is None:
                    out["msg"] = None

        # return pformat(out)
        return dumps(out)
        # return dumps(out, separators=(",", ":"))

    def trace(self, *args): self.format(10, *args)

    def debug(self, *args): self.format(20, *args)

    def info(self, *args): self.format(30, *args)

    def warn(self, *args): self.format(40, *args)

    def error(self, *args): self.format(50, *args)

    def fatal(self, *args): self.format(60, *args)

    def level(self, new_level=None):
        if new_level is not None:
            if isinstance(new_level, int):
                self.__level_threshold = new_level
            if isinstance(new_level, str) and new_level in self.__level_map:
                self.__level_threshold = self.__level_map[new_level]
        return self.__level_threshold

    def child(self, child_kv):
        base = self.__base.copy()
        for key in child_kv:
            base[key] = child_kv[key]
        opts = {"base": base}
        if "name" in base:
            opts["name"] = base["name"]
        return PyPino(opts)
