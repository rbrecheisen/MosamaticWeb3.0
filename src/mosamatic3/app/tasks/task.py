class Task:
    def __init__(self, name: str, display_name: str, description: str, html_page: str, url_pattern: str, visible: bool=True, installed: bool=False) -> None:
        self.name = name
        self.display_name = display_name
        self.description = description
        self.html_page = html_page
        self.url_pattern = url_pattern
        self.visible = visible
        self.installed = installed

    def run(self) -> None:
        raise NotImplementedError('Child tasks must implement this method')