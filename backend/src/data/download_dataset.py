import os
from pathlib import Path
import shutil
import logging
from tqdm import tqdm
import kagglehub

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_and_setup_dataset(
        dataset_name="alessandrasala79/ai-vs-human-generated-dataset",
        sample_size=500
):
    """
    Downloads the dataset from Kaggle and sets up the required directory structure.

    Args:
        dataset_name (str): Kaggle dataset name
        sample_size (int): Number of images to sample
    """
    try:
        # Setup paths
        base_dir = Path(__file__).parent.parent.parent
        data_dir = base_dir / "data"
        final_dir = data_dir / "images"

        # Create directories
        final_dir.mkdir(parents=True, exist_ok=True)

        # Download dataset
        logger.info(f"Downloading dataset from Kaggle: {dataset_name}")
        download_path = kagglehub.dataset_download(dataset_name)
        download_path = Path(download_path)

        # Find test_data_v2 directory
        source_dir = None
        for path in download_path.rglob("test_data_v2"):
            if path.is_dir():
                source_dir = path
                break

        if not source_dir:
            raise FileNotFoundError(f"test_data_v2 directory not found in downloaded dataset")

        # Get list of image files
        image_files = []
        for ext in [".jpg", ".jpeg", ".png"]:
            image_files.extend(list(source_dir.glob(f"*{ext}")))

        if not image_files:
            raise ValueError("No image files found in the dataset")

        # Sample images
        import random
        sampled_files = random.sample(image_files, min(sample_size, len(image_files)))

        # Copy sampled files to final directory
        logger.info(f"Copying {len(sampled_files)} images to {final_dir}")
        for src_file in tqdm(sampled_files):
            dst_file = final_dir / src_file.name
            shutil.copy2(src_file, dst_file)

        logger.info(f"Dataset setup complete. Images are available in {final_dir}")

    except Exception as e:
        logger.error(f"Error setting up dataset: {str(e)}")
        raise


if __name__ == "__main__":
    download_and_setup_dataset()
