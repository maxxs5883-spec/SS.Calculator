from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.animation import Animation
from kivy.uix.widget import Widget
import math

# ── Window size (desktop) ────────────────────────────────────────
Window.size = (380, 620)
Window.clearcolor = (0.06, 0.06, 0.06, 1)

# ── Colours (r,g,b,a 0-1) ───────────────────────────────────────
C_BG        = (0.06, 0.06, 0.06, 1)
C_DISP      = (0.10, 0.10, 0.10, 1)
C_NUM       = (0.14, 0.14, 0.16, 1)
C_OP        = (0.20, 0.20, 0.24, 1)
C_FUNC      = (0.17, 0.17, 0.20, 1)
C_EQUAL     = (1.00, 0.42, 0.21, 1)   # orange
C_CLEAR     = (0.90, 0.22, 0.27, 1)   # red
C_SPECIAL   = (0.13, 0.45, 0.80, 1)   # blue for sci funcs
C_TXT       = (1, 1, 1, 1)
C_GREY      = (0.55, 0.55, 0.55, 1)
C_ORNGE     = (1.00, 0.42, 0.21, 1)


# ── Rounded Button ───────────────────────────────────────────────
class RoundBtn(Button):
    def __init__(self, bg_color=C_NUM, radius=14, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.radius = radius
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ""
        self.color = C_TXT
        self.font_size = kwargs.get("font_size", 20)
        self.bold = True
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[self.radius])

    def on_press(self):
        anim = Animation(opacity=0.6, duration=0.05) + \
               Animation(opacity=1.0, duration=0.1)
        anim.start(self)


