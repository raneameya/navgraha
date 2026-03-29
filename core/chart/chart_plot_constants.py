from fractions import Fraction as fr

rasi_dict = {
    'Aries': '\u2648', 'Taurus': '\u2649', 'Gemini': '\u264A',
    'Cancer': '\u264B', 'Leo': '\u264C', 'Virgo': '\u264D',
    'Libra': '\u264E', 'Scorpio': '\u264F', 'Sagittarius': '\u2650',
    'Capricorn': '\u2651', 'Aquarius': '\u2652', 'Pisces': '\u2653'
}
rasi_dict = {str(i + 1):(k, v) for i, (k, v) in enumerate(rasi_dict.items())}
house_shapes = {
    # For South Indian, houses are assumed to be for a 
    # kalapurusha, because lagna is not known in advance
    'South Indian': {
        '1': [[1, 3], [1, 4], [2, 4], [2, 3]],
        '2': [[2, 3], [2, 4], [3, 4], [3, 3]],
        '3': [[3, 3], [3, 4], [4, 4], [4, 3]],
        '4': [[3, 2], [3, 3], [4, 3], [4, 2]],
        '5': [[3, 1], [3, 2], [4, 2], [4, 1]],
        '6': [[3, 0], [3, 1], [4, 1], [4, 0]],
        '7': [[2, 0], [2, 1], [3, 1], [3, 0]],
        '8': [[1, 0], [1, 1], [2, 1], [2, 0]],
        '9': [[0, 0], [0, 1], [1, 1], [1, 0]],
        '10': [[0, 1], [0, 2], [1, 2], [1, 1]],
        '11': [[0, 2], [0, 3], [1, 3], [1, 2]],
        '12': [[0, 3], [0, 4], [1, 4], [1, 3]]
    }, 
    'North Indian': {
        '1': [[2, 2], [3, 3], [2, 4], [1, 3]],
        '2': [[0, 4], [1, 3], [2, 4]],
        '3': [[0, 2], [1, 3], [0, 4]],
        '4': [[1, 1], [2, 2], [1, 3], [0, 2]],
        '5': [[0, 0], [1, 1], [0, 2]],
        '6': [[0, 0], [2, 0], [1, 1]],
        '7': [[2, 0], [3, 1], [2, 2], [1, 1]],
        '8': [[2, 0], [4, 0], [3, 1]],
        '9': [[4, 0], [3, 1], [4, 2]],
        '10': [[3, 1], [4, 2], [3, 3], [2, 2]],
        '11': [[4, 2], [4, 4], [3, 3]],
        '12': [[2, 4], [3, 3], [4, 4]]
    }
}
house_start_coords = {
    s:{
        h_num:house_shapes[s][h_num][0] for h_num in house_shapes[s]
    } for s in house_shapes
}
rasi_icon_offset = {
    'South Indian': {str(i): (0.1, 0.9) for i in list(range(1, 13, 1))}, 
    'North Indian': {
        # Same offsets for houses 2, 12
        **{str(i): (1, -0.1) for i in [2, 12]}, 
        # Same offsets for houses 3, 5
        **{str(i): (0.1, 1) for i in [3, 5]}, 
        # Same offsets for houses 6, 8
        **{str(i): (1, 0.1) for i in [6, 8]}, 
        # Same offsets for houses 9, 11
        **{str(i): (-0.1, 1) for i in [9, 11]}
    } | {
        '1': (0, 1.85), '4': (-0.85, 1), '7': (0, 0.15), '10': (0.85, 1)
    }
}
chart_frame = {
    'South Indian': [
        # Outer box
        [(0, 0), (0, 4)], [(0, 4), (4, 4)], [(4, 4), (4, 0)], [(4, 0), (0, 0)],
        # Inner box + Ju-Me houses
        [(1, 0), (1, 4)], [(0, 3), (4, 3)], [(3, 4), (3, 0)], [(4, 1), (0, 1)],
        # small segments differentiating Ma-Ve & Sa-Luminaries houses
        [(0, 2), (1, 2)], [(2, 4), (2, 3)], [(4, 2), (3, 2)], [(2, 0), (2, 1)]
    ],
    'North Indian': [
        # Outer box
        [(0, 0), (0, 4)], [(0, 4), (4, 4)], [(4, 4), (4, 0)], [(4, 0), (0, 0)],
        # Inner rhombus
        [(0, 2), (2, 4)], [(2, 4), (4, 2)], [(4, 2), (2, 0)], [(2, 0), (0, 2)],
        # Inner X
        [(0, 0), (4, 4)], [(0, 4), (4, 0)]
    ]
}
# Provide offsets for n grahas to be plotted in a house
graha_coord_offsets_raw = {
    'South Indian': {
        # South Indian houses (squares) are defined with origin (0, 0) at 
        # the bottom left corner. They have an edge length of 1
        '1': [(fr(1, 2), fr(1, 2))],
        '2': [(fr(1, 3), fr(1, 2)), (fr(2, 3), fr(1, 2))],
        '3': [
            (fr(1, 2), fr(2, 3)), (fr(1, 3), fr(1, 3)), (fr(2, 3), fr(1, 3))
        ],
        '4': [
            (fr(1, 3), fr(2, 3)), (fr(2, 3), fr(2, 3)), (fr(1, 3), fr(1, 3)), 
            (fr(2, 3), fr(1, 3))
        ],
        '5': [
            (fr(1, 3), fr(2, 3)), (fr(2, 3), fr(2, 3)), 
            (fr(1, 4), fr(1, 3)), (fr(1, 2), fr(1, 3)), (fr(3, 4), fr(1, 3))
        ],
        '6': [
            (fr(1, 4), fr(2, 3)), (fr(1, 2), fr(2, 3)), (fr(3, 4), fr(2, 3)),
            (fr(1, 4), fr(1, 3)), (fr(1, 2), fr(1, 3)), (fr(3, 4), fr(1, 3))
        ],
        '7': [
            (fr(1, 3), fr(3, 4)), (fr(2, 3), fr(3, 4)), 
            (fr(1, 3), fr(1, 2)), (fr(2, 3), fr(1, 2)), 
            (fr(1, 4), fr(1, 4)), (fr(1, 2), fr(1, 4)), (fr(3, 4), fr(1, 4))
        ],
        '8': [
            (fr(1, 3), fr(3, 4)), (fr(2, 3), fr(3, 4)), 
            (fr(1, 4), fr(1, 2)), (fr(1, 2), fr(1, 2)), (fr(3, 4), fr(1, 2)),
            (fr(1, 4), fr(1, 4)), (fr(1, 2), fr(1, 4)), (fr(3, 4), fr(1, 4))
        ],
        '9': [
            (fr(1, 4), fr(3, 4)), (fr(1, 2), fr(3, 4)), (fr(3, 4), fr(3, 4)),
            (fr(1, 4), fr(1, 2)), (fr(1, 2), fr(1, 2)), (fr(3, 4), fr(1, 2)),
            (fr(1, 4), fr(1, 4)), (fr(1, 2), fr(1, 4)), (fr(3, 4), fr(1, 4))
        ],
        # Need to be visually checked. Example needed.
        '10': [
            (fr(1, 4), fr(3, 4)), (fr(1, 2), fr(3, 4)), (fr(3, 4), fr(3, 4)),
            (fr(1, 5), fr(1, 2)), (fr(2, 5), fr(1, 2)), (fr(3, 5), fr(1, 2)), 
            (fr(4, 5), fr(1, 2)),
            (fr(1, 4), fr(1, 4)), (fr(1, 2), fr(1, 4)), (fr(3, 4), fr(1, 4))
        ]
    }, 
    'North Indian kendras': {
        # North Indian kendra houses (rhombuses) are defined with origin as 
        # the bottommost corner and the vertices (clockwise) are 
        # [(0, 0), (-1, 1), (0, 2), (1, 1)]
        '1': [(0, 1)],
        '2': [(fr(-1, 3), 1), (fr(1, 3), 1)],
        '3': [
            (fr(-1, 2), 1), (0, 1), (fr(1, 2), 1)
        ],
        '4': [
            (fr(-1, 4), fr(5, 4)), (fr(1, 4), fr(5, 4)), 
            (fr(-1, 4), fr(3, 4)), (fr(1, 4), fr(3, 4))
        ],
        '5': [
            (fr(-1, 3), fr(4, 3)), (fr(1, 3), fr(4, 3)),
            (0, 1),
            (fr(-1, 3), fr(2, 3)), (fr(1, 3), fr(2, 3))
        ],
        '6': [
            (fr(-1, 4), fr(17, 12)), (fr(1, 4), fr(17, 12)),
            (fr(-5, 12), 1), (fr(5, 12), 1),
            (fr(-1, 4), fr(7, 12)), (fr(1, 4), fr(7, 12))
        ],
        '7': [
            (fr(-1, 4), fr(17, 12)), (fr(1, 4), fr(17, 12)),
            (fr(-1, 2), 1), (0, 1), (fr(1, 2), 1),
            (fr(-1, 4), fr(7, 12)), (fr(1, 4), fr(7, 12))
        ],
        '8': [
            (fr(-1, 4), fr(17, 12)), (fr(1, 4), fr(17, 12)),
            (fr(-3, 5), 1), (fr(-1, 5), 1), (fr(1, 5), 1), (fr(3, 5), 1),
            (fr(-1, 4), fr(7, 12)), (fr(1, 4), fr(7, 12))
        ],
        '9': [
            (fr(-1, 4), fr(17, 12)), (fr(1, 4), fr(17, 12)),
            (fr(-4, 6), 1), (fr(-2, 6), 1), (0, 1), (fr(2, 6), 1), (fr(4, 6), 1),
            (fr(-1, 4), fr(7, 12)), (fr(1, 4), fr(7, 12))
        ],
        # 10 grahas in kendra needs to visually checked. Example needed
        '10': [
            (fr(-1, 4), fr(19, 12)), (fr(1, 4), fr(19, 12)),
            (fr(-1, 2), fr(14, 12)), (0, fr(14, 12)), (fr(1, 2), fr(14, 12)),
            (fr(-1, 2), fr(10, 12)), (0, fr(10, 12)), (fr(1, 2), fr(10, 12)),
            (fr(-1, 4), fr(5, 12)), (fr(1, 4), fr(5, 12))
        ]
    }, 
    'North Indian 3-5': {
        # North Indian houses (triangles) are defined with origin (0, 0) at 
        # the bottom left corner. The hypotenuse is 2 units and height is 1
        '1': [(fr(5, 12), 1)],
        '2': [(fr(1, 3), fr(2, 3)), (fr(1, 3), fr(4, 3))],
        '3': [
            (fr(1, 3), fr(2, 3)), (fr(2, 3), 1), (fr(1, 3), fr(4, 3))
        ],
        '4': [
            (fr(1, 3), fr(4, 3)), 
            (fr(1, 3), 1), (fr(2, 3), 1),
            (fr(1, 3), fr(2, 3))
        ],
        '5': [
            (fr(1, 4), fr(3, 2)), 
            (fr(1, 4), 1), (fr(1, 2), 1), (fr(3, 4), 1),
            (fr(1, 4), fr(1, 2))
        ],
        '6': [
            (fr(1, 4), fr(3, 2)), 
            (fr(1, 2), fr(5, 4)),
            (fr(1, 4), 1),
            (fr(3, 4), 1),
            (fr(1, 2), fr(3, 4)),
            (fr(1, 4), fr(1, 2))
        ],
        '7': [
            (fr(1, 4), fr(8, 5)), 
            (fr(1, 2), fr(5, 4)),
            (fr(1, 4), fr(6, 5)),
            (fr(3, 4), 1),
            (fr(1, 4), fr(4, 5)),
            (fr(1, 2), fr(3, 4)),
            (fr(1, 4), fr(2, 5))
        ],
        '8': [
            (fr(1, 4), fr(8, 5)), 
            (fr(1, 2), fr(5, 4)),
            (fr(1, 4), fr(6, 5)),
            (fr(1, 2), 1),
            (fr(3, 4), 1),
            (fr(1, 4), fr(4, 5)),
            (fr(1, 2), fr(3, 4)),
            (fr(1, 4), fr(2, 5))
        ],
        # Needs visual check. Need example
        '9': [
            (fr(1, 4), fr(8, 5)), 
            (fr(1, 2), fr(5, 4)),
            (fr(1, 4), fr(6, 5)),
            (fr(1, 2), 1),
            (fr(3, 4), fr(9, 8)),
            (fr(3, 4), fr(7, 8)),
            (fr(1, 4), fr(4, 5)),
            (fr(1, 2), fr(3, 4)),
            (fr(1, 4), fr(2, 5))
        ]
    }
}
graha_coord_offsets_raw = graha_coord_offsets_raw | {
    'North Indian 9-11': {
        k: [(-x[0], x[1]) for x in v]
        for k, v in graha_coord_offsets_raw['North Indian 3-5'].items()
    },
    'North Indian 2-12': {
        k: [(x[1], -x[0]) for x in v]
        for k, v in graha_coord_offsets_raw['North Indian 3-5'].items()
    },
    'North Indian 6-8': {
        k: [(x[1], x[0]) for x in v]
        for k, v in graha_coord_offsets_raw['North Indian 3-5'].items()
    }
}
graha_coords_offset = {
    'South Indian': {
        **{
            str(i): graha_coord_offsets_raw['South Indian'] 
            for i in list(range(1, 13, 1))
        }
    }, 
    'North Indian': {
        **{
            str(i): graha_coord_offsets_raw['North Indian kendras'] 
            for i in [1, 4, 7, 10]
        }, 
        **{
            str(i): graha_coord_offsets_raw['North Indian 3-5']
            for i in [3, 5]
        },
        **{
            str(i): graha_coord_offsets_raw['North Indian 6-8']
            for i in [6, 8]
        },
        **{
            str(i): graha_coord_offsets_raw['North Indian 9-11']
            for i in [9, 11]
        },
        **{
            str(i): graha_coord_offsets_raw['North Indian 2-12']
            for i in [2, 12]
        }
    }
}

def coord_plus(t1, t2):
    return (t1[0] + t2[0], t1[1] + t2[1])
