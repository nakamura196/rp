from rectpack import *
import requests
import json

# curation_uri = "https://utda.github.io/tenjiroom/genelib_vm2020-01.json"
curation_uri = "https://mp.ex.nii.ac.jp/api/curation/json/f6930a51-74fc-4bfd-965d-7a7a6a26c569"

result = requests.get(curation_uri).json()

selections = result["selections"]

rectangles = []

bin_w = 0
bin_h = 0

count = 0

resource_map = {}

m_map = {}

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

        '''
        resource["@id"] = resource["service"]["@id"] + "/" + mid.split("#xywh=")[1] + "/full/0/default.jpg"
        del resource["service"]
        resource["width"] = w
        resource["height"] = h
        '''

        resource_map[count] = res # resource

        rectangles.append((w, h, count))

        count += 1

        bin_w += w
        bin_h += h
        
print(bin_w, bin_h)

# bin_w = int(bin_w / 3)

bins = [(bin_w, bin_h)]

# bins = [(10240, 6000)]

algos = [
    MaxRectsBl, MaxRectsBssf, MaxRectsBaf, MaxRectsBlsf, 
    # SkylineBl, SkylineBlWm, SkylineMwf, SkylineMwfl, SkylineMwfWm, SkylineMwflWm
]
sort_algos = [
    SORT_NONE
    # , SORT_AREA, SORT_PERI, SORT_DIFF, SORT_SSIDE, SORT_LSIDE, SORT_RATIO
]


r_map = {}
r_check = {}

for sort in sort_algos:

    for algo in algos:

        packer = newPacker(pack_algo=algo, sort_algo=sort, rotation=False)

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

            if w != resource["width"]:
                resource["@id"] = resource["@id"].replace("/0/default.jpg", "/90/default.jpg")
                resource["height"] = h
                resource["width"] = w

            images.append({
                "@id": manifest_uri+"/annotation/p"+str(i+1).zfill(4)+"-image",
                "@type": "oa:Annotation",
                "motivation": "sc:painting",
                "on": canvas_uri+"#xywh="+str(x)+","+str(y)+","+str(resource["width"])+","+str(resource["height"]),
                "resource": resource
            })

        images.insert(0, {
                "@id": manifest_uri+"/annotation/p"+str(0).zfill(4)+"-image",
                "@type": "oa:Annotation",
                "motivation": "sc:painting",
                "on": canvas_uri+"#xywh="+str(0)+","+str(0)+","+str(max_x)+","+str(max_y),
                "resource": {
                    "@id" : "https://free-texture.net/wp-content/uploads/old-paper02.jpg",
                    "width" : max_x,
                    "height" : max_y,
                    "@type": "dctypes:Image",
                    "format": "image/jpeg",
                }
            })

        r = max_x / max_y

        if r > 1:
            r = r - 1
        else:
            r = 1 - r

        print(algo, sort, max_x, max_y, r)

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

        r_map[r] = manifest
        r_check[r] = algo, sort

flg = True

for key in sorted(r_map):
    print(key)
    print(r_check[key])

    if flg:

        fw = open("data.json", 'w')
        json.dump(r_map[key], fw, ensure_ascii=False, indent=4,
                    sort_keys=True, separators=(',', ': '))

        flg = False

