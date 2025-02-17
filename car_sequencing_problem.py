import os
import random
from qubots.base_problem import BaseProblem

class CarSequencingProblem(BaseProblem):
    """
    Car Sequencing Problem

    In this problem, a production sequence for a number of cars must be arranged.
    Cars come in different classes; each class requires a set of options (features).
    For each option, a window (block) of consecutive cars is considered, and there is
    an upper limit on the number of cars in that window that may require that option.
    
    Instance data (read from a file):
      - nb_positions: number of cars (positions in the sequence)
      - nb_options: number of options available
      - nb_classes: number of car classes
      - max_cars_per_window: list (length nb_options) of maximum allowed cars with that option in any window
      - window_size: list (length nb_options) of window sizes for each option
      - options: a list (length nb_classes) of Boolean lists (length nb_options) indicating, for each class, which options are required
      - initial_sequence: a list (length nb_positions) containing the class index for each car in the initial production plan

    Candidate solution representation:
      A list (permutation) of integers of length nb_positions, representing a rearrangement of the initial production plan.
    
    Objective:
      For each option and for each window (of the given size), if the number of cars requiring that option exceeds the maximum allowed, the excess counts as a violation. The objective is to minimize the total number of violations.
    """
    
    def __init__(self, instance_file=None, nb_positions=None, nb_options=None,
                 max_cars_per_window=None, window_size=None, options=None,
                 initial_sequence=None):
        if instance_file is not None:
            self._load_instance(instance_file)
        else:
            if (nb_positions is None or nb_options is None or 
                max_cars_per_window is None or window_size is None or
                options is None or initial_sequence is None):
                raise ValueError("Either 'instance_file' or all instance parameters must be provided.")
            self.nb_positions = nb_positions
            self.nb_options = nb_options
            self.max_cars_per_window = max_cars_per_window
            self.window_size = window_size
            self.options = options
            self.initial_sequence = initial_sequence

    def _load_instance(self, filename):
        # Resolve relative paths with respect to this module's directory.
        if not os.path.isabs(filename):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            filename = os.path.join(base_dir, filename)
        # Read all integers from the file.
        with open(filename, 'r') as f:
            data = [int(x) for x in f.read().split()]
        it = iter(data)
        self.nb_positions = next(it)
        self.nb_options = next(it)
        nb_classes = next(it)
        self.max_cars_per_window = [next(it) for _ in range(self.nb_options)]
        self.window_size = [next(it) for _ in range(self.nb_options)]
        nb_cars = []
        self.options = []
        self.initial_sequence = []
        for c in range(nb_classes):
            next(it)  # Skip class index (not used)
            count = next(it)
            nb_cars.append(count)
            # For each option, read a binary indicator (1 means required, 0 means not required)
            opt = [next(it) == 1 for _ in range(self.nb_options)]
            self.options.append(opt)
            # Append the class index 'count' times into the initial_sequence.
            for _ in range(count):
                self.initial_sequence.append(c)
        if len(self.initial_sequence) != self.nb_positions:
            raise ValueError("Sum of nb_cars does not equal nb_positions.")
    
    def evaluate_solution(self, solution) -> float:
        """
        Evaluate a candidate solution.

        The candidate solution should be a list (permutation) of integers of length nb_positions,
        representing indices into the initial_sequence.

        First, we check that solution is a valid permutation of 0,..., nb_positions-1.
        Then, we reconstruct the production sequence: for each position i, let
            sequence[i] = initial_sequence[ solution[i] ].
        For each option o (0 <= o < nb_options) and for every window (consecutive block) of length
        window_size[o], we count the number of cars that require option o (i.e., where
            options[ sequence[j] ][ o ] is True).
        If the count exceeds max_cars_per_window[o], the excess is a violation.
        The objective is the sum of all such violations.
        """
        PENALTY = 1e9
        if not isinstance(solution, (list, tuple)) or len(solution) != self.nb_positions:
            return PENALTY
        if sorted(solution) != list(range(self.nb_positions)):
            return PENALTY
        
        # Reconstruct the production sequence (list of class indices)
        sequence = [self.initial_sequence[i] for i in solution]
        total_violations = 0
        for o in range(self.nb_options):
            w = self.window_size[o]
            max_allowed = self.max_cars_per_window[o]
            # For each window starting at position j
            for j in range(self.nb_positions - w + 1):
                count = 0
                for k in range(w):
                    car_class = sequence[j+k]
                    if self.options[car_class][o]:
                        count += 1
                if count > max_allowed:
                    total_violations += (count - max_allowed)
        return total_violations

    def random_solution(self):
        """
        Generate a random candidate solution.

        Returns a random permutation of integers 0 to nb_positions - 1.
        """
        sol = list(range(self.nb_positions))
        random.shuffle(sol)
        return sol
