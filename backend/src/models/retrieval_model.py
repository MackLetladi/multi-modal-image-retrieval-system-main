import torch
from transformers import CLIPProcessor, CLIPModel
import faiss
import numpy as np
from typing import List, Tuple
from ..data.data_loader import ImageDataset
import logging
from functools import lru_cache
from PIL import Image

logger = logging.getLogger(__name__)


class MultiModalRetrieval:
    """Class for multi-modal image retrieval using CLIP and FAISS."""

    def __init__(self, model_name: str, device: str):
        """
        Initialize the retrieval model.
        
        Args:
            model_name (str): Name of the CLIP model to use
            device (str): Device to run the model on ('cuda' or 'cpu')
            
        Raises:
            RuntimeError: If model loading fails
        """
        try:
            self.device = device
            logger.info(f"Loading CLIP model {model_name} on {device}")
            self.model = CLIPModel.from_pretrained(model_name).to(device)
            self.processor = CLIPProcessor.from_pretrained(model_name)
            self.model.eval()  # Set model to evaluation mode
            self.index = None
            self.image_paths = []
            self.dataset = None
        except Exception as e:
            logger.error(f"Failed to initialize model: {str(e)}")
            raise RuntimeError(f"Failed to initialize model: {str(e)}")

    def build_index(self, dataset: ImageDataset) -> None:
        """
        Build the FAISS index from the dataset.

        Args:
            dataset (ImageDataset): Dataset containing the images

        Raises:
            ValueError: If dataset is empty
            RuntimeError: If index building fails
        """
        try:
            if len(dataset) == 0:
                raise ValueError("Dataset is empty")

            self.dataset = dataset
            self.image_paths = []
            features_list = []

            logger.info(f"Building index for {len(dataset)} images")
            total_images = len(dataset)

            for idx in range(total_images):
                try:
                    image, path = dataset[idx]
                    with torch.no_grad():
                        # Move image to device
                        image = image.unsqueeze(0).to(self.device)
                        
                        # Get image features directly since image is already preprocessed
                        image_features = self.model.get_image_features(pixel_values=image)
                        features_list.append(image_features.cpu().numpy()[0])
                        self.image_paths.append(path)

                        if (idx + 1) % 100 == 0:
                            logger.info(f"Processed {idx + 1}/{total_images} images")
                except Exception as e:
                    logger.warning(f"Failed to process image at index {idx}: {str(e)}")
                    continue

            if not features_list:
                raise RuntimeError("No valid images were processed")

            # Convert features to numpy array
            features_array = np.array(features_list)

            # Normalize features
            faiss.normalize_L2(features_array)

            # Build FAISS index
            self.index = faiss.IndexFlatIP(features_array.shape[1])
            self.index.add(features_array)

            logger.info(f"Index built successfully with {len(features_list)} images")

        except Exception as e:
            logger.error(f"Failed to build index: {str(e)}")
            raise RuntimeError(f"Failed to build index: {str(e)}")

    @lru_cache(maxsize=1000)
    def _process_query(self, query_text: str) -> np.ndarray:
        """Process and cache text query features."""
        with torch.no_grad():
            inputs = self.processor(text=query_text, return_tensors="pt", padding=True)
            text_features = self.model.get_text_features(**{k: v.to(self.device) for k, v in inputs.items()})
            text_features = text_features.cpu().numpy()
            faiss.normalize_L2(text_features)
            return text_features

    def search(self, query_text: str, k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for images matching the query text.
        
        Args:
            query_text (str): Text query to search for
            k (int): Number of results to return
            
        Returns:
            List[Tuple[str, float]]: List of (image_path, similarity_score) pairs
            
        Raises:
            ValueError: If index not built or invalid parameters
            RuntimeError: If search fails
        """
        try:
            if not self.index:
                raise ValueError("Index not built. Call build_index first.")

            if not query_text.strip():
                raise ValueError("Query text cannot be empty")

            if k <= 0:
                raise ValueError("k must be positive")

            k = min(k, len(self.image_paths))  # Ensure k is not larger than dataset

            # Get text features (cached)
            text_features = self._process_query(query_text)

            # Search the index
            scores, indices = self.index.search(text_features, k)

            # Convert paths to URLs and normalize scores to [0, 1]
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.image_paths):
                    image_path = self.image_paths[idx]
                    url = self.dataset.get_image_url(image_path)
                    normalized_score = (score + 1) / 2  # Convert from [-1, 1] to [0, 1]
                    results.append((url, float(normalized_score)))

            return results

        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise RuntimeError(f"Search failed: {str(e)}")
