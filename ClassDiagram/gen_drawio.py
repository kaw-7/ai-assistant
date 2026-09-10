# -*- coding: utf-8 -*-
"""Generate ClassDiagram/LauncherCore.drawio (uncompressed mxGraph XML).

Three pages: the discovery chain, the ConfigSource family, the run path.
Plain draw.io UML class shapes so everything stays editable by hand.
"""
from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(r"D:\who\AutomationValiReport\AIValiReport\ClassDiagram\LauncherCore.drawio")

ROW = 22          # height of one member row
DIV = 8           # height of the attribute / operation divider
GAP = 16          # extra header height per additional header line

CLASS_STYLE = (
    "swimlane;fontStyle=0;childLayout=stackLayout;horizontal=1;startSize={ss};"
    "horizontalStack=0;resizeParent=1;resizeParentMax=0;html=1;whiteSpace=wrap;"
    "verticalAlign=top;align=center;strokeWidth=1;"
)
MEMBER_STYLE = (
    "text;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;"
    "spacingLeft=6;spacingRight=6;overflow=hidden;rotatable=0;"
    "points=[[0,0.5],[1,0.5]];portConstraint=eastwest;whiteSpace=wrap;html=1;fontSize=11;"
)
DIV_STYLE = (
    "line;strokeWidth=1;fillColor=none;align=left;verticalAlign=middle;spacingTop=-1;"
    "spacingLeft=3;spacingRight=3;rotatable=0;labelPosition=right;points=[];"
    "portConstraint=eastwest;strokeColor=inherit;"
)
EDGE = ("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=open;endFill=0;"
        "strokeWidth=1;fontSize=10;")
EDGE_INHERIT = ("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;endFill=0;"
                "strokeWidth=1;fontSize=10;")
EDGE_DEP = ("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=open;endFill=0;"
            "dashed=1;strokeWidth=1;fontSize=10;")
EDGE_CROSS = ("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=blockThin;endFill=1;"
              "strokeWidth=2;strokeColor=#B85450;fontSize=10;fontColor=#B85450;")
FLOW_STYLE = "rounded=1;whiteSpace=wrap;html=1;align=left;spacingLeft=8;arcSize=8;"
LANE_STYLE = ("swimlane;html=1;startSize=30;horizontal=1;whiteSpace=wrap;"
              "fillColor=none;dashed=1;dashPattern=6 6;strokeWidth=1;")
NOTE_STYLE = "shape=note;whiteSpace=wrap;html=1;size=14;align=left;spacingLeft=8;verticalAlign=top;"
TITLE_STYLE = "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontSize=16;fontStyle=1;"
SUB_STYLE = "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontSize=11;fontColor=#666666;"


def esc(text: str) -> str:
    return escape(text, {'"': "&quot;"})


