from prequeue.handlers import preview_handler, image_preview
from subprocess import check_call
import uuid

from . import utils


from prequeue.handlers import preview_handler, preview_converter

#@preview_handler('pov')
@preview_handler('stl')
def preview_stl_3d(ext, in_path, preview_path_prefix, thumb_path_prefix, file_path_prefix):
    # Render STL to png
    img_out_path = preview_path_prefix + ".png"
    utils.render_to_png(in_path, img_out_path)

    # Then use image_preview to make the proper sized thumbs
    result = image_preview("png", img_out_path,
                                        preview_path_prefix,
                                        thumb_path_prefix,
                                        "",
                                        preview_override={'trim': True},
                                        thumb_override={'trim': True})

    # for now just return result
    return result


def meshlab_convert(in_path, out_path):
    return check_call(["meshlabserver", "-i", in_path, "-o", out_path])


# PLY, STL, OFF, OBJ, 3DS, COLLADA, PTX, V3D, PTS, APTS, XYZ, GTS, TRI, ASC, X3D, X3DV, VRML, ALN

# converts to STL for consistency
@preview_converter(('obj', 'off', '3ds', 'ptx', 'ply', 'dae', 'xyz', 'apts', 'pts', 'tri',
                        'asc', 'x3d', 'x3dv', 'vrml', 'aln'), 'stl', keep=True)
def meshlabserver_convert(in_path, out_path):
    return check_call(["meshlabserver", "-i", in_path, "-o", out_path])


'''
@preview_handler('obj') # converts to STL for consistency
@preview_handler('off')
@preview_handler('3ds')
@preview_handler('ptx')
@preview_handler('ply')
@preview_handler('dae') # COLLADA
def convert_to_stl(ext, in_path, preview_path_prefix, thumb_path_prefix, file_path_prefix):
    """
    Use meshlab convert to first convert into a STL, then generate a thumb in
    the normal way.
    """
    stl_path = file_path_prefix + ".stl"
    meshlab_convert(in_path, stl_path)
    result = preview_stl_3d(ext, stl_path, preview_path_prefix, thumb_path_prefix, "")
    result['file'] = stl_path
    return result
'''

