# import os.path
#
# from PIL import Image
#
#
# # 이미지 리사이즈
# def resize_image_from_file(file, size):
#     with Image.open(file) as image:
#         image_format = image.format
#         image_width, image_height = image.size
#         aspect_ratio = image.height / image.width
#         if image.width >= image.height:  # 가로 이미지
#             width = size
#             height = int(size * aspect_ratio)
#         else:  # 세로 이미지
#             height = size
#             width = int(size / aspect_ratio)
#
#     return image.resize((width, height), Image.Resampling.LANCZOS)
#
#
# class ImageMaker:
#     def __init__(self, source):
#         self.source_type = None
#         self.source = source
#         if self.source.startswith("http"):
#             self.source_type = "url"
#         elif os.path.isfile(source):
#             self.source_type = "file"
#
#     def get_image(self):
#         if self.source_type == "url":
#             return self.load_image_from_url()
#         elif self.source_type == "file":
#             return self.load_image_from_file()
#         else:
#             raise ValueError("Invalid source type")
#
#     def load_image_from_url(self):
#         pass
#
#     def load_image_from_file(self):
#         with Image.open(self.source) as image:
#             yield image
#
#     def resize(self, size):
#         if self.source_type == "url":
#             return self.resize_image_from_url(size)
#         elif self.source_type == "file":
#             return self.resize_image_from_file(size)
#         with Image.open(file) as image:
#             image_format = image.format
#             image_width, image_height = image.size
#             aspect_ratio = image.height / image.width
#             if image.width >= image.height:  # 가로 이미지
#                 width = size
#                 height = int(size * aspect_ratio)
#             else:  # 세로 이미지
#                 height = size
#                 width = int(size / aspect_ratio)
#
#         return image.resize((width, height), Image.Resampling.LANCZOS)