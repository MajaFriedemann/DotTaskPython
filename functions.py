class Participant:
    """ A class to represent participants in our study. """

    def __init__(self, sub_nr, condition):
        self.sub_nr = sub_nr
        self.condition = condition

    def larger_than_10(self):
        """ Checks if sub_nr is larger than 10. """
        if self.sub_nr > 10:
            ans = 'yes'
        else:
            ans = 'no'

        return ans







