"""Canonical camera optics and light transport for every FocalRuta visualization.

One definition per phenomenon, tested in Python and reused by the diagram
generators and by the interactive labs. The labs receive tables precomputed
here, so what pytest verifies is exactly what the browser draws.

Sources for each formula are recorded in
`architectural_photography/research/visualization_physics_review_2026-09-02.md`.

The models predict the direction and order of magnitude of each relationship.
They are not calibrated renders: they do not predict pixels, exposure or the
behaviour of a specific lens.
"""
from __future__ import annotations

import math

FULL_FRAME_WIDTH_MM = 36.0
FULL_FRAME_HEIGHT_MM = 24.0
CANON_6D_WIDTH_MM = 35.8
CANON_6D_HEIGHT_MM = 23.9
FULL_FRAME_COC_MM = 0.030
DEFAULT_EYE_HEIGHT_M = 1.6

SUN_ANGULAR_DIAMETER_DEG = 0.53
OVERCAST_ANGULAR_DIAMETER_DEG = 60.0
GLASS_NORMAL_REFLECTANCE = 0.04
AERIAL_SCALE_M = 200.0


def half_angle_of_view_deg(focal_mm: float, sensor_mm: float = FULL_FRAME_WIDTH_MM) -> float:
    """Half angle of view: atan(sensor / 2f). Longer focal lengths see less."""
    return math.degrees(math.atan(sensor_mm / (2.0 * focal_mm)))


def angle_of_view_deg(focal_mm: float, sensor_mm: float = FULL_FRAME_WIDTH_MM) -> float:
    """Full angle of view across the given sensor dimension."""
    return 2.0 * half_angle_of_view_deg(focal_mm, sensor_mm)


def projected_height(
    real_height_m: float,
    distance_m: float,
    focal_mm: float,
    sensor_mm: float = FULL_FRAME_HEIGHT_MM,
    frame_px: float = 1000.0,
) -> float:
    """Pinhole projection h = f*H/z, expressed in pixels of a frame_px frame."""
    return frame_px * focal_mm * real_height_m / (sensor_mm * distance_m)


def focal_in_pixels(focal_mm: float, sensor_mm: float, frame_px: float) -> float:
    """Focal length expressed in pixels of the rendered frame."""
    return focal_mm / sensor_mm * frame_px


def vertical_vanishing_point(
    tilt_deg: float,
    focal_mm: float,
    sensor_mm: float = FULL_FRAME_HEIGHT_MM,
    frame_px: float = 1000.0,
) -> float | None:
    """Distance from the principal point to the vertical vanishing point.

    None when the camera is level: parallel verticals meet at infinity.
    The point moves *towards* the frame as the tilt grows.
    """
    if abs(tilt_deg) < 1e-9:
        return None
    return focal_in_pixels(focal_mm, sensor_mm, frame_px) / math.tan(math.radians(tilt_deg))


def keystone_corners(
    tilt_deg: float,
    width_m: float,
    height_m: float,
    distance_m: float,
    focal_mm: float,
    sensor_mm: float = FULL_FRAME_HEIGHT_MM,
    frame_px: float = 1000.0,
    eye_height_m: float = DEFAULT_EYE_HEIGHT_M,
) -> dict[str, float]:
    """Project a rectangular facade seen by a camera tilted up by tilt_deg."""
    focal_px = focal_in_pixels(focal_mm, sensor_mm, frame_px)
    tilt = math.radians(tilt_deg)
    bottom_y = -eye_height_m
    top_y = height_m - eye_height_m
    result: dict[str, float] = {}
    for name, world_y in (("bottom", bottom_y), ("top", top_y)):
        depth = distance_m * math.cos(tilt) + world_y * math.sin(tilt)
        depth = max(depth, 1e-6)
        height = world_y * math.cos(tilt) - distance_m * math.sin(tilt)
        result[f"{name}_width"] = focal_px * width_m / depth
        result[f"{name}_y"] = focal_px * height / depth
    return result


def lambert_luminance(
    surface_azimuth_deg: float,
    light_azimuth_deg: float,
    albedo: float = 0.5,
    ambient: float = 0.0,
    irradiance: float = 1.0,
) -> float:
    """Diffuse response of a face: ambient + albedo*E*cos(theta), clamped at ambient."""
    cosine = math.cos(math.radians(light_azimuth_deg - surface_azimuth_deg))
    if cosine <= 0.0:
        return ambient
    return ambient + albedo * irradiance * cosine


def shadow_length(height_m: float, sun_altitude_deg: float) -> float:
    """Cast shadow length h/tan(altitude); unbounded as the source reaches the horizon."""
    if sun_altitude_deg <= 0.0:
        return math.inf
    return height_m / math.tan(math.radians(sun_altitude_deg))


