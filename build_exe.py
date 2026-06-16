import PyInstaller.__main__

def build():
    entry_point = 'main.py'

    args = [
        entry_point,
        '--onefile',
        '--noconsole',
        '--name=Tabletop Map Tool',
        '--add-data=styles.qss;.',
        '--clean',
    ]

    PyInstaller.__main__.run(args)

if __name__ == "__main__":
    build()