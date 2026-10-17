#!/usr/bin/env python3
"""Regenerate the offline route map pages from data/architecture/routes.json."""
from repair_architecture_route_ux import render_offline_maps

if __name__ == "__main__":
    print(f"{len(render_offline_maps())} offline map pages")
