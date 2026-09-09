# Launcher

A tkinter window on top of the other modules of the tool validation assistant.
It lists the runnable modules, lets their configuration be changed before a run
and shows the output of the running module.

```bash
python -m Launcher.main        # from the project root
python Launcher/main.py
```

## What it does

| | |
|---|---|
| **Module list** | every module found in `Launcher/modules` |
| **Configuration editor** | built from the configuration files of the selected module |
| **Run / Stop** | the module runs in its own python process, the launcher stays responsive |
| **Output pane** | everything the module prints, progress bars included |

The modules shipped with the launcher:

1. **Issue formatter and risk assessment** - `config.py`
2. **Issue viewer** - `UI/ui_config.py`
3. **Polarion import** - `config.py` (shared with 1) and `.polarion.env`
4. **Test specification builder** - `PolarionAssistant/TestSpec/testspec_config.py` and `.polarion.env`

## How the configuration is handled

The original configuration files are **never rewritten**. The launcher stores
only the values that differ from them in `Launcher/launcher_settings.json` and
injects them into the child process just before the module starts.

The overrides are keyed by *configuration source*, not by module, so the main
configuration really is shared: what is changed in the issue formatter is what
the Polarion import sees.

Two kinds of entries appear in the editor:

* **plain values** - literals of the configuration file, editable straight away.
  A value that differs from the file is marked with a `*` and stored;
* **derived values** - entries written as f-strings or as a reference to
  another entry, for example
  `TEMP_OUTPUT_FILE = f"output/{tool_folder}/temp_output_risk.txt"`.
  They are shown read only and recomputed while the entries they depend on are
  edited. Tick the box in front of such an entry to pin it to a value of your
  own.

Fields marked `persist=False` (the Polarion password) are kept for the running
launcher session only and never written to the settings file.

## Adding a module

Drop one file into `Launcher/modules/`. It is picked up automatically -
there is no registration list to maintain.

```python
# Launcher/modules/my_module.py
from Launcher.core.config_fields import ConfigField, FieldKind
from Launcher.core.config_sources import PyModuleConfigSource
from Launcher.core.module_descriptor import RunnableModule
from Launcher.core.project import project_path


class MyModule(RunnableModule):
    id = "my_module"                 # stable, also the key in the settings file
    title = "5. My module"
    description = "What the module does."
    order = 50                       # position in the module list
    extra_sys_path = ()              # extra folders added to sys.path, if needed
    opens_window = False             # True when the module opens its own window

    def config_sources(self):
        return [
            PyModuleConfigSource(
                source_id="my_config",
                title="My configuration (my_config.py)",
                module_name="MyPackage.my_config",
                file_path=project_path("MyPackage", "my_config.py"),
                field_specs=[                    # optional, only cosmetic
                    ConfigField("INPUT_FILE", "Input file", kind=FieldKind.FILE,
                                section="Files"),
                ],
            )
        ]

    def run(self):
        from MyPackage.entry import do_the_work
        do_the_work()
```

Notes:

* `field_specs` is optional. Constants that are not declared there still show
  up in the editor under "Other settings" with a widget guessed from their
  value, and the trailing `#` comment of the line becomes the hint text.
* `run()` is executed in the child process **after** the overrides have been
  applied, so it may import the module code, print, block or open a window.
* Returning an already used `source_id` from two modules shares those settings
  between them on purpose.
* A configuration that is not a python module or a dotenv file only needs a new
  `ConfigSource` subclass - see `Launcher/core/config_sources.py`.

## Layout

```
Launcher/
├── main.py                  # start the launcher
├── child_main.py            # entry point of the process running a module
├── core/
│   ├── config_fields.py     # what one editable value looks like
│   ├── config_sources.py    # python module / dotenv back ends
│   ├── module_descriptor.py # the RunnableModule contract
│   ├── registry.py          # discovery of Launcher/modules
│   ├── settings_store.py    # launcher_settings.json
│   ├── process_runner.py    # child process and its output
│   └── project.py           # project root helpers
├── modules/                 # one file per runnable module
└── ui/                      # the tkinter window
```
