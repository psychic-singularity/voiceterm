from main import handle_pending_confirmation, run_agent_turn
from security import pending_actions


def test_confirmation_input_is_consumed_without_agent_call(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    pending_actions.pending_action = None
    pending_actions.request_create_file("notes.txt", "hello")

    calls = []
    monkeypatch.setattr(
        "main.console.print",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )
    monkeypatch.setattr(
        "main.agent.stream",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("confirmation input reached agent.stream")
        ),
    )

    assert handle_pending_confirmation(" y ") is True
    assert pending_actions.pending_action is None
    assert (tmp_path / "notes.txt").read_text(encoding="utf-8") == "hello"


def test_confirmation_cancel_is_consumed_without_creating_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    pending_actions.pending_action = None
    pending_actions.request_create_file("notes.txt", "hello")

    monkeypatch.setattr("main.console.print", lambda *args, **kwargs: None)

    assert handle_pending_confirmation("n") is True
    assert pending_actions.pending_action is None
    assert not (tmp_path / "notes.txt").exists()


def test_non_confirmation_input_stays_in_confirmation_flow(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    pending_actions.pending_action = None
    pending_actions.request_create_file("notes.txt", "hello")

    monkeypatch.setattr("main.console.print", lambda *args, **kwargs: None)

    assert handle_pending_confirmation("run_command y") is True
    assert pending_actions.pending_action is not None
    assert not (tmp_path / "notes.txt").exists()


def test_agent_stream_stops_after_confirmation_request(monkeypatch):
    pending_actions.pending_action = None
    updates = iter(["confirmation update", "model command after confirmation"])
    seen = []

    class FakeStream:
        def __iter__(self):
            for update in updates:
                seen.append(update)
                if update == "confirmation update":
                    pending_actions.pending_action = {
                        "type": "create_file",
                        "path": None,
                        "content": "",
                    }
                yield update

        def close(self):
            pass

    monkeypatch.setattr("main.agent.stream", lambda *args, **kwargs: FakeStream())
    monkeypatch.setattr("main.handle_update", lambda update: None)

    run_agent_turn("create a file")

    assert seen == ["confirmation update"]
    pending_actions.pending_action = None

