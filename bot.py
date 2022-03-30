from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Race, Difficulty
from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId


class WorkerRushBot(BotAI):
    async def on_step(self, iteration: int):
        if iteration == 0:
            for worker in self.workers:
                worker.attack(self.enemy_start_locations[0])


class CurrentBot(BotAI):
    async def on_step(self, iteration: int):
        await self.distribute_workers()
        await self.build_workers()
        await self.build_depots()

    async def build_workers(self):
        command_center = self.townhalls.ready.random
        if(
            self.can_afford(UnitTypeId.SCV)
            and command_center.is_idle
            and self.workers.amount < self.townhalls.amount * 22
        ):
            command_center.train(UnitTypeId.SCV)

    async def build_depots(self):

        depot_positions = self.main_base_ramp.corner_depots

        if(
            self.can_afford(UnitTypeId.SUPPLYDEPOT)
            and self.supply_left < 4
            and self.already_pending(UnitTypeId.SUPPLYDEPOT) == 0
            and len(depot_positions) > 0
        ):

            await self.build(UnitTypeId.SUPPLYDEPOT, near=depot_positions.pop())


run_game(maps.get("HardwireAIE"), [
    Bot(Race.Terran, CurrentBot()),
    Computer(Race.Zerg, Difficulty.Medium)
], realtime=False)
