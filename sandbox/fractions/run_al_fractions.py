from apprentice.agents.WhereWhenHowNoFoa import WhereWhenHowNoFoa
from apprentice.working_memory.representation import Sai

from tutorenvs.fractions import FractionArithSymbolic


def run_training(agent, n=10):

    env = FractionArithSymbolic()

    p = 0

    while p < n:

        state = env.get_state()
        response = agent.request(state)

        if response == {}:
            print('hint')
            selection, action, inputs = env.request_demo()
            sai = Sai(selection=selection, action=action, inputs=inputs)

        else:
            sai = Sai(selection=response['selection'],
                      action=response['action'],
                      inputs=response['inputs'])

        reward = env.apply_sai(sai.selection, sai.action, sai.inputs)
        print('reward', reward)

        next_state = env.get_state()

        agent.train(state, sai, reward, next_state=next_state,
                    skill_label="fractions",
                    foci_of_attention=[])

        if sai.selection == "done" and reward == 1.0:
            print('Finished problem {} of {}'.format(p, n))
            p += 1


if __name__ == "__main__":

    agent = WhereWhenHowNoFoa('fraction arith', 'fraction arith',
                              search_depth=1)

    run_training(agent, n=500)
