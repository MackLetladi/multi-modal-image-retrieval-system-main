import os
from pathlib import Path
from PIL import Image, UnidentifiedImageError
import torch
from torch.utils.data import Dataset
from torchvision import transforms
from typing import List, Tuple, Optional
import logging
from ..config import IMAGE_SIZE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageDataset(Dataset):
    """Dataset class for loading and preprocessing images."""

    def __init__(self, data_dir: str, max_images: Optional[int] = None):
        """
        Initialize the dataset.
        
        Args:
            data_dir (str): Directory containing the images
            max_images (Optional[int]): Maximum number of images to load. If None, load all images.
            
        Raises:
            FileNotFoundError: If data_dir doesn't exist
            ValueError: If no valid images found in data_dir
        """
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Directory not found: {data_dir}")

        # Find all image files (supporting multiple formats)
        image_files = []
        for ext in [".jpg", ".jpeg", ".png"]:
            image_files.extend(self.data_dir.glob(f"*{ext}"))

        # Validate images and keep only valid ones
        self.image_paths = []
        for img_path in image_files:
            try:
                with Image.open(img_path) as img:
                    img.verify()
                self.image_paths.append(img_path)
                if max_images is not None and len(self.image_paths) >= max_images:
                    break
            except (UnidentifiedImageError, Exception) as e:
                logger.warning(f"Skipping invalid image {img_path}: {str(e)}")

        if not self.image_paths:
            raise ValueError(f"No valid images found in {data_dir}")

        logger.info(f"Loaded {len(self.image_paths)} valid images from {data_dir}")

        self.transform = transforms.Compose([
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])

    def __len__(self) -> int:
        return len(self.image_paths)

    def _load_and_preprocess_image(self, image_path: Path) -> torch.Tensor:
        """Load and preprocess an image while preserving quality."""
        try:
            with Image.open(image_path) as image:
                # Convert to RGB if needed
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Apply transformations
                if self.transform:
                    image = self.transform(image)
                return image
        except Exception as e:
            logger.error(f"Error preprocessing image {image_path}: {str(e)}")
            raise RuntimeError(f"Failed to preprocess image {image_path}")

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, str]:
        """
        Get an item from the dataset.
        
        Args:
            idx (int): Index of the item
            
        Returns:
            tuple: (preprocessed_image, image_path)
            
        Raises:
            RuntimeError: If image cannot be loaded or processed
            IndexError: If index is out of bounds
        """
        if idx < 0 or idx >= len(self.image_paths):
            raise IndexError(f"Index {idx} is out of bounds for dataset with {len(self.image_paths)} images")
            
        try:
            image_path = self.image_paths[idx]
            image = self._load_and_preprocess_image(image_path)
            return image, str(image_path)
        except Exception as e:
            error_msg = f"Error loading image {image_path}: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def get_image_paths(self) -> List[str]:
        """Get all image paths in the dataset."""
        return [str(path) for path in self.image_paths]

    def get_image_url(self, image_path: str) -> str:
        """Convert image path to absolute URL format for frontend."""
        # Convert to Path object for cross-platform compatibility
        image_path = Path(image_path)
        
        # Get the relative path from the data directory
        try:
            rel_path = image_path.relative_to(self.data_dir)
        except ValueError:
            # If path is already relative, use it as is
            rel_path = image_path.name
            
        # Convert path separators to forward slashes for URLs
        url_path = str(rel_path).replace(os.path.sep, '/')
        
        # Construct the full URL with the backend server address
        # Using environment variable or default to localhost:8000
        backend_url = os.getenv('BACKEND_URL', 'http://localhost:8000')
        return f"{backend_url}/images/{url_path}"