class Page:
    def __init__(self, name: str):
        self.name = name
        self.cells: list[str] = []

    # --- primitives ---------------------------------------------------------
    def raw(self, cell: str) -> None:
        self.cells.append(cell)

    def text(self, cid, value, x, y, w, h, style):
        self.raw(
            f'        <mxCell id="{cid}" value="{esc(value)}" style="{style}" vertex="1" parent="1">\n'
            f'          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />\n'
            f'        </mxCell>'
        )

    # --- UML class ----------------------------------------------------------
    def uml(self, cid, name, x, y, w, attrs=(), ops=(), stereo="", file=""):
        head = []
        if stereo:
            head.append(f"&amp;laquo;{stereo}&amp;raquo;")
        head.append(f"&lt;b&gt;{esc(name)}&lt;/b&gt;")
        if file:
            head.append(f"&lt;font style=&quot;font-size:9px&quot;&gt;{esc(file)}&lt;/font&gt;")
        start = 26 + GAP * (len(head) - 1)
        label = "&lt;br&gt;".join(head)

        rows = len(attrs) + len(ops)
        height = start + rows * ROW + (DIV if attrs and ops else 0)

        self.raw(
            f'        <mxCell id="{cid}" value="{label}" '
            f'style="{CLASS_STYLE.format(ss=start)}" vertex="1" parent="1">\n'
            f'          <mxGeometry x="{x}" y="{y}" width="{w}" height="{height}" as="geometry" />\n'
            f'        </mxCell>'
        )

        off = start
        for i, member in enumerate(attrs):
            self.raw(
                f'        <mxCell id="{cid}-a{i}" value="{esc(member)}" style="{MEMBER_STYLE}" '
                f'vertex="1" parent="{cid}">\n'
                f'          <mxGeometry y="{off}" width="{w}" height="{ROW}" as="geometry" />\n'
                f'        </mxCell>'
            )
            off += ROW
        if attrs and ops:
            self.raw(
                f'        <mxCell id="{cid}-div" value="" style="{DIV_STYLE}" vertex="1" parent="{cid}">\n'
                f'          <mxGeometry y="{off}" width="{w}" height="{DIV}" as="geometry" />\n'
                f'        </mxCell>'
            )
            off += DIV
        for i, member in enumerate(ops):
            self.raw(
                f'        <mxCell id="{cid}-o{i}" value="{esc(member)}" style="{MEMBER_STYLE}" '
                f'vertex="1" parent="{cid}">\n'
                f'          <mxGeometry y="{off}" width="{w}" height="{ROW}" as="geometry" />\n'
                f'        </mxCell>'
            )
            off += ROW
        return height

    # --- containers / boxes -------------------------------------------------
    def lane(self, cid, title, x, y, w, h):
        self.raw(
            f'        <mxCell id="{cid}" value="{esc(title)}" style="{LANE_STYLE}" vertex="1" parent="1">\n'
            f'          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />\n'
            f'        </mxCell>'
        )

    def flow(self, cid, parent, title, sub, x, y, w, h):
        label = f"&lt;b&gt;{esc(title)}&lt;/b&gt;"
        for line in sub:
            label += f"&lt;br&gt;&lt;font style=&quot;font-size:9px&quot;&gt;{esc(line)}&lt;/font&gt;"
        self.raw(
            f'        <mxCell id="{cid}" value="{label}" style="{FLOW_STYLE}" vertex="1" parent="{parent}">\n'
            f'          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />\n'
            f'        </mxCell>'
        )

    def note(self, cid, value, x, y, w, h):
        # html=1 shapes need <br>; a literal newline in an XML attribute
        # is normalised to a space by the parser.
        label = "&lt;br&gt;".join(esc(line) for line in value.split("\n"))
        self.raw(
            f'        <mxCell id="{cid}" value="{label}" style="{NOTE_STYLE}" vertex="1" parent="1">\n'
            f'          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />\n'
            f'        </mxCell>'
        )

    # --- edges --------------------------------------------------------------
    def edge(self, cid, src, tgt, label="", style=EDGE, exit=None, entry=None):
        st = style
        if exit:
            st += f"exitX={exit[0]};exitY={exit[1]};exitDx=0;exitDy=0;"
        if entry:
            st += f"entryX={entry[0]};entryY={entry[1]};entryDx=0;entryDy=0;"
        self.raw(
            f'        <mxCell id="{cid}" value="{esc(label)}" style="{st}" edge="1" parent="1" '
            f'source="{src}" target="{tgt}">\n'
            f'          <mxGeometry relative="1" as="geometry" />\n'
            f'        </mxCell>'
        )

    def xml(self, did: str) -> str:
        body = "\n".join(self.cells)
        return (
            f'  <diagram name="{esc(self.name)}" id="{did}">\n'
            f'    <mxGraphModel dx="1379" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" '
            f'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="850" pageHeight="1100" '
            f'math="0" shadow="0">\n'
            f'      <root>\n'
            f'        <mxCell id="0" />\n'
            f'        <mxCell id="1" parent="0" />\n'
            f'{body}\n'
            f'      </root>\n'
            f'    </mxGraphModel>\n'
            f'  </diagram>'
        )


# ===========================================================================
# Page 1 - discovery chain
# ===========================================================================
p1 = Page("1 - Discovery and contract")
p1.text("t1", "Launcher/core - discovery and the module contract", 30, 16, 560, 24, TITLE_STYLE)
p1.text("t1s", "A file in Launcher/modules becomes a class, which declares config sources, which produce fields.",
        30, 42, 700, 18, SUB_STYLE)

