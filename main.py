import math
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.graphics import Color, Line, Rectangle, RoundedRectangle
from kivy.core.text import Label as CoreLabel


class CenteredTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiline = False
        self.input_filter = 'float'
        self.font_size = '16sp'
        self.bold = True
        self.size_hint_y = None
        self.height = 42
        self.background_normal = ''
        self.background_color = (0.95, 0.97, 1.0, 1)
        self.foreground_color = (0.1, 0.1, 0.3, 1)
        self.cursor_color = (0.1, 0.5, 0.9, 1)
        self.padding = [10, 10, 10, 0]
        self.bind(size=self._update_padding)

    def _update_padding(self, *args):
        try:
            line_h = getattr(self, 'line_height', 20)
            pad_y = max((self.height - line_h) / 2, 5)
            self.padding = [10, pad_y, 10, 0]
        except Exception:
            self.padding = [10, 10, 10, 0]


class AdvancedLandVisualizer(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.n = 0.0
        self.s = 0.0
        self.e = 0.0
        self.w = 0.0
        self.cut_frac = [0.0, 0.0]
        self.direction = "From North"
        self.diag_choice = "Diagonal 1 (NE to SW)"
        self.angles = {}
        self.part_diag_pts = None
        self.part_diag_len = 0.0

    def draw_land(self, n, s, e, w, cut_frac, direction, diag_choice, angles, part_diag_pts=None, part_diag_len=0.0):
        self.n, self.s, self.e, self.w = n, s, e, w
        self.cut_frac = cut_frac
        self.direction = direction
        self.diag_choice = diag_choice
        self.angles = angles
        self.part_diag_pts = part_diag_pts
        self.part_diag_len = part_diag_len
        self.update_canvas()

    def update_canvas(self, *args):
        self.canvas.clear()
        cw, ch = self.width, self.height
        if cw <= 0 or ch <= 0:
            return

        with self.canvas:
            Color(0.12, 0.16, 0.28, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[10])

            max_dim = max(self.n, self.s, self.e, self.w)
            if max_dim <= 0:
                return

            cx, cy = self.x + cw / 2, self.y + ch / 2
            scale = (min(cw, ch) * 0.85) / max_dim

            hw_n, hw_s = (self.n * scale) / 2, (self.s * scale) / 2
            hh_w, hh_e = (self.w * scale) / 2, (self.e * scale) / 2

            nw = (cx - hw_n, cy + hh_w)
            ne = (cx + hw_n, cy + hh_e)
            se = (cx + hw_s, cy - hh_e)
            sw = (cx - hw_s, cy - hh_w)

            Color(0.2, 0.8, 1, 1)
            Line(points=[nw[0], nw[1], ne[0], ne[1], se[0], se[1], sw[0], sw[1], nw[0], nw[1]], width=2.5)

            Color(1, 0.84, 0, 0.8)
            if "NE" in self.diag_choice:
                Line(points=[ne[0], ne[1], sw[0], sw[1]], width=2, dash_length=6, dash_offset=2)
            else:
                Line(points=[nw[0], nw[1], se[0], se[1]], width=2, dash_length=6, dash_offset=2)

            self._render_angle_labels(nw, ne, se, sw)

            Color(1, 0.3, 0.3, 1)
            p1, p2 = (0, 0), (0, 0)

            if self.direction == "From North":
                p1 = (nw[0] + (sw[0] - nw[0]) * self.cut_frac[0], nw[1] + (sw[1] - nw[1]) * self.cut_frac[0])
                p2 = (ne[0] + (se[0] - ne[0]) * self.cut_frac[1], ne[1] + (se[1] - ne[1]) * self.cut_frac[1])
            elif self.direction == "From South":
                p1 = (sw[0] + (nw[0] - sw[0]) * self.cut_frac[0], sw[1] + (nw[1] - sw[1]) * self.cut_frac[0])
                p2 = (se[0] + (ne[0] - se[0]) * self.cut_frac[1], se[1] + (ne[1] - se[1]) * self.cut_frac[1])
            elif self.direction == "From East":
                p1 = (ne[0] + (nw[0] - ne[0]) * self.cut_frac[0], ne[1] + (nw[1] - ne[1]) * self.cut_frac[0])
                p2 = (se[0] + (sw[0] - se[0]) * self.cut_frac[1], se[1] + (sw[1] - se[1]) * self.cut_frac[1])
            elif self.direction == "From West":
                p1 = (nw[0] + (ne[0] - nw[0]) * self.cut_frac[0], nw[1] + (ne[1] - nw[1]) * self.cut_frac[0])
                p2 = (sw[0] + (se[0] - sw[0]) * self.cut_frac[1], sw[1] + (se[1] - sw[1]) * self.cut_frac[1])

            Line(points=[p1[0], p1[1], p2[0], p2[1]], width=3)

            if self.part_diag_pts and self.part_diag_len > 0:
                dp1, dp2 = self.part_diag_pts
                
                Color(1, 0.55, 0, 0.9)
                Line(points=[dp1[0], dp1[1], dp2[0], dp2[1]], width=2, dash_length=4, dash_offset=2)

                mid_x = (dp1[0] + dp2[0]) / 2
                mid_y = (dp1[1] + dp2[1]) / 2

                label_text = f"Part Diag: {self.part_diag_len:.2f} ft"
                core_label = CoreLabel(text=label_text, font_size=12, bold=True)
                core_label.refresh()
                texture = core_label.texture

                if texture:
                    Color(0, 0, 0, 0.8)
                    Rectangle(pos=(mid_x - texture.width / 2 - 4, mid_y - texture.height / 2 - 2),
                              size=(texture.width + 8, texture.height + 4))
                    Color(1, 0.8, 0.2, 1)
                    Rectangle(texture=texture, pos=(mid_x - texture.width / 2, mid_y - texture.height / 2), size=texture.size)

    def _render_angle_labels(self, nw, ne, se, sw):
        if not self.angles:
            return
        
        pts = {"NW": nw, "NE": ne, "SE": se, "SW": sw}
        for corner, pos in pts.items():
            ang_val = self.angles.get(corner, 0.0)
            txt = f"{corner}: {ang_val:.1f}°"
            core_lbl = CoreLabel(text=txt, font_size=11, bold=True)
            core_lbl.refresh()
            tex = core_lbl.texture
            if not tex:
                continue
            
            offset_x = -35 if "W" in corner else 5
            offset_y = 10 if "N" in corner else -20
            
            Color(0.1, 0.1, 0.1, 0.8)
            Rectangle(pos=(pos[0] + offset_x - 2, pos[1] + offset_y - 2), size=(tex.width + 4, tex.height + 4))
            Color(0.2, 1.0, 0.2, 1)
            Rectangle(texture=tex, pos=(pos[0] + offset_x, pos[1] + offset_y), size=tex.size)


class AdvancedLandCalculatorApp(App):
    def build(self):
        self.updating_internally = False
        self.has_calculated = False
        self.title = "Precision Land Calculator & Automatic Partition System"
        main_layout = BoxLayout(orientation='vertical', padding=12, spacing=10)

        with main_layout.canvas.before:
            Color(0.08, 0.1, 0.18, 1)
            self.bg_rect = Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self._update_bg, size=self._update_bg)

        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        content = BoxLayout(orientation='vertical', spacing=12, size_hint_y=None, padding=[0, 0, 0, 30])
        content.bind(minimum_height=content.setter('height'))

        content.add_widget(Label(text="[color=00e5ff][b]Advanced Precision Land Calculator[/b][/color]", markup=True, font_size="20sp", size_hint_y=None, height=40))

        grid = GridLayout(cols=2, spacing=10, row_default_height=42, size_hint_y=None, height=310)

        grid.add_widget(Label(text="North Side (ft):", font_size="15sp", bold=True, color=(0.9, 0.9, 0.9, 1)))
        self.north_in = CenteredTextInput(text="60")
        grid.add_widget(self.north_in)

        grid.add_widget(Label(text="South Side (ft):", font_size="15sp", bold=True, color=(0.9, 0.9, 0.9, 1)))
        self.south_in = CenteredTextInput(text="70")
        grid.add_widget(self.south_in)

        grid.add_widget(Label(text="East Side (ft):", font_size="15sp", bold=True, color=(0.9, 0.9, 0.9, 1)))
        self.east_in = CenteredTextInput(text="40")
        grid.add_widget(self.east_in)

        grid.add_widget(Label(text="West Side (ft):", font_size="15sp", bold=True, color=(0.9, 0.9, 0.9, 1)))
        self.west_in = CenteredTextInput(text="50")
        grid.add_widget(self.west_in)

        grid.add_widget(Label(text="Diagonal (Karna) (ft):", font_size="15sp", bold=True, color=(0.9, 0.9, 0.9, 1)))
        self.diag_in = CenteredTextInput(text="65")
        grid.add_widget(self.diag_in)

        grid.add_widget(Label(text="Select Diagonal:", font_size="15sp", bold=True, color=(0.9, 0.9, 0.9, 1)))
        
        self.diag_spinner = Spinner(
            text="Diagonal 1 (NE to SW)", 
            values=("Diagonal 1 (NE to SW)", "Diagonal 2 (NW to SE)"), 
            font_size="14sp", 
            size_hint_y=None, 
            height=42,
            background_normal='',
            background_color=(0.4, 0.2, 0.8, 1),
            color=(1, 1, 1, 1)
        )
        self.diag_spinner.bind(text=self.on_dropdown_change)
        grid.add_widget(self.diag_spinner)

        content.add_widget(grid)

        part_grid = GridLayout(cols=2, spacing=10, row_default_height=42, size_hint_y=None, height=150)
        
        part_grid.add_widget(Label(text="Target Land (Shotok):", font_size="15sp", bold=True, color=(0.9, 0.9, 0.9, 1)))
        self.target_shotok_in = CenteredTextInput(text="5")
        part_grid.add_widget(self.target_shotok_in)

        part_grid.add_widget(Label(text="Cut Direction:", font_size="15sp", bold=True, color=(0.9, 0.9, 0.9, 1)))
        self.direction_spinner = Spinner(
            text="From North", 
            values=("From North", "From South", "From East", "From West"), 
            font_size="15sp", 
            size_hint_y=None, 
            height=42,
            background_normal='',
            background_color=(0.1, 0.6, 0.7, 1),
            color=(1, 1, 1, 1)
        )
        self.direction_spinner.bind(text=self.on_dropdown_change)
        part_grid.add_widget(self.direction_spinner)

        part_grid.add_widget(Label(text="Target Part Diagonal:", font_size="15sp", bold=True, color=(0.9, 0.9, 0.9, 1)))
        self.part_diag_spinner = Spinner(
            text="Diagonal A", 
            values=("Diagonal A", "Diagonal B"), 
            font_size="14sp", 
            size_hint_y=None, 
            height=42,
            background_normal='',
            background_color=(0.8, 0.4, 0.1, 1),
            color=(1, 1, 1, 1)
        )
        self.part_diag_spinner.bind(text=self.on_dropdown_change)
        part_grid.add_widget(self.part_diag_spinner)

        content.add_widget(part_grid)

        btn_box = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)

        calc_btn = Button(
            text="Calculate & Partition", 
            font_size="16sp", 
            bold=True, 
            size_hint_x=0.7,
            background_normal='',
            background_color=(0.1, 0.7, 0.4, 1),
            color=(1, 1, 1, 1)
        )
        calc_btn.bind(on_press=self.on_calc_click)
        btn_box.add_widget(calc_btn)

        reset_btn = Button(
            text="Reset", 
            font_size="16sp", 
            bold=True, 
            size_hint_x=0.3,
            background_normal='',
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        reset_btn.bind(on_press=self.reset_inputs)
        btn_box.add_widget(reset_btn)

        content.add_widget(btn_box)

        content.add_widget(Label(text="[color=ffb703][b]Adjust Cut Segment Lengths:[/b][/color]", markup=True, font_size="16sp", size_hint_y=None, height=25))
        
        adjust_grid = GridLayout(cols=2, spacing=10, row_default_height=42, size_hint_y=None, height=95)
        
        self.cut1_label = Label(text="Cut Side 1 (ft):", font_size="15sp", bold=True, color=(0.9, 0.9, 0.9, 1))
        adjust_grid.add_widget(self.cut1_label)
        self.cut1_in = CenteredTextInput(text="")
        self.cut1_in.bind(text=self.on_cut1_change)
        adjust_grid.add_widget(self.cut1_in)

        self.cut2_label = Label(text="Cut Side 2 (ft):", font_size="15sp", bold=True, color=(0.9, 0.9, 0.9, 1))
        adjust_grid.add_widget(self.cut2_label)
        self.cut2_in = CenteredTextInput(text="")
        self.cut2_in.bind(text=self.on_cut2_change)
        adjust_grid.add_widget(self.cut2_in)

        content.add_widget(adjust_grid)

        diagram_box = BoxLayout(orientation='vertical', size_hint_y=None, height=380)
        self.visualizer = AdvancedLandVisualizer(size_hint=(1, 1))
        diagram_box.add_widget(self.visualizer)
        content.add_widget(diagram_box)

        self.result_label = Label(text="Enter values and click Calculate...", markup=True, font_size="15sp", size_hint_y=None, halign="left", valign="top")
        self.result_label.bind(size=self._update_text_size, texture_size=self._update_label_height)
        content.add_widget(self.result_label)

        formula_btn = Button(
            text="Formulas & Working Principles", 
            font_size="15sp", 
            bold=True, 
            size_hint_y=None, 
            height=45, 
            background_normal='',
            background_color=(0.85, 0.45, 0.1, 1),
            color=(1, 1, 1, 1)
        )
        formula_btn.bind(on_press=self.show_formula_popup)
        content.add_widget(formula_btn)

        developer_info = (
            "[color=00e5ff][b]Developed by[/b][/color]\n"
            "[color=ffffff]Md: Zual Badsha[/color]\n"
            "[color=aaaaaa]Word no: 07, union no: 09, post office: Radhanagor\n"
            "Thana: Badargonj, zilla+division: Rangpur[/color]"
        )
        self.dev_label = Label(
            text=developer_info,
            markup=True,
            font_size="13sp",
            halign="center",
            valign="middle",
            size_hint_y=None
        )
        self.dev_label.bind(size=self._update_dev_text_size, texture_size=self._update_dev_label_height)
        content.add_widget(self.dev_label)

        scroll.add_widget(content)
        main_layout.add_widget(scroll)

        return main_layout

    def on_calc_click(self, instance):
        self.has_calculated = True
        self.calculate()

    def on_dropdown_change(self, spinner, text):
        if self.has_calculated:
            self.calculate()

    def reset_inputs(self, instance=None):
        self.updating_internally = True
        self.has_calculated = False
        
        self.north_in.text = ""
        self.south_in.text = ""
        self.east_in.text = ""
        self.west_in.text = ""
        self.diag_in.text = ""
        self.target_shotok_in.text = ""
        self.diag_spinner.text = "Diagonal 1 (NE to SW)"
        self.direction_spinner.text = "From North"
        self.part_diag_spinner.text = "Diagonal A"
        self.cut1_in.text = ""
        self.cut2_in.text = ""

        self.result_label.text = "Enter values and click Calculate..."
        self.visualizer.draw_land(0, 0, 0, 0, [0, 0], "From North", "Diagonal 1 (NE to SW)", {})
        self.updating_internally = False

    def show_formula_popup(self, instance):
        info_text = (
            "[color=00e5ff][b]1. Heron's Formula (Area Calculation):[/b][/color]\n"
            "Used to compute the exact area of irregular quadrilaterals by splitting them into two triangles using a diagonal:\n"
            "• [color=ffb703]Semi-perimeter (s) = (a + b + c) / 2[/color]\n"
            "• [color=ffb703]Area = sqrt(s * (s - a) * (s - b) * (s - c))[/color]\n\n"

            "[color=00e5ff][b]2. Law of Cosines (Corner Angle Calculation):[/b][/color]\n"
            "Calculates precise corner angles of the land to construct accurate 2D coordinates:\n"
            "• [color=ffb703]cos(C) = (a^2 + b^2 - c^2) / (2 * a * b)[/color]\n"
            "• [color=ffb703]Angle C = acos(cos(C))[/color]\n\n"

            "[color=00e5ff][b]3. Binary Search Algorithm (Exact Partitioning):[/b][/color]\n"
            "Computes the exact cut length required for target area division across non-parallel boundaries:\n"
            "• Performs 40 iterations of binary search.\n"
            "• Guarantees precision up to [color=00ff66]0.0001 ft[/color].\n\n"

            "[color=00e5ff][b]4. Coordinate Geometry & Euclidean Distance:[/b][/color]\n"
            "Determines the exact lengths of the newly generated partition line and sub-diagonal:\n"
            "• [color=ffb703]Distance (d) = sqrt((x2 - x1)^2 + (y2 - y1)^2)[/color]\n\n"

            "[color=00e5ff][b]Precision & Accuracy Standard:[/b][/color]\n"
            "Unlike traditional average methods (which cause significant error), this application uses true [color=00ff66]Triangulation Architecture[/color] to ensure 100% mathematical accuracy."
        )

        popup_layout = BoxLayout(orientation='vertical', padding=12, spacing=10)
        popup_scroll = ScrollView(size_hint=(1, 1))
        popup_label = Label(text=info_text, markup=True, font_size="14sp", size_hint_y=None, halign="left", valign="top")
        popup_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
        popup_label.bind(texture_size=lambda inst, val: setattr(inst, 'height', val[1] + 10))
        
        popup_scroll.add_widget(popup_label)
        popup_layout.add_widget(popup_scroll)

        close_btn = Button(text="Close", size_hint_y=None, height=42, background_normal='', background_color=(0.8, 0.2, 0.2, 1), bold=True, font_size="15sp")
        popup_layout.add_widget(close_btn)

        popup = Popup(title="Formulas & Calculation Principles", content=popup_layout, size_hint=(0.92, 0.82))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def _update_text_size(self, instance, value):
        instance.text_size = (value[0], None)

    def _update_label_height(self, instance, value):
        instance.height = value[1] + 20

    def _update_dev_text_size(self, instance, value):
        instance.text_size = (value[0], None)

    def _update_dev_label_height(self, instance, value):
        instance.height = value[1] + 10

    def heron_area(self, a, b, c):
        s = (a + b + c) / 2
        if s <= a or s <= b or s <= c:
            return 0.0
        try:
            return math.sqrt(s * (s - a) * (s - b) * (s - c))
        except ValueError:
            return 0.0

    def triangle_angle(self, a, b, c):
        if a <= 0 or b <= 0:
            return 0.0
        try:
            cos_val = (a**2 + b**2 - c**2) / (2 * a * b)
            cos_val = max(-1.0, min(1.0, cos_val))
            return math.degrees(math.acos(cos_val))
        except ValueError:
            return 0.0

    def quad_area(self, p1, p2, p3, p4):
        return 0.5 * abs(p1[0]*(p2[1]-p4[1]) + p2[0]*(p3[1]-p1[1]) + p3[0]*(p4[1]-p2[1]) + p4[0]*(p1[1]-p3[1]))

    def get_quad_points_and_angles(self, n, s, e, w, d, diag_choice):
        angles = {}
        if "NE" in diag_choice:
            ang_NE1 = self.triangle_angle(n, e, d)
            ang_NW = self.triangle_angle(n, w, d)
            ang_SE = self.triangle_angle(s, e, d)
            ang_SW1 = self.triangle_angle(s, w, d)

            rad_NE = math.radians(ang_NE1)
            rad_NW = math.radians(ang_NW)

            nw = (0.0, 0.0)
            ne = (n, 0.0)
            se = (n - e * math.cos(rad_NE), -e * math.sin(rad_NE))
            sw = (-w * math.cos(rad_NW), -w * math.sin(rad_NW))

            angles['NW'] = ang_NW
            angles['NE'] = ang_NE1
            angles['SE'] = ang_SE
            angles['SW'] = ang_SW1
        else:
            ang_NW1 = self.triangle_angle(n, w, d)
            ang_NE = self.triangle_angle(n, e, d)
            ang_SE1 = self.triangle_angle(s, e, d)
            ang_SW = self.triangle_angle(s, w, d)

            rad_NW = math.radians(ang_NW1)

            nw = (0.0, 0.0)
            ne = (n, 0.0)
            sw = (-w * math.cos(rad_NW), -w * math.sin(rad_NW))
            se = (sw[0] + s, sw[1])

            angles['NW'] = ang_NW1
            angles['NE'] = ang_NE
            angles['SE'] = ang_SE1
            angles['SW'] = ang_SW

        return nw, ne, se, sw, angles

    def compute_exact_c2(self, c1, target_sqft):
        try:
            n = float(self.north_in.text or 0)
            s = float(self.south_in.text or 0)
            e = float(self.east_in.text or 0)
            w = float(self.west_in.text or 0)
            d = float(self.diag_in.text or 0)
            direction = self.direction_spinner.text
            diag_choice = self.diag_spinner.text
        except ValueError:
            return 0.0

        nw, ne, se, sw, _ = self.get_quad_points_and_angles(n, s, e, w, d, diag_choice)
        low, high = 0.0, (e if direction in ["From North", "From South"] else s)
        best_c2 = 0.0

        for _ in range(40):
            mid = (low + high) / 2
            f1 = (c1 / w) if (direction in ["From North", "From South"] and w > 0) else ((c1 / n) if n > 0 else 0)
            f2 = (mid / e) if (direction in ["From North", "From South"] and e > 0) else ((mid / s) if s > 0 else 0)

            f1 = min(max(f1, 0.0), 1.0)
            f2 = min(max(f2, 0.0), 1.0)

            if direction == "From North":
                p1 = (nw[0] + (sw[0]-nw[0])*f1, nw[1] + (sw[1]-nw[1])*f1)
                p2 = (ne[0] + (se[0]-ne[0])*f2, ne[1] + (se[1]-ne[1])*f2)
                curr_area = self.quad_area(nw, ne, p2, p1)
            elif direction == "From South":
                p1 = (sw[0] + (nw[0]-sw[0])*f1, sw[1] + (nw[1]-sw[1])*f1)
                p2 = (se[0] + (ne[0]-se[0])*f2, se[1] + (ne[1]-se[1])*f2)
                curr_area = self.quad_area(sw, se, p2, p1)
            elif direction == "From East":
                p1 = (ne[0] + (nw[0]-ne[0])*f1, ne[1] + (nw[1]-ne[1])*f1)
                p2 = (se[0] + (sw[0]-se[0])*f2, se[1] + (sw[1]-se[1])*f2)
                curr_area = self.quad_area(ne, se, p2, p1)
            elif direction == "From West":
                p1 = (nw[0] + (ne[0]-nw[0])*f1, nw[1] + (ne[1]-nw[1])*f1)
                p2 = (sw[0] + (se[0]-sw[0])*f2, sw[1] + (se[1]-sw[1])*f2)
                curr_area = self.quad_area(nw, sw, p2, p1)

            if curr_area < target_sqft:
                low = mid
            else:
                high = mid
            best_c2 = mid

        return best_c2

    def calculate(self, *args):
        if self.updating_internally:
            return

        try:
            n = float(self.north_in.text)
            s = float(self.south_in.text)
            e = float(self.east_in.text)
            w = float(self.west_in.text)
            d = float(self.diag_in.text)
            target_shotok = float(self.target_shotok_in.text)
            direction = self.direction_spinner.text
            diag_choice = self.diag_spinner.text

            if "NE" in diag_choice:
                min_d = max(abs(n - e), abs(s - w))
                max_d = min(n + e, s + w)
            else:
                min_d = max(abs(n - w), abs(s - e))
                max_d = min(n + w, s + e)

            if d <= min_d or d >= max_d:
                err_msg = f"[color=ff4d4d][b]Error: Invalid side lengths or diagonal![/b]\n"
                err_msg += f"Selected Diagonal Range:\n"
                err_msg += f"• Min: [color=00ff66]{min_d + 0.01:.2f} ft[/color]\n"
                err_msg += f"• Max: [color=00ff66]{max_d - 0.01:.2f} ft[/color][/color]"
                self.result_label.text = err_msg
                return

            if "NE" in diag_choice:
                area1 = self.heron_area(n, e, d)
                area2 = self.heron_area(s, w, d)
            else:
                area1 = self.heron_area(n, w, d)
                area2 = self.heron_area(s, e, d)

            total_sqft = area1 + area2

            if total_sqft == 0:
                self.result_label.text = "[color=ff4d4d]Error: Invalid side lengths or diagonal![/color]"
                return

            target_sqft = target_shotok * 435.6
            if target_sqft > total_sqft:
                self.result_label.text = "[color=ff4d4d]Error: Target land is larger than total land![/color]"
                return

            area_ratio = target_sqft / total_sqft
            scale_factor = math.sqrt(area_ratio)

            if direction in ["From North", "From South"]:
                self.cut1_label.text = "Cut West Side (ft):"
                self.cut2_label.text = "Cut East Side (ft):"
                c1_init = w * scale_factor
            else:
                self.cut1_label.text = "Cut North Side (ft):"
                self.cut2_label.text = "Cut South Side (ft):"
                c1_init = n * scale_factor

            c2_exact = self.compute_exact_c2(c1_init, target_sqft)

            self.updating_internally = True
            self.cut1_in.text = f"{c1_init:.2f}"
            self.cut2_in.text = f"{c2_exact:.2f}"
            self.updating_internally = False

            self.update_results(c1_init, c2_exact)

        except ValueError:
            pass

    def on_cut1_change(self, instance, value):
        if self.updating_internally or not value or not self.has_calculated:
            return
        try:
            c1 = float(value)
            target_sqft = float(self.target_shotok_in.text or 0) * 435.6
            c2 = self.compute_exact_c2(c1, target_sqft)

            self.updating_internally = True
            self.cut2_in.text = f"{c2:.2f}"
            self.updating_internally = False

            self.update_results(c1, c2)
        except ValueError:
            pass

    def on_cut2_change(self, instance, value):
        if self.updating_internally or not value or not self.has_calculated:
            return
        try:
            c2 = float(value)
            target_sqft = float(self.target_shotok_in.text or 0) * 435.6
            c1 = self.compute_exact_c2(c2, target_sqft)

            self.updating_internally = True
            self.cut1_in.text = f"{c1:.2f}"
            self.updating_internally = False

            self.update_results(c1, c2)
        except ValueError:
            pass

    def update_results(self, c1, c2):
        try:
            n = float(self.north_in.text)
            s = float(self.south_in.text)
            e = float(self.east_in.text)
            w = float(self.west_in.text)
            d = float(self.diag_in.text)
            direction = self.direction_spinner.text
            diag_choice = self.diag_spinner.text
            part_diag_choice = self.part_diag_spinner.text

            if "NE" in diag_choice:
                area1 = self.heron_area(n, e, d)
                area2 = self.heron_area(s, w, d)
            else:
                area1 = self.heron_area(n, w, d)
                area2 = self.heron_area(s, e, d)

            total_sqft = area1 + area2
            total_shotok = total_sqft / 435.6

            nw, ne, se, sw, angles = self.get_quad_points_and_angles(n, s, e, w, d, diag_choice)

            if direction in ["From North", "From South"]:
                f1 = min(c1 / w, 1.0) if w > 0 else 0
                f2 = min(c2 / e, 1.0) if e > 0 else 0
            else:
                f1 = min(c1 / n, 1.0) if n > 0 else 0
                f2 = min(c2 / s, 1.0) if s > 0 else 0

            cut_frac = [f1, f2]
            base_len = 0
            part_diag_pts = None
            diag_dir_name = ""

            if direction == "From North":
                p1 = (nw[0] + (sw[0]-nw[0])*f1, nw[1] + (sw[1]-nw[1])*f1)
                p2 = (ne[0] + (se[0]-ne[0])*f2, ne[1] + (se[1]-ne[1])*f2)
                sep_sqft = self.quad_area(nw, ne, p2, p1)
                base_len = n
                if part_diag_choice == "Diagonal A":
                    part_diag_pts = (nw, p2)
                    diag_dir_name = "North-West Corner to East Cut-Point"
                else:
                    part_diag_pts = (ne, p1)
                    diag_dir_name = "North-East Corner to West Cut-Point"

            elif direction == "From South":
                p1 = (sw[0] + (nw[0]-sw[0])*f1, sw[1] + (nw[1]-sw[1])*f1)
                p2 = (se[0] + (ne[0]-se[0])*f2, se[1] + (ne[1]-se[1])*f2)
                sep_sqft = self.quad_area(sw, se, p2, p1)
                base_len = s
                if part_diag_choice == "Diagonal A":
                    part_diag_pts = (sw, p2)
                    diag_dir_name = "South-West Corner to East Cut-Point"
                else:
                    part_diag_pts = (se, p1)
                    diag_dir_name = "South-East Corner to West Cut-Point"

            elif direction == "From East":
                p1 = (ne[0] + (nw[0]-ne[0])*f1, ne[1] + (nw[1]-ne[1])*f1)
                p2 = (se[0] + (sw[0]-se[0])*f2, se[1] + (sw[1]-se[1])*f2)
                sep_sqft = self.quad_area(ne, se, p2, p1)
                base_len = e
                if part_diag_choice == "Diagonal A":
                    part_diag_pts = (ne, p2)
                    diag_dir_name = "North-East Corner to South Cut-Point"
                else:
                    part_diag_pts = (se, p1)
                    diag_dir_name = "South-East Corner to North Cut-Point"

            elif direction == "From West":
                p1 = (nw[0] + (ne[0]-nw[0])*f1, nw[1] + (ne[1]-nw[1])*f1)
                p2 = (sw[0] + (se[0]-sw[0])*f2, sw[1] + (se[1]-sw[1])*f2)
                sep_sqft = self.quad_area(nw, sw, p2, p1)
                base_len = w
                if part_diag_choice == "Diagonal A":
                    part_diag_pts = (nw, p2)
                    diag_dir_name = "North-West Corner to South Cut-Point"
                else:
                    part_diag_pts = (sw, p1)
                    diag_dir_name = "South-West Corner to North Cut-Point"

            new_line = math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
            part_diag_len = math.sqrt((part_diag_pts[0][0] - part_diag_pts[1][0])**2 + (part_diag_pts[0][1] - part_diag_pts[1][1])**2)

            sep_shotok = sep_sqft / 435.6
            rem_sqft = max(total_sqft - sep_sqft, 0)
            rem_shotok = rem_sqft / 435.6

            res = f"[color=00e5ff][b]=== Precision Land Report ===[/b][/color]\n"
            res += f"Total Area: {total_sqft:.2f} Sq.Ft ([color=00ffff]{total_shotok:.3f} Shotok[/color])\n"
            res += f"Calculated Angles: NW: {angles.get('NW',0):.1f}°, NE: {angles.get('NE',0):.1f}°, SE: {angles.get('SE',0):.1f}°, SE: {angles.get('SE',0):.1f}°, SW: {angles.get('SW',0):.1f}°\n"
            res += f"Separated Target Area: [color=00ff66]{sep_shotok:.3f} Shotok ({sep_sqft:.2f} Sq.Ft)[/color]\n\n"
            res += f"[color=ffb703][b]Partition Boundary Measures ({direction}):[/b][/color]\n"
            res += f"• Main Base Line: {base_len:.2f} ft\n"
            res += f"• Adjusted Cut Side 1: {c1:.2f} ft\n"
            res += f"• Adjusted Cut Side 2: {c2:.2f} ft\n"
            res += f"• Exact Divider Line: [color=ff5555]{new_line:.2f} ft[/color]\n"
            res += f"• Sub-Partition Diagonal ([color=ffaa00]{part_diag_choice}[/color]): [color=ffaa00]{part_diag_len:.2f} ft[/color]\n"
            res += f"  ({diag_dir_name})\n\n"
            res += f"[color=00e5ff][b]Remaining Main Land:[/b][/color] {rem_shotok:.3f} Shotok ({rem_sqft:.2f} Sq.Ft)"

            self.visualizer.draw_land(n, s, e, w, cut_frac, direction, diag_choice, angles, part_diag_pts=part_diag_pts, part_diag_len=part_diag_len)
            self.result_label.text = res

        except Exception:
            pass


if __name__ == "__main__":
    AdvancedLandCalculatorApp().run()
