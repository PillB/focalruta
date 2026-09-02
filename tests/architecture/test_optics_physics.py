"""RED/GREEN physical invariants for the shared optics module.

Requirements: G05, G07, H03, H04, H05, H06, H07.

These assertions observe physical relationships, not implementation strings:
monotonicity, limiting behaviour, closed-form agreement and sign of change.
"""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import optics_physics as op


def test_half_angle_of_view_matches_closed_form_and_narrows_with_focal():
    for focal in (24, 35, 50, 85, 135):
        expected = math.degrees(math.atan(36.0 / (2 * focal)))
        assert op.half_angle_of_view_deg(focal, 36.0) == pytest.approx(expected, abs=1e-9)
    angles = [op.half_angle_of_view_deg(f, 36.0) for f in (24, 35, 50, 85, 135)]
    assert angles == sorted(angles, reverse=True)
    assert op.half_angle_of_view_deg(35, 36.0) == pytest.approx(27.2, abs=0.2)
    assert op.half_angle_of_view_deg(85, 36.0) == pytest.approx(11.9, abs=0.2)


def test_projected_height_is_inverse_in_distance_and_linear_in_focal():
    near = op.projected_height(10.0, 5.0, 50.0, 36.0, 1000.0)
    far = op.projected_height(10.0, 10.0, 50.0, 36.0, 1000.0)
    assert near == pytest.approx(2 * far, rel=1e-9)
    longer = op.projected_height(10.0, 5.0, 100.0, 36.0, 1000.0)
    assert longer == pytest.approx(2 * near, rel=1e-9)


def test_relative_size_of_two_planes_depends_on_position_not_focal():
    """H03/H04: focal length cannot change perspective from a fixed position."""

    def ratio(focal, distance):
        return op.projected_height(4.0, distance, focal, 36.0, 900.0) / op.projected_height(
            4.0, distance + 4.0, focal, 36.0, 900.0
        )

    assert ratio(35.0, 4.0) == pytest.approx(ratio(85.0, 4.0), rel=1e-9)
    assert ratio(35.0, 4.0) > ratio(35.0, 9.0)


def test_vertical_vanishing_point_approaches_frame_as_tilt_grows():
    assert op.vertical_vanishing_point(0.0, 50.0, 36.0, 900.0) is None
    distances = [
        abs(op.vertical_vanishing_point(tilt, 50.0, 36.0, 900.0))
        for tilt in (2.0, 5.0, 10.0, 20.0)
    ]
    assert distances == sorted(distances, reverse=True)
    tilt = 10.0
    expected = (50.0 / 36.0 * 900.0) / math.tan(math.radians(tilt))
    assert abs(op.vertical_vanishing_point(tilt, 50.0, 36.0, 900.0)) == pytest.approx(expected, rel=1e-9)


def test_keystone_corners_converge_only_when_tilted():
    level = op.keystone_corners(0.0, width_m=12.0, height_m=18.0, distance_m=20.0, focal_mm=35.0)
    assert level["top_width"] == pytest.approx(level["bottom_width"], rel=1e-9)
    tilted = op.keystone_corners(15.0, width_m=12.0, height_m=18.0, distance_m=20.0, focal_mm=35.0)
    assert tilted["top_width"] < tilted["bottom_width"]
    more = op.keystone_corners(25.0, width_m=12.0, height_m=18.0, distance_m=20.0, focal_mm=35.0)
    assert more["top_width"] / more["bottom_width"] < tilted["top_width"] / tilted["bottom_width"]


def test_lambert_luminance_follows_cosine_and_never_goes_negative():
    front = op.lambert_luminance(surface_azimuth_deg=0.0, light_azimuth_deg=0.0, albedo=0.5, ambient=0.0)
    oblique = op.lambert_luminance(surface_azimuth_deg=0.0, light_azimuth_deg=60.0, albedo=0.5, ambient=0.0)
    assert oblique == pytest.approx(front * math.cos(math.radians(60.0)), rel=1e-9)
    grazing = op.lambert_luminance(surface_azimuth_deg=0.0, light_azimuth_deg=90.0, albedo=0.5, ambient=0.0)
    assert grazing == pytest.approx(0.0, abs=1e-9)
    away = op.lambert_luminance(surface_azimuth_deg=0.0, light_azimuth_deg=170.0, albedo=0.5, ambient=0.12)
    assert away == pytest.approx(0.12, abs=1e-9)


def test_shadow_length_grows_without_bound_as_sun_drops():
    lengths = [op.shadow_length(10.0, altitude) for altitude in (75.0, 45.0, 20.0, 5.0)]
    assert lengths == sorted(lengths)
    assert op.shadow_length(10.0, 45.0) == pytest.approx(10.0, rel=1e-9)
    assert op.shadow_length(10.0, 0.0) == math.inf


