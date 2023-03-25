import io
from PIL import Image as Img
from django.core.files.uploadedfile import InMemoryUploadedFile



def crop_pwa_favicon(image_data, list_size):
            
        # Read file
        img = Img.open(image_data.file)
        list_crop_imgs = []

        # Crop size by list size
        for i in range(len(list_size)):
            img_crop = img.resize([list_size[i],list_size[i]])
            img_byte_arr = io.BytesIO()
            img_crop.save(img_byte_arr, img.format)

            # Convert to InMemoryUploadedFile
            # Add to list crop size
            list_crop_imgs.append(InMemoryUploadedFile(img_byte_arr, image_data.field_name, str(list_size[i]) + "_" + image_data._name, image_data.content_type, list_size[i], None))
        
        return list_crop_imgs
