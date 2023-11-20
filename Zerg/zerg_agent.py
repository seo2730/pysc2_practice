# 필수 모듈 불러오기
from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features
from absl import app

class ZergAgent(base_agent.BaseAgent):
  # 행동하는 함수 (action)
  def step(self, obs):
    super(ZergAgent, self).step(obs)

    return actions.FUNCTIONS.no_op()
  

def main(unused_argv):
    agent = ZergAgent()
    try:
        while True:
            with sc2_env.SC2Env(
                map_name="Simple64", # 맵을 simple64으로 세팅
                players=[sc2_env.Agent(sc2_env.Race.zerg), # 저그 선택. (zerg, protoss, terran, random 선택 가능)
                        sc2_env.Bot(sc2_env.Race.random,
                        sc2_env.Difficulty.very_easy)],
                        # 상대를 Bot으로 할 것이며, 종족은 random, 난이도:very_easy
                        # 여기에 다른 agent를 설정할 수 있음
                agent_interface_format=features.AgentInterfaceFormat(
                        feature_dimensions=features.Dimensions(screen=84, minimap=64)), # screen 차원 : 84x84, minimap : 64x64
                        step_mul=16,
                        # 액션 설정. 8 -> 300APM, 16 --> 150APM 
                        game_steps_per_episode=0,
                        # 디폴트는 30분인데, 여기에서는 endless로 설정
                        visualize=True) as env:
                        # 스크린과 미니맵 해상도 설정
                        # PySC2 2.0에서는 RGB 레이어를 추가할 수 있음 
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