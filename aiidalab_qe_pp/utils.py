def resized_cube_files(folder: str = "parent_folder"):
    import os
    import numpy as np
    from pymatgen.io.common import VolumetricData
    from skimage.transform import resize
    from skimage.metrics import structural_similarity as ssim
    import re

    def optimal_scaling_factor(
        data, min_factor=0.1, max_factor=1.0, step=0.1, threshold=0.99
    ):
        """
        Determine the optimal scaling factor for downsampling 3D data without significant loss of information.
        """
        original_shape = data.shape
        best_factor = max_factor

        for factor in np.arange(max_factor, min_factor, -step):
            new_shape = tuple(max(1, int(dim * factor)) for dim in original_shape)
            resized_data = resize(
                data, new_shape, anti_aliasing=True
            )  # Upsample back to original shape for comparison
            upsampled_data = resize(resized_data, original_shape, anti_aliasing=True)
            current_ssim = ssim(
                data, upsampled_data, data_range=data.max() - data.min()
            )  # Compute structural_similarity between the original and upsampled data

            if current_ssim >= threshold:
                best_factor = factor
                # best_ssim = current_ssim
            else:
                break

        return best_factor

    results = {}
    for filename in os.listdir(folder):
        if filename.endswith(".fileout"):
            filepath = os.path.join(folder, filename)
            volumetric_data = VolumetricData.from_cube(filepath)
            data = volumetric_data.data["total"]
            scaling_factor = optimal_scaling_factor(data)
            new_shape = tuple(int(dim * scaling_factor) for dim in data.shape)
            resized_data = resize(data, new_shape, anti_aliasing=True).tolist()

            if "aiida.fileout" == filename:
                results["aiida_fileout"] = resized_data
            else:
                filename_prefix = "aiida.filplot"
                filename_suffix = "aiida.fileout"
                pattern = (
                    rf"{re.escape(filename_prefix)}_?(.*?){re.escape(filename_suffix)}"
                )
                matches = re.search(pattern, filename)
                label = matches.group(1).rstrip("_")
                results[label] = resized_data

    return results
