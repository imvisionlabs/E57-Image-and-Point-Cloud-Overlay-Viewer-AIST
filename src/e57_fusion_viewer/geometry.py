from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Tuple
import math
import numpy as np

@dataclass
class Correction:
    """Viewer-side correction for pinhole principal point.

    Values are stored as pixel offsets from the E57 principal point.
    corrected_cx = camera.cx + delta_cx_px
    corrected_cy = camera.cy + delta_cy_px
    """
    delta_cx_px: float = 0.0
    delta_cy_px: float = 0.0

    @classmethod
    def from_dict(cls, d: Dict) -> "Correction":
        # Backward/robust loading: ignore old pose-correction keys if present.
        return cls(
            delta_cx_px=float(d.get("delta_cx_px", d.get("cx_offset_px", 0.0))),
            delta_cy_px=float(d.get("delta_cy_px", d.get("cy_offset_px", 0.0))),
        )

    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class Camera:
    guid: str
    name: str
    image_path: str
    width: int
    height: int
    focal_length_mm: float
    pixel_width_mm: float
    pixel_height_mm: float
    cx: float
    cy: float
    rotation_wxyz: Tuple[float, float, float, float]
    translation_xyz: Tuple[float, float, float]

    @property
    def fx(self) -> float:
        return self.focal_length_mm / self.pixel_width_mm

    @property
    def fy(self) -> float:
        return self.focal_length_mm / self.pixel_height_mm

    def corrected_cx(self, correction: Correction | None = None) -> float:
        return float(self.cx + (correction.delta_cx_px if correction is not None else 0.0))

    def corrected_cy(self, correction: Correction | None = None) -> float:
        return float(self.cy + (correction.delta_cy_px if correction is not None else 0.0))

    def to_dict(self, correction: Correction | None = None, include_original: bool = True) -> Dict:
        cx_out = self.corrected_cx(correction)
        cy_out = self.corrected_cy(correction)
        d = {
            "guid": self.guid,
            "name": self.name,
            "image_path": self.image_path,
            "width": int(self.width),
            "height": int(self.height),
            "focal_length_mm": float(self.focal_length_mm),
            "pixel_width_mm": float(self.pixel_width_mm),
            "pixel_height_mm": float(self.pixel_height_mm),
            "cx": float(cx_out),
            "cy": float(cy_out),
            "rotation_wxyz": [float(x) for x in self.rotation_wxyz],
            "translation_xyz": [float(x) for x in self.translation_xyz],
        }
        if include_original:
            d["original_cx"] = float(self.cx)
            d["original_cy"] = float(self.cy)
            d["delta_cx_px"] = float(cx_out - self.cx)
            d["delta_cy_px"] = float(cy_out - self.cy)
        return d

    @classmethod
    def from_dict(cls, d: Dict) -> "Camera":
        return cls(
            guid=d["guid"], name=d["name"], image_path=d["image_path"],
            width=int(d["width"]), height=int(d["height"]),
            focal_length_mm=float(d["focal_length_mm"]),
            pixel_width_mm=float(d["pixel_width_mm"]), pixel_height_mm=float(d["pixel_height_mm"]),
            cx=float(d["cx"]), cy=float(d["cy"]),
            rotation_wxyz=tuple(float(x) for x in d["rotation_wxyz"]),
            translation_xyz=tuple(float(x) for x in d["translation_xyz"]),
        )

def quat_wxyz_to_rotmat(q_wxyz) -> np.ndarray:
    q = np.asarray(q_wxyz, dtype=float)
    n = np.linalg.norm(q)
    if n == 0:
        return np.eye(3)
    w, x, y, z = q / n
    return np.array([
        [1 - 2*(y*y + z*z), 2*(x*y - z*w), 2*(x*z + y*w)],
        [2*(x*y + z*w), 1 - 2*(x*x + z*z), 2*(y*z - x*w)],
        [2*(x*z - y*w), 2*(y*z + x*w), 1 - 2*(x*x + y*y)],
    ], dtype=float)

def camera_pose_matrix(camera: Camera) -> np.ndarray:
    """E57 Image2D pose is normally camera->world."""
    T = np.eye(4, dtype=float)
    T[:3,:3] = quat_wxyz_to_rotmat(camera.rotation_wxyz)
    T[:3,3] = np.asarray(camera.translation_xyz, dtype=float)
    return T

def _transform_points_row(points: np.ndarray, T: np.ndarray) -> np.ndarray:
    """Column-convention 4x4 T applied to Nx3 points, returned as Nx3."""
    return points @ T[:3, :3].T + T[:3, 3][None, :]

