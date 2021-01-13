from rectpack import *
import requests
import json

# curation_uri = "https://utda.github.io/tenjiroom/genelib_vm2020-01.json"
# curation_uri = "https://mp.ex.nii.ac.jp/api/curation/json/f6930a51-74fc-4bfd-965d-7a7a6a26c569"
curation_uri = "https://mp.ex.nii.ac.jp/api/curation/json/388b085f-772e-472d-8866-9951747c6719" #百鬼夜行

result = requests.get(curation_uri).json()

selections = result["selections"]

rectangles = []

bin_w = 0
bin_h = 0

count = 0

resource_map = {}

m_map = {}

margin = 20

for selection in selections:
    members = selection["members"]

    manifest = selection["within"]["@id"]
    
    print(manifest)

    if manifest not in m_map:

        m_map[manifest] = requests.get(manifest).json()

    mdata = m_map[manifest]

    canvases = mdata["sequences"][0]["canvases"]

    cmap = {}
    for canvas in canvases:
        cmap[canvas["@id"]] = canvas["images"][0]["resource"]

    # print(cmap)

    for member in members:

        mid = member["@id"]

        canvas = mid.split("#xywh=")[0]

        resource = cmap[canvas]

        xywh_str = ""

        if "#xywh=" not in mid:
            xywh_str = "0,0,"+str(resource["width"])+","+str(resource["height"])
        else:
            xywh_str = mid.split("#xywh=")[1]

        xywh = xywh_str.split(",")

        w = int(xywh[2])
        h = int(xywh[3])

        max = 300

        if w > h and w > max:
            h = int(h * max / w)
            w = max
        elif h > w and h > max:
            w = int(w * max / h)
            h = max

        # print(resource)

        res = {
            "@id" : resource["service"]["@id"] + "/" + xywh_str + "/"+str(w)+",/0/default.jpg",
            "width" : w,
            "height" : h,
            "@type": "dctypes:Image",
            "format": "image/jpeg",
        }

        resource_map[count] = res # resource

        rectangles.append((w + margin, h + margin, count))

        count += 1

        bin_w += w + margin
        bin_h += h + margin
        

bin_w = int(bin_w / 10)

bins = [(bin_w, bin_h)]


r_map = {}
r_check = {}

packer = newPacker(rotation=False) # sort_algo=sort, rotation=False) # pack_algo=algo, 

# Add the rectangles to packing queue
for r in rectangles:
    packer.add_rect(*r)

# Add the bins where the rectangles will be placed
for b in bins:
    packer.add_bin(*b)

# Start packing
packer.pack()

max_x = 0
max_y = 0

# Full rectangle list
all_rects = packer.rect_list()

images = []
manifest_uri = curation_uri
canvas_uri = manifest_uri + "/canvas/p1"

for i in range(len(all_rects)):
    rect = all_rects[i]

    b, x, y, w, h, rid = rect

    if max_x < x + w:
        max_x = x + w
    
    if max_y < y + h:
        max_y = y + h
        
    resource = resource_map[rid]

    if w != resource["width"] + margin:
        resource["@id"] = resource["@id"].replace("/0/default.jpg", "/90/default.jpg")
        resource["height"] = resource["height"]
        resource["width"] = resource["width"]

    images.append({
        "@id": manifest_uri+"/annotation/p"+str(i+1).zfill(4)+"-image",
        "@type": "oa:Annotation",
        "motivation": "sc:painting",
        "on": canvas_uri+"#xywh="+str(x + margin / 2)+","+str(y + margin / 2)+","+str(resource["width"])+","+str(resource["height"]),
        "resource": resource
    })

r = max_x / max_y

paper_w = 3072
paper_h = 2048

r2 = paper_w / paper_h

if r > 1: # Xのほうが長い
    rot = 0
else: # Yのほうが長い
    r = 1/r
    rot = 90

if r > r2:
    w2 = paper_w
    h2 = int(paper_h * r2 / r)
else:
    h2 = paper_h
    w2 = int(paper_w * r / r2)

images.insert(0, {
    "@id": manifest_uri+"/annotation/p"+str(0).zfill(4)+"-image",
    "@type": "oa:Annotation",
    "motivation": "sc:painting",
    "on": canvas_uri+"#xywh="+str(0)+","+str(0)+","+str(max_x)+","+str(max_y),
    "resource": {
        "@id" : "https://05r4t6462c.execute-api.us-east-1.amazonaws.com/latest/iiif/2/test%2Fold-paper02/0,0,"+str(w2)+","+str(h2)+"/full/"+str(rot)+"/default.jpg",
        "width" : max_x,
        "height" : max_y,
        "@type": "dctypes:Image",
        "format": "image/jpeg",
    }
})

canvas =  {
    "@id": canvas_uri,
    "@type": "sc:Canvas",
    "label": "[1]",
    "width": max_x,
    "height": max_y,
    "images": images,
    "thumbnail": {
        "@id": "http://codh.rois.ac.jp/software/iiif-curation-viewer/demo/iiif-curation-viewer/icp-logo.svg"
    }
}

manifest = {
    "@context": "http://iiif.io/api/presentation/2/context.json",
    "@id": manifest_uri,
    "@type": "sc:Manifest",
    "label": result["label"],
    "sequences": [
        {
        "@id": manifest_uri + "/sequence/normal",
        "@type": "sc:Sequence",
        "label": "Current Page Order",
        "canvases": [
            canvas
        ]
        }
    ]
}

fw = open("data.json", 'w')
json.dump(manifest, fw, ensure_ascii=False, indent=4,
            sort_keys=True, separators=(',', ': '))

