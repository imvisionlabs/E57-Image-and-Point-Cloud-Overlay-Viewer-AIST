from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple
import numpy as np

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
    camera_id: str = ""
    image_index: int = 0
    associated_data3d_guid: str = ""
    scan_index: int | None = None
    points_path: str = "points.npz"

    @property
    def correction_key(self) -> str:
        return self.camera_id or self.guid

    @property
    def fx(self) -> float:
        return self.focal_length_mm / self.pixel_width_mm

    @property
    def fy(self) -> float:
        return self.focal_length_mm / self.pixel_height_mm

    @classmethod
    def from_dict(cls, d: Dict) -> "Camera":
        scan_index_raw = d.get("scan_index", None)
        scan_index = int(scan_index_raw) if scan_index_raw is not None else None
        image_index = int(d.get("image_index", 0))
        camera_id = str(d.get("camera_id") or d.get("guid", "") or f"image_{image_index:04d}")
        points_path = d.get("points_path")
        if not points_path:
            points_path = f"points_scan_{scan_index:03d}.npz" if scan_index is not None else "points.npz"
        return cls(
            guid=d["guid"], name=d["name"], image_path=d["image_path"],
            width=int(d["width"]), height=int(d["height"]),
            focal_length_mm=float(d["focal_length_mm"]),
            pixel_width_mm=float(d["pixel_width_mm"]), pixel_height_mm=float(d["pixel_height_mm"]),
            cx=float(d["cx"]), cy=float(d["cy"]),
            rotation_wxyz=tuple(float(x) for x in d["rotation_wxyz"]),
            translation_xyz=tuple(float(x) for x in d["translation_xyz"]),
            camera_id=camera_id,
            image_index=image_index,
            associated_data3d_guid=str(d.get("associated_data3d_guid", "")),
            scan_index=scan_index,
            points_path=str(points_path),
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
    # Avoid NumPy's BLAS-backed ``@`` here. On Windows, importing PySide6 can
    # change DLL resolution and make an otherwise valid MKL installation fail
    # when the first matrix multiplication is evaluated (0xc06d007f).
    rotated = np.einsum("ij,kj->ik", points, T[:3, :3], optimize=False)
    return rotated + T[:3, 3][None, :]

def invert_se3(T: np.ndarray) -> np.ndarray:
    Ti = np.eye(4, dtype=float)
    R = T[:3,:3]
    t = T[:3,3]
    Ti[:3,:3] = R.T
    Ti[:3,3] = -np.einsum("ji,j->i", R, t, optimize=False)
    return Ti

def world_to_camera(points_world: np.ndarray, camera: Camera) -> np.ndarray:
    """E57 Image2D pose is camera->world, so invert it to get world->camera."""
    return _transform_points_row(points_world, invert_se3(camera_pose_matrix(camera)))

# Verified against the provided Pentax E57 samples: camera front is -Z and
# camera +Y points upward, while image +V points downward.
FORWARD_SIGN = -1

def project_points(points_world: np.ndarray, camera: Camera, z_min: float = 0.05):
    """Project world points to the image plane using the E57 principal point."""
    pc = world_to_camera(points_world, camera)
    # Positive distance along the camera's forward direction. The signed E57
    # camera coordinate itself is negative for points in front of the camera.
    depth_all = float(FORWARD_SIGN) * pc[:,2]
    eps = 1e-12
    front = depth_all > z_min
    if not np.any(front):
        return np.empty((0,2), dtype=float), front, np.empty((0,), dtype=float)
    idx_front = np.flatnonzero(front)
    pf = pc[front]
    depth = depth_all[front]
    u = camera.cx + camera.fx * (pf[:,0] / (depth + eps))
    # Preserve principalPointY. Only the camera Y axis changes sign when it is
    # mapped from camera-up coordinates to the image's downward V axis.
    v = camera.cy - camera.fy * (pf[:,1] / (depth + eps))
    in_img = (u >= 0) & (u < camera.width) & (v >= 0) & (v < camera.height)
    idx = idx_front[in_img]
    uv = np.column_stack([u[in_img], v[in_img]])
    depth = depth[in_img]

    mask = np.zeros(points_world.shape[0], dtype=bool)
    mask[idx] = True
    return uv, mask, depth

def nearest_projected_point(click_uv, projected_uv: np.ndarray, projected_xyz: np.ndarray, max_pixel_distance: float = 10.0):
    if projected_uv.size == 0:
        return None, None, None
    d2 = np.sum((projected_uv - np.asarray(click_uv)[None,:])**2, axis=1)
    i = int(np.argmin(d2))
    dist = float(np.sqrt(d2[i]))
    if dist > max_pixel_distance:
        return None, dist, None
    return i, dist, projected_xyz[i]
