# NOT USED ANY MORE I DONt THINK


import Image
import sys


fn = sys.argv[1]

im = Image.open(fn)

width, height = im.size

known_pixels = { }
# photographer deltafrut is awesome, btw
number_lines = list(filter(str.strip, """
11    1170211: Urban                                                 
12    1357412: Mixed settlements                                     
21    2822921: Rice villages                                         
22    2439522: Irrigated villages                                    
23    5066423: Rainfed villages                                      
24    1091524: Pastoral villages                                     
31    1600631: Residential irrigated croplands                       
32   15894532: Residential rainfed croplands                         
33    9675533: Populated croplands                                   
34    4071934: Remote croplands                                      
41   10447641: Residential rangelands                                
42   18773842: Populated rangelands                                  
43   27895143: Remote rangelands                                     
51    7156451: Residential woodlands                                 
52   14732552: Populated woodlands                                   
53    8011153: Remote woodlands                                      
54    8223254: Inhabited treeless and barren lands                   
61   40267961: Wild woodlands                                        
62   32495362: Wild treeless and barren lands
""".splitlines()))

types = dict([(l.split()[0], l.split()[2]) for l in number_lines])


for x in range(width):
    for y in range(height):
        p = im.getpixel((x, y))
        # p is simply the number!
        if p in known_pixels:
            # known
            pass
        else:
            print(p)
            #name = "color_%i_%i_%i" % p
            known_pixels[p] = True
            if p == 0:
                print("Blank")
            else:
                print(types[str(p)])
            #print name

def get_type(longitude, latitude):

    im = Image.open(fn)
    width, height = im.size
    # TODO Do conversion
    #x = 
    #y = 
    return types[im.getpixel]




