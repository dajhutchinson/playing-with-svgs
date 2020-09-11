"""
Draw a grid
Merge svgs
"""
import re
class Styler:

    # universal styler
    def __init__(self,line_colour="#000",line_width=1):
        self.line_colour=line_colour
        self.line_width=line_width

    # string used as style tag for a <line> object
    def line_style_str(self):
        return "stroke:{};stroke-width:{}".format(self.line_colour,self.line_width)

class SVGManipulator:

    # produce an image with grid lines on it
    def grid(cols=5,rows=5,img_width=100,img_height=100,styler=None,output_name="test.svg") -> (str,([],[])):
        if output_name[-4]!=".svg": output_name+=".svg"
        if styler is None: styler=Styler()

        # calculate gridline positions
        horiz_lines=[int((i/rows)*img_height) for i in range(1,rows)]
        vert_lines=[int((i/cols)*img_width) for i in range (1,cols)]
        grid_lines=(horiz_lines,vert_lines)

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
    def embed_svg(original_svg,embedding_svg,x,y,embed_width,embed_height,output_name="new_name"):

        with open(original_svg,"r") as f:
            contents=f.read()

            # split opening <svg> tag from rest of original image
            svg_tag=re.search("(<svg[^>]*>)",contents).group(0)
            rest_img=contents[len(svg_tag):]

            # calculate width and height of original image for scaling
            p_width=re.compile('viewbox=\"([0-9]+) [0-9]+ ([0-9]+) [0-9]+\"')
            original_widths=p_width.search(contents)
            p_height=re.compile('viewbox=\"[0-9]+ ([0-9]+) [0-9]+ ([0-9]+)\"')
            original_heights=p_height.search(contents)


        # calculations for scaling
        original_height=int(original_widths.group(2))-int(original_widths.group(1))
        original_width=int(original_widths.group(2))-int(original_widths.group(1))

        width=round((embed_width/original_width),2)
        height=round((embed_height/original_height),2)
        transformation_string="scale({} {}) translate({},{})".format(width,height,x,y)

        # embed image
        with open(output_name,"w+") as new_f:
            new_f.write(svg_tag+"\n")
            new_f.write('\t<image x="{}" y="{}" width="100%" height="100%" href="{}" transform="{}"></image>'.format(x,y,embedding_svg,transformation_string))
            new_f.write(rest_img)

        return

if __name__=="__main__":
    styler=Styler()
    SVGManipulator.grid(cols=2,rows=2,styler=styler,output_name="cross")

    styler.line_colour="#0f0"
    SVGManipulator.grid(cols=5,rows=5,styler=styler,output_name="green_grid")
    styler.line_colour="#00f"
    SVGManipulator.grid(cols=5,rows=0,styler=styler,output_name="blue_grid")
    styler.line_colour="#0ff"
    SVGManipulator.grid(cols=0,rows=5,styler=styler,output_name="turq_grid")

    SVGManipulator.embed_svg("cross.svg","green_grid.svg",0,0,50,50,output_name="cross.svg")
    SVGManipulator.embed_svg("cross.svg","blue_grid.svg",50,50,50,50,output_name="cross.svg")
    SVGManipulator.embed_svg("cross.svg","turq_grid.svg",0,50,50,50,output_name="cross.svg")