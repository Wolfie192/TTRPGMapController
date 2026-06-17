import json
from PyQt6.QtWidgets import (
QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
QLabel, QFileDialog,  QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
QSlider, QLineEdit, QApplication
)
from PyQt6.QtGui import QPixmap, QMouseEvent, QTransform, QIntValidator, QPainter
from PyQt6.QtCore import Qt, QPointF, pyqtSignal
from PyQt6.QtSvgWidgets import QGraphicsSvgItem

class ControlScreen(QMainWindow):
    map_loaded = pyqtSignal(str, float)
    view_state_changed = pyqtSignal(QPointF, float, float)
    closing = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control Screen")
        self.setGeometry(100, 100, 1000, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(-100000, -100000, 200000, 200000)
        self.view =  QGraphicsView(self.scene)
        self.view.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.view.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.view.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        main_layout.addWidget(self.view)

        self.map_item = None
        self.original_pixmap = None
        self.current_map_path = None

        self.zoom_factor = 1.0
        self.current_rotation = 0

        self.map_history = self._load_history()

        self._pan = False
        self._pan_start_point = QPointF()

        controls_layout = QHBoxLayout()
        main_layout.addLayout(controls_layout)

        self.load_map_button = QPushButton("Load Map")
        self.load_map_button.clicked.connect(self._load_map)
        controls_layout.addWidget(self.load_map_button)

        self.recenter_map_button = QPushButton("Re-Center Maps")
        self.recenter_map_button.clicked.connect(self._recenter_map)
        self.recenter_map_button.setEnabled(False)
        controls_layout.addWidget(self.recenter_map_button)

        self.rotate_map_button = QPushButton("Rotate 90°")
        self.rotate_map_button.clicked.connect(self._rotate_map)
        self.rotate_map_button.setEnabled(False)
        controls_layout.addWidget(self.rotate_map_button)

        scale_label = QLabel("Map Scale:")
        controls_layout.addWidget(scale_label)

        self.minus_button = QPushButton("-")
        self.minus_button.setFixedWidth(30)
        self.minus_button.setObjectName("scaleMinusButton")
        self.minus_button.clicked.connect(self._decrease_player_scale)
        controls_layout.addWidget(self.minus_button)

        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setRange(10, 5000)
        self.scale_slider.setValue(100)
        self.scale_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.scale_slider.valueChanged.connect(self._on_player_scale_slider_changed)
        controls_layout.addWidget(self.scale_slider)

        self.plus_button = QPushButton("+")
        self.plus_button.setFixedWidth(30)
        self.plus_button.setObjectName("scalePlusButton")
        self.plus_button.clicked.connect(self._increase_player_scale)
        controls_layout.addWidget(self.plus_button)

        self.scale_input = QLineEdit("100")
        self.scale_input.setFixedWidth(60)
        self.scale_input.setValidator(QIntValidator(10, 5000))
        self.scale_input.editingFinished.connect(self._on_player_scale_input_finished)
        controls_layout.addWidget(self.scale_input)
        controls_layout.addWidget(QLabel("%"))

        self.view.mousePressEvent = self._view_mouse_press_event
        self.view.mouseMoveEvent = self._view_mouse_move_event
        self.view.mouseReleaseEvent = self._view_mouse_release_event
        self.view.wheelEvent = self._view_wheel_event

    def _load_history(self):
        try:
            with open("map_settings.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_history(self):
        with open("map_settings.json", "w") as f:
            json.dump(self.map_history, f, indent=4)

    def _save_current_map_state(self):
        if self.current_map_path and self.map_item:
            self.map_history[self.current_map_path] = {
                "pos": [self.map_item.pos().x(), self.map_item.pos().y()],
                "zoom_factor": self.zoom_factor,
                "rotation": self.current_rotation
            }

    def _load_map(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.svg)")
        if file_dialog.exec():
            self._save_current_map_state()
            file_path = file_dialog.selectedFiles()[0]
            self.current_map_path = file_path
            
            state = self.map_history.get(self.current_map_path)
            if state:
                self.current_rotation = state.get("rotation", 0)
            else:
                self.current_rotation = 0
                
            self._display_map(file_path, state)
            self.recenter_map_button.setEnabled(True)
            self.rotate_map_button.setEnabled(True)

    def _get_base_scale(self):
        if not self.map_item:
            return 1.0
        rect = self.map_item.boundingRect()
        if rect.width() <= 0 or rect.height() <= 0:
            return 1.0
        return min(self.view.viewport().width() / rect.width(), self.view.viewport().height() / rect.height())

    def _display_map(self, file_path: str, state=None):
        self.scene.clear()
        
        is_svg = file_path.lower().endswith('.svg')
        if is_svg:
            self.map_item = QGraphicsSvgItem(file_path)
            self.original_pixmap = None
        else:
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                print("Failed to load image.")
                self.map_item = None
                self.original_pixmap = None
                return
            self.map_item = QGraphicsPixmapItem(pixmap)
            self.original_pixmap = pixmap

        self.scene.addItem(self.map_item)

        # Set transform origin to center for rotation
        self.map_item.setTransformOriginPoint(self.map_item.boundingRect().center())
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)

        if state:
            self.map_item.setPos(QPointF(state["pos"][0], state["pos"][1]))
            self.zoom_factor = state.get("zoom_factor", 1.0)
            self.current_rotation = state.get("rotation", 0)
            
            # Update UI
            val = int(self.zoom_factor * 100)
            self.scale_slider.blockSignals(True)
            self.scale_slider.setValue(val)
            self.scale_slider.blockSignals(False)
            self.scale_input.setText(str(val))
        else:
            # Center the map item on the scene origin
            self.map_item.setPos(-self.map_item.boundingRect().center())
            self.zoom_factor = 1.0

        self._apply_view_transform()

        if not state:
            self.scale_slider.setValue(int(self.zoom_factor * 100))

        self.map_item.setRotation(self.current_rotation)
        
        self.map_loaded.emit(file_path, self.current_rotation)
        self._emit_map_view_state()

    def _rotate_map(self):
        if self.map_item is None:
            return

        self.current_rotation = (self.current_rotation + 90) % 360
        self.map_item.setRotation(self.current_rotation)
        self._emit_map_view_state()

    def _recenter_map(self):
        if self.map_item is None:
            return

        # Move the center of the map image to the center of the screen (origin)
        self.map_item.setPos(-self.map_item.boundingRect().center())
        self.view.centerOn(0, 0)
        self._emit_map_view_state()

    def _view_mouse_press_event(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.map_item:
            self._pan = True
            self._pan_start_point = self.view.mapToScene(event.position().toPoint())
            self.view.setCursor(Qt.CursorShape.ClosedHandCursor)
        super(QGraphicsView, self.view).mousePressEvent(event)

    def _view_mouse_move_event(self, event: QMouseEvent):
        if self._pan and self.map_item:
            current_mouse_pos_scene = self.view.mapToScene(event.position().toPoint())
            delta_scene = current_mouse_pos_scene - self._pan_start_point

            self.map_item.setPos(self.map_item.pos() + delta_scene)

            self._pan_start_point = current_mouse_pos_scene
            self._emit_map_view_state()
        super(QGraphicsView, self.view).mouseMoveEvent(event)

    def _view_mouse_release_event(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._pan = False
            self.view.setCursor(Qt.CursorShape.ArrowCursor)
            self._emit_map_view_state()
        super(QGraphicsView, self.view).mouseReleaseEvent(event)

    def _view_wheel_event(self, event):
        zoom_factor = 1.15
        current_value = self.scale_slider.value()
        if event.angleDelta().y() > 0:
            new_value = int(current_value * zoom_factor)
        else:
            new_value = int(current_value / zoom_factor)
        
        # Clamp value and set slider, which triggers synchronization
        self.scale_slider.setValue(max(self.scale_slider.minimum(), min(self.scale_slider.maximum(), new_value)))

    def _apply_view_transform(self):
        if not self.map_item:
            return
        base = self._get_base_scale()
        total_scale = base * self.zoom_factor
        self.view.setTransform(QTransform().scale(total_scale, total_scale))
        self.view.centerOn(0, 0)

    def _on_player_scale_slider_changed(self, value):
        self.zoom_factor = value / 100.0
        self.scale_input.setText(str(value))
        self._apply_view_transform()
        self._emit_map_view_state()

    def _on_player_scale_input_finished(self):
        try:
            value = int(self.scale_input.text())
            if 10 <= value <= 5000:
                self.scale_slider.setValue(value)
            else:
                self.scale_input.setText(str(self.scale_slider.value()))
        except ValueError:
            self.scale_input.setText(str(self.scale_slider.value()))

    def _increase_player_scale(self):
        step = 10 if QApplication.keyboardModifiers() & Qt.KeyboardModifier.ShiftModifier else 1
        current_value = self.scale_slider.value()
        new_value = min(self.scale_slider.maximum(), current_value + step)
        self.scale_slider.setValue(new_value)

    def _decrease_player_scale(self):
        step = 10 if QApplication.keyboardModifiers() & Qt.KeyboardModifier.ShiftModifier else 1
        current_value = self.scale_slider.value()
        new_value = max(self.scale_slider.minimum(), current_value - step)
        self.scale_slider.setValue(new_value)

    def _emit_map_view_state(self):
        if self.map_item:
            self.view_state_changed.emit(self.map_item.pos(), self.zoom_factor, self.current_rotation)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.map_item:
            self._apply_view_transform()

    def closeEvent(self, event):
        self._save_current_map_state()
        self._save_history()
        self.closing.emit()
        super().closeEvent(event)