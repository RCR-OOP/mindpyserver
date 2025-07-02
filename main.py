from __future__ import annotations

from jpype import startJVM, imports, __version__, JPackage
imports.registerDomain("mindustry")
imports.registerDomain("arc")
imports
import os
from glob import glob
import sys
__name__ = "mindpyserver"

startJVM(classpath=['server-release.jar'])

import arc
from arc import *
from arc.util import Log, CommandHandler
from mindustry.mod import Mods
from types import ModuleType
from sys import version, argv
from modhelper import init_modhelper

Log.level = Log.LogLevel.debug
class Mod:
    name: str
    def register_srv_cmds(self, handler: CommandHandler) -> None: ...
    def register_client_cmds(self, handler: CommandHandler) -> None: ...


mods: list[Mod] = []


def scan_mods() -> list[ModuleType]:
    l = []
    # NOTE: Придумай потом как это сделать рекурсивно
    for i in glob("mods/*.py"):
        imp = __import__(f"mods.{i.removeprefix('mods/').removesuffix('.py')}")
        l.append(getattr(imp, i.removeprefix('mods/').removesuffix('.py')))
    return l

from mindustry.game import EventType
from mindustry.gen import Player


def on_srv_load(ev: EventType.ServerLoadEvent) -> None:
    global srvctrl
    global netsrv
    Log.info(f"Please wait while we load mods(or plugins) and inject some stuff into server...")
    listeners = Core.app.getListeners()
    for i in listeners:
        if isinstance(i, ServerControl):
            srvctrl = i
        elif isinstance(i, NetServer):
            netsrv = i
    #srvctrl.handler.register("hello_world", "Hello, python world!", hello_world)
    #netsrv.clientCommands.register("fastfetch", "Yes, this is a fastfetch", fastfetch_mindustry)
    srvctrl.handler.register("pymods", "Displays what mods/plugins are loaded", pymods)
    init_modhelper()
    m = scan_mods()
    for i in m:
        try:
            cl: Mod = i.mod_class()
            mods.append(cl)
        except Exception as e:
            print(e)
    for cl in mods:
        cl.register_srv_cmds(srvctrl.handler)
        cl.register_client_cmds(netsrv.clientCommands)
    Log.info(f"Loaded: {len(mods)}. Total: {len(m)}")

from mindustry.core import NetServer

Events.on(EventType.ServerLoadEvent, on_srv_load)


def pymods(args: list) -> None:
    Log.info(f"Loaded mods list:")
    for i in mods:
        Log.info(f" - {i.name}")
    Log.info(f"Loaded mod count: {len(mods)}")

def hello_world(args: list) -> None:
    Log.info(f"Hello, world!")
    print(f"Args: {args} Python version: {version} JPype version: {__version__}")
    print("Well, it works")

def fastfetch_mindustry(arg: list, player: Player) -> None:
    ff = os.popen("fastfetch").read()
    player.sendMessage(ff)


from mindustry.server import ServerLauncher, ServerControl

argv_normal = argv
argv_normal.pop(0)
ServerLauncher.main(argv_normal)