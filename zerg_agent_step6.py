# 필수모듈 불러오기
from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units
from absl import app
import random

class ZergAgent(base_agent.BaseAgent):
  # 리스트 중 첫번쨰 유닛이 원하는 타입인지 체크함
  def unit_type_is_selected(self, obs, unit_type):
    if (len(obs.observation.single_select) > 0 and
        obs.observation.single_select[0].unit_type == unit_type):
      return True

    if (len(obs.observation.multi_select) > 0 and
        obs.observation.multi_select[0].unit_type == unit_type):
      return True

    return False

  # 리스트 중 유닛을 변수로 저장
  def get_units_by_type(self, obs, unit_type):
    return [unit for unit in obs.observation.feature_units
            if unit.unit_type == unit_type]

  # 해당 행동이 가능한지 체크
  def can_do(self, obs, action):
    return action in obs.observation.available_actions

  # 행동하는 함수 (action)
  def step(self, obs):
    super(ZergAgent, self).step(obs)

    spawning_pools = self.get_units_by_type(obs, units.Zerg.SpawningPool)
    if len(spawning_pools) == 0:
      if self.unit_type_is_selected(obs, units.Zerg.Drone):
        if self.can_do(obs, actions.FUNCTIONS.Build_SpawningPool_screen.id):
          x = random.randint(0, 83)
          y = random.randint(0, 83)

          return actions.FUNCTIONS.Build_SpawningPool_screen("now", (x, y))

      drones = self.get_units_by_type(obs, units.Zerg.Drone)
      if len(drones) > 0:
        drone = random.choice(drones)

        return actions.FUNCTIONS.select_point("select_all_type", (drone.x,
                                                                  drone.y))

    # 라바 선택가 되었다면
    if self.unit_type_is_selected(obs, units.Zerg.Larva):
      # 인구 수가 체크
      free_supply = (obs.observation.player.food_cap -
                     obs.observation.player.food_used)
      # 인구 수가 부족하면 오버로드 추가
      if free_supply == 0:
        if self.can_do(obs, actions.FUNCTIONS.Train_Overlord_quick.id):
          return actions.FUNCTIONS.Train_Overlord_quick("now")

      # 저글링 소환
      if self.can_do(obs, actions.FUNCTIONS.Train_Zergling_quick.id):
        return actions.FUNCTIONS.Train_Zergling_quick("now")

    larvae = self.get_units_by_type(obs, units.Zerg.Larva)
    if len(larvae) > 0:
      larva = random.choice(larvae)

      return actions.FUNCTIONS.select_point("select_all_type", (larva.x, larva.y))

    return actions.FUNCTIONS.no_op()

def main(unused_argv):
  agent = ZergAgent()
  try:
    while True:
      with sc2_env.SC2Env(
          map_name="Simple96",
          players=[sc2_env.Agent(sc2_env.Race.zerg),
                   sc2_env.Bot(sc2_env.Race.random,
                               sc2_env.Difficulty.very_easy)],
          agent_interface_format=features.AgentInterfaceFormat(
              feature_dimensions=features.Dimensions(screen=84, minimap=64),
              use_feature_units=True),
          step_mul=16,
          game_steps_per_episode=0,
          visualize=True) as env:

        agent.setup(env.observation_spec(), env.action_spec())

        timesteps = env.reset()
        agent.reset()

        while True:
          step_actions = [agent.step(timesteps[0])]
          if timesteps[0].last():
            break
          timesteps = env.step(step_actions)

  except KeyboardInterrupt:
    pass

if __name__ == "__main__":
  app.run(main)