W = 370
p1.uml("reg", "ModuleRegistry", 30, 80, W, file="registry.py",
       attrs=["package_name: str", "errors: list[str]"],
       ops=["+ discover(): ModuleRegistry",
            "+ get(module_id): RunnableModule | None",
            "+ modules: list[RunnableModule]",
            "+ sources_by_id(): dict[str, ConfigSource]",
            "+ __len__() / __iter__()",
            "- _collect(py_module)"])

p1.uml("mod", "RunnableModule", 30, 360, W, stereo="abstract", file="module_descriptor.py",
       attrs=["id: str", "title: str", "description: str", "order: int = 100",
              "extra_sys_path: Sequence[str] = ()", "opens_window: bool = False"],
       ops=["+ config_sources(): list[ConfigSource]",
            "+ run()  {abstract}",
            "+ label(): str"])

p1.uml("src", "ConfigSource", 30, 700, W, stereo="abstract", file="config_sources.py",
       attrs=["id: str", "title: str", "description: str"],
       ops=["+ fields(): list[ConfigField]  {abstract}",
            "+ evaluate(ovr, side_effects): dict  {abstract}",
            "+ apply(ovr)  {abstract}"])

p1.uml("fld", "ConfigField", 440, 360, W, stereo="dataclass", file="config_fields.py",
       attrs=["name: str", "label: str", "kind: FieldKind", "choices: Sequence[str]",
              "help / section: str", "secret / derived: bool",
              "editable / persist: bool", "default: Any"],
       ops=["+ to_python(raw): Any",
            "+ to_display(value): str",
            "+ validate(raw): str",
            "- __post_init__()"])

p1.uml("knd", "FieldKind", 440, 760, W, stereo="str, Enum", file="config_fields.py",
       attrs=["TEXT / MULTILINE", "INT / FLOAT / BOOL", "CHOICE", "FILE / DIR"],
       ops=[])

p1.text("knf", "kind_for_value(value) -> FieldKind   (module level helper)",
        440, 960, W, 20, SUB_STYLE)

p1.edge("e1", "reg", "mod", "discovers 0..*   imports Launcher/modules/*.py")
p1.edge("e2", "mod", "src", "config_sources() 0..*")
p1.edge("e3", "src", "fld", "fields() 0..*", exit=("1", "0.5"), entry=("0", "1"))
p1.edge("e4", "fld", "knd", "kind", exit=("0.5", "1"), entry=("0.5", "0"))

# ===========================================================================
# Page 2 - the ConfigSource family
# ===========================================================================
p2 = Page("2 - ConfigSource family")
p2.text("t2", "Two backends behind the same three operations", 30, 16, 560, 24, TITLE_STYLE)
p2.text("t2s", "fields() / evaluate() / apply() - the editor and the child process treat both alike.",
        30, 42, 700, 18, SUB_STYLE)

p2.uml("src2", "ConfigSource", 240, 80, W, stereo="abstract", file="config_sources.py",
       attrs=["id: str", "title: str", "description: str"],
       ops=["+ fields(): list[ConfigField]  {abstract}",
            "+ evaluate(ovr, side_effects): dict  {abstract}",
            "+ apply(ovr)  {abstract}"])

p2.uml("py", "PyModuleConfigSource", 20, 340, W, file="config.py / ui_config.py",
       attrs=["module_name: str", "file_path: Path", "ignore: set[str]",
              "section_default: str", "show_undeclared: bool",
              "- _specs / _spec_order", "- _parsed: dict | None"],
       ops=["+ fields(): list[ConfigField]",
            "+ evaluate(ovr, side_effects): dict",
            "+ apply(ovr)   setattr on the module",
            "- _parse(): dict   ast.parse + comments",
            "- _trailing_comments(source): dict",
            "- _exec_source(ovr, side_effects)",
            "- _import_values(): dict   fallback"])

p2.uml("env", "EnvFileConfigSource", 450, 340, W, file=".polarion.env",
       attrs=["file_path: Path", "write_back: bool = False",
              "section_default: str", "- _specs / _spec_order"],
       ops=["+ fields(): list[ConfigField]",
            "+ evaluate(ovr, side_effects): dict",
            "+ apply(ovr)   -> os.environ",
            "- _read_file(): dict[str, str]"])

