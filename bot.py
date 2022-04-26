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
        await self.build_command_centers()
        await self.build_refineries()

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

        barracks = self.units(UnitTypeId.BARRACKS)
        if barracks:
            print("bruh")
            depot_positions = {d for d in depot_positions if barracks[0].closest_distance_to(d) == 0}

        

        if(
            self.can_afford(UnitTypeId.SUPPLYDEPOT)
            and self.supply_left < 4
            and self.already_pending(UnitTypeId.SUPPLYDEPOT) <= 1
            and len(depot_positions) > 0
            
        ):

            await self.build(UnitTypeId.SUPPLYDEPOT, near=depot_positions.pop())

    async def build_barracks(self):

        barrack_positions = self.main_base_ramp.barracks_correct_placement ##may need to change that to include addons

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

        for depot in self.structures(UnitTypeId.SUPPLYDEPOT).ready:
            for unit in self.enemy_units:
                if unit.distance_to(depot) < 15:
                    break
            else:
                depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER)


        for depot in self.structures(UnitTypeId.SUPPLYDEPOTLOWERED).ready:
            for unit in self.enemy_units:
                if unit.distance_to(depot) < 10:
                    depot(AbilityId.MORPH_SUPPLYDEPOT_RAISE)
                    break

    async def build_command_centers(self):
        if(
            self.can_afford(UnitTypeId.COMMANDCENTER)
            and self.army_count > self.townhalls.amount * 10 #temporary condition
            and self.already_pending(UnitTypeId.COMMANDCENTER) == 0
        ):
            await self.expand_now()

    async def build_refineries(self):

        for command_center in self.townhalls:
            vespene_geysers = self.vespene_geyser.closer_than(10, command_center)
            for vespene in vespene_geysers:
                if(
                    self.can_afford(UnitTypeId.REFINERY)
                    #needs to add more conditions
                ):
                    await self.build(UnitTypeId.REFINERY, vespene)

    async def build_engineering_bay(self):
        engineering_bay_positions = self.start_location.center


        if(
            self.can_afford(UnitTypeId.ENGINEERINGBAY)
            and self.units(UnitTypeId.ENGINEERINGBAY).amount < 2
        ):
            await print("bruh")



            
        


run_game(maps.get("HardwireAIE"), [
    Bot(Race.Terran, CurrentBot()),
    Computer(Race.Zerg, Difficulty.VeryHard)
], realtime=False)
