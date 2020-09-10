"""
Draw a grid
Merge svgs
"""

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
    def grid(cols=5,rows=5,img_width=100,img_height=100,styler=None,file_name="test.svg"):
        if styler is None: styler=Styler()

        # calculate gridline positions
        horiz_lines=[int((i/rows)*img_height) for i in range(1,rows)]
        vert_lines=[int((i/cols)*img_width) for i in range (1,cols)]
        grid_lines=(horiz_lines,vert_lines)

        # prepare image
        svg_file=open(file_name,"w+")
        svg_file.write('<svg xmlns="http://www.w3.org/2000/svg" viewbox="0 0 {} {}" width="100%" height="100%" version="1.1">\n'.format(img_width,img_height))

        # draw grid_lines
        line_style=styler.line_style_str()
        for y in horiz_lines: svg_file.write('\t<line x1="0" y1="{0}" x2="{1}" y2="{0}" style="{2}"></line>\n'.format(y,img_width,line_style))
        for x in vert_lines: svg_file.write('\t<line x1="{0}" y1="0" x2="{0}" y2="{1}" style="{2}"></line>\n'.format(x,img_height,line_style))

        # close image
        svg_file.write('</svg>')
        svg_file.close()

        return file_name,grid_lines

if __name__=="__main__":
    styler=Styler(line_colour="#f00")
    file_name,grid_lines=SVGManipulator.grid(cols=10,rows=10,styler=styler)
    print(file_name,grid_lines,sep="\n")
