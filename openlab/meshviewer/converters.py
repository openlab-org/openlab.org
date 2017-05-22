
from prequeue.handlers import preview_handler, preview_converter

# converts to STL for consistency
@preview_converter(('obj', 'off', '3ds', 'ptx', 'ply', 'dae'), 'stl', keep=True)
def meshlabserver_convert(in_path, out_path):
    return check_call(["meshlabserver", "-i", in_path, "-o", out_path])


