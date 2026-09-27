def _parse_tile_name(name: str):
    lat_base = float(name[1:3])
    lon_sign = 1.0 if name[3:4] == "E" else -1.0
    lon_base = float(name[4:7]) * lon_sign
    return lat_base, lon_base


def _add_edge(edges: dict, x1: int, y1: int, x2: int, y2: int):
    rev = f"{x2},{y2}>{x1},{y1}"
    key = f"{x1},{y1}>{x2},{y2}"
    if rev in edges:
        del edges[rev]
    else:
        edges[key] = [x1, y1, x2, y2]


def build_footprint(tiles: list):
    edges = {}
    for name in tiles:
        lat_base, lon_base = _parse_tile_name(name)
        base_x = round(lon_base * 5)
        base_y = round(lat_base * 5)
        for i in range(5):
            for j in range(5):
                min_x = base_x + j
                max_x = min_x + 1
                min_y = base_y + i
                max_y = min_y + 1
                _add_edge(edges, min_x, min_y, max_x, min_y)
                _add_edge(edges, max_x, min_y, max_x, max_y)
                _add_edge(edges, max_x, max_y, min_x, max_y)
                _add_edge(edges, min_x, max_y, min_x, min_y)

    unused = set(edges.keys())
    rings = []

    while unused:
        first_key = next(iter(unused))
        first = edges[first_key]
        unused.remove(first_key)
        ring = [[first[0], first[1]], [first[2], first[3]]]
        cx, cy = first[2], first[3]
        dx, dy = first[2] - first[0], first[3] - first[1]

        while cx != ring[0][0] or cy != ring[0][1]:
            prefs = [(-dy, dx), (dx, dy), (dy, -dx), (-dx, -dy)]
            advanced = False
            for px, py in prefs:
                tx, ty = cx + px, cy + py
                key = f"{cx},{cy}>{tx},{ty}"
                if key in unused:
                    unused.remove(key)
                    cx, cy, dx, dy = tx, ty, px, py
                    ring.append([cx, cy])
                    advanced = True
                    break
            if not advanced:
                break

        if cx == ring[0][0] and cy == ring[0][1] and len(ring) >= 4:
            rings.append([[point[0] / 5.0, point[1] / 5.0] for point in ring])

    def signed_area(ring):
        area = 0.0
        for index in range(len(ring) - 1):
            area += (
                ring[index][0] * ring[index + 1][1]
                - ring[index + 1][0] * ring[index][1]
            )
        return area / 2.0

    outers = [ring for ring in rings if signed_area(ring) > 0]
    holes = [ring for ring in rings if signed_area(ring) < 0]

    def contains_point(ring, point):
        inside = False
        previous = len(ring) - 1
        for index in range(len(ring)):
            xa, ya = ring[index]
            xb, yb = ring[previous]
            if (ya > point[1]) != (yb > point[1]) and point[0] < (
                (xb - xa) * (point[1] - ya) / (yb - ya) + xa
            ):
                inside = not inside
            previous = index
        return inside

    polygons = [[outer] for outer in outers]
    for hole in holes:
        for polygon in polygons:
            if contains_point(polygon[0], hole[0]):
                polygon.append(hole)
                break

    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {"type": "MultiPolygon", "coordinates": polygons},
            }
        ],
    }