p2.uml("ns", "_OverridingNamespace", 20, 760, W, stereo="dict", file="config_sources.py",
       attrs=["- _overrides: dict"],
       ops=["+ __setitem__(key, value)", "+ apply_unassigned()"])

p2.note("n2",
        "Why re-execute instead of setattr?\n\n"
        "config.py derives values from each other:\n"
        "  tool_folder = \"STM32Cube\"\n"
        "  TEMP_OUTPUT_FILE = f\"output/{tool_folder}/temp.txt\"\n\n"
        "__setitem__ substitutes the user value at the moment\n"
        "tool_folder is assigned, so every derived entry is\n"
        "recomputed instead of going stale.",
        450, 620, 370, 170)

p2.text("n2b",
        "_no_directory_creation(enabled) - context manager that no-ops Path.mkdir and os.makedirs, "
        "so a preview evaluation while the user types cannot create folders on disk.",
        450, 810, 370, 60, NOTE_STYLE)

p2.edge("f1", "py", "src2", "", EDGE_INHERIT, exit=("0.5", "0"), entry=("0.25", "1"))
p2.edge("f2", "env", "src2", "", EDGE_INHERIT, exit=("0.5", "0"), entry=("0.75", "1"))
p2.edge("f3", "py", "ns", "exec globals / locals", EDGE_DEP, exit=("0.5", "1"), entry=("0.5", "0"))

# ===========================================================================
# Page 3 - the run path
# ===========================================================================
p3 = Page("3 - Run path")
p3.text("t3", "Where a run crosses the process boundary", 30, 16, 560, 24, TITLE_STYLE)
p3.text("t3s", "One child process per run - clean configuration state, output streamed back through a queue.",
        30, 42, 700, 18, SUB_STYLE)

p3.lane("laneL", "LAUNCHER PROCESS", 20, 80, 390, 780)
p3.lane("laneR", "CHILD PROCESS - one per run", 430, 80, 390, 780)

BW, BX = 350, 20
p3.flow("L1", "laneL", "LauncherApp (Tk)", ["ui/app.py - module list + config editor"], BX, 50, BW, 50)
p3.flow("L2", "laneL", "SettingsStore.as_dict()",
        ["{source_id: {key: value}}", "stored + volatile (secrets) merged"], BX, 140, BW, 60)
p3.flow("L3", "laneL", "ProcessRunner.start(id, overrides)",
        ["writes %TEMP%/launcher_cfg_*.json", "subprocess.Popen - CREATE_NO_WINDOW"], BX, 250, BW, 60)
p3.flow("L4", "laneL", "reader thread -> queue",
        ["MSG_OUTPUT / MSG_STATUS / MSG_FINISHED", "4 KiB chunks, incremental utf-8 decode"],
        BX, 560, BW, 60)
p3.flow("L5", "laneL", "LauncherApp._drain_queue()",
        ["polled from the Tk main loop"], BX, 670, BW, 50)

p3.flow("R1", "laneR", "child_main.main(id, json)",
        ["ensure_project_root_on_path()", "use_project_root_as_cwd()"], BX, 250, BW, 60)
p3.flow("R2", "laneR", "ModuleRegistry().discover() -> get(id)",
        ["discovery errors printed, never raised"], BX, 360, BW, 50)
p3.flow("R3", "laneR", "source.apply(ovr) per config source",
        ["PyModule -> setattr, Env -> os.environ", "secret fields echoed as ***"], BX, 450, BW, 60)
p3.flow("R4", "laneR", "RunnableModule.run()",
        ["prints, own Tk window, sys.exit - all safe", "exit 0 / 1 failed / 2 usage / 3 unknown id"],
        BX, 560, BW, 60)

p3.edge("r1", "L1", "L2")
p3.edge("r2", "L2", "L3")
p3.edge("r3", "L3", "R1", "python -u -m Launcher.child_main", EDGE_CROSS,
        exit=("1", "0.5"), entry=("0", "0.5"))
p3.edge("r4", "R1", "R2")
p3.edge("r5", "R2", "R3")
p3.edge("r6", "R3", "R4")
p3.edge("r7", "R4", "L4", "stdout + stderr (piped)", EDGE_CROSS,
        exit=("0", "0.5"), entry=("1", "0.5"))
