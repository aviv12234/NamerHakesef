from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Race, Difficulty
from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId



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
        await self.build_barracks()
        await self.build_marines()
        await self.micro()
        await self.depot_control()

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
            and self.already_pending(UnitTypeId.SUPPLYDEPOT) <= 1
            and len(depot_positions) > 0
        ):

            await self.build(UnitTypeId.SUPPLYDEPOT, near=depot_positions.pop())

    async def build_barracks(self):

        barrack_positions = self.main_base_ramp.barracks_correct_placement

        if(
            self.can_afford(UnitTypeId.BARRACKS)
            and self.already_pending(UnitTypeId.BARRACKS) == 0
            and len(barrack_positions) > 0
        ):

            await self.build(UnitTypeId.BARRACKS, near=barrack_positions)


    async def build_marines(self):

        if( 
            self.can_afford(UnitTypeId.MARINE)
            and self.supply_left > 0
        ):
            for barrack in self.structures(UnitTypeId.BARRACKS).idle:
                barrack.train(UnitTypeId.MARINE)

    async def micro(self):

        marinecount = self.units(UnitTypeId.MARINE).amount
        marines = self.units(UnitTypeId.MARINE).ready

        if(marinecount > 25):

            for marine in marines:
                
                if marine.weapon_cooldown == 0:
                    marine.attack(self.enemy_start_locations[0])
                else:
                    marine.move(self.start_location)


    async def depot_control(self):

        for depo in self.structures(UnitTypeId.SUPPLYDEPOT).ready:
            for unit in self.enemy_units:
                if unit.distance_to(depo) < 15:
                    break
            else:
                depo(AbilityId.MORPH_SUPPLYDEPOT_LOWER)


        for depo in self.structures(UnitTypeId.SUPPLYDEPOTLOWERED).ready:
            for unit in self.enemy_units:
                if unit.distance_to(depo) < 10:
                    depo(AbilityId.MORPH_SUPPLYDEPOT_RAISE)
                    break





            
        


run_game(maps.get("GlitteringAshesAIE"), [
    Bot(Race.Terran, CurrentBot()),
    Computer(Race.Zerg, Difficulty.VeryHard)
], realtime=False)
