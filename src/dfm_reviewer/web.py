from nicegui import ui


@ui.page("/")
def index() -> None:
    ui.label("Mechanical DFM Reviewer")


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Mechanical DFM Reviewer", reload=False)