p3.edge("r8", "L4", "L5")

p3.text("t3f",
        "project.py holds PROJECT_ROOT and SETTINGS_FILE and has no classes.   "
        "stop() -> taskkill /F /T on the whole tree.   "
        "The overrides file is unlinked when the child exits.",
        20, 880, 800, 40, SUB_STYLE)

# ===========================================================================
# Page 4 - launcher side services
# ===========================================================================
p4 = Page("4 - Launcher-side services")
p4.text("t4", "The two classes that run the launcher side", 30, 16, 560, 24, TITLE_STYLE)
p4.text("t4s", "Drawn as steps on page 3; here as classes. Neither is imported by the child process.",
        30, 42, 700, 18, SUB_STYLE)

p4.uml("set", "SettingsStore", 30, 80, W, file="settings_store.py",
       attrs=["path: Path = SETTINGS_FILE",
              "- _sources: dict[str, dict]   persisted",
              "- _volatile: dict[str, dict]  session only",
              "- _ui: dict[str, Any]"],
       ops=["+ load() / save()",
            "+ overrides(source_id): dict",
            "+ set_overrides(id, values, volatile_keys)",
            "+ clear_source(source_id)",
            "+ as_dict(): dict[str, dict]",
            "+ ui_value(key, default) / set_ui_value()"])

p4.uml("run", "ProcessRunner", 440, 80, W, file="process_runner.py",
       attrs=["queue: Queue[tuple[str, Any]]",
              "- _process: Popen | None",
              "- _reader: Thread | None",
              "- _overrides_file: Path | None",
              "- _module_id: str",
              "- _stopping: bool"],
       ops=["+ is_running(): bool",
            "+ module_id: str",
            "+ start(module_id, overrides)",
            "+ stop()   taskkill /F /T on the tree",
            "- _write_overrides(ovr): Path",
            "- _cleanup_overrides()",
            "- _child_env(): dict   PYTHONPATH, utf-8",
            "- _creation_flags(): int",
            "- _pump_output()   the reader thread"])

p4.uml("prj", "project", 30, 470, W, stereo="module", file="project.py",
       attrs=["PROJECT_ROOT: Path", "SETTINGS_FILE: Path"],
       ops=["project_path(*parts): Path",
            "ensure_project_root_on_path()",
            "use_project_root_as_cwd()"])

p4.note("n4", """Queue payloads are (kind, value) tuples:

  MSG_OUTPUT    str, a chunk of child stdout
  MSG_STATUS    str, a launcher status line
  MSG_FINISHED  int, the child exit code

CHILD_MODULE = Launcher.child_main""",
        440, 620, 370, 140)

p4.note("n4b", """Overrides are keyed by ConfigSource.id, never by
module id - two modules returning a source with the
same id share the values.

persist=False fields live only in _volatile: they are
merged into as_dict() for the child, but never written
to launcher_settings.json.""",
        30, 700, 370, 150)

p4.edge("g1", "set", "run", "as_dict() feeds start()", EDGE,
        exit=("1", "0.25"), entry=("0", "0.25"))
p4.edge("g2", "set", "prj", "SETTINGS_FILE", EDGE_DEP, exit=("0.5", "1"), entry=("0.5", "0"))
p4.edge("g3", "run", "prj", "PROJECT_ROOT", EDGE_DEP, exit=("0", "0.75"), entry=("1", "0.5"))


# ===========================================================================
pages = [
    (p1, "LauncherCorePage1"),
    (p2, "LauncherCorePage2"),
    (p3, "LauncherCorePage3"),
    (p4, "LauncherCorePage4"),
]
doc = (
    '<mxfile host="Electron" agent="Claude Code" version="22.0.3" type="device">\n'
    + "\n".join(page.xml(did) for page, did in pages)
    + "\n</mxfile>\n"
)

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(doc, encoding="utf-8")

# sanity: it has to parse
import xml.etree.ElementTree as ET
tree = ET.fromstring(doc)
diagrams = tree.findall("diagram")
print(f"OK  {OUT}")
print(f"    {len(doc)} bytes, {len(diagrams)} pages")
for d in diagrams:
    cells = d.findall(".//mxCell")
    print(f"    - {d.get('name')}: {len(cells)} cells")