def invert_se3(T: np.ndarray) -> np.ndarray:
    Ti = np.eye(4, dtype=float)
    R = T[:3,:3]
    t = T[:3,3]
    Ti[:3,:3] = R.T
    Ti[:3,3] = -(R.T @ t)
    return Ti

def world_to_camera(
    points_world: np.ndarray,
    camera: Camera,
    transform_mode: str = "cam2world_inv",
) -> np.ndarray:
    """
    transform_mode:
      cam2world_inv : Interpret E57 pose as camera->world, then invert it. This is the expected E57 convention.
      raw_world2cam : Interpret the raw E57 pose matrix itself as world->camera. Kept for debugging vendor/exporter differences.
    """
    T = camera_pose_matrix(camera)
    if transform_mode == "cam2world_inv":
        return _transform_points_row(points_world, invert_se3(T))
    if transform_mode == "raw_world2cam":
        return _transform_points_row(points_world, T)
    raise ValueError(f"Unknown transform_mode: {transform_mode}")

def project_points(
    points_world: np.ndarray,
    camera: Camera,
    correction: Correction | None = None,
    z_min: float = 0.05,
    transform_mode: str = "cam2world_inv",
    forward_sign: int = -1,
    flip_v: bool = False,
    z_buffer: bool = False,
):
    """
    Project world points to the image plane.

    forward_sign:
      +1: camera front is +Z
      -1: camera front is -Z. This matches many E57/projective-camera exports and the user's proven script.
    """
    pc = world_to_camera(points_world, camera, transform_mode=transform_mode)
    x, y, z = pc[:,0], pc[:,1], pc[:,2]
    zf = float(forward_sign) * z
    eps = 1e-12
    front = zf > z_min
    if not np.any(front):
        return np.empty((0,2), dtype=float), front, np.empty((0,), dtype=float)
    idx_front = np.flatnonzero(front)
    pf = pc[front]
    zff = zf[front]
    cx = camera.corrected_cx(correction)
    cy = camera.corrected_cy(correction)
    u = camera.fx * (pf[:,0] / (zff + eps)) + cx
    v = camera.fy * (pf[:,1] / (zff + eps)) + cy
    if flip_v:
        v = (camera.height - 1) - v
    in_img = (u >= 0) & (u < camera.width) & (v >= 0) & (v < camera.height)
    idx = idx_front[in_img]
    uv = np.column_stack([u[in_img], v[in_img]])
    depth = zff[in_img]

    if z_buffer and idx.size > 0:
        # Keep only the nearest point for each image pixel.
        pix_x = np.floor(uv[:,0]).astype(np.int64)
        pix_y = np.floor(uv[:,1]).astype(np.int64)
        pix = pix_y * int(camera.width) + pix_x
        order = np.lexsort((depth, pix))  # primary=pix, secondary=depth ascending within pixel
        pix_sorted = pix[order]
        keep_sorted = np.ones_like(order, dtype=bool)
        keep_sorted[1:] = pix_sorted[1:] != pix_sorted[:-1]
        keep = order[keep_sorted]
        idx = idx[keep]
        uv = uv[keep]
        depth = depth[keep]

    mask = np.zeros(points_world.shape[0], dtype=bool)
    mask[idx] = True
    return uv, mask, depth

def projection_stats(
    points_world: np.ndarray,
    camera: Camera,
    correction: Correction | None = None,
    transform_mode: str = "cam2world_inv",
    forward_sign: int = -1,
    flip_v: bool = False,
):
    uv, mask, depth = project_points(
        points_world, camera, correction,
        transform_mode=transform_mode,
        forward_sign=forward_sign,
        flip_v=flip_v,
        z_buffer=False,
    )
    return {
        "projected": int(mask.sum()),
        "rate": float(mask.mean()) if mask.size else 0.0,
        "depth_min": float(depth.min()) if depth.size else None,
        "depth_max": float(depth.max()) if depth.size else None,
    }

def nearest_projected_point(click_uv, projected_uv: np.ndarray, projected_xyz: np.ndarray, max_pixel_distance: float = 10.0):
    if projected_uv.size == 0:
        return None, None, None
    d2 = np.sum((projected_uv - np.asarray(click_uv)[None,:])**2, axis=1)
    i = int(np.argmin(d2))
    dist = float(np.sqrt(d2[i]))
    if dist > max_pixel_distance:
        return None, dist, None
    return i, dist, projected_xyz[i]
