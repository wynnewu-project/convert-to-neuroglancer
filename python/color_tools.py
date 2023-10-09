import matplotlib as mpl
import fsleyes
import numpy as np

"""
  translate colors from 0~1 to 0~255
"""
def trans_float_color_to_uint8(colors):
  assert(len(colors) == 3 or len(colors) == 4)
  assert(np.min(colors) >= 0 and np.max(colors) <= 1)

  colors_temp = 255 * np.array(colors)
  return list(colors_temp.astype(np.uint8))

"""
  return a colormap in fsleyes or mpl
"""
def get_colour_map(cmap_name, cmaps_type):
  match cmaps_type:
    case "fsleyes":
      fsleyes.colourmaps.init()
      return fsleyes.colourmaps.getColourMap(cmap_name)
    case "mpl":
      return mpl.colormaps[cmap_name]
    case _ :
      raise ValueError(f"Not support colormap {cmap_name} in {cmaps_type}")



class ColorNormalized:

  def __init__(self, data, colormap_func, norm_func=None, reverse=False, **normalize_args):
    self.cmap = colormap_func
    self.data = data
    self.reverse = reverse
    if norm_func:
      self.set_norm(norm_func, **normalize_args)
  
  def set_norm(self, norm_function, **normalize_args):
    self.data = np.negative(self.data) if self.reverse else self.data
    vmin = np.min(self.data)
    vmax = np.max(self.data)
    print(self.data, vmin, vmax)
    self.norm = norm_function(vmin=vmin, vmax=vmax, **normalize_args)
  
  def get_colors(self):
    return [self.cmap(v)[:3] for v in self.norm(self.data)]
  
  def get_value_color(self, value):
    color = self.cmap(self.norm(value))
    return list(color)[:3]


def normalized_to_single_color_map(data, type="linearly", colormap_func=None, reverse=False, cmap_name="Blues", cmaps_type="mpl", vcenter=0):
  print('cmap_name', cmap_name)
  print('cmap_type', cmaps_type)
  cmap_func = colormapFunc if colormap_func else get_colour_map(cmap_name, cmaps_type)
  color_normalized = ColorNormalized(data, cmap_func, reverse=reverse)
  match type:
    case "log":
      assert(np.min(data) > 0)
      color_normalized.set_norm(mpl.colors.LogNorm)
    case "two_slope":
      color_normalized.set_norm(mpl.colors.TwoSlopeNorm, vcenter=vcenter)
    case _:
      color_normalized.set_norm(mpl.colors.Normalize)
  return color_normalized.get_colors()


def normalized_to_two_color_maps(data, negative_cmap="blue-lightblue", positive_cmap="red-yellow", cmaps_type="fsleyes", zero_color=[1,1,1], negative_reverse=True, positive_reverse=False):
  negative_v = data[np.where(data< 0.0)]
  positive_v = data[np.where(data> 0.0)]
  print(negative_cmap, positive_cmap, cmaps_type)

  if len(negative_v):
    n_cmap_func = get_colour_map(negative_cmap, cmaps_type)
    negative_color_normalize = ColorNormalized(negative_v, n_cmap_func, reverse=negative_reverse)
    negative_color_normalize.set_norm(mpl.colors.Normalize)
  
  if len(positive_v):
    p_cmap_func = get_colour_map(positive_cmap, cmaps_type)
    positive_color_normalize = ColorNormalized(positive_v, p_cmap_func,  reverse=positive_reverse)
    positive_color_normalize.set_norm(mpl.colors.Normalize)

  color_v = []

  for v in data:
    if v>0:
      _v = -v if positive_reverse else v
      color_v.append(positive_color_normalize.get_value_color(_v))
    elif v < 0:
      _v = -v if negative_reverse else v
      color_v.append(negative_color_normalize.get_value_color(_v))
    else:
      color_v.append(zero_color)

  return color_v

