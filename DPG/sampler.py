import numpy as np

class Sampler(object):
    def __init__(self,
                 policy,
                 env,
                 batch_size=200,
                 max_step=200,
                 discount=0.99):
        self.policy = policy
        self.env = env
        self.batch_size = batch_size
        self.max_step = max_step
        self.discount = discount

    def compute_monte_carlo_returns(self, rewards):
        return_so_far = 0
        returns = []
        for reward in rewards[::-1]:
            return_so_far = reward + self.discount * return_so_far
            returns.append(return_so_far)
        return returns[::-1]

    def collect_one_episode(self):
        state = self.env.reset()
        states, actions, rewards, next_states, dones = [], [], [], [], []
        for t in xrange(self.max_step):
            action = self.policy.sampleAction(state[np.newaxis,:])
            next_state, reward, done, _ = self.env.step(action)
            # appending the experience
            states.append(state)
            actions.append(action)
            rewards.append(reward)
            next_states.append(next_state)
            dones.append(done)
            # going to next state
            state = next_state
            if done: break
        returns = self.compute_monte_carlo_returns(rewards)
        return dict(
                    states = states,
                    actions = actions,
                    rewards = rewards,
                    monte_carlo_returns = returns,
                    next_states = next_states,
                    dones = dones
                    )


    def collect_one_batch(self):
        episodes = []
        for i_batch in xrange(self.batch_size):
            episodes.append(self.collect_one_episode())
        # prepare input
        states = np.concatenate([episode["states"] for episode in episodes])
        actions = np.concatenate([episode["actions"] for episode in episodes])
        rewards = np.concatenate([episode["rewards"] for episode in episodes])
        monte_carlo_returns = np.concatenate([episode["monte_carlo_returns"] for episode in episodes])
        next_states = np.concatenate([episode["next_states"] for episode in episodes])
        dones = np.concatenate([episode["dones"] for episode in episodes])
        return dict(
                    states = states,
                    actions = actions,
                    rewards = rewards,
                    monte_carlo_returns = monte_carlo_returns,
                    next_states = next_states,
                    dones = dones
                    )

    def samples(self):
        return self.collect_one_batch()
