from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image
from PySide6.QtCore import Qt, QPointF, Signal, QThread
from PySide6.QtGui import QImage, QPainter, QPen, QColor
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressDialog,
    QSlider,
    QSpinBox,
    QDoubleSpinBox,
    QVBoxLayout,
    QWidget,
)

from .geometry import Camera, Correction, project_points, projection_stats, nearest_projected_point


APP_VERSION = "v8"

# The first convention is the default verified with the provided Pentax E57 sample.
CONVENTIONS = [
    ("E57 pose=cam→world, front=-Z  ※推奨", "cam2world_inv", -1),
    ("E57 pose=cam→world, front=+Z", "cam2world_inv", +1),
    ("raw pose=world→cam, front=-Z", "raw_world2cam", -1),
    ("raw pose=world→cam, front=+Z", "raw_world2cam", +1),
]


class PrepareWorker(QThread):
    message = Signal(str)
    succeeded = Signal(str)
    failed = Signal(str)

    def __init__(self, e57_path: Path, dataset_dir: Path, max_points: int = 500000):
        super().__init__()
        self.e57_path = Path(e57_path)
        self.dataset_dir = Path(dataset_dir)
        self.max_points = int(max_points)

    @staticmethod
    def project_root() -> Path:
        """Return the application root in both source and PyInstaller builds."""
        if getattr(sys, "frozen", False):
            return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
        # main.py is located at <project>/src/e57_fusion_viewer/main.py
        return Path(__file__).resolve().parents[2]

    def _run_tool(self, script: Path, args: list[str], step_name: str):
        """Run a bundled tool script in-process.

        This avoids calling ``sys.executable`` as a Python interpreter, which is
        important after PyInstaller packaging because ``sys.executable`` becomes
        E57FusionViewer.exe.
        """
        self.message.emit(f"{step_name}...\n{script} " + " ".join(args))
        if not script.exists():
            raise RuntimeError(f"Tool script not found: {script}")

        old_argv = sys.argv[:]
        try:
            sys.argv = [str(script)] + [str(a) for a in args]
            runpy.run_path(str(script), run_name="__main__")
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
            if code != 0:
                raise RuntimeError(f"{step_name} failed with code {code}")
        finally:
            sys.argv = old_argv

    def run(self):
        try:
            root = self.project_root()
            tools = root / "tools"
            self.dataset_dir.mkdir(parents=True, exist_ok=True)

            self._run_tool(
                tools / "extract_images_from_e57_xml.py",
                [
                    "--e57",
                    str(self.e57_path),
                    "--out",
                    str(self.dataset_dir),
                ],
                "Step 1/2: Extract images and camera metadata",
            )
            self._run_tool(
                tools / "convert_points_with_pye57.py",
                [
                    "--e57",
                    str(self.e57_path),
                    "--out",
                    str(self.dataset_dir / "points.npz"),
                    "--all-scans",
                    "--max-points",
                    str(self.max_points),
                ],
                "Step 2/2: Convert point cloud",
            )
            self.message.emit(f"Prepared dataset: {self.dataset_dir}")
            self.succeeded.emit(str(self.dataset_dir))
        except Exception as e:
            self.failed.emit(str(e))


