#  Custom kick idle player script by mr.smoothy#5824

import setting

import babase
import bascenev1 as bs
from tools import logger

settings = setting.get_settings_data()
INGAME_TIME = settings["afk_remover"]["ingame_idle_time_in_secs"]
LOBBY_KICK = settings['afk_remover']["kick_idle_from_lobby"]
INLOBBY_TIME = settings['afk_remover']["lobby_idle_time_in_secs"]
cIdle = 0  # players/player found idle within very short time
cLastIdle = 0


class checkIdle(object):
    def start(self):
        self.t1 = babase.AppTimer(2, babase.CallStrict(self.check), repeat=True)
        self.lobbies = {}
        self._logged_missing_input_api = False

    def check(self):
        global cLastIdle
        global cIdle
        current = bs.apptime() * 1000
        if not bs.get_foreground_host_session():
            return
        for player in bs.get_foreground_host_session().sessionplayers:
            input_device = player.inputdevice
            if hasattr(input_device, "get_last_input_time"):
                last_input = int(input_device.get_last_input_time())
            else:
                # API 9+ no longer exposes get_last_input_time() on
                # InputDevice in this environment; skip in-game AFK checks.
                if not self._logged_missing_input_api:
                    logger.log(
                        "afk_check: InputDevice.get_last_input_time() unavailable; in-game AFK check disabled",
                        "sys",
                    )
                    self._logged_missing_input_api = True
                continue
            afk_time = int((current - last_input) / 1000)
            if afk_time in range(INGAME_TIME,
                                 INGAME_TIME + 20) or afk_time > INGAME_TIME + 20:
                if (current - cLastIdle) / 1000 < 3:
                    cIdle = cIdle + 1
                    if cIdle >= 3:
                        return
                else:
                    cIdle = 0
                cLastIdle = current

            if afk_time in range(INGAME_TIME, INGAME_TIME + 20):
                player_id = (
                    player.get_account_id()
                    if hasattr(player, "get_account_id")
                    else player.get_v1_account_id()
                )
                self.warn_player(player_id,
                                 "Press any button within " + str(
                                     INGAME_TIME + 20 - afk_time) + " secs")
            if afk_time > INGAME_TIME + 20:
                player.remove_from_game()
        if LOBBY_KICK:
            current_players = []
            for player in bs.get_game_roster():
                if player['client_id'] != -1 and len(player['players']) == 0:
                    current_players.append(player['client_id'])
                    if player['client_id'] not in self.lobbies:
                        self.lobbies[player['client_id']] = current
                    lobby_afk = int(
                        (current - self.lobbies[player['client_id']]) / 1000)
                    if lobby_afk in range(INLOBBY_TIME, INLOBBY_TIME + 10):
                        bs.broadcastmessage("Join game within " + str(
                            INLOBBY_TIME + 10 - lobby_afk) + " secs",
                            color=(1, 0, 0), transient=True,
                            clients=[player['client_id']])
                    if lobby_afk > INLOBBY_TIME + 10:
                        bs.disconnect_client(player['client_id'], 0)
            # clean the lobbies dict
            temp = self.lobbies.copy()
            for clid in temp:
                if clid not in current_players:
                    del self.lobbies[clid]

    def warn_player(self, pbid, msg):
        for player in bs.get_game_roster():
            if player["account_id"] == pbid:
                bs.broadcastmessage(msg, color=(1, 0, 0), transient=True,
                                    clients=[player['client_id']])
