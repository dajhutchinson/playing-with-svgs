from SVGManipulator import Styler, SVGManipulator
from math import ceil, sqrt
import re

class GridImageStyler:

    def __init__(self,svg_class=None,centre_embedding=False,align_start=True,grid_layout=None,title=None,title_class=None,grid_dy=0,feature_svg_path=None,feature_svg_pos="bot",feature_dy=0,feature_text=None,feature_text_class=None,img_width=1000,img_height=1000):
        """
        DESCRIPTION
        Holds styling options for SVGArtist.grid_image

        PARAMETERS
            svg_class (str): name for css class for plots in grid (default=`None`)
            grid_layout ((int,int)): cols x rows in grid (default=`None`)
            centre_embedding (bool): whether to centre grid images in their box
            align_start (bool): whether to align start positions of grid images
            title (str): Title of plot (default=`None`)
            title_class (str): name for css class for title (default=`None`)
            grid_dy (int): amount of vertical shift on grid (default=0)
            feature_svg_path (str): path to file to have as feature (ie larger) plot (default=`None`)
            feature_svg_pos (str): where to position feature plot "bot" or "top" (default="bot")
            feature_dy (int): amount of vertical shift on features (default=0)
            feature_text ((str,str)): text to position around feature plot (left,centre,right)(default=`None`)
            feature_text_class (str): name for css class for feature plot (default=`None`)
            img_width (int): width of produced image (default=1000)
            img_height (int): height of produced image (default=1000)
        """
        self.svg_class=svg_class

        self.centre_embedding=centre_embedding
        self.align_start=align_start
        self.grid_layout=grid_layout
        self.grid_dy=grid_dy

        self.title=title
        self.title_class=title_class

        self.feature_svg_path=feature_svg_path
        self.feature_svg_pos=feature_svg_pos
        self.feature_dy=feature_dy
        self.feature_text=feature_text
        self.feature_text_class=feature_text_class
        self.img_width=img_width
        self.img_height=img_height

