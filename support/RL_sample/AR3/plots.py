import matplotlib.pyplot as plt

class Plotter:
    def plot_rewards(self, rewards):
        plt.plot(rewards)
        plt.title("Reward over time")
        plt.xlabel("Episode")
        plt.ylabel("Reward")
        plt.show()