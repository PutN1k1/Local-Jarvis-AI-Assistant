from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.text import Text


console = Console()

with Live(console=console, refresh_per_second=10) as live:

    live.update(Panel(Markdown("Трек переключен, громкость повышена. Вы тратите больше усилий на настройку среды, чем на саму работу."), title="[bold white]Response[/bold white]", border_style="gold1"))