class SVGArtist:

    """GRID IMAGE"""

    def grid_image(svg_paths:[str],styler=None,output_name="grid") -> dict:
        """
        DESCRIPTION
        plot several svgs on a grid, with optional title and feature plot

        PARAMETERS
            svg_paths ([str]): path to files to include in grid
            styler (GridImageStyler): define styling details about image (inc title and features)
            output_name (str): name for generated files, don't include extension  (default="grid")

        RETURNS
            {str:str} describes created files
        """
        grid_layout=styler.grid_layout if styler.grid_layout is not None else SVGArtist.__choose_grid_layout(len(svg_paths))

        svg_file_name=output_name if output_name[-4:]==".svg" else output_name+".svg"

        # blank canvas
        svg_file_name=SVGManipulator.blank(styler.img_width,styler.img_height,svg_file_name)

        # create grid images
        grid_svg_name,grid_height=SVGArtist.__create_grid_image(svg_paths,svg_file_name,styler)

        # embed grid
        svg_file_name=SVGArtist.__embed_grid(svg_file_name,grid_svg_name,styler,grid_height)

        # add title
        if styler.title is not None:
            svg_file_name=SVGArtist.__add_title(svg_file_name,styler)

        # add feature image
        svg_file_name=SVGArtist.__add_features(svg_file_name,styler)

        return {"main_svg":svg_file_name,"grid_svg":grid_svg_name}

    def __choose_grid_layout(n_plots:int) -> (int,int):
        # choose dimebsions of grid st there is sufficient space
        n_cols=ceil(sqrt(n_plots))
        n_rows=ceil(n_plots/n_cols)
        return (n_cols,n_rows)

    def __create_grid_image(svg_paths:[str],svg_file_name:str,styler:GridImageStyler) -> str:
        grid_layout=styler.grid_layout if styler.grid_layout is not None else SVGArtist.__choose_grid_layout(len(svg_paths))

        spl=svg_file_name.split(".")
        grid_svg_name=spl[0]+"_grid."+spl[1]
        grid_height=styler.img_height
        if styler.title is not None: grid_height-=.1*styler.img_height
        if styler.feature_svg_path is not None: grid_height-=.1*styler.img_height
        grid_svg_name=SVGManipulator.plot_multiple_svg_on_grid(svg_paths,align_start=styler.align_start,centre_embedding=styler.centre_embedding,cols=grid_layout[0]+1,rows=grid_layout[1]+1,img_width=styler.img_width,img_height=int(grid_height),output_name=grid_svg_name)

        return grid_svg_name,grid_height

    def __embed_grid(svg_file_name:str,grid_svg_name:str,styler:GridImageStyler,grid_height:int) -> str:
        grid_y=0
        if styler.title is not None: grid_y+=.1*styler.img_height
        if (styler.feature_svg_path is not None) and (styler.feature_svg_pos=="top"): grid_y+=.1*styler.img_height
        SVGManipulator.svg_add_object(svg_file_name,'</g>',svg_file_name)
        svg_file_name=SVGManipulator.deep_embed_svg(svg_file_name,grid_svg_name,x=0,y=grid_y,embed_width=styler.img_width,embed_height=int(grid_height),output_name=svg_file_name,dy=styler.grid_dy)
        SVGManipulator.svg_add_object(svg_file_name,'<g class="grid_group">',svg_file_name)
        return svg_file_name

    def __add_title(svg_file_name:str,styler:GridImageStyler) -> str:
        title_font_size=int(.06*styler.img_height)
        extra_details='class="{}"'.format(styler.title_class) if styler.title_class is not None else ""
        title_object_str='<text x="{}" y="{}" font-size="{}px" text-anchor="middle" {}>{}</text>'.format(int(styler.img_width/2),int(.07*styler.img_height),title_font_size,extra_details,styler.title)

        # add title object
        SVGManipulator.svg_add_object(svg_file_name,'</g>',svg_file_name)
        SVGManipulator.svg_add_object(svg_file_name,title_object_str,svg_file_name)
        SVGManipulator.svg_add_object(svg_file_name,'<g class="title_group">',svg_file_name)

        return svg_file_name

    def __add_features(svg_file_name:str,styler:GridImageStyler) -> str:
        SVGManipulator.svg_add_object(svg_file_name,"</g>",svg_file_name)
        if styler.feature_svg_path is not None:
            svg_file_name=SVGArtist.__add_features_image(svg_file_name,styler)

        # add feature text
        if styler.feature_text is not None:
            svg_file_name=SVGArtist.__add_features_text(svg_file_name,styler)

        SVGManipulator.svg_add_object(svg_file_name,'<g class="feature_group">',svg_file_name)
        return svg_file_name

    def __add_features_image(svg_file_name:str,styler:GridImageStyler) -> str:
        feat_img_x=int(styler.img_width/3)
        feat_img_y=int(.1*styler.img_height) if styler.feature_svg_pos=="top" else int(.8*styler.img_height)
        feat_img_y+=styler.feature_dy
        feat_img_width=int(styler.img_height/3)
        feat_img_height=int(.1*styler.img_height)

        svg_file_name=SVGManipulator.embed_svg(svg_file_name,styler.feature_svg_path,x=feat_img_x,y=feat_img_y,embed_width=feat_img_width,embed_height=feat_img_height,output_name=svg_file_name)

        return svg_file_name

    def __add_features_text(svg_file_name:str,styler:GridImageStyler) -> str:
        left_x=int(styler.img_width/6)
        right_x=int(styler.img_width*(5/6))

        feature_font_size=int(.06*styler.img_height)
        y=int(.1*styler.img_height) if styler.feature_svg_pos=="top" else int(.8*styler.img_height)
        y+=feature_font_size+styler.feature_dy

        extra_details='class="{}"'.format(styler.feature_text_class) if styler.feature_text_class is not None else ""
        left_text_str='<text x="{}" y="{}" font-size="{}px" text-anchor="middle" {}>{}</text>'.format(left_x,y,feature_font_size,extra_details,styler.feature_text[0])
        right_text_str='<text x="{}" y="{}" font-size="{}px" text-anchor="middle" {}>{}</text>'.format(right_x,y,feature_font_size,extra_details,styler.feature_text[1])
        SVGManipulator.svg_add_object(svg_file_name,left_text_str,svg_file_name)
        SVGManipulator.svg_add_object(svg_file_name,right_text_str,svg_file_name)
        return svg_file_name


if __name__=="__main__":
    # route_svg_names=["examples/{}_route.svg".format(i) for i in range(1,44)]
    # ele_svg_names=["examples/{}_ele.svg".format(i) for i in range(2,44)]
    #
    # styler=GridImageStyler(grid_dy=-100,feature_dy=-100,feature_svg_path=ele_svg_names[-1],feature_svg_pos="bot",feature_text=("21.1km","1:35:01"),title="Liverpool Half Marathon",title_class="title")
    # files=SVGArtist.grid_image(ele_svg_names[:-1],styler=styler,output_name="profiles")
    # print(files)
    #
    # styler.align_start=False
    # styler.centre_embedding=True
    # styler.feature_dy=0
    # styler.feature_svg_path=route_svg_names[-1]
    # files=SVGArtist.grid_image(route_svg_names[:-1],styler=styler,output_name="routes")
    # print(files)

    pass