def test_penumbra_width_scales_with_source_size_and_distance():
    sun = op.penumbra_width(0.53, 2.0)
    overcast = op.penumbra_width(60.0, 2.0)
    assert overcast > 20 * sun
    assert sun == pytest.approx(2.0 * math.tan(math.radians(0.53)), rel=1e-9)
    assert op.penumbra_width(0.53, 4.0) == pytest.approx(2 * sun, rel=1e-9)


def test_schlick_reflectance_is_f0_at_normal_and_rises_to_one_at_grazing():
    assert op.schlick_reflectance(0.0) == pytest.approx(0.04, abs=1e-9)
    values = [op.schlick_reflectance(angle) for angle in (0.0, 30.0, 60.0, 80.0, 89.0)]
    assert values == sorted(values)
    assert op.schlick_reflectance(89.9) > 0.9


def test_depth_of_field_widens_when_stopping_down_and_moving_back():
    wide = op.depth_of_field(50.0, 1.8, 3.0)
    stopped = op.depth_of_field(50.0, 11.0, 3.0)
    assert stopped["total"] > wide["total"]
    assert stopped["near"] < wide["near"] and stopped["far"] > wide["far"]
    assert op.depth_of_field(50.0, 8.0, 8.0)["total"] > op.depth_of_field(50.0, 8.0, 3.0)["total"]


def test_motion_blur_length_is_linear_in_shutter_time_and_speed():
    slow = op.motion_blur_px(walking_speed_mps=1.4, shutter_seconds=1 / 30, distance_m=6.0, focal_mm=50.0, sensor_mm=36.0, frame_px=900.0)
    fast = op.motion_blur_px(walking_speed_mps=1.4, shutter_seconds=1 / 240, distance_m=6.0, focal_mm=50.0, sensor_mm=36.0, frame_px=900.0)
    assert slow == pytest.approx(8 * fast, rel=1e-9)
    assert op.motion_blur_px(2.8, 1 / 30, 6.0, 50.0, 36.0, 900.0) == pytest.approx(2 * slow, rel=1e-9)


def test_aerial_perspective_contrast_decays_with_distance():
    contrasts = [op.aerial_contrast(distance_m=d, haze=0.35) for d in (5.0, 50.0, 200.0, 800.0)]
    assert contrasts == sorted(contrasts, reverse=True)
    assert contrasts[0] <= 1.0 and contrasts[-1] > 0.0
    assert op.aerial_contrast(200.0, haze=0.9) < op.aerial_contrast(200.0, haze=0.1)


def test_halo_radius_grows_with_source_brightness_and_shrinks_when_stopping_down():
    bright = op.halo_radius(source_luminance=1.0, exposure_ev=0.0)
    dim = op.halo_radius(source_luminance=0.25, exposure_ev=0.0)
    assert bright > dim
    assert op.halo_radius(1.0, exposure_ev=-2.0) < bright


def test_exposure_triangle_stays_balanced_when_one_stop_is_traded():
    """Opening exactly one stop and halving the time must cancel out."""
    base = op.exposure_value(aperture=8.0, shutter_seconds=1 / 125, iso=100)
    traded = op.exposure_value(aperture=8.0 / math.sqrt(2), shutter_seconds=1 / 250, iso=100)
    assert base == pytest.approx(traded, abs=1e-9)
    assert op.exposure_value(8.0, 1 / 125, 200) == pytest.approx(base - 1.0, abs=1e-9)
    assert op.exposure_value(11.0, 1 / 125, 100) > base


def test_specular_visibility_uses_the_luminance_ratio_not_reflectance_alone():
    """A shop window hides its interior in daylight even at low reflectance."""
    head_on = op.specular_visibility(op.schlick_reflectance(0.0), sky_luminance=8000.0, interior_luminance=200.0)
    grazing = op.specular_visibility(op.schlick_reflectance(75.0), sky_luminance=8000.0, interior_luminance=200.0)
    assert 0.0 < head_on < grazing < 1.0
    assert head_on > op.schlick_reflectance(0.0)
    lit_interior = op.specular_visibility(op.schlick_reflectance(0.0), sky_luminance=8000.0, interior_luminance=8000.0)
    assert lit_interior == pytest.approx(op.schlick_reflectance(0.0), abs=1e-9)
    assert op.specular_visibility(0.5, 1000.0, 0.0) == pytest.approx(1.0, abs=1e-9)


def test_nearest_full_stop_iso_snaps_to_the_real_ladder():
    assert op.nearest_iso(1477.0) == 1600
    assert op.nearest_iso(95.0) == 100
    assert op.nearest_iso(260.0) == 200
    assert op.nearest_iso(20000.0) == 12800
