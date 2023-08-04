def mark_swing_points(swing_points):
    marked_swing_points = []
    
    for i in range(len(swing_points)):
        if i == 0:
            continue
        elif i == 1:
            if swing_points[i] > swing_points[i - 1]:
                marked_swing_points.append((swing_points[i - 1], 'L'))
                marked_swing_points.append((swing_points[i], 'H'))
            else:
                marked_swing_points.append((swing_points[i - 1], 'H'))
                marked_swing_points.append((swing_points[i], 'L'))
        else:
            if swing_points[i] > swing_points[i - 1]:
                if swing_points[i] > swing_points[i - 2]:
                    marked_swing_points.append((swing_points[i], 'HH'))
                else:
                    marked_swing_points.append((swing_points[i], 'HL'))
            else:
                if swing_points[i] > swing_points[i - 2]:
                    marked_swing_points.append((swing_points[i], 'LH'))
                else:
                    marked_swing_points.append((swing_points[i], 'LL'))
    
    return marked_swing_points

swing_points = [29030.0, 29414.0, 29181.5, 29353.5, 29121.5, 29346.0, 29077.0]
marked_swing_points = mark_swing_points(swing_points)
print(marked_swing_points)