# ── Main Layout ──────────────────────────────────────────────────
class CalcLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=6,
                         padding=[12, 12, 12, 12], **kwargs)
        self.expression = ""
        self.just_calculated = False
        self.memory = 0

        self._build()

    def _build(self):
        # ── Display panel ──
        disp_panel = BoxLayout(orientation="vertical",
                               size_hint_y=0.28, padding=[16, 10])
        with disp_panel.canvas.before:
            Color(*C_DISP)
            self._disp_rect = RoundedRectangle(radius=[18])
        disp_panel.bind(pos=self._upd_disp, size=self._upd_disp)

        # Title row
        title_row = BoxLayout(size_hint_y=0.2)
        lbl_title = Label(text="SS.CALCULATOR", font_size=11,
                          color=C_ORNGE, bold=True,
                          halign="left", valign="middle")
        lbl_title.bind(size=lbl_title.setter("text_size"))
        self.lbl_mem = Label(text="", font_size=11,
                             color=C_GREY, halign="right", valign="middle")
        self.lbl_mem.bind(size=self.lbl_mem.setter("text_size"))
        title_row.add_widget(lbl_title)
        title_row.add_widget(self.lbl_mem)
        disp_panel.add_widget(title_row)

        # Expression label
        self.lbl_expr = Label(text="", font_size=14,
                              color=C_GREY, halign="right", valign="middle")
        self.lbl_expr.bind(size=self.lbl_expr.setter("text_size"))
        disp_panel.add_widget(self.lbl_expr)

        # Result label
        self.lbl_result = Label(text="0", font_size=46,
                                bold=True, color=C_TXT,
                                halign="right", valign="middle")
        self.lbl_result.bind(size=self.lbl_result.setter("text_size"))
        disp_panel.add_widget(self.lbl_result)

        self.add_widget(disp_panel)
        self.add_widget(Widget(size_hint_y=0.01))

        # ── Scientific row ──
        sci = GridLayout(cols=5, spacing=5, size_hint_y=0.10)
        sci_btns = [
            ("sin", C_SPECIAL), ("cos", C_SPECIAL), ("tan", C_SPECIAL),
            ("√",   C_SPECIAL), ("x²",  C_SPECIAL),
        ]
        for label, color in sci_btns:
            b = RoundBtn(text=label, bg_color=color,
                         font_size=15, radius=10)
            b.bind(on_press=self._press)
            sci.add_widget(b)
        self.add_widget(sci)

        # ── Memory row ──
        mem = GridLayout(cols=4, spacing=5, size_hint_y=0.09)
        mem_btns = [
            ("MC", C_FUNC), ("MR", C_FUNC),
            ("M+", C_FUNC), ("M−", C_FUNC),
        ]
        for label, color in mem_btns:
            b = RoundBtn(text=label, bg_color=color,
                         font_size=15, radius=10)
            b.bind(on_press=self._press)
            mem.add_widget(b)
        self.add_widget(mem)

        # ── Main button grid ──
        main_grid = GridLayout(cols=4, spacing=6, size_hint_y=0.52)
        layout = [
            ("AC",  C_CLEAR), ("+/-", C_FUNC), ("%",  C_FUNC), ("÷",  C_OP),
            ("7",   C_NUM),   ("8",   C_NUM),  ("9",  C_NUM),  ("×",  C_OP),
            ("4",   C_NUM),   ("5",   C_NUM),  ("6",  C_NUM),  ("−",  C_OP),
            ("1",   C_NUM),   ("2",   C_NUM),  ("3",  C_NUM),  ("+",  C_OP),
            ("⌫",   C_FUNC),  ("0",   C_NUM),  (".",  C_NUM),  ("=",  C_EQUAL),
        ]
        for label, color in layout:
            b = RoundBtn(text=label, bg_color=color,
                         font_size=22, radius=14)
            b.bind(on_press=self._press)
            main_grid.add_widget(b)
        self.add_widget(main_grid)

    def _upd_disp(self, inst, _):
        self._disp_rect.pos  = inst.pos
        self._disp_rect.size = inst.size

    # ── Button logic ─────────────────────────────────────────────
    def _press(self, btn):
        label = btn.text

        # ── Clear / backspace ──
        if label == "AC":
            self.expression = ""
            self.lbl_result.text = "0"
            self.lbl_expr.text = ""
            self.just_calculated = False
            return

        if label == "⌫":
            self.expression = self.expression[:-1]
            self.lbl_result.text = self.expression or "0"
            return

        # ── Memory ──
        if label == "MC":
            self.memory = 0
            self.lbl_mem.text = ""
            return
        if label == "MR":
            self.expression += str(self.memory)
            self.lbl_result.text = self.expression
            return
        if label == "M+":
            try:
                self.memory += float(self._safe_expr())
                self.lbl_mem.text = f"M={self.memory:g}"
            except: pass
            return
        if label == "M−":
            try:
                self.memory -= float(self._safe_expr())
                self.lbl_mem.text = f"M={self.memory:g}"
            except: pass
            return

        # ── Scientific ──
        if label in ("sin", "cos", "tan", "√", "x²"):
            try:
                val = float(self._safe_expr())
                if label == "sin":
                    res = math.sin(math.radians(val))
                elif label == "cos":
                    res = math.cos(math.radians(val))
                elif label == "tan":
                    res = math.tan(math.radians(val))
                elif label == "√":
                    res = math.sqrt(val)
                elif label == "x²":
                    res = val ** 2
                res = int(res) if isinstance(res, float) and res.is_integer() else round(res, 8)
                self.lbl_expr.text = f"{label}({val}) ="
                self.lbl_result.text = str(res)
                self.expression = str(res)
                self.just_calculated = True
            except:
                self.lbl_result.text = "Error"
                self.expression = ""
            return

        # ── Percent / negate ──
        if label == "%":
            try:
                res = float(self._safe_expr()) / 100
                self.expression = str(res)
                self.lbl_result.text = self.expression
            except:
                self.lbl_result.text = "Error"
            return

        if label == "+/-":
            if self.expression.startswith("-"):
                self.expression = self.expression[1:]
            else:
                self.expression = "-" + self.expression
            self.lbl_result.text = self.expression
            return

        # ── Equals ──
        if label == "=":
            try:
                expr = (self.expression
                        .replace("÷", "/")
                        .replace("×", "*")
                        .replace("−", "-"))
                result = eval(expr)
                if isinstance(result, float) and result.is_integer():
                    result = int(result)
                self.lbl_expr.text = self.expression + " ="
                self.lbl_result.text = str(result)
                self.expression = str(result)
                self.just_calculated = True
            except:
                self.lbl_result.text = "Error"
                self.expression = ""
            return

        # ── Digits / operators ──
        if self.just_calculated and label not in "÷×−+":
            self.expression = ""
            self.lbl_expr.text = ""
        self.just_calculated = False
        self.expression += label
        self.lbl_result.text = self.expression

    def _safe_expr(self):
        return (self.expression
                .replace("÷", "/")
                .replace("×", "*")
                .replace("−", "-")) or "0"


# ── App ──────────────────────────────────────────────────────────
class CalculatorApp(App):
    def build(self):
        self.title = "SS.Calculator"
        return CalcLayout()


if __name__ == "__main__":
    CalculatorApp().run()