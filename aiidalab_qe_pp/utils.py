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


def get_jupyter_base_url():
    from notebook import notebookapp

    """Detects whether the Jupyter server is running in a multi-user setup and returns the appropriate base URL."""
    try:
        servers = list(notebookapp.list_running_servers())
        if servers:
            base_url = servers[0].get("base_url", "/")
            return base_url.rstrip("/")
    except Exception as e:
        print(f"Error detecting Jupyter server base URL: {e}")
    return ""


def download_remote_file(remote_folder, temp_file_name, file_download):
    import os
    import threading
    import time
    from IPython.display import display, Javascript

    jupyter_dir = "/home/jovyan"
    os.makedirs(jupyter_dir, exist_ok=True)

    temp_file_path = os.path.join(jupyter_dir, temp_file_name)

    try:
        remote_folder.getfile(file_download, temp_file_path)

        # Ensure file exists and is not empty
        if not os.path.exists(temp_file_path) or os.path.getsize(temp_file_path) == 0:
            print("ERROR: Downloaded file is empty.")
            return

        base_url = get_jupyter_base_url()
        jupyter_path = f"{base_url}/files/{temp_file_name}"

        js_download = Javascript(
            f"""
            var link = document.createElement('a');
            link.href = "{jupyter_path}";
            link.download = "{temp_file_name}";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            setTimeout(function() {{
                fetch("{jupyter_path}", {{ method: 'HEAD' }})
                .then(response => {{
                    if (response.status === 404) {{
                        console.log("File already deleted.");
                    }} else {{
                        fetch('/delete_file', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{'file_path': '{temp_file_path}'}})
                        }})
                        .then(response => console.log("File deletion request sent."));
                    }}
                }});
            }}, 90000);
            """
        )
        display(js_download)

        def delete_file():
            time.sleep(120)
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

        threading.Thread(target=delete_file, daemon=True).start()

    except Exception as e:
        print(f"Error: {e}")
