def first_difference(code):
    return [(code[i+1] - code[i]) % 8 for i in range(len(code) - 1)]

def rotate_to_minimal(code_diff):
    rotations = [code_diff[i:] + code_diff[:i] for i in range(len(code_diff))]
    return min(rotations)

bcc1 = [5, 5, 6, 6, 6, 0, 0, 6, 6, 7, 0, 1, 1, 1, 3, 3, 3, 2, 2, 4, 4]
bcc2 = [6, 6, 7, 7, 0, 0, 0, 2, 2, 0, 0, 1, 2, 3, 3, 3, 5, 5, 5, 4, 4]

# First differences
fd_bcc1 = first_difference(bcc1)
fd_bcc2 = first_difference(bcc2)

# Normalised (rotate to minimal lexicographic form)
norm_bcc1 = rotate_to_minimal(fd_bcc1)
norm_bcc2 = rotate_to_minimal(fd_bcc2)

# Compare
print("Are the shapes the same (after normalisation)?", norm_bcc1 == norm_bcc2)
