from rich.console import Console
from rich.table import Table
from rich.live import Live
import readchar


class SelectableMenu:
    def __init__(
        self,
        options,
        title=None,
        highlight_style="bold white on blue",
    ):
        """
        options: list[str] OR list[tuple[label, value]]
        title: optional title
        highlight_style: Rich style for selected row
        """

        if not options:
            raise ValueError("Options cannot be empty")

        # Normalize to (label, value)
        self._options = [
            (opt, opt) if isinstance(opt, str) else opt
            for opt in options
        ]

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

        for i, (label, _) in enumerate(self._options):
            if i == self._selected_index:
                table.add_row(
                    f"[{self._highlight_style}]> {label}[/{self._highlight_style}]"
                )
            else:
                table.add_row(f"  {label}")

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

    def run(self):
        """
        Returns:
            selected value
            None if ESC pressed
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
                    return self._options[self._selected_index][1]

                elif key == readchar.key.ESC:
                    return None

                live.update(self._render())
    
if __name__ == "__main__":
    menu = SelectableMenu(
        options=[
            ("Option 1", "value1"),
            ("Option 2", "value2"),
            ("Option 3", "value3"),
        ],
        title="Select an option",
    )
    result = menu.run()
    print(f"Selected: {result}")