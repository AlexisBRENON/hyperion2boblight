"""
Rainbow light effect unit tests
"""

from hyperion2boblight.lib.effects import rainbow

class TestRainbowEffect:
    """ Raibow effect test class """

    def test_rainbow_effect(self):
        """ Test that the rainbow effect actually display each rainbow color """
        rainbow_instance = rainbow.RainbowEffect()
        commands = set()
        first_command = rainbow_instance.get_color(None)
        commands.add(first_command)

        while True:
            rainbow_instance.increment()
            command = rainbow_instance.get_color(None)
            if command == first_command:
                break
            else:
                commands.add(command)
        # The message must contains command to light every rainbow color
        assert (1., 0., 0.) in commands # Red
        assert (1., 1., 0.) in commands # Yellow
        assert (0., 1., 0.) in commands # Green
        assert (0., 1., 1.) in commands # Turquoise
        assert (0., 0., 1.) in commands # Blue
        assert (1., 0., 1.) in commands # Purple

