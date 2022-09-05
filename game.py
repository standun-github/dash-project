"""A class for representing normal form game"""

import numpy as np
import nashpy as nash

class Game():
    def __init__(self, data):
        """
        Initialise game object

        Parameters
        ----------
        data : array
            The payoff matrix
        """

        player1 = []
        player2 = []
        for d in data:
            p1 = []
            p2 = []
            for item in d.items():
                a, b = item[1].split(',')
                p1.append(int(a))
                p2.append(int(b))

            player1.append(p1)
            player2.append(p2)
        self.game = nash.Game(player1, player2)  # Create the payoff matrices
        # print(game.__str__())

    def solve_nash(self):
        """
        Calculate the Nash equilibria using Lemke Howson algorithm
        and convert the calculated result into one output string

        Returns
        -------
        String
            The solution result
        """
        try:
            equilibria = self.game.lemke_howson_enumeration()

            string = ''
            strategy = ''
            nash_a = []
            nash_b = []
            for eq in equilibria:
                a, b = eq
                val = a[0]
                if val == 0.0 or val == 1.0:
                    strategy = 'pure strategies'
                else:
                    strategy = 'mixed strategies'
                nash_a.append(np.array2string(a))
                nash_b.append(np.array2string(b))

            print(list(set(nash_a))[0])
            print(list(set(nash_b))[0])

            string = string + "The Nash equilibrium found using " + strategy
            string = string + " for Player 1 is: " + list(set(nash_a))[0]
            string = string + " and for Player 2: " + list(set(nash_b))[0]

            return string
        except RuntimeError:
            error_message = "An exception occurred: The Lemke Howson algorithm has returned probability vectors of incorrect shapes. " \
                            "This is a degenerate game. " \
                            "Consider creating a game of equal size."
            return error_message
        else:
            return "Something went wrong"

    def __str__(self):
        return self.game


if __name__ == "__main__":

    A = np.array([[3, 0], [5, 1]])  # A is the row player
    B = np.array([[3, 5], [0, 1]])  # B is the column player

    A2 = np.array([[1, 1, -1], [2, -1, 0]])
    B2 = np.array([[1 / 2, -1, -1 / 2], [-1, 3, 2]])

    game1 = nash.Game(A2, B2)  # Create the payoff matrices

    # print(game1.__str__())

    equilibria = game1.lemke_howson_enumeration()  # Find the Nash Equilibrium with Support Enumeration
    string = ''
    for eq in equilibria:
        a, b = eq
        string += np.array2string(a)
        string += np.array2string(b)

    # print(string)

    p = Game(A2, B2)
    s = p.solve_nash()
    print(s)
