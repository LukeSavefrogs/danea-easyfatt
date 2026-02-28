from rich.console import Console
from rich.table import Table
from rich.live import Live
import readchar

from typing import Any

class Option(object):
    def __init__(self, label: str, value: Any, highlight_style: str | None = None, indicator: str | None = None):
        if type(label) != str:
            raise ValueError("Label must be a string")
        if highlight_style is not None and type(highlight_style) != str:
            raise ValueError("Highlight style must be a string")
        if indicator is not None and type(indicator) != str:
            raise ValueError("Indicator must be a string")
        
        self.label = label
        self.value = value
        self.highlight_style = highlight_style
        self.indicator = indicator

    def __str__(self):
        return self.label
    
    def __repr__(self) -> str:
        return f"Option({','.join(f'{k}={v}' for k,v in self.__dict__.items())})"

class SelectableMenu(object):
    _options: list[Option]

    def __init__(
        self,
        options: list[str | tuple[str, Any] | Option],
        title: str | None = None,
        highlight_style: str = "bold white on blue",
        indicator: str = ">",
    ):
        """
        Args:
            options (list[str | tuple[str, Any] | Option]): List of options. Each option can be either 
                a string (label and value will be the same), 
                a tuple of (label, value) or 
                an Option instance (gives more control).
            title (str, optional): Title of the menu. Defaults to None.
            highlight_style (str, optional): Rich style for the highlighted option. Defaults to "bold white on blue".
            indicator (str, optional): Indicator symbol for the selected option. Defaults to ">".
        """

        if not options:
            raise ValueError("Options cannot be empty")

        # Normalize options
        self._options = []
        for option in options:
            if isinstance(option, str):
                self._options.append(Option(label=option, value=option, highlight_style=highlight_style, indicator=indicator))
            elif isinstance(option, tuple) and len(option) == 2:
                self._options.append(Option(label=option[0], value=option[1], highlight_style=highlight_style, indicator=indicator))
            elif isinstance(option, Option):
                if option.highlight_style is None:
                    option.highlight_style = highlight_style
                if option.indicator is None:
                    option.indicator = indicator
                self._options.append(option)
            else:
                raise ValueError(f"Invalid option format: {option}")

        self._title = title
        self._highlight_style = highlight_style
        self._selected_index = 0
        self._console = Console()

    # ------------------------
    # Rendering
    # ------------------------

    def _render(self):
        table = Table(
            show_header=False,
            expand=True,
            title=self._title,
        )
        table.add_column()

        for i, option in enumerate(self._options):
            if i == self._selected_index:
                table.add_row(
                    f"[{option.highlight_style}]{option.indicator} {option.label}[/{option.highlight_style}]"
                )
            else:
                table.add_row(f"  {option.label}")

        return table

    # ------------------------
    # Navigation
    # ------------------------

    def _move_up(self):
        self._selected_index = (
            self._selected_index - 1
        ) % len(self._options)

    def _move_down(self):
        self._selected_index = (
            self._selected_index + 1
        ) % len(self._options)

    # ------------------------
    # Public API
    # ------------------------

    def get_options(self) -> list[Option]:
        return self._options
    
    def run(self, exit_on_esc: bool = True) -> Any | None:
        """
        Run the menu and wait for the user to select an option.
        
        Args:
            exit_on_esc (bool, optional): Whether to exit the menu and return None when the ESC key is pressed. Defaults to True.

        Returns:
            The value of the selected option, or None if exited with ESC (if exit_on_esc is True).
        """

        with Live(
            self._render(),
            console=self._console,
            refresh_per_second=10,
        ) as live:

            while True:
                key = readchar.readkey()

                if key == readchar.key.UP:
                    self._move_up()

                elif key == readchar.key.DOWN:
                    self._move_down()

                elif key == readchar.key.ENTER:
                    return self._options[self._selected_index].value

                elif key == readchar.key.ESC and exit_on_esc:
                    return None

                live.update(self._render())
    
if __name__ == "__main__":
    menu = SelectableMenu(
        options=[
            ("Option 1", "value1"),
            ("Option 2", "value2"),
            ("Option 3", "value3"),
            Option(label="Exit the program", value="exit", highlight_style="bold white on red", indicator="!"),
        ],
        title="Select an option",
    )
    result = menu.run()
    print(f"Selected: {result}")