def penumbra_width(source_angular_diameter_deg: float, occluder_distance_m: float) -> float:
    """Soft-edge width on the receiving plane: distance * tan(angular diameter)."""
    return occluder_distance_m * math.tan(math.radians(source_angular_diameter_deg))


def schlick_reflectance(incidence_deg: float, normal_reflectance: float = GLASS_NORMAL_REFLECTANCE) -> float:
    """Fresnel reflectance, Schlick approximation: F0 + (1-F0)(1-cos)^5."""
    cosine = max(0.0, math.cos(math.radians(incidence_deg)))
    return normal_reflectance + (1.0 - normal_reflectance) * (1.0 - cosine) ** 5


def hyperfocal_mm(focal_mm: float, f_number: float, coc_mm: float = FULL_FRAME_COC_MM) -> float:
    """Hyperfocal distance H = f^2/(N*c) + f, in millimetres."""
    return (focal_mm * focal_mm) / (f_number * coc_mm) + focal_mm


def depth_of_field(
    focal_mm: float,
    f_number: float,
    subject_m: float,
    coc_mm: float = FULL_FRAME_COC_MM,
) -> dict[str, float]:
    """Near/far/total depth of field in metres; far and total may be infinite."""
    hyperfocal = hyperfocal_mm(focal_mm, f_number, coc_mm)
    subject_mm = subject_m * 1000.0
    offset = subject_mm - focal_mm
    near_mm = (hyperfocal * subject_mm) / (hyperfocal + offset)
    denominator = hyperfocal - offset
    far_mm = math.inf if denominator <= 0 else (hyperfocal * subject_mm) / denominator
    near = near_mm / 1000.0
    far = math.inf if far_mm == math.inf else far_mm / 1000.0
    return {
        "near": near,
        "far": far,
        "total": math.inf if far == math.inf else far - near,
        "hyperfocal": hyperfocal / 1000.0,
    }


def motion_blur_px(
    walking_speed_mps: float,
    shutter_seconds: float,
    distance_m: float,
    focal_mm: float,
    sensor_mm: float = FULL_FRAME_WIDTH_MM,
    frame_px: float = 1000.0,
) -> float:
    """Streak length of a subject crossing the frame during the exposure."""
    displacement_m = walking_speed_mps * shutter_seconds
    return projected_height(displacement_m, distance_m, focal_mm, sensor_mm, frame_px)


def aerial_contrast(distance_m: float, haze: float = 0.35) -> float:
    """Contrast surviving atmospheric scattering: exp(-haze * d / scale)."""
    return math.exp(-haze * distance_m / AERIAL_SCALE_M)


def halo_radius(source_luminance: float, exposure_ev: float = 0.0, base_px: float = 1.0) -> float:
    """Visible veiling glare radius; grows with source luminance, shrinks when stopping down."""
    return base_px * math.sqrt(max(0.0, source_luminance) * (2.0 ** exposure_ev))


def exposure_value(aperture: float, shutter_seconds: float, iso: float = 100.0) -> float:
    """EV at the given ISO: log2(N^2/t) - log2(ISO/100)."""
    return math.log2((aperture * aperture) / shutter_seconds) - math.log2(iso / 100.0)


def iso_noise_sigma(iso: float, base_iso: float = 100.0, base_sigma: float = 0.006) -> float:
    """Shot-noise standard deviation, proportional to sqrt(ISO gain)."""
    return base_sigma * math.sqrt(max(base_iso, iso) / base_iso)


DAYLIGHT_SKY_LUMINANCE = 8000.0
DIM_INTERIOR_LUMINANCE = 200.0
ISO_LADDER = (100, 200, 400, 800, 1600, 3200, 6400, 12800)


def specular_visibility(
    reflectance: float,
    sky_luminance: float = DAYLIGHT_SKY_LUMINANCE,
    interior_luminance: float = DIM_INTERIOR_LUMINANCE,
) -> float:
    """Share of the observed luminance that comes from the reflection.

    Glass hides a dim interior long before its Fresnel reflectance is high:
    what decides the view is the ratio between reflected and transmitted light.
    """
    reflected = reflectance * sky_luminance
    transmitted = (1.0 - reflectance) * interior_luminance
    total = reflected + transmitted
    if total <= 0.0:
        return 0.0
    return reflected / total


def nearest_iso(value: float) -> int:
    """Snap a computed sensitivity to the nearest full stop on the ISO ladder."""
    return min(ISO_LADDER, key=lambda step: abs(math.log2(max(1.0, value) / step)))
