from wand.image import Image as WandImage

import exceptions


class ImageProcessor:
    @staticmethod
    def resize_image(in_filename: str, out_filename: str or None, size: dict):
        """
        Resize image with aspect ratio

        :param in_filename:
        :param out_filename: if not set, in_filename value used
        :param size: Width and/or height
        :return:
        """

        if not out_filename:
            out_filename = in_filename

        try:
            with WandImage(filename=in_filename) as img:
                old_size = {
                    "width": img.width,
                    "height": img.height,
                }
        except ImportError:
            raise exceptions.ImageProcessorException(
                "ImageMagick is not installed in your system; required for TRIM option."
            )
        except Exception as e:
            raise exceptions.ImageProcessorException(f"Unhandled exception: {e}")

        width, height = int(size.get("width", 0)), int(size.get("height", 0))

        if width and height and width > 0 and height > 0:
            new_size = {
                "width": width,
                "height": height
            }
        elif width and width > 0:
            resize_percent = float(float(width) / old_size["width"])
            new_size = {
                "width": width,
                "height": int(float(old_size["height"]) * resize_percent)
            }
        elif height and height > 0:
            resize_percent = float(float(height) / old_size["height"])
            new_size = {
                "width": int(float(old_size["width"]) * resize_percent),
                "height": height
            }
        else:
            raise exceptions.ImageProcessorException(f"Incorrect parameters: (width = {width}, height = {height})")
        try:
            with WandImage(filename=in_filename) as img:
                img.resize(new_size["width"], new_size["height"])
                img.save(filename=out_filename)
        except Exception as e:
            raise exceptions.ImageProcessorException(str(e))

    @staticmethod
    def trim_image(in_filename: str, out_filename: str or None):
        if not out_filename:
            out_filename = in_filename
        try:
            with WandImage(filename=in_filename) as img:
                # noinspection PyTypeChecker
                img.trim(color=None, fuzz=0)
                img.save(filename=out_filename)
        except ImportError:
            raise exceptions.ImageProcessorException(
                "ImageMagick is not installed in your system; required for TRIM option."
            )
        except Exception as e:
            raise exceptions.ImageProcessorException(f"Unhandled exception: {e}")
