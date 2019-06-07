def setup_nbvscode():
    return {
        "command": ["code-server", "-p", "{port}",
                    "--no-auth", "--allow-http", "--disable-telemetry",
                    "--user-data-dir", "/home/jovyan/"
                    "--extensions-dir", "/home/jovyan/vscode_extensions/"],
        "absolute_url": False,
        "launcher_entry": {
            "title": "VS Code",
        }
    }
