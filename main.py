
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from agent.graph import agent
import security.pending_actions as pending_actions


console = Console()


def extract_text(content):
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []

        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item["text"])

        return "\n".join(parts)

    return str(content)


def main():
    console.print(
        Panel(
            "[bold]VoiceTerm[/bold]\n"
            "[dim]AI terminal agent[/dim]",
            expand=False
        )
    )

    while True:
        try:
            user_input = console.input(
                "[bold cyan]You > [/bold cyan]"
            ).strip()

            if user_input.lower() in {"exit", "quit"}:
                break

            # Handle pending confirmations before starting a new agent turn.
            if pending_actions.pending_action is not None:
                answer = user_input.lower()

                if answer in {"y", "yes"}:
                    result = pending_actions.confirm_pending_action()
                    console.print(
                        Panel(result, border_style="green")
                    )

                elif answer in {"n", "no"}:
                    result = pending_actions.cancel_pending_action()
                    console.print(
                        Panel(result, border_style="yellow")
                    )

                else:
                    console.print(
                        "[yellow]Please enter y to confirm "
                        "or n to cancel.[/yellow]"
                    )
                    continue

                console.print()
                continue

            console.print()

            for update in agent.stream(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": user_input
                        }
                    ]
                },
                stream_mode="updates",
            ):
                handle_update(update)

            console.print()

        except KeyboardInterrupt:
            console.print("\n[dim]Exiting VoiceTerm.[/dim]")
            break

        except Exception as e:
            console.print(
                f"[bold red]Error:[/bold red] {e}"
            )


def handle_update(update):
    for node_name, data in update.items():
        messages = data.get("messages", [])

        for message in messages:

            # Gemini requested a tool call.
            if (
                hasattr(message, "tool_calls")
                and message.tool_calls
            ):
                for call in message.tool_calls:
                    tool_name = call["name"]
                    args = call["args"]

                    console.print(
                        f"[yellow]● Tool call:[/yellow] "
                        f"[bold]{tool_name}[/bold]"
                    )

                    for key, value in args.items():
                        console.print(
                            f"  [dim]{key}:[/dim] {value}"
                        )

            # A tool has returned its result.
            elif getattr(message, "type", None) == "tool":
                console.print(
                    f"[green]✓ Tool completed:[/green] "
                    f"{message.name}"
                )

                output = extract_text(message.content)

                if len(output) > 500:
                    output = output[:500] + "\n..."

                console.print(
                    Panel(output, border_style="dim")
                )

            # Display AI responses.
            elif getattr(message, "type", None) == "ai":
                text = extract_text(message.content)

                if text:
                    console.print(
                        Panel(
                            Markdown(text),
                            title="AI",
                            border_style="green"
                        )
                    )


if __name__ == "__main__":
    main()
