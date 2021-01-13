from rectpack import newPacker

rectangles = [(200, 200, "k"), (200, 200), (200,400)]
bins = [(400,400)]

packer = newPacker()

# Add the rectangles to packing queue
for r in rectangles:
	packer.add_rect(*r)

# Add the bins where the rectangles will be placed
for b in bins:
	packer.add_bin(*b)

# Start packing
packer.pack()

# Full rectangle list
all_rects = packer.rect_list()
for rect in all_rects:
    b, x, y, w, h, rid = rect
    print(b, x, y, w, h, rid)

nbins = len(packer)
print(nbins)