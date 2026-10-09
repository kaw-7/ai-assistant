# -*- coding: utf-8 -*-
"""Generate three class diagrams in ClassDiagram/ (uncompressed mxGraph XML).

AIAssistant.drawio        AI providers, the AI engine (preprocessing, risk assessment),
                          and a flow sequence through the engine
PolarionAssistant.drawio  the PolarionAssistant packages
IssueReviewUI.drawio      the issue review UI
Plain draw.io UML class shapes so everything stays editable by hand.
"""
from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape


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


# header fill / stroke per config source - the "(uses ...)" line names it as well
CONFIG_COLOURS = {
    "config": ("#DAE8FC", "#6C8EBF"),               # config.py - AI engine
    "testspec_config": ("#D5E8D4", "#82B366"),      # PolarionAssistant/TestSpec
    "valid_report_config": ("#FFE6CC", "#D79B00"),  # PolarionAssistant/ValidReport
    "ui_config": ("#E1D5E7", "#9673A6"),            # UI
}
CONFIG_FILES = {
    "config": "config  (config.py)",
    "testspec_config": "testspec_config  (PolarionAssistant/TestSpec)",
    "valid_report_config": "valid_report_config  (PolarionAssistant/ValidReport)",
    "ui_config": "ui_config  (UI/ui_config.py)",
}


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
    def uml(self, cid, name, x, y, w, attrs=(), ops=(), stereo="", file="", uses=(), cfg=None):
        """uses: config sources the class reads, shown as "(uses ...)" in the header.
        The header is filled in the colour of the first one (or of cfg, for a config box)."""
        head = []
        if stereo:
            head.append(f"&amp;laquo;{stereo}&amp;raquo;")
        head.append(f"&lt;b&gt;{esc(name)}&lt;/b&gt;")
        if file:
            head.append(f"&lt;font style=&quot;font-size:9px&quot;&gt;{esc(file)}&lt;/font&gt;")
        if uses:
            head.append(f"&lt;font style=&quot;font-size:10px&quot; color=&quot;#333333&quot;&gt;"
                        f"&lt;i&gt;(uses {esc(', '.join(uses))})&lt;/i&gt;&lt;/font&gt;")
        start = 26 + GAP * (len(head) - 1)
        label = "&lt;br&gt;".join(head)

        rows = len(attrs) + len(ops)
        height = start + rows * ROW + (DIV if attrs and ops else 0)

        style = CLASS_STYLE.format(ss=start)
        colour = CONFIG_COLOURS.get(cfg or (uses[0] if uses else ""))
        if colour:
            style += f"fillColor={colour[0]};strokeColor={colour[1]};"

        self.raw(
            f'        <mxCell id="{cid}" value="{label}" '
            f'style="{style}" vertex="1" parent="1">\n'
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

    def legend(self, cid, x, y, keys):
        """Colour key for the "(uses ...)" headers on this page."""
        self.text(cid, "Config used by a class - header colour", x, y, 340, 20,
                  SUB_STYLE.replace("fontColor=#666666;", "fontStyle=1;"))
        for i, key in enumerate(keys):
            fill, stroke = CONFIG_COLOURS[key]
            row = y + 26 + i * 24
            self.text(f"{cid}-c{i}", "", x, row, 24, 16,
                      f"rounded=0;html=1;fillColor={fill};strokeColor={stroke};")
            self.text(f"{cid}-t{i}", CONFIG_FILES[key], x + 32, row - 2, 380, 20, SUB_STYLE)

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
# Page 1 - AI providers
# ===========================================================================
p1 = Page("1 - AI providers")
p1.text("t1", "AIProvider - one interface per LLM vendor", 30, 16, 700, 24, TITLE_STYLE)
p1.text("t1s", "Every provider implements both abstract classes: generate_response() for the call, "
        "AIContext for the running question/answer transcript.", 30, 42, 1000, 18, SUB_STYLE)

p1.uml("aip", "AIProvider", 230, 80, 340, stereo="abstract", file="AIProvider/AIProvider.py",
       ops=["+ generate_response(prompt: str): str  {abstract}"])
p1.uml("aic", "AIContext", 770, 80, 340, stereo="abstract", file="AIProvider/AIContext.py",
       ops=["+ save_question(prompt: str)  {abstract}",
            "+ save_response(prompt: str)  {abstract}",
            "+ retrieve_context(): str  {abstract}"])

PW, PY = 250, 320
COMMON = ["+ generate_response(user_input): str",
          "+ save_question(q) / save_response(r)",
          "+ retrieve_context(): str"]
p1.uml("gem", "GeminiProvider", 30, PY, PW, file="google.genai",
       attrs=["client: genai.Client", "context: str"],
       ops=COMMON + ["- _get_key_from_env()"],
       uses=['config'])
p1.uml("azu", "AzureOpenAIProvider", 300, PY, PW, file="openai.AzureOpenAI",
       attrs=["client: AzureOpenAI", "context: str"],
       ops=COMMON + ["- _get_key_from_env()", "- _print_token_usage(response)"])
p1.uml("oai", "OpenAIProvider", 570, PY, PW, file="openai",
       attrs=["context: str"],
       ops=COMMON + ["- _get_key_from_env()"],
       uses=['config'])
p1.uml("ppx", "PerplexityProvider", 840, PY, PW, file="openai.OpenAI (Perplexity endpoint)",
       attrs=["client: OpenAI", "context: str"],
       ops=COMMON + ["- _get_key_from_env()"],
       uses=['config'])
p1.uml("cla", "ClaudeProvider", 1110, PY, PW, file="claude_agent_sdk",
       attrs=["context: str"],
       ops=COMMON + ["- _ask(prompt): str  async"],
       uses=['config'])

for i, cid in enumerate(["gem", "azu", "oai", "ppx", "cla"]):
    entry = (f"{0.1 + i * 0.2:.1f}", "1")
    p1.edge(f"ip{i}", cid, "aip", "", EDGE_INHERIT, exit=("0.3", "0"), entry=entry)
    p1.edge(f"ic{i}", cid, "aic", "", EDGE_INHERIT, exit=("0.7", "0"), entry=entry)

p1.note("n1",
        "Which provider runs?\n"
        "main.ai_engine() constructs one by hand - today ClaudeProvider()\n"
        "(todo in code: an AI factory). That single instance is passed to\n"
        "every preprocessor and agent on page 2.\n\n"
        "Model selection\n"
        "  OpenAI, Perplexity: config.MODEL_NAME\n"
        "  Gemini, Azure: model name hardcoded in the provider\n"
        "  Claude: SDK default, signs in with the claude.ai login",
        30, 560, 560, 180)
p1.note("n1b",
        "ClaudeProvider.py - module helper\n"
        "run_async(coro): runs the SDK coroutine with asyncio.run(), or on a\n"
        "dedicated thread with its own Proactor loop when a loop is already\n"
        "running (Spyder / Jupyter).\n\n"
        "Gemini and Claude also write the transcript to config.CONTEXT_FILE.",
        620, 560, 490, 140)

p1.legend("lg1", 1140, 560, ["config"])

# ===========================================================================
# Page 2 - AI engine: preprocessing and risk assessment
# ===========================================================================
p2 = Page("2 - AI engine")
p2.text("t2", "main.py - release notes in, risk report out", 30, 16, 700, 24, TITLE_STYLE)
p2.text("t2s", "Every class that talks to the LLM takes the AIProvider from page 1 in its constructor "
        "and keeps it as ai_engine.", 30, 42, 1000, 18, SUB_STYLE)

p2.uml("main", "main", 30, 80, 320, stereo="module", file="main.py",
       ops=["AskUser(question, answer=None): bool",
            "ai_engine()   match TOOL_PREPROCESSOR -> preprocessor"],
       uses=['config'])
p2.uml("pipe", "PreprocessingPipeline", 410, 80, 400, file="Preprocessor/PreprocessingPipeline.py",
       attrs=["chunk_preprocessor: TextChunkerPreprocessor",
              "ai_preprocessor: AbstractPreprocessor",
              "structured_issues: str"],
       ops=["+ Start()   one pass if USE_PREPROCESS_CHUNKING=n",
            "+ getIssues(): str"],
       uses=['config'])
p2.uml("cfg", "config", 870, 80, 380, stereo="module", file="config.py",
       attrs=["tool_folder, TOOL_NAME, TOOL_RELEASE_NOTES",
              "TOOL_VERSION_START / TOOL_VERSION_END",
              "TOOL_PREPROCESSOR, USE_PREPROCESS_CHUNKING",
              "CHUNK_SIZE / CHUNK_DELIMITER",
              "PROCEED_WITH_AI_RISK_ASSESSMENT",
              "MAX_COUNT_OF_ISSUES_PROCESSED_AT_ONCE_BY_AI",
              "*_INSTRUCTIONS_PATH, REF_PATH",
              "TEMP_* / *_OUTPUT_FILE, CONTEXT_FILE",
              "CSV_TEMPLATE, ISSUE_END_MARKER",
              "MODEL_NAME"],
       cfg='config')

p2.uml("ptype", "PreprocessorType", 1330, 160, 340, stereo="Enum", file="Preprocessor/AbstractPreprocessor.py",
       attrs=["AI = \"AI\"", "IAR_EmbeddedWorkbench", "RELOAD = \"Reload_Existing\""])
p2.uml("absp", "AbstractPreprocessor", 410, 330, 400, stereo="abstract",
       file="Preprocessor/AbstractPreprocessor.py",
       ops=["+ preprocess_file(release_notes_file_path): str  {abstract}",
            "+ save_output(text, file_path, opts=\"w\")",
            "+ check_characters(release_notes)"])

QY, QW = 540, 270
p2.uml("chunk", "TextChunkerPreprocessor", 30, QY, QW, file="Preprocessor/TextChunkerPreprocessor.py",
       attrs=["ai_engine: AIProvider", "it, slice_position", "end: bool"],
       ops=["+ preprocess_file(path): str", "+ End(): bool",
            "- _slice_input(path)", "- _generate_chunk(path)"],
       uses=['config'])
p2.uml("aipre", "AIPreprocessor", 320, QY, QW, file="Preprocessor/AIPreprocessor.py",
       attrs=["ai_engine: AIProvider"],
       ops=["+ preprocess_file(path): str", "+ generate_input(path): str"],
       uses=['config'])
p2.uml("reload", "ReloadExistingPreprocessor", 610, QY, QW, file="Preprocessor/ReloadExistingPreprocessor.py",
       attrs=["ai_engine: AIProvider"],
       ops=["+ preprocess_file(path): str", "reuses TEMP_OUTPUT_FILE, no AI call"],
       uses=['config'])
p2.uml("iar", "IAREWPreprocessor", 900, QY, QW, file="Preprocessor/IAREWPreprocessor.py",
       ops=["+ preprocess_file(path): str",
            "parse_txt_to_csv(...)   module function"],
       uses=['config'])

for i, cid in enumerate(["chunk", "aipre", "reload", "iar"]):
    p2.edge(f"pi{i}", cid, "absp", "", EDGE_INHERIT, exit=("0.5", "0"), entry=(f"{0.15 + i * 0.23:.2f}", "1"))

p2.uml("absr", "AbstractRiskAssessmentAgent", 410, 820, 400, stereo="abstract",
       file="RiskAssessment/AbstractRiskAssessmentAgent.py",
       ops=["+ process_issues()  {abstract}"])
p2.uml("agent", "AIRiskAssessmentAgent", 410, 960, 400, file="RiskAssessment/AIRiskAssessmentAgent.py",
       attrs=["ai_engine: AIProvider"],
       ops=["+ process_issues(input_data_content)",
            "- _process_issues_in_chunks(content)",
            "- _generate_input(content): str",
            "- _get_up_to_nth(text, substring, n, start)",
            "- _get_total_occurances(text, substring): int"],
       uses=['config'])
p2.uml("summ", "AIRiskSummary", 870, 820, 380, file="RiskAssessment/AIRiskSummary.py",
       attrs=["ai_engine: AIProvider"],
       ops=["+ generate_summary()", "+ generate_input(user_context): str"],
       uses=['config'])
p2.text("summn", "not called at the moment - commented out in main.ai_engine()",
        870, 960, 380, 20, SUB_STYLE)

p2.edge("m1", "main", "pipe", "builds, Start()", EDGE, exit=("1", "0.5"), entry=("0", "0.3"))
p2.edge("m3", "main", "agent", "process_issues() if PROCEED_...=y", EDGE, exit=("0", "0.5"), entry=("0", "0.5"))
p2.edge("m4", "pipe", "chunk", "chunk_preprocessor", EDGE, exit=("0", "0.8"), entry=("0.5", "0"))
p2.edge("m5", "pipe", "absp", "ai_preprocessor", EDGE, exit=("0.5", "1"), entry=("0.5", "0"))
p2.edge("m6", "agent", "absr", "", EDGE_INHERIT, exit=("0.5", "0"), entry=("0.5", "1"))

p2.note("n2",
        "File hand-offs (paths from config.py, under output/{tool_folder}/)\n\n"
        "TOOL_RELEASE_NOTES\n"
        "  -> TextChunker -> temp_chunk.txt   (only if USE_PREPROCESS_CHUNKING=y)\n"
        "  -> AI / IAR / Reload preprocessor -> temp_output_risk.txt\n"
        "  -> AIRiskAssessmentAgent -> final_risk_report.txt\n"
        "  -> reviewed in the UI (IssueReviewUI.drawio),\n"
        "     imported into Polarion (PolarionAssistant.drawio)",
        870, 995, 460, 140)

p2.legend("lg2", 1290, 80, ["config"])

# ===========================================================================
# Page 3 - flow sequence through the AI engine
# ===========================================================================
SEQ_CALL = "html=1;verticalAlign=bottom;endArrow=block;endFill=1;fontSize=10;"
SEQ_RET = "html=1;verticalAlign=bottom;endArrow=open;endFill=0;dashed=1;fontSize=10;"
SEQ_FILE = ("html=1;verticalAlign=bottom;endArrow=open;endFill=0;fontSize=10;"
            "strokeColor=#6C8EBF;fontColor=#3A5A8C;")
SEQ_SELF = "html=1;endArrow=block;endFill=1;rounded=0;"
LIFELINE = ("shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=0;"
            "collapsible=0;recursiveResize=0;outlineConnect=0;portConstraint=eastwest;size=50;")
FRAME = "shape=umlFrame;whiteSpace=wrap;html=1;pointerEvents=0;fillColor=none;height=24;fontSize=11;"
SEP = "html=1;endArrow=none;dashed=1;dashPattern=8 4;fontSize=10;align=left;verticalAlign=top;"


class SeqPage(Page):
    """UML sequence page: lifelines at fixed x, messages placed down a y cursor."""

    def __init__(self, name, lanes, top=80):
        super().__init__(name)
        self.lanes = lanes          # key -> (x centre, header html, fill colour or "")
        self.top = top
        self.y = top + 90
        self.n = 0
        self.mark = None

    def begin(self):
        self.mark = len(self.cells)    # lifelines get inserted here, behind everything

    def _edge(self, cid, label, style, x1, y1, x2, y2, points=()):
        pts = "".join(f'<mxPoint x="{px}" y="{py}" />' for px, py in points)
        arr = f'            <Array as="points">{pts}</Array>\n' if points else ""
        self.raw(
            f'        <mxCell id="{cid}" value="{esc(label)}" style="{style}" edge="1" parent="1">\n'
            f'          <mxGeometry relative="1" as="geometry">\n'
            f'            <mxPoint x="{x1}" y="{y1}" as="sourcePoint" />\n'
            f'            <mxPoint x="{x2}" y="{y2}" as="targetPoint" />\n'
            f'{arr}'
            f'          </mxGeometry>\n'
            f'        </mxCell>'
        )

    def msg(self, src, tgt, label, kind="call", dy=34):
        style = {"call": SEQ_CALL, "ret": SEQ_RET, "file": SEQ_FILE}[kind]
        if kind != "ret":
            self.n += 1
            label = f"{self.n}. {label}"
        self.y += dy
        self._edge(f"m{self.n}-{self.y}", label, style,
                   self.lanes[src][0], self.y, self.lanes[tgt][0], self.y)

    def self_msg(self, who, label, dy=34):
        self.n += 1
        self.y += dy
        x = self.lanes[who][0]
        self._edge(f"s{self.n}", "", SEQ_SELF, x, self.y, x, self.y + 16,
                   points=[(x + 30, self.y), (x + 30, self.y + 16)])
        self.text(f"st{self.n}", f"{self.n}. {label}", x + 36, self.y - 6, 300, 20,
                  SUB_STYLE.replace("fontColor=#666666;", "fontSize=10;").replace("fontSize=11;", ""))
        self.y += 16

    def frame(self, cid, label, x1, x2, y1, y2, tab=260):
        self.text(cid, label, x1, y1, x2 - x1, y2 - y1, FRAME + f"width={tab};")

    def separator(self, cid, label, x1, x2, y):
        self._edge(cid, label, SEP, x1, y, x2, y)

    def seq_note(self, cid, text, x, y, w, h):
        self.note(cid, text, x, y, w, h)

    def finish(self, bottom):
        tmp = Page("")
        for key, (x, head, fill) in self.lanes.items():
            st = LIFELINE + (f"fillColor={fill};" if fill else "")
            tmp.raw(
                f'        <mxCell id="ll-{key}" value="{head}" style="{st}" vertex="1" parent="1">\n'
                f'          <mxGeometry x="{x - 80}" y="{self.top}" width="160" height="{bottom - self.top}" as="geometry" />\n'
                f'        </mxCell>'
            )
        self.cells[self.mark:self.mark] = tmp.cells


def lane_head(name, sub):
    return f"&lt;b&gt;{esc(name)}&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size:9px&quot;&gt;{esc(sub)}&lt;/font&gt;"


BLUE = CONFIG_COLOURS["config"][0]
p3 = SeqPage("3 - Flow sequence", {
    "main": (110, lane_head("main", "main.py - ai_engine()"), BLUE),
    "pipe": (310, lane_head("PreprocessingPipeline", ""), BLUE),
    "chunk": (510, lane_head("TextChunkerPreprocessor", ""), BLUE),
    "pre": (710, lane_head("AIPreprocessor", "the selected preprocessor"), BLUE),
    "agent": (910, lane_head("AIRiskAssessmentAgent", ""), BLUE),
    "prov": (1110, lane_head("ClaudeProvider", "the AIProvider instance"), BLUE),
    "llm": (1310, lane_head("Claude", "claude_agent_sdk.query()"), "#F5F5F5"),
    "files": (1510, lane_head("Files", "output/{tool_folder}/ + input/"), "#F5F5F5"),
})
p3.text("t3", "Flow sequence - one run of main.ai_engine()", 30, 16, 700, 24, TITLE_STYLE)
p3.text("t3s", "Blue arrows are file reads and writes - the steps hand data to each other through files, "
        "not only through return values. Paths are config.py names.", 30, 42, 1300, 18, SUB_STYLE)
p3.begin()

# --- setup ---------------------------------------------------------------
p3.msg("main", "prov", "ClaudeProvider()", dy=10)
p3.msg("main", "pre", "AIPreprocessor(ai_provider)   - match TOOL_PREPROCESSOR")
p3.msg("pre", "files", "truncate TEMP_OUTPUT_FILE (temp_output_risk.txt)", "file")
p3.msg("main", "chunk", "TextChunkerPreprocessor(ai_provider)")
p3.msg("main", "pipe", "PreprocessingPipeline(chunker, preprocessor)")
p3.msg("main", "pipe", "Start()")

# --- preprocessing: alt chunking ------------------------------------------
fx1, fx2 = 200, 1600
alt_top = p3.y + 20
p3.y += 30
p3.msg("pipe", "pre", "preprocess_file(TOOL_RELEASE_NOTES)")
ai_pre_top = p3.y + 14
p3.y += 14
p3.msg("pre", "files", "read INSTRUCTIONS_PATH + release notes", "file")
p3.self_msg("pre", "generate_input(): fill tool_name, vstart, vend")
p3.msg("pre", "prov", "generate_response(prompt)")
p3.self_msg("prov", "save_question(prompt)")
p3.msg("prov", "files", "write transcript to CONTEXT_FILE", "file")
p3.msg("prov", "llm", "query(prompt), allowed_tools=[]")
p3.msg("llm", "prov", "AssistantMessage text blocks", "ret")
p3.self_msg("prov", "save_response(text)")
p3.msg("prov", "pre", "response: structured issues", "ret")
p3.msg("pre", "files", "append to TEMP_OUTPUT_FILE", "file")
p3.y += 14
p3.frame("fr-ai", "AI preprocessing  (reused below)", 620, 1590, ai_pre_top, p3.y, tab=230)
p3.msg("pre", "pipe", "structured issues", "ret")

sep_y = p3.y + 22
p3.separator("sep-chunk", "[else: USE_PREPROCESS_CHUNKING = y]", fx1, fx2, sep_y)
p3.y = sep_y + 10
p3.msg("pipe", "files", "copy TOOL_RELEASE_NOTES -> TEMP_REL_NOTES, clear TEMP_CHUNK_FILE", "file")
loop_top = p3.y + 14
p3.y += 30
p3.msg("pipe", "chunk", "preprocess_file(TEMP_REL_NOTES)")
p3.msg("chunk", "files", "read TEMP_REL_NOTES", "file")
p3.self_msg("chunk", "_generate_chunk(): cut at CHUNK_DELIMITER / ~CHUNK_SIZE")
p3.msg("chunk", "files", "write chunk to TEMP_CHUNK_FILE", "file")
p3.msg("chunk", "files", "_slice_input(): drop the chunk from TEMP_REL_NOTES", "file")
p3.msg("chunk", "pipe", "chunk text", "ret")
p3.msg("pipe", "pre", "preprocess_file(TEMP_CHUNK_FILE)   -> AI preprocessing as above")
p3.msg("pre", "pipe", "issues of this chunk, added to structured_issues", "ret")
p3.msg("pipe", "chunk", "End()")
p3.msg("chunk", "pipe", "True once the rest fits in one chunk", "ret")
p3.y += 16
p3.frame("fr-loop", "loop  [until End()]", fx1 + 20, fx2 - 20, loop_top, p3.y, tab=150)
p3.y += 14
p3.frame("fr-alt", "alt  [USE_PREPROCESS_CHUNKING = n]", fx1, fx2, alt_top, p3.y, tab=270)
p3.msg("pipe", "main", "Start() returns", "ret")

# --- risk assessment -----------------------------------------------------
p3.msg("main", "files", "read TEMP_OUTPUT_FILE -> structured_issues", "file")
p3.self_msg("main", "AskUser(\"Proceed with AI risk assessment\", PROCEED_WITH_AI_RISK_ASSESSMENT)")
opt_top = p3.y + 20
p3.y += 30
p3.msg("main", "agent", "AIRiskAssessmentAgent(ai_provider)")
p3.msg("main", "agent", "process_issues(structured_issues)")
p3.msg("agent", "files", "truncate RISK_ASSESSMENT_OUTPUT_FILE (final_risk_report.txt)", "file")
rl_top = p3.y + 14
p3.y += 30
p3.self_msg("agent", "_get_up_to_nth(): next MAX_COUNT_OF_ISSUES_... issues, split at ISSUE_END_MARKER")
p3.msg("agent", "files", "_generate_input(): read RISK_INSTRUCTIONS_PATH + REF_PATH", "file")
p3.msg("agent", "prov", "generate_response(prompt)")
p3.msg("prov", "llm", "query(prompt)   - transcript and context as above")
p3.msg("llm", "prov", "text blocks", "ret")
p3.msg("prov", "agent", "risk assessment of these issues", "ret")
p3.msg("agent", "files", "append to RISK_ASSESSMENT_OUTPUT_FILE", "file")
p3.y += 16
p3.frame("fr-risk", "loop  [until all issues sent]", 820, fx2 - 20, rl_top, p3.y, tab=200)
p3.msg("agent", "main", "done", "ret")
p3.y += 14
p3.frame("fr-opt", "opt  [answer = y]", 20, fx2, opt_top, p3.y, tab=150)

bottom = p3.y + 30
p3.finish(bottom)

p3.note("n3a",
        "TOOL_PREPROCESSOR picks the class on the AIPreprocessor lifeline:\n"
        "- AI: AIPreprocessor, as drawn\n"
        "- IAR_EmbeddedWorkbench: IAREWPreprocessor - no AI call,\n"
        "   parse_txt_to_csv() writes TEMP_OUTPUT_FILE\n"
        "- Reload_Existing: ReloadExistingPreprocessor - no AI call,\n"
        "   returns the TEMP_OUTPUT_FILE of an earlier run",
        1640, 280, 440, 120)
p3.note("n3b",
        "main reads TEMP_OUTPUT_FILE itself instead of using\n"
        "PreprocessingPipeline.getIssues(); in chunk mode the\n"
        "AI preprocessor appends each chunk's result to it.",
        1640, 420, 440, 70)
p3.note("n3c",
        "Result: final_risk_report.txt\n"
        "  -> reviewed in the UI (IssueReviewUI.drawio)\n"
        "  -> imported into Polarion (PolarionAssistant.drawio)",
        1640, bottom - 80, 440, 70)

# ===========================================================================
# Page 4 - PolarionAssistant (own file)
# ===========================================================================
p4 = Page("PolarionAssistant")
p4.text("t3", "PolarionAssistant - documents and issues in Polarion", 30, 16, 700, 24, TITLE_STYLE)
p4.text("t3s", "Every worker shares one module-level PolarionConnector and exits the process "
        "when it cannot connect.", 30, 42, 1000, 18, SUB_STYLE)

p4.uml("conn", "PolarionConnector", 30, 80, 360, file="Core/PolarionConnector.py",
       attrs=["client", "polarion_username: str"],
       ops=["+ connect(): client | None",
            "+ get_current_user_info(): (full_name, email)",
            "+ is_connected(): bool",
            "+ disconnect()"])
p4.uml("work", "PolarionWorker", 430, 80, 400, stereo="abstract", file="Core/PolarionWorker.py",
       attrs=["- _connector: PolarionConnector   shared", "- _client"],
       ops=["+ PrintDocDetails()  {abstract}",
            "+ getTemplate(proj_id, template_path)",
            "- _ModifyItems(items, placeholder, substitute)",
            "- _moveChildren(document, workitem, target_parent)"])
p4.uml("item", "ItemUtil", 870, 80, 370, file="Core/ItemUtil.py",
       ops=["+ find_heading_item_by_name(document, heading_name)  {static}"])
p4.uml("fact", "IssueDAOFactory", 870, 180, 370, file="Core/IssueDAOFactory.py",
       ops=["+ create(connector, issueDTO): work item  {static}"],
       uses=['valid_report_config'])
p4.uml("pars", "IssueParser", 1280, 80, 380, file="Core/IssueParser.py",
       attrs=["file_path", "issues: list[IssueDTO]", "issues_as_string: str"],
       ops=["+ read_file()",
            "+ preprocess_initial_string_issues()",
            "+ parse_markdown_to_dto(raw_text): list[IssueDTO]  {static}",
            "- _fix_status(issue)  {static}",
            "- _fix_source(issue)  {static}"],
       uses=['valid_report_config'])

p4.lane("lts", "TestSpec", 20, 350, 1080, 270)
p4.lane("lvr", "ValidReport", 1110, 350, 550, 270)
WY, WW = 390, 250
p4.uml("tsb", "TestSpecBuilder", 30, WY, WW, file="TestSpec/TestSpecBuilder.py",
       ops=["+ createFinalDoc()", "- _createDoc()", "- _changeDocToolName(spec)",
            "- _ChangeDocStatus(items)", "- _ChangeItems(items)", "- _MoveDummyTestCases(doc)"],
       uses=['testspec_config'])
p4.uml("tsd", "TestSpecDebugger", 300, WY, WW, file="TestSpec/TestSpecDebugger.py",
       ops=["+ PrintDocDetails()", "- _PrintDocStatus(items)", "- _PrintItems(items)"],
       uses=['testspec_config'])
p4.uml("tcb", "TestCaseBuilder", 570, WY, WW, file="TestSpec/TestCaseBuilder.py",
       ops=["+ MoveTestCases()", "- _ModifyATestCase(tc, req_desc)",
            "- _CreateDescription(desc)", "- _CreateTestAction(desc)"],
       uses=['testspec_config'])
p4.uml("tcd", "TestCaseDebugger", 840, WY, WW, file="TestSpec/TestCaseDebugger.py",
       ops=["+ PrintDocDetails()", "- _ReadATestCase(tc, req_desc)",
            "- _CreateDescription(desc)", "- _CreateTestAction(desc)"],
       uses=['testspec_config'])
p4.uml("vrb", "ValidReportBuilder", 1120, WY, WW, file="ValidReport/ValidReportBuilder.py",
       ops=["+ createFinalDoc()", "- _createDoc()", "- _changeDocToolName(report)",
            "- _ChangeDocStatus(items)", "- _ChangeItems(items)"],
       uses=['valid_report_config'])
p4.uml("imp", "PolarionIssueImporter", 1390, WY, WW, file="ValidReport/PolarionIssueImporter.py",
       ops=["+ GetDocItems(): (doc, heading, name, email)",
            "+ ImportIssuesInPolarion()"],
       uses=['valid_report_config'])

for i, cid in enumerate(["tsb", "tsd", "tcb", "tcd", "vrb", "imp"]):
    p4.edge(f"wi{i}", cid, "work", "", EDGE_INHERIT, exit=("0.5", "0"), entry=(f"{0.08 + i * 0.168:.2f}", "1"))
p4.edge("wc", "work", "conn", "_connector", EDGE, exit=("0", "0.3"), entry=("1", "0.3"))
p4.edge("ip", "imp", "pars", "read_file()", EDGE, exit=("0.8", "0"), entry=("0.6", "1"))
p4.edge("if", "imp", "fact", "create() on 11 threads", EDGE_DEP, exit=("0.2", "0"), entry=("0.8", "1"))

p4.uml("tsm", "test_spec_main", 30, 660, 520, stereo="script", file="PolarionAssistant/test_spec_main.py",
       ops=["CREATE_TEST_SPEC=y, DEBUG=n  ->  TestSpecBuilder.createFinalDoc()",
            "CREATE_TEST_SPEC=y, DEBUG=y  ->  TestSpecDebugger.PrintDocDetails()",
            "DEBUG=n  ->  TestCaseBuilder.MoveTestCases()",
            "DEBUG=y  ->  TestCaseDebugger.PrintDocDetails()"],
       uses=['testspec_config'])
p4.uml("tsc", "testspec_config", 580, 660, 400, stereo="module", file="TestSpec/testspec_config.py",
       attrs=["PROJECT_ID, TOOL_NAME, CREATE_TEST_SPEC, DEBUG",
              "TEST_SPEC_TEMPLATE, PLAN_DOCU, TEST_DOCU",
              "TARGET_LOCATION / TARGET_NAME_ID / TARGET_TITLE",
              "PLACEHOLDER, PLACEHOLDER_DOCSTATUS, LINK_ROLE",
              "DOC_INPUT_HEADING, VALI_PLAN_EXCLUDED_HEADINGS"],
       cfg='testspec_config')
p4.uml("vrm", "valid_report_main", 1120, 660, 520, stereo="script", file="PolarionAssistant/valid_report_main.py",
       ops=["BUILD_VALID_REPORT=y  ->  ValidReportBuilder.createFinalDoc()",
            "always  ->  PolarionIssueImporter.ImportIssuesInPolarion()"],
       uses=['valid_report_config'])
p4.uml("vrc", "valid_report_config", 1120, 800, 520, stereo="module", file="ValidReport/valid_report_config.py",
       attrs=["PROJECT_ID, TOOL_NAME, BUILD_VALID_REPORT",
              "VALID_REPORT_TEMPLATE, TARGET_LOCATION / _NAME_ID / _TITLE",
              "PLACEHOLDER, PLACEHOLDER_DOCSTATUS, LINK_ROLE",
              "DOC_NAME, DOC_INPUT_HEADING",
              "ISSUE_INPUT_FILE = final_risk_report.txt",
              "ISSUE_MARKER_BEG / _END, ISSUE_END_MARKER"],
       cfg='valid_report_config')

p4.uml("dto", "IssueDTO", 1700, 80, 320, stereo="dataclass", file="Model/IssueDTO.py",
       attrs=["author_name / author_email", "polarion_username", "title / description",
              "defect_id / defect_description", "risk_assessment",
              "source: str = SourceDTO.KNOWN_PROBLEM_BY_VENDOR",
              "status: str = StatusDTO.NOT_EVALUATED"],
       ops=["+ __str__(): str"])
p4.uml("sdto", "StatusDTO", 1700, 380, 220, stereo="StrEnum", file="Model/IssueDTO.py",
       attrs=["RISK", "NO_RISK", "NOT_EVALUATED"])
p4.uml("ist", "IssueStatus", 1960, 380, 260, stereo="StrEnum", file="Model/DAO/IssueFields.py",
       attrs=["RISK = \"risk_exists\"", "NO_RISK = \"no_risk\"", "NOT_EVALUATED = \"not_evaluated\""])
p4.uml("srdto", "SourceDTO", 1700, 540, 220, stereo="StrEnum", file="Model/IssueDTO.py",
       attrs=["KNOWN_PROBLEM_BY_VENDOR", "KNOWN_PROBLEM_3RD_PARTY", "CORRECTION_IN_REL_NOTES",
              "KNOWN_PROBLEM_IN_NEWER_VERS", "OCCURED_AT_OTTOBOCK", "OTHER_SOURCE"])
p4.uml("isr", "IssueSource", 1960, 540, 260, stereo="StrEnum", file="Model/DAO/IssueFields.py",
       attrs=["\"knownBug\"", "\"3rdPartyBug\"", "\"fixedInNewerVersion\"",
              "\"knownBugNewerVersion\"", "\"ottobock\"", "\"otherSource\""])

p4.edge("pd", "pars", "dto", "produces", EDGE, exit=("1", "0.3"), entry=("0", "0.3"))
p4.edge("ms", "sdto", "ist", "_fix_status", EDGE_DEP, exit=("1", "0.5"), entry=("0", "0.5"))
p4.edge("mr", "srdto", "isr", "_fix_source", EDGE_DEP, exit=("1", "0.5"), entry=("0", "0.5"))
p4.note("n3",
        "The DTO enums hold the names the AI writes in the report;\n"
        "IssueParser maps them by member name to the Polarion enum ids.\n"
        "Free-text status (\"Risk exists\" / \"No risk\") is matched by regex,\n"
        "anything else becomes not_evaluated.",
        1700, 790, 520, 90)

p4.legend("lg3", 30, 870, ["testspec_config", "valid_report_config"])

# ===========================================================================
# Page 5 - issue review UI (own file)
# ===========================================================================
p5 = Page("Issue review UI")
p5.text("t4", "UI - review and edit the risk report before the Polarion import", 30, 16, 800, 24, TITLE_STYLE)
p5.text("t4s", "Tkinter. Reads ui_config.ISSUES_FILE (final_risk_report.txt), writes it back on save; "
        "a backup is taken on start.", 30, 42, 1000, 18, SUB_STYLE)

p5.uml("umain", "main", 30, 80, 380, stereo="script", file="UI/main.py",
       ops=["read ISSUES_FILE -> markup_to_issueCards()",
            "createIssuesBackUp()",
            "App(items, ISSUES_FILE).mainloop()"],
       uses=['ui_config'])
p5.uml("ser", "IssueSerializer", 30, 260, 380, stereo="module", file="UI/IssueSerializer.py",
       ops=["createIssuesBackUp(out_file, out_back)",
            "markup_to_issueCards(text): list[dict]",
            "issueCards_to_markup(issues, out_file)   App, on save"],
       uses=['ui_config'])
p5.uml("app", "App", 470, 80, 380, stereo="tk.Tk", file="UI/App.py",
       attrs=["items: list[dict]", "items_file_path", "card_widgets: list[IssueCard]",
              "filter_var", "canvas / scrollable / canvas_window"],
       ops=["+ apply_filter()",
            "- _on_canvas_configure(event)",
            "- _bind_mousewheel()",
            "- _on_mousewheel(e) / _on_mousewheel2(e)",
            "- _on_issue_save()"],
       uses=['ui_config'])
p5.uml("card", "IssueCard", 910, 80, 400, stereo="tk.Frame", file="UI/IssueCard.py",
       attrs=["item: dict", "header: IssueCardHeader",
              "status_var / status_menu   editable status",
              "desc_text / risk_text", "expanded, _edit"],
       ops=["+ matches_filter(mode): bool",
            "- _current_status(status_options)",
            "- _status_pattern(mode)  {static}",
            "- _status_matches(mode, text)",
            "- _on_status_change(value)",
            "- _toggle_expand() / _toggle_widget_expand(w)",
            "- _on_edit()",
            "- _bind_sync(widget, key) / _sync(widget, key)"],
       uses=['ui_config'])
p5.uml("hdr", "IssueCardHeader", 910, 560, 400, stereo="tk.Frame", file="UI/IssueCardHeader.py",
       attrs=["edit_btn", "save_btn"],
       ops=["__init__(master, title, on_edit, on_save)"],
       uses=['ui_config'])
p5.uml("ucfg", "ui_config", 470, 480, 380, stereo="module", file="UI/ui_config.py",
       attrs=["ISSUES_FILE / ISSUES_BACKUP_FILE",
              "TOKEN_BEG / TOKEN_END / END_ISSUE_TOKEN",
              "DEFECT_ID, DESCRIPTION, DEFECT_DESCRIPTION",
              "RISK_ASSESSMENT, STATUS",
              "RISK_EXISTS / NO_RISK / NOT_EVALUATED / ALL",
              "FONT, FONT_SIZE, GEOMETRY, PADX, PADY"],
       cfg='ui_config')

p5.edge("u1", "umain", "app", "creates", EDGE, exit=("1", "0.5"), entry=("0", "0.2"))
p5.edge("u2", "umain", "ser", "", EDGE_DEP, exit=("0.5", "1"), entry=("0.5", "0"))
p5.edge("u3", "app", "card", "0..*", EDGE, exit=("1", "0.3"), entry=("0", "0.3"))
p5.edge("u4", "card", "hdr", "header", EDGE, exit=("0.5", "1"), entry=("0.5", "0"))
p5.edge("u5", "app", "ser", "", EDGE_DEP, exit=("0", "0.85"), entry=("1", "0.8"))
p5.note("n4",
        "Mouse wheel only scrolls the issue list - widgets\n"
        "never change value on wheel (the status dropdown\n"
        "included).",
        30, 440, 380, 70)

p5.legend("lg4", 30, 540, ["ui_config"])

# ===========================================================================
import xml.etree.ElementTree as ET

OUT_DIR = Path(r"D:\who\AutomationValiReport\AIValiReport\ClassDiagram")
FILES = {
    "AIAssistant.drawio": [(p1, "AIAssistantPage1"), (p2, "AIAssistantPage2"),
                           (p3, "AIAssistantPage3")],
    "PolarionAssistant.drawio": [(p4, "PolarionAssistantPage1")],
    "IssueReviewUI.drawio": [(p5, "IssueReviewUIPage1")],
}

OUT_DIR.mkdir(parents=True, exist_ok=True)
for file_name, pages in FILES.items():
    doc = (
        '<mxfile host="Electron" agent="Claude Code" version="22.0.3" type="device">\n'
        + "\n".join(page.xml(did) for page, did in pages)
        + "\n</mxfile>\n"
    )
    out = OUT_DIR / file_name
    out.write_text(doc, encoding="utf-8")

    # sanity: it has to parse
    diagrams = ET.fromstring(doc).findall("diagram")
    print(f"OK  {out}")
    print(f"    {len(doc)} bytes, {len(diagrams)} pages")
    for d in diagrams:
        print(f"    - {d.get('name')}: {len(d.findall('.//mxCell'))} cells")
