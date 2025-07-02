import arc
from arc import Events
from mindustry.game import EventType
from mindustry.gen import Player, Groups
from dataclasses import dataclass
from loguru import logger

__name__ = "ModHelper"

def init_modhelper():
    Events.run(EventType.Trigger.update, _event_tick)

_events: dict[object, list] = {}

def mdh_events_fire(event: object): # Everything can be event, so this is why event is object
    e = _events.get(event.__class__, None)
    if e == None:
        return
    for func in e:
        func(event)

def mdh_events_on(event: object, handler):
    e = _events.get(event, None)
    if e == None:
        _events[event] = [handler]
    else:
        e.append(handler)

@dataclass
class player2:
    x: float
    y: float
    uuid: str
@logger.catch
def _event_tick():
    try:
        for player in Groups.player:
            pl = get_pl(player)
            if pl == None:
                _players.append(player2(player.x(), player.y(), player.uuid()))
                mdh_events_fire(PlayerMoveEvent(player.x(), player.y(), player.x(), player.y(), player))
            else:
                if (pl.x != player.x()) or (pl.y != player.y()):
                    mdh_events_fire(PlayerMoveEvent(pl.x, pl.y, player.x(), player.y(), player))
                    pl.x, pl.y = player.x(), player.y()
    except Exception as e:
        print(e)
        raise e
            
def get_pl(pl: Player):
    for i in _players:
        if pl.uuid() == i.uuid:
            return i
    return None
_players: list[player2] = []

@dataclass
class PlayerMoveEvent:
    oldx: float
    oldy: float
    x: float
    y: float
    player: Player