class OverlayWidget(QWidget):
    clicked_image = Signal(float, float)

    def __init__(self):
        super().__init__()
        self.setMinimumSize(900, 700)
        self.image = None
        self.uv = np.empty((0, 2))
        self.rgb = None
        self.point_alpha = 160
        self.image_alpha = 255
        self.point_size = 2
        self.rect_img = (0, 0, 1, 1)

    def set_image(self, path: Path):
        im = Image.open(path).convert("RGB")
        w, h = im.size
        data = im.tobytes("raw", "RGB")
        self.image = QImage(data, w, h, 3 * w, QImage.Format_RGB888).copy()
        self.update()

    def set_overlay(self, uv, rgb):
        self.uv = uv
        self.rgb = rgb
        self.update()

    def paintEvent(self, ev):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(30, 30, 30))
        if self.image is None:
            p.setPen(QColor(230, 230, 230))
            p.drawText(self.rect(), Qt.AlignCenter, "Open prepared dataset or Open E57 and prepare")
            p.end()
            return

        iw, ih = self.image.width(), self.image.height()
        scale = min(self.width() / iw, self.height() / ih)
        dw, dh = iw * scale, ih * scale
        x0, y0 = (self.width() - dw) / 2, (self.height() - dh) / 2
        self.rect_img = (x0, y0, dw, dh)
        p.setOpacity(max(0.0, min(1.0, self.image_alpha / 255.0)))
        p.drawImage(
            int(x0),
            int(y0),
            self.image.scaled(int(dw), int(dh), Qt.KeepAspectRatio, Qt.SmoothTransformation),
        )
        p.setOpacity(1.0)

        if self.uv.size:
            step = max(1, self.uv.shape[0] // 120000)
            uv = self.uv[::step]
            rgb = self.rgb[::step] if self.rgb is not None and len(self.rgb) >= len(self.uv) else None
            for j, (u, v) in enumerate(uv):
                if rgb is not None:
                    r, g, b = map(int, rgb[j])
                    c = QColor(r, g, b, self.point_alpha)
                else:
                    c = QColor(255, 40, 40, self.point_alpha)
                p.setPen(QPen(c, max(1, self.point_size)))
                p.drawPoint(QPointF(float(x0 + u * scale), float(y0 + v * scale)))
        p.end()

    def mousePressEvent(self, ev):
        if self.image is None:
            return
        x0, y0, dw, dh = self.rect_img
        x, y = ev.position().x(), ev.position().y()
        if x0 <= x <= x0 + dw and y0 <= y <= y0 + dh:
            self.clicked_image.emit(
                float((x - x0) * self.image.width() / dw),
                float((y - y0) * self.image.height() / dh),
            )


class PrincipalPointPanel(QWidget):
    changed = Signal()

    def __init__(self):
        super().__init__()
        self.camera: Optional[Camera] = None
        self.e57_label = QLabel("E57 CX/CY: -")
        self.delta_label = QLabel("Delta CX/CY: -")
        self.corrected_cx = QDoubleSpinBox()
        self.corrected_cy = QDoubleSpinBox()
        for b in (self.corrected_cx, self.corrected_cy):
            b.setRange(-10000.0, 10000.0)
            b.setSingleStep(0.1)
            b.setDecimals(3)
            b.setSuffix(" px")
            b.valueChanged.connect(self._on_value_changed)

        lay = QFormLayout(self)
        lay.addRow(self.e57_label)
        lay.addRow("Corrected CX", self.corrected_cx)
        lay.addRow("Corrected CY", self.corrected_cy)
        lay.addRow(self.delta_label)
        reset = QPushButton("Reset CX/CY to E57 values")
        reset.clicked.connect(self.reset_to_e57)
        lay.addRow(reset)

    def _on_value_changed(self):
        self._refresh_delta_label()
        self.changed.emit()

    def _refresh_delta_label(self):
        if self.camera is None:
            self.e57_label.setText("E57 CX/CY: -")
            self.delta_label.setText("Delta CX/CY: -")
            return
        dx = self.corrected_cx.value() - self.camera.cx
        dy = self.corrected_cy.value() - self.camera.cy
        self.e57_label.setText(f"E57 CX/CY: {self.camera.cx:.3f}, {self.camera.cy:.3f} px")
        self.delta_label.setText(f"Delta CX/CY: {dx:+.3f}, {dy:+.3f} px")

    def set_camera_and_correction(self, camera: Camera, corr: Correction):
        self.camera = camera
        old = self.blockSignals(True)
        wold = [self.corrected_cx.blockSignals(True), self.corrected_cy.blockSignals(True)]
        try:
            margin = max(camera.width, camera.height)
            self.corrected_cx.setRange(-margin, camera.width + margin)
            self.corrected_cy.setRange(-margin, camera.height + margin)
            self.corrected_cx.setValue(float(camera.cx + corr.delta_cx_px))
            self.corrected_cy.setValue(float(camera.cy + corr.delta_cy_px))
        finally:
            self.corrected_cx.blockSignals(wold[0])
            self.corrected_cy.blockSignals(wold[1])
            self.blockSignals(old)
        self._refresh_delta_label()
        self.changed.emit()

    def correction(self) -> Correction:
        if self.camera is None:
            return Correction()
        return Correction(
            delta_cx_px=float(self.corrected_cx.value() - self.camera.cx),
            delta_cy_px=float(self.corrected_cy.value() - self.camera.cy),
        )

    def reset_to_e57(self):
        if self.camera is None:
            return
        old = [self.corrected_cx.blockSignals(True), self.corrected_cy.blockSignals(True)]
        try:
            self.corrected_cx.setValue(float(self.camera.cx))
            self.corrected_cy.setValue(float(self.camera.cy))
        finally:
            self.corrected_cx.blockSignals(old[0])
            self.corrected_cy.blockSignals(old[1])
        self._refresh_delta_label()
        self.changed.emit()


class MainWindow(QMainWindow):
    def __init__(self, dataset_dir: Optional[Path] = None):
        super().__init__()
        self.setWindowTitle(f"E57 Fusion Viewer MVP {APP_VERSION}")
        self.resize(1500, 920)
        self.dataset_dir = None
        self.cameras = []
        self.points_xyz = None
        self.points_rgb = None
        self.points_cache = {}
        self.current_points_path = None
        self.current_uv = np.empty((0, 2))
        self.current_xyz = np.empty((0, 3))
        self.corrections = {}
        self.prepare_worker = None
        self.prepare_dialog = None

        root = QWidget()
        self.setCentralWidget(root)
        ml = QHBoxLayout(root)
        self.overlay = OverlayWidget()
        self.overlay.clicked_image.connect(self.on_click)
        ml.addWidget(self.overlay, 1)

        side = QWidget()
        sl = QVBoxLayout(side)
        ml.addWidget(side, 0)

        open_btn = QPushButton("Open prepared dataset")
        open_btn.clicked.connect(self.choose)
        sl.addWidget(open_btn)

        open_e57_btn = QPushButton("Open E57 and prepare")
        open_e57_btn.clicked.connect(self.choose_e57_and_prepare)
        sl.addWidget(open_e57_btn)

        self.combo = QComboBox()
        self.combo.currentIndexChanged.connect(self.on_camera)
        sl.addWidget(QLabel("Image"))
        sl.addWidget(self.combo)

        sl.addWidget(QLabel("Projection convention"))
        self.conv = QComboBox()
        for label, _mode, _fs in CONVENTIONS:
            self.conv.addItem(label)
        self.conv.setCurrentIndex(0)
        self.conv.currentIndexChanged.connect(self.update_projection)
        sl.addWidget(self.conv)

        self.auto_btn = QPushButton("Auto choose convention")
        self.auto_btn.clicked.connect(self.auto_choose_convention)
        sl.addWidget(self.auto_btn)

        self.defaults_btn = QPushButton("Apply Pentax E57 defaults")
        self.defaults_btn.clicked.connect(self.apply_pentax_defaults)
        sl.addWidget(self.defaults_btn)

        self.flip_v = QCheckBox("Flip image V axis / vertical mirror  ※このE57では通常ON")
        self.flip_v.setChecked(True)
        self.flip_v.stateChanged.connect(self.update_projection)
        sl.addWidget(self.flip_v)

        self.zbuf = QCheckBox("Use simple Z-buffer")
        self.zbuf.setChecked(False)
        self.zbuf.stateChanged.connect(self.update_projection)
        sl.addWidget(self.zbuf)

        self.pp = PrincipalPointPanel()
        self.pp.changed.connect(self.update_projection)
        sl.addWidget(QLabel("Principal point correction"))
        sl.addWidget(self.pp)

        form = QFormLayout()
        self.point_alpha = QSlider(Qt.Horizontal)
        self.point_alpha.setRange(20, 255)
        self.point_alpha.setValue(160)
        self.point_alpha.valueChanged.connect(self.update_overlay)
        form.addRow("point alpha", self.point_alpha)

        self.image_alpha = QSlider(Qt.Horizontal)
        self.image_alpha.setRange(0, 255)
        self.image_alpha.setValue(255)
        self.image_alpha.valueChanged.connect(self.update_overlay)
        form.addRow("image alpha", self.image_alpha)

        self.ps = QSpinBox()
        self.ps.setRange(1, 8)
        self.ps.setValue(2)
        self.ps.valueChanged.connect(self.update_overlay)
        form.addRow("point size", self.ps)

        self.maxn = QSpinBox()
        self.maxn.setRange(1000, 1000000)
        self.maxn.setSingleStep(1000)
        self.maxn.setValue(120000)
        self.maxn.valueChanged.connect(self.update_projection)
        form.addRow("max overlay points", self.maxn)

        self.prepare_max_points = QSpinBox()
        self.prepare_max_points.setRange(10000, 10000000)
        self.prepare_max_points.setSingleStep(10000)
        self.prepare_max_points.setValue(500000)
        form.addRow("prepare max points", self.prepare_max_points)
        sl.addLayout(form)

        save = QPushButton("Save corrections.json + settings")
        save.clicked.connect(self.save_corrections)
        sl.addWidget(save)

        export = QPushButton("Export corrected_cameras.json")
        export.clicked.connect(self.export_corrected_cameras_json)
        sl.addWidget(export)

        self.status = QLabel("No dataset loaded")
        self.status.setWordWrap(True)
        sl.addWidget(self.status)
        sl.addStretch(1)

        if dataset_dir:
            self.load(dataset_dir)

    def choose_e57_and_prepare(self):
        e57_file, _ = QFileDialog.getOpenFileName(
            self,
            "Open E57 file and prepare dataset",
            "",
            "E57 files (*.e57);;All files (*.*)",
        )
        if not e57_file:
            return
        e57_path = Path(e57_file)
        dataset_dir = e57_path.parent / f"{e57_path.stem}_prepared_dataset"
        self.prepare_e57(e57_path, dataset_dir)

    def prepare_e57(self, e57_path: Path, dataset_dir: Path):
        if self.prepare_worker is not None and self.prepare_worker.isRunning():
            return
        self.status.setText(f"Preparing E57 dataset...\n{e57_path}\nOutput: {dataset_dir}")
        self.prepare_dialog = QProgressDialog(
            "E57を前処理中です...\n画像・カメラ情報と点群を抽出しています。",
            None,
            0,
            0,
            self,
        )
        self.prepare_dialog.setWindowTitle("Preparing E57")
        self.prepare_dialog.setWindowModality(Qt.ApplicationModal)
        self.prepare_dialog.setCancelButton(None)
        self.prepare_dialog.setMinimumDuration(0)
        self.prepare_dialog.setAutoClose(False)
        self.prepare_dialog.setAutoReset(False)
        self.centralWidget().setEnabled(False)
        self.prepare_dialog.show()

        self.prepare_worker = PrepareWorker(
            e57_path,
            dataset_dir,
            max_points=self.prepare_max_points.value(),
        )
        self.prepare_worker.message.connect(self.on_prepare_message)
        self.prepare_worker.succeeded.connect(self.on_prepare_success)
        self.prepare_worker.failed.connect(self.on_prepare_failed)
        self.prepare_worker.finished.connect(self.on_prepare_finished)
        self.prepare_worker.start()

    def on_prepare_message(self, text: str):
        self.status.setText(text)
        if self.prepare_dialog is not None:
            last = text.splitlines()[-1] if text else "E57を前処理中です..."
            if len(last) > 120:
                last = last[:117] + "..."
            self.prepare_dialog.setLabelText("E57を前処理中です...\n" + last)

    def on_prepare_success(self, dataset_dir: str):
        self.load(Path(dataset_dir))
        self.status.setText(f"Preprocessing completed.\nLoaded: {dataset_dir}")

    def on_prepare_failed(self, message: str):
        self.status.setText("Preprocessing failed:\n" + message)
        QMessageBox.critical(self, "Preprocessing failed", message)

    def on_prepare_finished(self):
        self.centralWidget().setEnabled(True)
        if self.prepare_dialog is not None:
            self.prepare_dialog.close()
            self.prepare_dialog = None
        self.prepare_worker = None

    def choose(self):
        d = QFileDialog.getExistingDirectory(self, "Open prepared dataset")
        if d:
            self.load(Path(d))

    def load(self, d: Path):
        self.dataset_dir = d
        meta = json.loads((d / "cameras.json").read_text(encoding="utf-8"))
        camera_rows = []
        for image_index, row in enumerate(meta["cameras"]):
            row = dict(row)
            row.setdefault("image_index", image_index)
            if not row.get("camera_id"):
                row["camera_id"] = f"image_{int(row['image_index']):04d}_{row.get('guid') or row.get('name', '')}"
            camera_rows.append(row)
        self.cameras = [Camera.from_dict(c) for c in camera_rows]
        self.points_cache = {}
        self.current_points_path = None
        self.points_xyz = None
        self.points_rgb = None

        self.load_corrections_and_settings()

        self.combo.blockSignals(True)
        self.combo.clear()
        for c in self.cameras:
            self.combo.addItem(self.camera_label(c))
        self.combo.blockSignals(False)
        self.combo.setCurrentIndex(0)
        self.on_camera(0)
        point_count = self.points_xyz.shape[0] if self.points_xyz is not None else 0
        self.status.setText(f"Loaded {len(self.cameras)} images, {point_count:,} points")

    def camera_label(self, camera: Camera) -> str:
        label = f"{camera.image_index:04d}: {camera.name}"
        if camera.scan_index is not None:
            label += f" [scan {camera.scan_index}]"
        return label

    def points_path_for_camera(self, camera: Camera) -> Path:
        candidates = []
        if camera.points_path:
            candidates.append(self.dataset_dir / camera.points_path)
        if camera.scan_index is not None:
            candidates.append(self.dataset_dir / f"points_scan_{camera.scan_index:03d}.npz")
        candidates.append(self.dataset_dir / "points.npz")
        for path in candidates:
            if path.exists():
                return path
        raise FileNotFoundError(f"Point cloud file not found for {camera.name}: {candidates[0]}")

    def load_points_for_camera(self, camera: Camera):
        path = self.points_path_for_camera(camera)
        key = str(path.resolve())
        if key not in self.points_cache:
            with np.load(path) as pts:
                xyz = pts["xyz"].astype(float)
                rgb = pts["rgb"].astype(np.uint8) if "rgb" in pts.files else None
            self.points_cache[key] = (xyz, rgb)
        self.points_xyz, self.points_rgb = self.points_cache[key]
        self.current_points_path = path

    def load_corrections_and_settings(self):
        self.corrections = {}
        path = self.dataset_dir / "corrections.json"
        if not path.exists():
            self.apply_pentax_defaults(update=False)
            return
        data = json.loads(path.read_text(encoding="utf-8"))
        self.corrections = {
            g: Correction.from_dict(v) for g, v in data.get("corrections", {}).items()
        }

        saved_version = data.get("version") or data.get("settings", {}).get("app_version")
        if saved_version == APP_VERSION:
            self.apply_settings(data.get("settings", {}))
        else:
            self.apply_pentax_defaults(update=False)

    def correction_for_camera(self, camera: Camera) -> Correction:
        return self.corrections.get(
            camera.correction_key,
            self.corrections.get(camera.guid, Correction()),
        )

    def set_correction_for_camera(self, camera: Camera, correction: Correction):
        self.corrections[camera.correction_key] = correction

    def apply_pentax_defaults(self, update: bool = True):
        """Apply verified defaults for the provided Pentax E57 sample."""
        widgets = [self.conv, self.flip_v, self.zbuf, self.point_alpha, self.image_alpha, self.ps, self.maxn]
        old = [w.blockSignals(True) for w in widgets]
        try:
            self.conv.setCurrentIndex(0)
            self.flip_v.setChecked(True)
            self.zbuf.setChecked(False)
            self.point_alpha.setValue(160)
            self.image_alpha.setValue(255)
            self.ps.setValue(2)
            self.maxn.setValue(120000)
        finally:
            for w, state in zip(widgets, old):
                w.blockSignals(state)
        if update:
            self.update_projection()

    def current_settings(self):
        mode, fs = self.current_convention()
        return {
            "app_version": APP_VERSION,
            "projection_convention_index": int(self.conv.currentIndex()),
            "transform_mode": mode,
            "forward_sign": int(fs),
            "flip_v": bool(self.flip_v.isChecked()),
            "z_buffer": bool(self.zbuf.isChecked()),
            "point_alpha": int(self.point_alpha.value()),
            "overlay_alpha": int(self.point_alpha.value()),
            "image_alpha": int(self.image_alpha.value()),
            "point_size": int(self.ps.value()),
            "max_overlay_points": int(self.maxn.value()),
        }

    def apply_settings(self, settings: dict):
        if not settings:
            return
        widgets = [self.conv, self.flip_v, self.zbuf, self.point_alpha, self.image_alpha, self.ps, self.maxn]
        old = [w.blockSignals(True) for w in widgets]
        try:
            idx = settings.get("projection_convention_index", None)
            if isinstance(idx, int) and 0 <= idx < len(CONVENTIONS):
                self.conv.setCurrentIndex(idx)
            else:
                mode = settings.get("transform_mode")
                fs = settings.get("forward_sign")
                for j, (_label, m, f) in enumerate(CONVENTIONS):
                    if m == mode and int(f) == int(fs):
                        self.conv.setCurrentIndex(j)
                        break
            self.flip_v.setChecked(bool(settings.get("flip_v", True)))
            self.zbuf.setChecked(bool(settings.get("z_buffer", False)))
            self.point_alpha.setValue(int(settings.get("point_alpha", settings.get("overlay_alpha", 160))))
            self.image_alpha.setValue(int(settings.get("image_alpha", 255)))
            self.ps.setValue(int(settings.get("point_size", 2)))
            self.maxn.setValue(int(settings.get("max_overlay_points", 120000)))
        finally:
            for w, state in zip(widgets, old):
                w.blockSignals(state)

    def save_corrections(self):
        cam = self.current_camera()
        if cam:
            self.set_correction_for_camera(cam, self.pp.correction())
        path = self.dataset_dir / "corrections.json"
        payload = {
            "version": APP_VERSION,
            "settings": self.current_settings(),
            "correction_type": "principal_point_delta_px",
            "corrections": {g: c.to_dict() for g, c in self.corrections.items()},
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        self.status.setText(f"Saved {path}\nPrincipal point corrections will be restored on next launch.")

    def export_corrected_cameras_json(self):
        if self.dataset_dir is None or not self.cameras:
            return
        cam = self.current_camera()
        if cam:
            self.set_correction_for_camera(cam, self.pp.correction())
        out = self.dataset_dir / "corrected_cameras.json"
        payload = {
            "version": APP_VERSION,
            "note": "CX/CY are corrected by applying delta_cx_px and delta_cy_px to the original E57 principalPointX/Y values. This is metadata export, not an E57 rewrite.",
            "settings": self.current_settings(),
            "cameras": [c.to_dict(self.correction_for_camera(c), include_original=True) for c in self.cameras],
        }
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        self.status.setText(f"Exported {out}\nUse this to verify CX/CY before writing a corrected E57.")

    def current_camera(self):
        i = self.combo.currentIndex()
        return self.cameras[i] if 0 <= i < len(self.cameras) else None

    def current_convention(self):
        i = self.conv.currentIndex()
        if i < 0:
            i = 0
        _label, mode, fs = CONVENTIONS[i]
        return mode, fs

    def on_camera(self, idx):
        cam = self.current_camera()
        if not cam or not self.dataset_dir:
            return
        try:
            self.load_points_for_camera(cam)
            self.overlay.set_image(self.dataset_dir / cam.image_path)
        except Exception as e:
            self.status.setText(f"Failed to load camera data:\n{e}")
            QMessageBox.warning(self, "Failed to load camera data", str(e))
            return
        self.pp.set_camera_and_correction(cam, self.correction_for_camera(cam))
        self.update_projection()

    def update_overlay(self):
        self.overlay.point_alpha = self.point_alpha.value()
        self.overlay.image_alpha = self.image_alpha.value()
        self.overlay.point_size = self.ps.value()
        self.overlay.update()

    def auto_choose_convention(self):
        cam = self.current_camera()
        if cam is None or self.points_xyz is None:
            return
        corr = self.pp.correction()
        rows = []
        for idx, (label, mode, fs) in enumerate(CONVENTIONS):
            st = projection_stats(
                self.points_xyz,
                cam,
                corr,
                transform_mode=mode,
                forward_sign=fs,
                flip_v=self.flip_v.isChecked(),
            )
            rows.append((idx, label, st["projected"], st["rate"]))
        valid = [r for r in rows if 0.0001 < r[3] < 0.95]
        best = max(valid or rows, key=lambda r: r[2])
        self.conv.setCurrentIndex(best[0])
        msg = ["Auto convention result:"]
        for _idx, label, projected, rate in rows:
            mark = "* " if _idx == best[0] else "  "
            msg.append(f"{mark}{label}: {projected:,} pts ({rate:.4%})")
        self.status.setText("\n".join(msg))
        self.update_projection()

    def update_projection(self):
        cam = self.current_camera()
        if cam is None or self.points_xyz is None:
            return
        corr = self.pp.correction()
        self.set_correction_for_camera(cam, corr)
        mode, fs = self.current_convention()
        uv, mask, depth = project_points(
            self.points_xyz,
            cam,
            corr,
            transform_mode=mode,
            forward_sign=fs,
            flip_v=self.flip_v.isChecked(),
            z_buffer=self.zbuf.isChecked(),
        )
        xyz = self.points_xyz[mask]
        rgb = self.points_rgb[mask] if self.points_rgb is not None else None
        if uv.shape[0] > self.maxn.value():
            idx = np.linspace(0, uv.shape[0] - 1, self.maxn.value()).astype(int)
            uv = uv[idx]
            xyz = xyz[idx]
            rgb = rgb[idx] if rgb is not None else None
        self.current_uv, self.current_xyz = uv, xyz
        self.overlay.point_alpha = self.point_alpha.value()
        self.overlay.image_alpha = self.image_alpha.value()
        self.overlay.point_size = self.ps.value()
        self.overlay.set_overlay(uv, rgb)
        cx_corr = cam.corrected_cx(corr)
        cy_corr = cam.corrected_cy(corr)
        self.status.setText(
            f"Projected {uv.shape[0]:,} points. fx={cam.fx:.2f}, fy={cam.fy:.2f}\n"
            f"CX/CY={cx_corr:.3f}, {cy_corr:.3f} px "
            f"(delta {corr.delta_cx_px:+.3f}, {corr.delta_cy_px:+.3f})\n"
            f"mode={mode}, front={'-Z' if fs < 0 else '+Z'}, "
            f"flip_v={self.flip_v.isChecked()}, z_buffer={self.zbuf.isChecked()}\n"
            f"points={self.current_points_path.name if self.current_points_path else '-'}"
        )

    def on_click(self, u, v):
        _, dist, xyz = nearest_projected_point((u, v), self.current_uv, self.current_xyz, 15.0)
        if xyz is None:
            self.status.setText(f"Clicked ({u:.1f}, {v:.1f}); no projected point within 15 px")
        else:
            self.status.setText(
                f"Clicked ({u:.1f}, {v:.1f})\n"
                f"Nearest distance: {dist:.2f} px\n"
                f"XYZ: ({xyz[0]:.4f}, {xyz[1]:.4f}, {xyz[2]:.4f})"
            )


def main():
    app = QApplication(sys.argv)
    win = MainWindow(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
