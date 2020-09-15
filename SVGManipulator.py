"""
Draw a grid
Merge svgs
"""
import re, itertools
class Styler:

    # universal styler
    def __init__(self,line_colour="#000",line_width=1):
        self.line_colour=line_colour
        self.line_width=line_width

    # string used as style tag for a <line> object
    def line_style_str(self):
        return "stroke:{};stroke-width:{}".format(self.line_colour,self.line_width)

class SVGManipulator:

    # A blank svg with given dimensions as viewbox
    def blank(img_width=100,img_height=100,output_name="test.svg") -> str:
        svg_file=open(output_name,"w+")
        svg_file.write('<svg xmlns="http://www.w3.org/2000/svg" viewbox="0 0 {} {}" width="100%" height="100%" version="1.1">\n'.format(img_width,img_height))
        svg_file.write('</svg>')
        svg_file.close()
        return output_name

    # produce an image with grid lines on it
    def grid(cols=5,rows=5,img_width=100,img_height=100,styler=None,output_name="test.svg") -> (str,([],[])):
        if styler is None: styler=Styler()

        # calculate gridline positions
        vert_lines=SVGManipulator.__grid_lines(cols,img_width)
        horiz_lines=SVGManipulator.__grid_lines(rows,img_height)
        grid_lines=(vert_lines,horiz_lines)

        # prepare image
        svg_file=open(output_name,"w+")
        svg_file.write('<svg xmlns="http://www.w3.org/2000/svg" viewbox="0 0 {} {}" width="100%" height="100%" version="1.1">\n'.format(img_width,img_height))

        # draw grid_lines
        line_style=styler.line_style_str()
        for y in horiz_lines: svg_file.write('\t<line x1="0" y1="{0}" x2="{1}" y2="{0}" style="{2}"></line>\n'.format(y,img_width,line_style))
        for x in vert_lines: svg_file.write('\t<line x1="{0}" y1="0" x2="{0}" y2="{1}" style="{2}"></line>\n'.format(x,img_height,line_style))

        # close image
        svg_file.write('</svg>')
        svg_file.close()

        return output_name,grid_lines

    # embed one svg on top of another, at a given position
    def embed_svg(original_svg:str,embedding_svg:str,x:int,y:int,embed_width:int,embed_height:int,dx=0,dy=0,
        centre_embedding=True,output_name="new_name.svg") -> str:

        p_width=re.compile('viewbox=\"([0-9]+) [0-9]+ ([0-9]+) [0-9]+\"')
        p_height=re.compile('viewbox=\"[0-9]+ ([0-9]+) [0-9]+ ([0-9]+)\"')

        # calculations for scaling
        with open(embedding_svg,"r") as e:
            e_contents=e.read()

            image_widths=p_width.search(e_contents)
            image_heights=p_height.search(e_contents)

            image_width=int(image_widths.group(2))-int(image_widths.group(1))
            image_height=int(image_heights.group(2))-int(image_heights.group(1))

        horiz_scale=round((embed_width/image_width),3)
        vert_scale=round((embed_height/image_height),3)
        scale_factor=min(horiz_scale,vert_scale) # keep aspect ratio

        # work out transform distance if centering embedding
        if centre_embedding==True:
            vert_centre_extra =int((embed_height-(image_height*scale_factor))*.5*(1/scale_factor))
            horiz_centre_extra=int((embed_width-(image_width*scale_factor))*.5*(1/scale_factor))
        else:
            vert_centre_extra =0
            horiz_centre_extra=0

        # define object to embed
        transformation_string="scale({0} {0}) translate({1},{2})".format(scale_factor,int(x/scale_factor)+horiz_centre_extra+dx,int(y/scale_factor)+vert_centre_extra+dy)
        embedding_str='<image x="0" y="0" width="100%" height="100%" href="{}" transform="{}"></image>'.format(embedding_svg,transformation_string)

        # embed image
        SVGManipulator.svg_add_object(original_svg,embedding_str,output_name)

        return output_name

    # insert object at top of svg object
    def svg_add_object(original_svg:str,object_str:str,output_name:str) -> str:
        with open(original_svg,"r") as f:
            contents=f.read()
            svg_tag=re.search("(<svg[^>]*>)",contents).group(0)
            rest_img=contents[len(svg_tag):]

        with open(output_name,"w+") as new_f:
            new_f.write(svg_tag+"\n")
            new_f.write("\t"+object_str)
            new_f.write(rest_img)
        return output_name


    def plot_multiple_svg_on_grid(svg_names:[str],h_padding_prop=.1,cols=5,rows=5,img_width=1000,img_height=1000,styler=None,output_name="test.svg") -> str:
        output_name=SVGManipulator.blank(img_width,img_height,output_name)

        x_poss=[0]+SVGManipulator.__grid_lines(cols,img_width)
        y_poss=SVGManipulator.__grid_lines(rows,img_height)

        h_padding_val=int(h_padding_prop*x_poss[1])
        width=x_poss[1]-2*h_padding_val
        height=y_poss[0]

        for i,svg_file_name in enumerate(svg_names):
            # determine height of start position so it can be aligned
            first_y=SVGManipulator.__start_height(svg_file_name)
            # prop_first_y=0

            # determine position on grid
            grid_x=i%cols
            grid_y=i//cols

            # determine position in image
            pos_x=x_poss[grid_x]+h_padding_val
            pos_y=y_poss[grid_y]

            # embed it
            SVGManipulator.embed_svg(output_name,svg_file_name,x=pos_x,y=pos_y,embed_width=width,embed_height=height,centre_embedding=False,output_name=output_name,dy=-first_y)

        return output_name

    # returns the proportional y-coordinate of the first point in path for an svg file
    def __start_height(svg_file_name:str) -> int:
        with open(svg_file_name,"r") as f:
            contents=f.read()

            # calculate mean y_pos of first 10 readings
            first_ys=[]
            points_str=re.search('<path .* d="(.*)"',contents).group(1)
            ys=re.findall(",([0-9]*)",points_str)
            ys=[int(y) for y in ys]
            first_y=ys[0]
            min_y=min(ys); max_y=max(ys)

        print(first_y,min_y,max_y)
        # return (first_y-min_y)/(max_y-min_y)
        return first_y

    # returns the positions from the lines to define n cols/rows in a box of dim width/cols
    def __grid_lines(n:int,dim:int) -> [int]:
        poss=[int((i/n)*dim) for i in range(1,n)]
        return poss

if __name__=="__main__":
    styler=Styler()
    # NOTE I think the issue is due to paddining in the individual images
    # or to do with the transforms and where scale() is centred

    svg_names=["examples/{}.svg".format(i) for i in range(2,44)]
    output_name=SVGManipulator.plot_multiple_svg_on_grid(svg_names,h_padding_prop=.1,cols=6,rows=7+1,styler=styler)
    print(output_name)
